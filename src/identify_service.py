#!/usr/bin/env python3
"""Servicio de identificación por patrones BioCLIP-2 (CPU, robusto, always-on).
- Inferencia por foto en CPU (no compite con qwen por la GPU).
- Hilo en segundo plano: embebe especies NUEVAS (descargadas, sin prototipo) y
  recarga los patrones. Auto-mantenimiento sin GPU.
NO toca fotofauna."""
import io, json, re, threading, time, os
from pathlib import Path
import numpy as np, torch, open_clip
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

ROOT = Path("/work"); IMG = ROOT/"dataset/images"; PAT = ROOT/"dataset/patterns"
PAT.mkdir(parents=True, exist_ok=True)
MIN_IMGS = 10; BATCH = 16
torch.set_num_threads(max(2, (torch.get_num_threads() or 4)))
def _free_gpu():
    """Descarga qwen de la GPU (BioFauna tiene prioridad; qwen es puntual)."""
    try:
        import urllib.request as _u
        _u.urlopen(_u.Request('http://172.17.0.1:11434/api/generate',
            data=b'{"model":"qwen3.6-hansolo","keep_alive":0}',
            headers={'Content-Type':'application/json'}), timeout=20).read()
        print('[identify] qwen liberado (GPU para BioFauna)', flush=True)
    except Exception: pass
_free_gpu()
def _load(dev):
    m,_,pp=open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip-2"); return m.to(dev).eval(), pp
import time as _t
model=None; preprocess=None; device="cpu"
if torch.cuda.is_available():
    for _try in range(6):
        _free_gpu(); _t.sleep(1.5)   # ganar la carrera al poller de qwen (si BIOFAUNA_KEEP_QWEN no está activo)
        try:
            model,preprocess=_load("cuda")
            with torch.no_grad(): _=model.encode_image(torch.zeros(1,3,224,224).to("cuda"))
            device="cuda"; print("[identify] modelo en GPU (intento %d)"%(_try+1), flush=True); break
        except RuntimeError as e:
            print("[identify] intento GPU %d OOM: %s"%(_try+1,str(e)[:50]), flush=True)
            model=None
            try:
                import torch as _th; _th.cuda.empty_cache()
            except Exception: pass
if model is None:
    print("[identify] cargando en CPU (GPU no disponible tras reintentos)", flush=True)
    device="cpu"; model,preprocess=_load("cpu")

def _slug(n): return re.sub(r"[^a-z0-9]+","_",n.lower()).strip("_")
NAMEMAP={}
try:
    _inatcache={}
    try: _inatcache=json.load(open(ROOT/"dataset/inat_taxon_cache.json"))
    except Exception: pass
    for _s in json.load(open(ROOT/"dataset/target_species.json")):
        NAMEMAP[_slug(_s["name"])]={"scientific":_s["name"],"common":_s.get("common",""),
                                    "minka_taxon":_s.get("minka_taxon"),
                                    "inat_taxon":_inatcache.get(_s["name"]),
                                    "family":_s.get("family"),"family_minka":_s.get("family_minka"),
                                    "genus":_s.get("genus"),"genus_minka":_s.get("genus_minka")}
except Exception: pass

# Margen de similitud por debajo del cual, si el top-1 y top-2 comparten familia,
# abstenemos a nivel FAMILIA (regla de producto: Minka manda; ver BIOFAUNA.md sec. F).
FAMILY_MARGIN=float(os.environ.get("BIOFAUNA_FAMILY_MARGIN","0.06"))

_lock = threading.Lock()
_model_lock = threading.Lock()
NAMES=[]; P=np.zeros((0,512),dtype="float32")
KE=np.zeros((0,512),dtype="float32"); KY=np.zeros((0,),dtype="int32")  # kNN: todos los embeddings + su especie
NREF=np.zeros((0,),dtype="int32")   # nº de embeddings de referencia por especie (feature de calibración)
def load_protos():
    global NAMES,P,KE,KY,NREF
    names=[]; vecs=[]; allE=[]; allY=[]; nref=[]
    for d in sorted(PAT.iterdir()) if PAT.exists() else []:
        if not (d/"prototype.npy").exists(): continue
        gi=len(names); names.append(d.name); vecs.append(np.load(d/"prototype.npy").astype("float32"))
        ef=d/"embeddings.npy"
        if ef.exists():
            e=np.load(ef).astype("float32"); allE.append(e); allY.append(np.full(len(e),gi,dtype="int32"))
            nref.append(len(e))
        else:
            nref.append(0)
    with _lock:
        NAMES=names; P=(np.stack(vecs) if vecs else np.zeros((0,512),dtype="float32"))
        KE=(np.concatenate(allE) if allE else np.zeros((0,512),dtype="float32"))
        KY=(np.concatenate(allY) if allY else np.zeros((0,),dtype="int32"))
        NREF=np.array(nref,dtype="int32")
    return len(names)
load_protos()

# --- Calibración de la confianza (BIOFAUNA.md sec. L) ------------------------
# La similitud coseno NO es una probabilidad: un 0.938 puede ser un error. Este
# bloque mapea las features del kNN -> P(el top-1 de especie sea correcto), con
# los coeficientes ajustados OUT-OF-SAMPLE por scripts/fit_calib.py. Si el fichero
# no existe, el servicio funciona igual que antes (sin el campo extra).
CAL=None
def load_calib():
    global CAL
    try:
        c=json.load(open(ROOT/"dataset/calibration.json"))
        if not str(c.get("kind","")).startswith("logistic"): CAL=None; return False
        c["_coef"]=np.array(c["coef"],dtype="float32")
        c["_mu"]=np.array(c["mu"],dtype="float32"); c["_sd"]=np.array(c["sd"],dtype="float32")
        # Preprocesar niveles también (genus/family)
        for lk in c.get("levels", {}):
            lc = c["levels"][lk]
            lc["_coef"] = np.array(lc.get("coef", []), dtype="float32")
            lc["_mu"] = np.array(lc.get("mu", []), dtype="float32")
            lc["_sd"] = np.array(lc.get("sd", []), dtype="float32")
        if "isotonic" in c:
            c["_ix"]=np.array(c["isotonic"]["x"],dtype="float32")
            c["_iy"]=np.array(c["isotonic"]["y"],dtype="float32")
        CAL=c
        print("[identify] calibración %s (n=%s, ECE ver calibration.json)"%(
            c.get("kind"),c.get("n_samples")),flush=True)
        return True
    except Exception as e:
        CAL=None; print("[identify] sin calibración: %s"%str(e)[:70],flush=True); return False
load_calib()

# --- Priors geograficos (GPS+fecha) ------------------------------------------
# Si existe dataset/geo_priors.json, se usa para re-rankear candidatos
# favoreciendo especies observadas cerca de la ubicacion de la consulta.
# Suelo=1.0: sin GPS no se penaliza, solo se premia la cercania.
GEO_PRIORS = None
GEO_BOOST = float(os.environ.get("BIOFAUNA_GEO_BOOST","2.0"))
GEO_SIGMA_KM = float(os.environ.get("BIOFAUNA_GEO_SIGMA","200"))
def load_geo():
    global GEO_PRIORS
    try:
        gp = json.load(open(ROOT/"dataset/geo_priors.json"))
        GEO_PRIORS = gp
        spp = sum(1 for v in gp.values() if v)
        pts = sum(len(v) for v in gp.values())
        print(f"[identify] geo priors: {spp} especies, {pts} puntos", flush=True)
        return True
    except Exception:
        GEO_PRIORS = None
        return False
load_geo()

def _haversine_km(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos puntos (formula haversine)."""
    from math import radians, cos, sin, asin, sqrt
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(min(a, 1.0)))

def _geo_prior(slug, lat, lon):
    """Boost geografico para una especie dada la ubicacion de consulta.
    Devuelve factor >= 1.0. Sin datos -> 1.0 (sin penalizacion)."""
    if not GEO_PRIORS or not lat or not lon:
        return 1.0
    pts = GEO_PRIORS.get(slug)
    if not pts:
        return 1.0
    min_dist = min(_haversine_km(lat, lon, pt[0], pt[1]) for pt in pts)
    from math import exp
    return 1.0 + GEO_BOOST * exp(-min_dist**2 / (2 * GEO_SIGMA_KM**2))

def _calibrate(feats, level="species"):
    """Calibra P(correcto) al nivel taxonómico indicado (species/genus/family).
    Usa el modelo calibrado de calibration.json para ese nivel."""
    c=CAL
    if not c: return None
    try:
        level_cfg = c.get("levels", {}).get(level, c)  # fallback a c (top-level = species)
        x=np.array([float(feats[k]) for k in c["features"]],dtype="float32")
        z=float(((x-level_cfg["_mu"])/level_cfg["_sd"]) @ level_cfg["_coef"] + level_cfg["intercept"])
        p=1.0/(1.0+np.exp(-z))
        if level == "species" and "_ix" in c: p=float(np.interp(p,c["_ix"],c["_iy"]))
        return round(float(p),4)
    except Exception: return None
print(f"[identify] {len(NAMES)} prototipos, device={device}", flush=True)

def _embed_paths(paths):
    vecs=[]
    for i in range(0,len(paths),BATCH):
        batch=[]
        for p in paths[i:i+BATCH]:
            try: batch.append(preprocess(Image.open(p).convert("RGB")))
            except Exception: pass
        if not batch: continue
        with torch.no_grad(), _model_lock:
            f=model.encode_image(torch.stack(batch).to(device)); f=f/f.norm(dim=-1,keepdim=True)
        vecs.append(f.cpu().numpy().astype("float16"))
    return np.concatenate(vecs) if vecs else None

def _embed_new_species():
    """Embebe especies descargadas sin prototipo. Devuelve nº embebidas."""
    n=0
    for d in sorted(IMG.iterdir()) if IMG.exists() else []:
        if not d.is_dir() or not (d/".done").exists(): continue
        if (PAT/d.name/"prototype.npy").exists(): continue
        jpgs=sorted(d.glob("*.jpg"))
        if len(jpgs)<MIN_IMGS: continue
        try:
            emb=_embed_paths(jpgs)
        except RuntimeError as _e:
            print('[embed] OOM en %s -> libero GPU y reintento (%s)'%(d.name,str(_e)[:50]), flush=True)
            _free_gpu(); time.sleep(2)
            try: emb=_embed_paths(jpgs)
            except Exception as _e2:
                print('[embed] fallo %s: %s'%(d.name,str(_e2)[:60]), flush=True); continue
        if emb is None: continue
        o=PAT/d.name; o.mkdir(parents=True,exist_ok=True)
        np.save(o/"embeddings.npy",emb)
        proto=emb.astype("float32").mean(0); proto/=(np.linalg.norm(proto)+1e-9)
        np.save(o/"prototype.npy",proto.astype("float16"))
        print(f"[embed] {d.name}: {len(jpgs)} imgs -> patrón", flush=True); n+=1
    return n

def _write_eval():
    """Evaluación kNN (split 50/50 por especie): refleja lo que hace /identify."""
    names=[]; ref=[]; refy=[]; qry=[]; qyi=[]; ntot={}
    for gi,d in enumerate([d for d in sorted(PAT.iterdir()) if (d/"embeddings.npy").exists()]):
        e=np.load(d/"embeddings.npy").astype("float32")
        names.append(d.name); ntot[d.name]=len(e)
        m=max(1,len(e)//2)
        ref.append(e[:m]); refy+=[gi]*m
        qry.append((d.name,e[m:]))
    if not names: return
    R=np.concatenate(ref); RY=np.array(refy)
    per={}; correct=tot=0
    for gi,(nm,q) in enumerate(qry):
        if len(q)==0: per[nm]={"n":ntot[nm],"acc":None}; continue
        S=q@R.T; k=min(25,R.shape[0])
        topk=np.argpartition(-S,k-1,axis=1)[:,:k]
        good=0
        for r,row in enumerate(topk):
            sc={};
            for i in row:
                l=int(RY[i]); sc[l]=sc.get(l,0.0)+max(float(S[r,i]),0.0)
            if max(sc,key=sc.get)==gi: good+=1
        per[nm]={"n":ntot[nm],"correct":good,"acc":round(good/len(q),4)}; correct+=good; tot+=len(q)
    (PAT/"_eval.json").write_text(json.dumps({"overall":round(correct/max(tot,1),4),
        "n_species":len(names),"total_imgs":tot,"method":"knn","per_species":per},ensure_ascii=False))

def _bg_loop():
    while True:
        try:
            pend = any((d/".done").exists() and not (PAT/d.name/"prototype.npy").exists()
                       and len(list(d.glob("*.jpg")))>=MIN_IMGS
                       for d in (IMG.iterdir() if IMG.exists() else []) if d.is_dir())
            if pend:
                if device=="cuda": _free_gpu()   # prioridad GPU BioFauna
                if _embed_new_species()>0:
                    _write_eval(); load_protos()
        except Exception as e:
            print("[embed] error", e, flush=True)
        time.sleep(30)
def _qwen_suppressor():
    # Mantener qwen FUERA de la GPU cada 8s MIENTRAS haya backlog (prioridad
    # BioFauna; qwen puntual). Al terminar, deja de tocar qwen.
    # Desactivado con BIOFAUNA_KEEP_QWEN=true (para entrenamiento).
    if os.environ.get("BIOFAUNA_KEEP_QWEN", "").lower() in ("true", "1", "yes"):
        print("[identify] BIOFAUNA_KEEP_QWEN=true: no se libera qwen", flush=True)
        return
    while True:
        try:
            pend = any((d/".done").exists() and not (PAT/d.name/"prototype.npy").exists()
                       and len(list(d.glob("*.jpg")))>=MIN_IMGS
                       for d in (IMG.iterdir() if IMG.exists() else []) if d.is_dir())
            if pend and device=="cuda": _free_gpu()
        except Exception: pass
        time.sleep(8)
threading.Thread(target=_qwen_suppressor, daemon=True).start()
threading.Thread(target=_bg_loop, daemon=True).start()   # ARRANCAR el auto-embed (se había perdido)

app=FastAPI(title="BioFauna identify")
@app.get("/health")
def health(): return {"ok":True,"device":device,"species":len(NAMES)}
@app.get("/species")
def species(): return {"count":len(NAMES),"names":NAMES}
@app.post("/reload")
def reload_(): return {"loaded":load_protos(),"calibrated":load_calib(),"geo":load_geo()}

@app.post("/embed")
async def embed_endpoint(file: UploadFile = File(...)):
    """Embedding 768-dim float16 para una imagen (re-embedding batch)."""
    try:
        im = Image.open(io.BytesIO(await file.read())).convert("RGB")
        with torch.no_grad(), _model_lock:
            f = model.encode_image(preprocess(im).unsqueeze(0).to(device))
            f = f / f.norm(dim=-1, keepdim=True)
        return JSONResponse({"ok": True, "vec": f.cpu().numpy().astype("float16").tolist()})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.post("/identify")
async def identify(file: UploadFile = File(...), topk: int = 5,
                           lat: float = None, lon: float = None, date: str = None):
    with _lock:
        Nl=list(NAMES); E=KE; Y=KY; Pl=P; Nr=NREF
    if len(Nl)==0: return JSONResponse({"error":"sin prototipos"},status_code=503)
    im=Image.open(io.BytesIO(await file.read())).convert("RGB")
    with torch.no_grad(), _model_lock:
        f=model.encode_image(preprocess(im).unsqueeze(0).to(device)); f=f/f.norm(dim=-1,keepdim=True)
    q=f.cpu().numpy()[0]
    scores={}; maxsim={}; cnt={}; kf=None
    if E.shape[0] >= 25:   # kNN sobre todos los embeddings (mejor con especies crípticas)
        S=q@E.T; k=min(25,len(S)); top=np.argpartition(-S,k-1)[:k]
        for i in top:
            l=int(Y[i]); sc=float(S[i])
            scores[l]=scores.get(l,0.0)+max(sc,0.0); maxsim[l]=max(maxsim.get(l,-1.0),sc)
            cnt[l]=cnt.get(l,0)+1
        # Aplicar prior geografico si hay coordenadas (re-rank sin eliminar)
        if lat is not None and lon is not None and GEO_PRIORS:
            for l in list(scores.keys()):
                scores[l] *= _geo_prior(Nl[l], lat, lon)
        ranked=sorted(scores, key=lambda l:-scores[l])[:topk]
        method="knn"
        kf={"k":k,"meansim":float(S[top].mean()),"kclasses":len(scores),
            "sumsc":float(sum(scores.values()))}
    else:                  # fallback: prototipo-media
        sims=q@Pl.T
        if lat is not None and lon is not None and GEO_PRIORS:
            for i in range(len(sims)):
                sims[i] *= _geo_prior(Nl[i], lat, lon)
        ranked=list(sims.argsort()[::-1][:topk]); maxsim={int(i):float(sims[i]) for i in ranked}; method="proto"
    res=[]
    for l in ranked:
        nm=NAMEMAP.get(Nl[l],{})
        res.append({"slug":Nl[l],"species":nm.get("scientific") or Nl[l].replace('_',' ').capitalize(),
                    "common":nm.get("common",""),"inat_taxon":nm.get("inat_taxon"),
                    "minka_taxon":nm.get("minka_taxon"),          # Minka manda: ID canónico
                    "family":nm.get("family"),"family_minka":nm.get("family_minka"),
                    "genus":nm.get("genus"),"genus_minka":nm.get("genus_minka"),
                    "similarity":round(float(maxsim.get(l,0.0)),4)})
    # ── Abstención jerárquica mejorada (Sec.4 plan maestro) ──
    # Regla original: si top-1 y top-2 comparten género/familia Y el margen
    # es pequeño, abstenemos al nivel compartido. Añadimos:
    # 1) Familia compartida por top-3 (no solo top-2): más robusto.
    # 2) Familia como fallback del género (si mismo género → ya es género).
    prediction = None
    if res:
        t0 = res[0]
        prediction = {"rank": "species", "name": t0["species"], "id": t0["minka_taxon"],
                      "id_source": "minka", "inat_taxon": t0["inat_taxon"],
                      "confidence": round(float(t0["similarity"]), 4)}
        if len(res) >= 2:
            margin = res[0]["similarity"] - res[1]["similarity"]
            gen = res[0].get("genus")
            fam = res[0].get("family")
            cands = [r["species"] for r in res[:3]]
            conf = round(float(res[0]["similarity"]), 4)
            
            # Mismo género en top-2 → abstener a género
            if margin < FAMILY_MARGIN and gen and gen == res[1].get("genus"):
                prediction = {"rank": "genus", "name": gen, "id": res[0].get("genus_minka"),
                              "id_source": "minka", "confidence": conf,
                              "note": "congéneres indistinguibles; se devuelve el género",
                              "candidates": cands}
            # Misma familia en top-2 → abstener a familia
            elif margin < FAMILY_MARGIN and fam and fam == res[1].get("family"):
                prediction = {"rank": "family", "name": fam, "id": res[0].get("family_minka"),
                              "id_source": "minka", "confidence": conf,
                              "note": "misma familia indistinguible; se devuelve la familia",
                              "candidates": cands}
            # Misma familia en top-3 (aunque top-2 sea distinta) → familia
            elif margin < FAMILY_MARGIN and fam and len(res) >= 3 and fam == res[2].get("family"):
                prediction = {"rank": "family", "name": fam, "id": res[0].get("family_minka"),
                              "id_source": "minka", "confidence": conf,
                              "note": "familia mayoritaria en top-3 → familia",
                              "candidates": cands}

        # p_species calibrada (para auto-publicar)
        if CAL is not None and method == "knn" and kf:
            cal_conf = _calibrate({
                "s1": res[0]["similarity"],
                "s2": res[1]["similarity"] if len(res) > 1 else 0.0,
                "margin": (res[0]["similarity"] - res[1]["similarity"]) if len(res) > 1 else 1.0,
                "votes1": cnt.get(ranked[0], 0) / max(kf["k"], 1),
                "share1": scores.get(ranked[0], 0.0) / (kf["sumsc"] + 1e-9),
                "lognref1": float(np.log1p(int(Nr[ranked[0]]) if ranked[0] < len(Nr) else 0)),
                "meansim": kf["meansim"], "kclasses": kf["kclasses"],
                "same_genus_12": 1.0 if (len(res) > 1 and res[0].get("genus")
                                          and res[0].get("genus") == res[1].get("genus")) else 0.0,
                "same_family_12": 1.0 if (len(res) > 1 and res[0].get("family")
                                           and res[0].get("family") == res[1].get("family")) else 0.0})
            if isinstance(cal_conf, (int, float)):
                prediction["p_species"] = round(float(cal_conf), 4)
                prediction["calibrated"] = True
    return {"source":"biofauna-local","method":method,"top":res[0] if res else None,
            "prediction":prediction,"results":res}
