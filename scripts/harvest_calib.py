#!/usr/bin/env python3
"""FASE 2 · paso 1 — COSECHA del set de calibración (out-of-sample REAL).

Por qué: la similitud coseno que devuelve /identify NO es una probabilidad. Un 0.938
puede ser un error (caso Peltodoris->Chondrosia). Para auto-publicar en Minka hace falta
que "0.90" signifique "90% de acierto real" => hay que calibrar sobre datos honestos.

Honestidad del set (esto es lo que lo diferencia de _write_eval / test_head):
  - Las fotos se bajan de Minka y se EXCLUYEN por `obs id` contra `_manifest.jsonl`
    de cada especie (lista de observaciones ya usadas en la BBDD). No es la heurística
    "las recientes seguro que no están": es exclusión comprobada.
  - Se puntúa contra la BBDD COMPLETA de embeddings, igual que producción.
  - Se replica la decisión de producción (kNN k=15, agregador temperado T=0.05,
    fusión ROI 65%, boost de prototipo, prior geo).

Salida: dataset/calib_raw.jsonl (una línea por foto, resumible: se salta lo ya cosechado).
Usa GPU si hay CUDA; si no, CPU.

Uso:
  python3 scripts/harvest_calib.py [PER_SP] [MAX_SPECIES]
  python3 scripts/harvest_calib.py --trusted-only --out dataset/calib_trusted.jsonl [PER_SP]
"""
# HF_TOKEN optional (env). Rate-limits on Hugging Face without it.
import os
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from api_keys import bootstrap_hf_env
    bootstrap_hf_env(fatal=False)
except Exception:
    pass
import io, json, os, re, sys, time, urllib.request
from pathlib import Path

import numpy as np
import torch
from PIL import Image


def _crop_center_roi(im):
    """Mismo TTA que identify_service.py: crop central al 65% (ROI de producción)."""
    w, h = im.size
    nw, nh = max(1, int(w * 0.65)), max(1, int(h * 0.65))
    left, top = (w - nw) // 2, (h - nh) // 2
    return im.crop((left, top, left + nw, top + nh))

ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
IMG = Path(os.environ.get("IMAGES_DIR", str(ROOT / "dataset/images")))
_pat_candidates = [ROOT / "dataset/patterns", ROOT / "data/patterns"]
PAT = next((p for p in _pat_candidates if p.exists()), _pat_candidates[0])
CALIB_PHOTOS = ROOT / "dataset/calib_photos"
CALIB_PHOTOS.mkdir(parents=True, exist_ok=True)
OUT_DEFAULT = ROOT / "dataset/calib_raw.jsonl"

# Parse args
TRUSTED_ONLY = False
OUT = OUT_DEFAULT
PER_SP = 2
MAX_SP = 0
SLUGS_FILE = ""
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--slugs-file" and i + 1 < len(args):
        i += 1
        SLUGS_FILE = args[i]
    elif args[i] == "--trusted-only":
        TRUSTED_ONLY = True
    elif args[i] == "--out" and i + 1 < len(args):
        i += 1
        OUT = Path(args[i])
    else:
        try:
            PER_SP = int(args[i])
        except ValueError:
            pass
    i += 1
# Re-parse: positional args after flags
pos_args = [a for a in args if not a.startswith("--") and a not in ("--trusted-only", "--out")]
# Skip the value after --out
clean_args = []
skip = False
for a in args:
    if skip:
        skip = False
        continue
    if a in ("--out", "--slugs-file"):
        skip = True
        continue
    if a == "--trusted-only":
        continue
    clean_args.append(a)
if clean_args:
    PER_SP = int(clean_args[0]) if clean_args else PER_SP
    MAX_SP = int(clean_args[1]) if len(clean_args) > 1 else MAX_SP

if TRUSTED_ONLY:
    PER_SP = max(PER_SP, 5)  # mínimo 5 para set de confianza

from inference_decide import build_scores, load_geo_priors, obs_coords

log = lambda *a: print(*a, flush=True)
slug = lambda n: re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")

K = int(os.environ.get("BIOFAUNA_KNN_K", "15"))  # alineado con identify_service / inference_decide
FAMILY_MARGIN = float(os.environ.get("BIOFAUNA_FAMILY_MARGIN", os.environ.get("YOLOFAUNA_FAMILY_MARGIN", "0.08")))
GEO_PRIORS = load_geo_priors()
if GEO_PRIORS:
    log(f"[geo] {sum(1 for v in GEO_PRIORS.values() if v)} especies, "
        f"{sum(len(v) for v in GEO_PRIORS.values())} puntos")
UA = {"User-Agent": "biofauna-calib/1.0"}

# Cargar curadores de confianza + observadores excluidos (SIEMPRE, no solo --trusted-only:
# el bloqueo de excluded no depende del modo de cosecha).
TRUSTED_CURATORS = set()
EXCLUDED_OBSERVERS = set()
_tc_path = ROOT / "dataset/trusted_curators.json"
if _tc_path.exists():
    _tc = json.loads(_tc_path.read_text())
    EXCLUDED_OBSERVERS = set(_tc.get("excluded", []))
    if EXCLUDED_OBSERVERS:
        log(f"[excluded] observadores bloqueados: {sorted(EXCLUDED_OBSERVERS)}")
    if TRUSTED_ONLY:
        TRUSTED_CURATORS = set(_tc.get("curators", []))
        log(f"[trusted] curadores: {sorted(TRUSTED_CURATORS)}")
elif TRUSTED_ONLY:
    log("[trusted] ERROR: dataset/trusted_curators.json no encontrado")
    sys.exit(1)


def free_qwen():
    return False  # public reconstruction: do not touch other GPU processes


def load_ref():
    qlora_pat = os.environ.get("QLORA_PATTERNS")
    qlora_root = Path(qlora_pat) if qlora_pat else None
    names, allE, allY, nref, allP = [], [], [], [], []
    for d in sorted(PAT.iterdir()):
        if not (d / "prototype.npy").exists():
            continue
        gi = len(names)
        names.append(d.name)
        src = d
        if qlora_root and (qlora_root / d.name / "prototype.npy").exists():
            src = qlora_root / d.name
        allP.append(np.load(src / "prototype.npy").astype("float32"))
        ef = src / "embeddings.npy"
        if ef.exists():
            e = np.load(ef).astype("float32")
            allE.append(e)
            allY.append(np.full(len(e), gi, dtype="int32"))
            nref.append(len(e))
        else:
            nref.append(0)
    E = np.concatenate(allE)
    Y = np.concatenate(allY)
    P = np.stack(allP)
    if qlora_root:
        n_ov = sum(1 for n in names if (qlora_root / n / "prototype.npy").exists())
        log(f"[qlora-patterns] overlay {n_ov}/{len(names)} spp desde {qlora_root}")
    return names, E, Y, np.array(nref), P


def decide(q, E, Y, names, meta, nref, P=None, arc_weight=3.0, lat=None, lon=None):
    """k-NN + prototipo + geo (misma lógica que identify_service vía inference_decide)."""
    sc, mx, cnt, meansim = build_scores(
        q, E, Y, names, P, lat=lat, lon=lon, k=K, arc_weight=arc_weight, geo_priors=GEO_PRIORS
    )
    ranked = sorted(sc, key=lambda l: -sc[l])[:5]
    l1 = ranked[0]
    m1 = meta.get(names[l1], {})
    f = {
        "top": [names[l] for l in ranked],
        "s1": round(mx[l1], 5),
        "sc1": round(sc[l1], 5),
        "votes1": cnt[l1] / K,
        "share1": round(sc[l1] / (sum(sc.values()) + 1e-9), 5),
        "nref1": int(nref[l1]),
        "meansim": round(meansim, 5),
        "kclasses": len(sc),
    }
    if len(ranked) > 1:
        l2 = ranked[1]
        m2 = meta.get(names[l2], {})
        f["s2"] = round(mx[l2], 5)
        f["margin"] = round(mx[l1] - mx[l2], 5)
        f["same_genus_12"] = bool(m1.get("genus") and m1.get("genus") == m2.get("genus"))
        f["same_family_12"] = bool(m1.get("family") and m1.get("family") == m2.get("family"))
    else:
        f["s2"] = 0.0; f["margin"] = 1.0
        f["same_genus_12"] = f["same_family_12"] = False
    if f["margin"] < FAMILY_MARGIN and f["same_genus_12"]:
        f["rank"] = "genus"
    elif f["margin"] < FAMILY_MARGIN and f["same_family_12"]:
        f["rank"] = "family"
    else:
        f["rank"] = "species"
    return f


def _is_trusted_observation(obs, minka_taxon):
    """Verifica si la observacion tiene al menos una identificacion de confianza.
    Condiciones (las 4 deben cumplirse a la vez):
    1. user.login en TRUSTED_CURATORS
    2. own_observation == false (no auto-ID)
    3. vision == false (humano, no CV)
    4. current == true Y taxon_id coincide con minka_taxon
    """
    idents = obs.get("identifications") or []
    for ident in idents:
        user = (ident.get("user") or {}).get("login", "")
        if (user in TRUSTED_CURATORS
                and not ident.get("own_observation", False)
                and not ident.get("vision", False)
                and ident.get("current", False)
                and ident.get("taxon_id") == minka_taxon):
            return True
    return False


def main():
    global MAX_SP
    t0 = time.time()
    tgt = json.loads((ROOT / "dataset/target_species.json").read_text())
    meta = {slug(s["name"]): s for s in tgt}
    names, E, Y, nref, P = load_ref()
    log(f"[ref] {len(names)} especies · {E.shape[0]} embeddings · dim {E.shape[1]} "
        f"({time.time()-t0:.0f}s)")

    done = {}
    harvested_obs: dict[str, set] = {}
    if OUT.exists():
        for ln in OUT.read_text().splitlines():
            try:
                r = json.loads(ln)
                t = r["true"]
            except Exception:
                continue
            done[t] = done.get(t, 0) + 1
            harvested_obs.setdefault(t, set()).add(r.get("obs"))
        log(f"[resume] {sum(done.values())} muestras ya cosechadas, "
            f"{len(done)} especies tocadas")

    model, _, prep = __import__("open_clip").create_model_and_transforms(
        "hf-hub:imageomics/bioclip-2.5-vith14")
    qlora_ckpt = os.environ.get("QLORA_CKPT")
    if qlora_ckpt and Path(qlora_ckpt).is_file():
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from load_qlora_vith_torchao import load_qlora_vith
        log(f"[qlora] cargando adapters desde {qlora_ckpt}")
        dev_pre = "cuda" if torch.cuda.is_available() else "cpu"
        model, prep, qlora_meta = load_qlora_vith(qlora_ckpt, device=dev_pre)
        if MAX_SP <= 0 and qlora_meta.get("spp"):
            MAX_SP = len(qlora_meta["spp"])
            log(f"[qlora] MAX_SP={MAX_SP} (cohorte entrenamiento)")
    dev = "cpu"
    if torch.cuda.is_available():
        for intento in range(4):
            log(f"[gpu] qwen liberado: {free_qwen()}")
            time.sleep(2)
            try:
                model = model.to("cuda").eval()
                with torch.no_grad():
                    model.encode_image(torch.zeros(1, 3, 224, 224, device="cuda"))
                dev = "cuda"
                break
            except RuntimeError as e:
                log(f"[gpu] intento {intento+1} OOM: {str(e)[:60]}")
                model = model.to("cpu"); torch.cuda.empty_cache()
    if dev == "cpu":
        model = model.to("cpu").eval()
        torch.set_num_threads(max(2, (os.cpu_count() or 4) // 2))
    else:
        try:
            E = torch.from_numpy(E).float().to("cuda")
            log("[gpu] referencia kNN en GPU")
        except RuntimeError as e:
            log(f"[gpu] referencia se queda en CPU: {str(e)[:60]}")
    log(f"[model] BioCLIP-2 en {dev.upper()} ({time.time()-t0:.0f}s)")

    pool = [n for n in names
            if meta.get(n, {}).get("minka_taxon") and meta.get(n, {}).get("family")]
    if SLUGS_FILE:
        pedidos = set(json.loads(Path(SLUGS_FILE).read_text()))
        fuera = pedidos - set(pool)
        if fuera:
            log(f"[plan] fuera del pool (sin prototipo/minka_taxon/family): {len(fuera)}")
        pool = [n for n in pool if n in pedidos]
    pool.sort(key=lambda n: (meta[n].get("tier", 9), n))
    if MAX_SP:
        pool = pool[:MAX_SP]
    log(f"[plan] {len(pool)} especies × hasta {PER_SP} fotos no vistas"
        + (" (solo curadores de confianza)" if TRUSTED_ONLY else ""))

    last_free = time.time()
    fh = OUT.open("a")
    nnew = nskip = nfiltered = nexcluded = nerror = nleaked = 0
    # LEAK_SIM_THRESHOLD: por encima de esto la foto es (casi) la misma que ya
    # está en el catalogo de referencia. El chequeo de "ya visto" via
    # IMG/_manifest.jsonl esta roto para el pipeline actual (IMG apunta al
    # directorio legacy dataset/images/, que ya no se usa desde la migracion a
    # /mnt/gpu/fotofauna-images/ y no tiene manifiestos) -- confirmado el
    # 25-ago-2026: 42.7% de calib_raw_k15.jsonl resulto ser fotos ya
    # embebidas en el catalogo. Esta comprobacion por similitud de embedding
    # contra el catalogo real es la defensa que de verdad funciona.
    LEAK_SIM_THRESHOLD = 0.999
    for i, sl in enumerate(pool, 1):
        if done.get(sl, 0) >= PER_SP:
            continue
        s = meta[sl]
        mid = s["minka_taxon"]
        seen = set()
        mf = IMG / sl / "_manifest.jsonl"
        if mf.exists():
            for ln in mf.read_text().splitlines():
                try:
                    seen.add(json.loads(ln)["obs"])
                except Exception:
                    pass
        seen |= harvested_obs.get(sl, set())
        used = done.get(sl, 0)
        # Pagina TODO el histórico de Minka para la especie, no solo las 30 más
        # recientes: si el training ya consumió las más nuevas, las únicas
        # observaciones sin usar pueden estar más atrás (visto en aeolidiella_alderi:
        # 77/81 ya entrenadas, las 4 libres estaban repartidas en las primeras 60,
        # pero para otras especies pueden estar en páginas posteriores).
        page = 1
        empty_streak = 0
        obs_list: list = []
        while used < PER_SP and page <= 20:  # tope 600 obs/especie, margen de sobra
            try:
                url = ("https://api.minka-sdg.org/v1/observations?"
                       f"taxon_id={mid}&quality_grade=research&photos=true"
                       f"&per_page=30&order=desc&order_by=id&page={page}")
                page_res = json.load(urllib.request.urlopen(
                    urllib.request.Request(url, headers=UA), timeout=30))["results"]
            except Exception as e:
                log(f"  [{i}] {sl}: obs error pag {page} {str(e)[:60]}")
                break
            if not page_res:
                break
            n_unseen_page = sum(1 for o in page_res if o["id"] not in seen)
            obs_list.extend(page_res)
            empty_streak = empty_streak + 1 if n_unseen_page == 0 else 0
            page += 1
            if empty_streak >= 3:
                # 3 páginas seguidas sin nada nuevo: probablemente agotada, no
                # merece la pena seguir paginando indefinidamente.
                break
            time.sleep(0.2)

        for o in obs_list:
            if used >= PER_SP:
                break
            if o["id"] in seen:
                nskip += 1
                continue
            # Bloqueo de observador excluido (dataset/trusted_curators.json:"excluded").
            # Gana siempre, independientemente de TRUSTED_ONLY.
            if (o.get("user") or {}).get("login") in EXCLUDED_OBSERVERS:
                nexcluded += 1
                continue
            # Filtro de curadores de confianza
            if TRUSTED_ONLY and not _is_trusted_observation(o, mid):
                nfiltered += 1
                continue
            ph = (o.get("photos") or [None])[0]
            if not ph:
                continue
            try:
                jpg_path = CALIB_PHOTOS / f"{o['id']}.jpg"
                json_path = CALIB_PHOTOS / f"{o['id']}.json"
                if jpg_path.exists() and jpg_path.stat().st_size > 100:
                    raw = jpg_path.read_bytes()
                else:
                    raw = urllib.request.urlopen(urllib.request.Request(
                        ph["url"].replace("square", "medium"), headers=UA), timeout=30).read()
                    jpg_path.write_bytes(raw)
                olat, olon = obs_coords(o)
                if not json_path.exists():
                    json_path.write_text(json.dumps({"lat": olat, "lon": olon}))
                im = Image.open(io.BytesIO(raw)).convert("RGB")
                with torch.no_grad():
                    # TTA: mismo orig+crop65 promediado que identify_service.py en produccion.
                    batch = torch.stack([prep(im), prep(_crop_center_roi(im))]).to(dev)
                    q_batch = model.encode_image(batch)
                    q_batch = q_batch / q_batch.norm(dim=-1, keepdim=True)
                    q = q_batch.mean(dim=0, keepdim=True)
                    q = q / q.norm(dim=-1, keepdim=True)
                    q = (q[0].float() if torch.is_tensor(E) and E.is_cuda
                         else q.cpu().numpy()[0].astype("float32"))
                if torch.is_tensor(E) and E.is_cuda:
                    max_sim = float((E @ q).max())
                else:
                    max_sim = float((np.asarray(E) @ np.asarray(q)).max())
                if max_sim > LEAK_SIM_THRESHOLD:
                    nleaked += 1
                    continue
            except Exception as e:
                nerror += 1
                if nerror <= 3 or nerror % 10 == 0:
                    log(f"  [{i}] {sl}: descarga/embed falló obs={o['id']} "
                        f"{type(e).__name__}: {str(e)[:120]}")
                continue
            f = decide(q, E, Y, names, meta, nref, P=P, lat=olat, lon=olon)
            rec = {"true": sl, "true_genus": s.get("genus"), "true_family": s.get("family"),
                   "tier": s.get("tier", 9), "obs": o["id"], **f}
            rec["ok_species"] = (f["top"][0] == sl)
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            used += 1; nnew += 1
        fh.flush()
        if dev == "cuda" and time.time() - last_free > 60:
            free_qwen(); last_free = time.time()
        if i % 25 == 0:
            extra = f" descartadas_trusted={nfiltered}" if TRUSTED_ONLY else ""
            log(f"  [{i}/{len(pool)}] nuevas={nnew} descartadas_vistas={nskip} "
                f"descartadas_fuga={nleaked}{extra} ({time.time()-t0:.0f}s)")
        time.sleep(0.25)
    fh.close()
    log(f"=== COSECHA FIN: {nnew} muestras nuevas, {nskip} descartadas por estar "
        f"en la BBDD, {nleaked} descartadas por fuga (embedding ya en el catalogo, "
        f"sim>{LEAK_SIM_THRESHOLD}), {nexcluded} de observador excluido, {nerror} "
        f"con error de descarga/embed"
        + (f", {nfiltered} sin curador de confianza" if TRUSTED_ONLY else "") +
        f" · {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
