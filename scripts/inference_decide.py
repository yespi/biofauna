"""Lógica compartida de decisión kNN + prototipo + geo.

Usada por identify_service, harvest_calib y exp_ab_species para que la
puntuación sea idéntica en producción, cosecha y evaluación A/B.

Orden (igual que identify_service):
  1. kNN: acumular similitudes positivas de los k vecinos más cercanos
  2. Boost de prototipo: añadir sim_coseno(prototipo) × ARC_WEIGHT a TODAS las especies
  3. Geo: multiplicar por factor geo con blend (evita que GPS anule al kNN)

El blend geo (BIOFAUNA_GEO_BLEND, default 0.35) limita cuánto puede ganar una
especie solo por tener puntos GPS cercanos. Sin blend, un factor geo de 3× podía
hacer ganar a fustiaria_rubescens sobre nototeredo_norvagica aunque el kNN
favoreciera claramente a esta última (obs Costa Brava, ago-2026).
"""
from __future__ import annotations

import json
import os
from math import asin, cos, exp, radians, sin, sqrt
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

KNN_K = int(os.environ.get("BIOFAUNA_KNN_K", "15"))
KNN_TEMP = float(os.environ.get("BIOFAUNA_KNN_TEMP", "0.05"))
ARC_WEIGHT = float(os.environ.get("BIOFAUNA_ARC_WEIGHT", "3.0"))
GEO_BOOST = float(
    os.environ.get("BIOFAUNA_GEO_BOOST", os.environ.get("YOLOFAUNA_GEO_BOOST", "2.0"))
)
GEO_SIGMA_KM = float(
    os.environ.get("BIOFAUNA_GEO_SIGMA", os.environ.get("YOLOFAUNA_GEO_SIGMA", "200"))
)
# 0 = ignorar GPS; 1 = multiplicador geo completo (hasta 1+GEO_BOOST).
GEO_BLEND = float(os.environ.get("BIOFAUNA_GEO_BLEND", "0.35"))

_GEO_PRIORS: dict | None = None


def load_geo_priors(path: Path | None = None) -> dict | None:
    global _GEO_PRIORS
    if _GEO_PRIORS is not None:
        return _GEO_PRIORS
    p = path
    if p is None:
        for cand in (ROOT / "dataset/geo_priors.json", ROOT / "data/geo_priors.json"):
            if cand.exists():
                p = cand
                break
        else:
            p = ROOT / "dataset/geo_priors.json"
    try:
        _GEO_PRIORS = json.loads(p.read_text())
    except Exception:
        _GEO_PRIORS = None
    return _GEO_PRIORS


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(min(a, 1.0)))


def geo_prior_raw(slug: str, lat, lon, geo_priors: dict | None = None) -> float:
    """Factor geo sin blend: rango [1.0, 1.0+GEO_BOOST]."""
    gp = geo_priors if geo_priors is not None else load_geo_priors()
    if not gp or lat is None or lon is None:
        return 1.0
    pts = gp.get(slug)
    if not pts:
        return 1.0
    min_d = min(haversine_km(lat, lon, pt[0], pt[1]) for pt in pts)
    return 1.0 + GEO_BOOST * exp(-(min_d ** 2) / (2 * GEO_SIGMA_KM ** 2))


def geo_prior(slug: str, lat, lon, geo_priors: dict | None = None, blend: float | None = None) -> float:
    """Factor geo con blend: interpola entre 1.0 (sin efecto) y geo_prior_raw."""
    g = geo_prior_raw(slug, lat, lon, geo_priors)
    b = GEO_BLEND if blend is None else blend
    return 1.0 + b * (g - 1.0)


def knn_scores(q, E, Y, k: int | None = None):
    """Votos kNN por especie. Devuelve (scores, maxsim, counts, meansim)."""
    k = k or KNN_K
    import torch

    if torch.is_tensor(E):
        Sg = E @ q
        kk = min(k, int(Sg.shape[0]))
        vals, idx = torch.topk(Sg, kk)
        topsims = vals.float().cpu().numpy()
        top = idx.cpu().numpy()
    else:
        Ea = np.asarray(E)
        qn = np.asarray(q)
        S = qn @ Ea.T
        kk = min(k, len(S))
        top = np.argpartition(-S, kk - 1)[:kk]
        topsims = S[top]
    meansim = float(np.mean(topsims)) if len(topsims) else 0.0
    sc: dict[int, float] = {}
    mx: dict[int, float] = {}
    cnt: dict[int, int] = {}
    for j, i in enumerate(top):
        l = int(Y[i])
        s = float(topsims[j])
        pos = max(s, 0.0)
        contrib = pos if KNN_TEMP <= 0 else float(__import__("math").exp(min(pos / KNN_TEMP, 40.0)))
        sc[l] = sc.get(l, 0.0) + contrib
        mx[l] = max(mx.get(l, -1.0), s)
        cnt[l] = cnt.get(l, 0) + 1
    return sc, mx, cnt, meansim


def add_prototype_boost(sc: dict[int, float], mx: dict[int, float], q, P, arc_weight: float | None = None) -> None:
    arc_weight = ARC_WEIGHT if arc_weight is None else arc_weight
    import torch

    Pn = P.cpu().numpy() if torch.is_tensor(P) else np.asarray(P)
    qn = q.cpu().numpy() if torch.is_tensor(q) else np.asarray(q)
    proto_sims = qn @ Pn.T
    for l in range(len(proto_sims)):
        boost = max(float(proto_sims[l]), 0.0) * arc_weight
        sc[l] = sc.get(l, 0.0) + boost
        mx[l] = max(mx.get(l, -1.0), float(proto_sims[l]))


def apply_geo(sc: dict[int, float], names: list[str], lat, lon, geo_priors: dict | None = None) -> None:
    if lat is None or lon is None:
        return
    gp = geo_priors if geo_priors is not None else load_geo_priors()
    if not gp:
        return
    for l in list(sc.keys()):
        sc[l] *= geo_prior(names[l], lat, lon, gp)


def build_scores(q, E, Y, names, P, lat=None, lon=None, k: int | None = None, arc_weight: float | None = None,
                 geo_priors: dict | None = None):
    """Pipeline completo: kNN → boost prototipo → geo blend."""
    sc, mx, cnt, meansim = knn_scores(q, E, Y, k=k)
    if P is not None:
        add_prototype_boost(sc, mx, q, P, arc_weight=arc_weight)
    apply_geo(sc, names, lat, lon, geo_priors)
    return sc, mx, cnt, meansim


def top_species(q, E, Y, names, P, lat=None, lon=None, k: int | None = None, arc_weight: float | None = None,
                geo_priors: dict | None = None) -> str:
    sc, _, _, _ = build_scores(q, E, Y, names, P, lat, lon, k=k, arc_weight=arc_weight, geo_priors=geo_priors)
    return names[max(sc, key=lambda k: sc[k])]


def obs_coords(obs: dict) -> tuple[float | None, float | None]:
    """Extrae lat/lon de una observación Minka (lista o detalle).

    Minka a menudo deja latitude/longitude vacíos en el listado pero sí trae
    geojson.coordinates — misma lógica que build_geo_priors.py e identify en prod.
    """
    lat = lon = None
    raw_lat = obs.get("latitude")
    if isinstance(raw_lat, str) and "," in raw_lat:
        try:
            parts = raw_lat.split(",")
            lat, lon = float(parts[0]), float(parts[1])
        except (TypeError, ValueError):
            pass
    elif raw_lat is not None:
        try:
            lat = float(raw_lat)
            raw_lon = obs.get("longitude")
            lon = float(raw_lon) if raw_lon is not None else None
        except (TypeError, ValueError):
            lat = lon = None
    if lat is None:
        geo = obs.get("geojson") or {}
        gc = geo.get("coordinates") or []
        if len(gc) >= 2:
            try:
                lon, lat = float(gc[0]), float(gc[1])
            except (TypeError, ValueError):
                lat = lon = None
    return lat, lon
