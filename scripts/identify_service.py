#!/usr/bin/env python3
"""Public BioFauna identifier (reconstruction).

Frozen BioCLIP-2.5 ViT-H + nearest-centroid over data/patterns/*/prototype.npy.
If embeddings.npy files are present locally, uses tempered k-NN (k=15, T=0.05).
No HanSolo paths, no AutoID, no MiniCPM sidecar.
"""
from __future__ import annotations

import io, json, math, os, re
from pathlib import Path

import numpy as np
import open_clip
import torch
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parent.parent))
PAT = Path(os.environ.get("BIOFAUNA_PATTERNS", ROOT / "data" / "patterns"))
EMBED_DIM = 1024
K = int(os.environ.get("BIOFAUNA_K", "15"))
KNN_TEMP = float(os.environ.get("BIOFAUNA_KNN_TEMP", "0.05"))
KNN_CLASS_CAP = int(os.environ.get("BIOFAUNA_KNN_CLASS_CAP", "3"))  # max votes per species among the k neighbours (K23, 2026-09-22); 0 = off
FAMILY_MARGIN = float(os.environ.get("BIOFAUNA_FAMILY_MARGIN", "0.08"))
ARC_WEIGHT = float(os.environ.get("BIOFAUNA_ARC_WEIGHT", "3.0"))
CROP = float(os.environ.get("BIOFAUNA_ROI_CROP", "0.65"))

def _slug(n: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")

def _load_json(*cands: Path):
    for p in cands:
        if p.exists():
            return json.loads(p.read_text()), p
    return None, None

NAMEMAP = {}
_ts, _ = _load_json(ROOT / "dataset" / "target_species.json", ROOT / "data" / "target_species.json")
_inat, _ = _load_json(ROOT / "dataset" / "inat_taxon_cache.json", ROOT / "data" / "inat_taxon_cache.json")
_inat = _inat or {}
if isinstance(_ts, list):
    for s in _ts:
        NAMEMAP[_slug(s["name"])] = {
            "scientific": s["name"],
            "common": s.get("common", ""),
            "minka_taxon": s.get("minka_taxon"),
            "inat_taxon": _inat.get(s["name"]),
            "family": s.get("family"),
            "genus": s.get("genus"),
        }

_TAXO, _ = _load_json(ROOT / "dataset" / "taxonomic_exceptions.json")
_TAXO = _TAXO or {}

device = "cuda" if torch.cuda.is_available() else "cpu"
model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip-2.5-vith14")
model = model.to(device).eval()

NAMES, PROTOS, NREF = [], np.zeros((0, EMBED_DIM), np.float32), np.zeros((0,), np.int32)
KE, KY = np.zeros((0, EMBED_DIM), np.float32), np.zeros((0,), np.int32)

def load_gallery():
    global NAMES, PROTOS, NREF, KE, KY
    names, vecs, nref, all_e, all_y = [], [], [], [], []
    if PAT.exists():
        for d in sorted(p for p in PAT.iterdir() if p.is_dir()):
            pf = d / "prototype.npy"
            if not pf.exists():
                continue
            gi = len(names)
            names.append(d.name)
            v = np.load(pf).astype(np.float32).reshape(-1)
            if v.shape[0] != EMBED_DIM:
                continue
            n = float(np.linalg.norm(v) + 1e-9)
            vecs.append(v / n)
            ef = d / "embeddings.npy"
            if ef.exists():
                e = np.load(ef).astype(np.float32)
                if e.ndim == 1:
                    e = e.reshape(1, -1)
                e = e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-9)
                all_e.append(e)
                all_y.append(np.full(len(e), gi, np.int32))
                nref.append(len(e))
            else:
                nref.append(1)
    NAMES = names
    PROTOS = np.stack(vecs) if vecs else np.zeros((0, EMBED_DIM), np.float32)
    NREF = np.array(nref, np.int32)
    KE = np.concatenate(all_e) if all_e else np.zeros((0, EMBED_DIM), np.float32)
    KY = np.concatenate(all_y) if all_y else np.zeros((0,), np.int32)

load_gallery()

CAL = None
_cal, _ = _load_json(ROOT / "data" / "calibration.json", ROOT / "dataset" / "calibration.json", ROOT / "results" / "calibration.json")
if _cal and str(_cal.get("kind", "")).startswith("logistic"):
    _cal["_coef"] = np.array(_cal["coef"], np.float32)
    _cal["_mu"] = np.array(_cal["mu"], np.float32)
    _cal["_sd"] = np.array(_cal["sd"], np.float32)
    for lc in _cal.get("levels", {}).values():
        lc["_coef"] = np.array(lc.get("coef", []), np.float32)
        lc["_mu"] = np.array(lc.get("mu", []), np.float32)
        lc["_sd"] = np.array(lc.get("sd", []), np.float32)
    CAL = _cal

GEO, _ = _load_json(ROOT / "dataset" / "geo_priors.json", ROOT / "data" / "geo_priors.json")
GEO_BOOST = float(os.environ.get("BIOFAUNA_GEO_BOOST", "2.0"))
GEO_SIGMA = float(os.environ.get("BIOFAUNA_GEO_SIGMA", "200"))

def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(min(a, 1.0)))

def _geo(slug, lat, lon):
    if not GEO or lat is None or lon is None:
        return 1.0
    pts = GEO.get(slug) or []
    if not pts:
        return 1.0
    d = min(_haversine(lat, lon, pt[0], pt[1]) for pt in pts)
    return 1.0 + GEO_BOOST * math.exp(-(d ** 2) / (2 * GEO_SIGMA ** 2))

def _calibrate(feats):
    if not CAL:
        return None
    try:
        x = np.array([float(feats[k]) for k in CAL["features"]], np.float32)
        z = float(((x - CAL["_mu"]) / CAL["_sd"]) @ CAL["_coef"] + CAL["intercept"])
        return round(float(1.0 / (1.0 + math.exp(-z))), 4)
    except Exception:
        return None

def _embed_pil(im: Image.Image) -> np.ndarray:
    t = preprocess(im.convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        f = model.encode_image(t)
        f = f / f.norm(dim=-1, keepdim=True)
    return f.cpu().numpy().astype(np.float32)[0]

def _center_crop(im: Image.Image, frac: float) -> Image.Image:
    w, h = im.size
    nw, nh = int(w * frac), int(h * frac)
    l, t = (w - nw) // 2, (h - nh) // 2
    return im.crop((l, t, l + nw, t + nh))

def _knn_contrib(s: float) -> float:
    pos = max(float(s), 0.0)
    if KNN_TEMP <= 0:
        return pos
    return math.exp(min(pos / KNN_TEMP, 40.0))

def _abstain(top_slug, second_slug, margin):
    pairs = _TAXO.get("indistinguishable_pairs") or {}
    if second_slug and pairs.get(top_slug) == second_slug:
        return "genus"
    g = (NAMEMAP.get(top_slug) or {}).get("genus") or ""
    if g.lower() in {x.lower() for x in (_TAXO.get("abstain_genera") or [])}:
        return "genus"
    for grp in _TAXO.get("abstain_groups") or []:
        slugs = set(grp.get("slugs") or [])
        if top_slug in slugs and (not second_slug or second_slug in slugs):
            return "group"
    a, b = NAMEMAP.get(top_slug) or {}, NAMEMAP.get(second_slug) or {}
    if margin < FAMILY_MARGIN and a.get("family") and a.get("family") == b.get("family"):
        if a.get("genus") and a.get("genus") == b.get("genus"):
            return "genus"
        return "family"
    return "species"

app = FastAPI(title="BioFauna", version="2026-09-23")

@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "biofauna-public",
        "device": device,
        "species": len(NAMES),
        "knn_gallery": int(KE.shape[0]),
        "encoder": "bioclip-2.5-vith14",
        "k": K,
        "knn_temp": KNN_TEMP,
        "knn_class_cap": KNN_CLASS_CAP,
        "note": "prototype-only unless embeddings.npy present beside each prototype",
    }

@app.post("/reload")
def reload_():
    load_gallery()
    return {"ok": True, "species": len(NAMES), "knn_gallery": int(KE.shape[0])}

@app.post("/embed")
async def embed(file: UploadFile = File(...)):
    """Global L2-normalised embedding of the whole image (no ROI fusion) -- what the gallery stores.
    Used by scripts/leak_audit_calib.py for the evaluation leak gate."""
    im = Image.open(io.BytesIO(await file.read())).convert("RGB")
    v = _embed_pil(im)
    return {"vec": [float(x) for x in np.asarray(v).reshape(-1)]}

@app.post("/identify")
async def identify(file: UploadFile = File(...), topk: int = 5, lat: float | None = None, lon: float | None = None):
    if not NAMES:
        return JSONResponse({"error": "empty gallery"}, status_code=503)
    raw = await file.read()
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    q = _embed_pil(im)
    if 0.4 < CROP < 1.0:
        q2 = _embed_pil(_center_crop(im, CROP))
        q = q + q2
        q = q / (np.linalg.norm(q) + 1e-9)

    if KE.shape[0] >= K:
        sims = KE @ q
        k = min(K, KE.shape[0])
        idx = np.argpartition(-sims, k - 1)[:k]
        idx = idx[np.argsort(-sims[idx])]
        scores, taken = {}, {}
        for i in idx:
            gi = int(KY[i])
            if KNN_CLASS_CAP > 0 and taken.get(gi, 0) >= KNN_CLASS_CAP:
                continue
            taken[gi] = taken.get(gi, 0) + 1
            scores[gi] = scores.get(gi, 0.0) + _knn_contrib(float(sims[i]))
        proto_s = PROTOS @ q
        for gi, sc in list(scores.items()):
            scores[gi] = sc + ARC_WEIGHT * max(float(proto_s[gi]), 0.0)
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        s1 = float(sims[idx[0]])
        s2 = float(sims[idx[1]]) if len(idx) > 1 else 0.0
        votes1 = sum(1 for i in idx if int(KY[i]) == ranked[0][0]) / len(idx)
        kclasses = len({int(KY[i]) for i in idx})
        meansim = float(np.mean(sims[idx]))
    else:
        proto_s = PROTOS @ q
        ranked = sorted(enumerate(proto_s.tolist()), key=lambda x: -x[1])
        s1 = float(ranked[0][1])
        s2 = float(ranked[1][1]) if len(ranked) > 1 else 0.0
        votes1, kclasses, meansim = 1.0, 1, s1

    top_i = ranked[0][0]
    second_i = ranked[1][0] if len(ranked) > 1 else None
    top_slug = NAMES[top_i]
    second_slug = NAMES[second_i] if second_i is not None else None
    if lat is not None and lon is not None:
        ranked = sorted(
            ((gi, sc * _geo(NAMES[gi], lat, lon)) for gi, sc in ranked),
            key=lambda x: -x[1],
        )
        top_i, second_i = ranked[0][0], ranked[1][0] if len(ranked) > 1 else None
        top_slug = NAMES[top_i]
        second_slug = NAMES[second_i] if second_i is not None else None

    margin = s1 - s2
    rank = _abstain(top_slug, second_slug, margin)
    nm = NAMEMAP.get(top_slug) or {}
    share1 = ranked[0][1] / (sum(sc for _, sc in ranked[:10]) + 1e-9)
    feats = {
        "s1": s1, "s2": s2, "margin": margin, "votes1": votes1, "share1": share1,
        "lognref1": math.log1p(float(NREF[top_i])), "meansim": meansim,
        "kclasses": float(kclasses),
        "same_genus_12": 1.0 if (nm.get("genus") and nm.get("genus") == (NAMEMAP.get(second_slug) or {}).get("genus")) else 0.0,
        "same_family_12": 1.0 if (nm.get("family") and nm.get("family") == (NAMEMAP.get(second_slug) or {}).get("family")) else 0.0,
    }
    p = _calibrate(feats)
    cands = []
    for gi, sc in ranked[: max(1, topk)]:
        slug = NAMES[gi]
        meta = NAMEMAP.get(slug) or {}
        cands.append({
            "slug": slug,
            "scientific": meta.get("scientific", slug),
            "score": round(float(sc), 5),
            "minka_taxon": meta.get("minka_taxon"),
        })
    pred_name = nm.get("scientific", top_slug)
    if rank == "genus" and nm.get("genus"):
        pred_name = nm["genus"]
    elif rank == "family" and nm.get("family"):
        pred_name = nm["family"]
    return {
        "source": "biofauna-public",
        "method": "knn" if KE.shape[0] >= K else "prototype",
        "prediction": {
            "rank": rank,
            "slug": top_slug,
            "name": pred_name,
            "confidence": round(s1, 4),
            "p_species": p,
            "calibrated": p is not None,
        },
        "candidates": cands,
    }
