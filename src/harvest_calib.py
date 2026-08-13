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
  - Se replica EXACTAMENTE la decisión de identify_service.py (kNN k=25, score = suma de
    sims positivas, `similarity` = max sim de la clase, abstención por margen de maxsim).

Salida: dataset/calib_raw.jsonl (una línea por foto, resumible: se salta lo ya cosechado).
Usa GPU si cabe (echando a qwen, que ocupa ~11 de 12 GB) y cae a CPU si no.

Uso:
  python3 scripts/harvest_calib.py [PER_SP] [MAX_SPECIES]
  python3 scripts/harvest_calib.py --trusted-only --out dataset/calib_trusted.jsonl [PER_SP]
"""
import io, json, os, re, sys, time, urllib.request
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ROOT = Path("/work")
IMG = ROOT / "dataset/images"
PAT = ROOT / "dataset/patterns"
OUT_DEFAULT = ROOT / "dataset/calib_raw.jsonl"

# Parse args
TRUSTED_ONLY = False
OUT = OUT_DEFAULT
PER_SP = 2
MAX_SP = 0
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--trusted-only":
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
    if a == "--out":
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

K = 25
FAMILY_MARGIN = float(os.environ.get("BIOFAUNA_FAMILY_MARGIN", "0.06"))
UA = {"User-Agent": "biofauna-calib/1.0"}

log = lambda *a: print(*a, flush=True)
slug = lambda n: re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")

# Cargar curadores de confianza
TRUSTED_CURATORS = set()
if TRUSTED_ONLY:
    tc_path = ROOT / "dataset/trusted_curators.json"
    if tc_path.exists():
        TRUSTED_CURATORS = set(json.loads(tc_path.read_text()).get("curators", []))
        log(f"[trusted] curadores: {sorted(TRUSTED_CURATORS)}")
    else:
        log("[trusted] ERROR: dataset/trusted_curators.json no encontrado")
        sys.exit(1)


def free_qwen():
    try:
        urllib.request.urlopen(urllib.request.Request(
            "http://172.17.0.1:11434/api/generate",
            data=b'{"model":"qwen3.6-hansolo","keep_alive":0}',
            headers={"Content-Type": "application/json"}), timeout=20).read()
        return True
    except Exception:
        return False


def load_ref():
    names, allE, allY, nref = [], [], [], []
    for d in sorted(PAT.iterdir()):
        if not (d / "prototype.npy").exists():
            continue
        gi = len(names)
        names.append(d.name)
        ef = d / "embeddings.npy"
        if ef.exists():
            e = np.load(ef).astype("float32")
            allE.append(e)
            allY.append(np.full(len(e), gi, dtype="int32"))
            nref.append(len(e))
        else:
            nref.append(0)
    E = np.concatenate(allE)
    Y = np.concatenate(allY)
    return names, E, Y, np.array(nref)


def decide(q, E, Y, names, meta, nref):
    if torch.is_tensor(E):
        Sg = E @ q
        vals, idx = torch.topk(Sg, K)
        topsims = vals.float().cpu().numpy(); top = idx.cpu().numpy()
        meansim = float(topsims.mean())
    else:
        S = q @ E.T
        top = np.argpartition(-S, K - 1)[:K]
        topsims = S[top]; meansim = float(topsims.mean())
    sc, mx, cnt = {}, {}, {}
    for j, i in enumerate(top):
        l = int(Y[i]); s = float(topsims[j])
        sc[l] = sc.get(l, 0.0) + max(s, 0.0)
        mx[l] = max(mx.get(l, -1.0), s)
        cnt[l] = cnt.get(l, 0) + 1
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
    t0 = time.time()
    tgt = json.loads((ROOT / "dataset/target_species.json").read_text())
    meta = {slug(s["name"]): s for s in tgt}
    names, E, Y, nref = load_ref()
    log(f"[ref] {len(names)} especies · {E.shape[0]} embeddings · dim {E.shape[1]} "
        f"({time.time()-t0:.0f}s)")

    done = {}
    if OUT.exists():
        for ln in OUT.read_text().splitlines():
            try:
                done[json.loads(ln)["true"]] = done.get(json.loads(ln)["true"], 0) + 1
            except Exception:
                pass
        log(f"[resume] {sum(done.values())} muestras ya cosechadas, "
            f"{len(done)} especies tocadas")

    model, _, prep = __import__("open_clip").create_model_and_transforms(
        "hf-hub:imageomics/bioclip-2")
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
    pool.sort(key=lambda n: (meta[n].get("tier", 9), n))
    if MAX_SP:
        pool = pool[:MAX_SP]
    log(f"[plan] {len(pool)} especies × hasta {PER_SP} fotos no vistas"
        + (" (solo curadores de confianza)" if TRUSTED_ONLY else ""))

    last_free = time.time()
    fh = OUT.open("a")
    nnew = nskip = nfiltered = 0
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
        try:
            url = ("https://api.minka-sdg.org/v1/observations?"
                   f"taxon_id={mid}&quality_grade=research&photos=true"
                   "&per_page=30&order=desc&order_by=id")
            obs_list = json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=30))["results"]
        except Exception as e:
            log(f"  [{i}] {sl}: obs error {str(e)[:60]}")
            continue

        used = done.get(sl, 0)
        for o in obs_list:
            if used >= PER_SP:
                break
            if o["id"] in seen:
                nskip += 1
                continue
            # Filtro de curadores de confianza
            if TRUSTED_ONLY and not _is_trusted_observation(o, mid):
                nfiltered += 1
                continue
            ph = (o.get("photos") or [None])[0]
            if not ph:
                continue
            try:
                raw = urllib.request.urlopen(urllib.request.Request(
                    ph["url"].replace("square", "medium"), headers=UA), timeout=30).read()
                im = Image.open(io.BytesIO(raw)).convert("RGB")
                with torch.no_grad():
                    q = model.encode_image(prep(im).unsqueeze(0).to(dev))
                    q = q / q.norm(dim=-1, keepdim=True)
                    q = (q[0].float() if torch.is_tensor(E) and E.is_cuda
                         else q.cpu().numpy()[0].astype("float32"))
            except Exception:
                continue
            f = decide(q, E, Y, names, meta, nref)
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
            log(f"  [{i}/{len(pool)}] nuevas={nnew} descartadas_vistas={nskip}{extra} "
                f"({time.time()-t0:.0f}s)")
        time.sleep(0.25)
    fh.close()
    log(f"=== COSECHA FIN: {nnew} muestras nuevas, {nskip} descartadas por estar "
        f"en la BBDD" + (f", {nfiltered} sin curador de confianza" if TRUSTED_ONLY else "") +
        f" · {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
