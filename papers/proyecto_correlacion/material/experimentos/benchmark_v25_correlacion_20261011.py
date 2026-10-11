#!/usr/bin/env python3
"""Correlación v25 (11-oct-2026): 5 mejoras del benchmark Robotin. Solo CPU.

1) Modelo nulo Veech 2013 (cooccur) real en Python: pares +/-, figura obs vs esp.
2) Covariables de esfuerzo + tabla sensibilidad Johnston 2021.
3) Graphical lasso (top ~300 spp) → red residual.
4) Precisión/recall vs GloBI+literatura (Freilich), tróficas/no tróficas, IC bootstrap.
5) Análisis a 3 escalas + datos para tabla Blanchet 2020.

Salida: papers/proyecto_correlacion/experimentos/ + figuras/
"""
from __future__ import annotations

import collections
import csv
import json
import math
import os
import random
import re
import sys
from pathlib import Path

import numpy as np
from scipy.stats import hypergeom
from sklearn.covariance import GraphicalLasso

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

D = Path("/mnt/docker/biofauna/dataset")
ART_BF = Path("/mnt/docker/biofauna/artifacts")
OUT = Path("/mnt/docker/biofauna-public/papers/proyecto_correlacion/experimentos")
FIG = Path("/mnt/docker/biofauna-public/papers/proyecto_correlacion/figuras")
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

TOP_SPP = int(os.environ.get("TOP_SPP", "300"))
ALPHA = float(os.environ.get("GLASSO_ALPHA", "0.005"))
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

slug = lambda s: re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")

TROPHIC_TYPES = {
    "preyson", "preyeduponby", "eats", "eatenby", "predatorof", "preyof",
    "parasiteof", "hostof", "parasitoidof", "pathogenof",
}
NONTROPHIC_TYPES = {
    "interactswith", "adjacentto", "liveson", "livesinside", "livesnear",
    "epiphyteof", "hasepiphyte", "symbiontof", "mutualistof", "commensalof",
    "pollinates", "visitsflowersof", "flowersvisitedby", "hasvector",
}


def log(msg: str) -> None:
    print(msg, flush=True)


def load_catalog() -> dict:
    cat = json.loads((D / "target_species.json").read_text())
    return {slug(s["name"]): s for s in cat}


def build_events(info: dict):
    """Return list of event dicts with spp set and keys for scales/filters."""
    meta = json.loads((D / "enrich_obs_metadata_progress_20260919.json").read_text())
    events = collections.defaultdict(set)
    # also track photo-level co-occurrence (same observation id → species? usually 1 spp/photo)
    # For same-photo scale we use existing copresencia CSV; here build event/month matrices.
    for _src, dd in meta.items():
        for _oid, v in dd.items():
            tax = v.get("obs_taxon_name_api") or ""
            s = slug(tax)
            if " " not in tax or s not in info:
                continue
            try:
                la, lo = float(v.get("obs_lat")), float(v.get("obs_lon"))
            except (TypeError, ValueError):
                continue
            d = str(v.get("obs_date") or "")[:10]
            if len(d) < 10:
                continue
            dt = str(v.get("obs_datetime") or "")
            h = int(dt[11:13]) if len(dt) >= 13 and dt[10] == "T" else None
            obs = str(v.get("observer_id") or v.get("observer_login") or "?")
            cy01, cx01 = round(la / 0.01), round(lo / 0.01)
            slot = h // 3 if h is not None else "s"
            month = d[:7]
            key = (obs, cy01, cx01, d, slot)
            events[key].add(s)
            # stash month/cell on side via parallel structure
    ev_list = []
    for (obs, cy, cx, d, slot), spp in events.items():
        if len(spp) < 1:
            continue
        ev_list.append({
            "obs": obs,
            "cy": cy,
            "cx": cx,
            "day": d,
            "month": d[:7],
            "slot": slot,
            "spp": spp,
            "list_len": len(spp),
        })
    log(f"eventos totales (incl. 1 spp): {len(ev_list)}")
    return ev_list


def veech_pair(N: int, N1: int, N2: int, obs: int) -> dict:
    """Veech 2013 / Griffith et al. 2016 cooccur probabilities (hypergeometric)."""
    if N < 1 or N1 < 1 or N2 < 1:
        return None
    lo = max(0, N1 + N2 - N)
    hi = min(N1, N2)
    if obs < lo or obs > hi:
        # clamp for numerical safety
        obs_c = min(max(obs, lo), hi)
    else:
        obs_c = obs
    expected = N1 * N2 / N
    # P(J >= obs) and P(J <= obs)
    # hypergeom: M=N, n=N1, N=N2 draws → k co-occurrences; scipy: M, n, N
    rv = hypergeom(M=N, n=N1, N=N2)
    p_gt = float(rv.sf(obs_c - 1))  # P(X >= obs)
    p_lt = float(rv.cdf(obs_c))    # P(X <= obs)
    # classification as in cooccur
    if p_gt < 0.05 and obs_c > expected:
        kind = "positive"
        p_main = p_gt
    elif p_lt < 0.05 and obs_c < expected:
        kind = "negative"
        p_main = p_lt
    else:
        kind = "random"
        p_main = min(p_gt, p_lt)
    return {
        "obs": obs,
        "expected": expected,
        "effect": obs - expected,
        "p_gt": p_gt,
        "p_lt": p_lt,
        "p": p_main,
        "kind": kind,
    }


def sites_matrix(ev_list, spp_keep: list[str], min_spp: int = 1):
    """Binary site×species from event list; sites with >= min_spp of kept species."""
    idx = {s: i for i, s in enumerate(spp_keep)}
    rows = []
    meta = []
    for e in ev_list:
        present = [s for s in e["spp"] if s in idx]
        if len(present) < min_spp:
            continue
        row = np.zeros(len(spp_keep), dtype=np.uint8)
        for s in present:
            row[idx[s]] = 1
        rows.append(row)
        meta.append(e)
    if not rows:
        return np.zeros((0, len(spp_keep)), dtype=np.uint8), []
    return np.vstack(rows), meta


def run_veech_all(X: np.ndarray, spp: list[str], min_obs: int = 1) -> list[dict]:
    N = X.shape[0]
    occ = X.sum(axis=0).astype(np.int64)
    co = (X.T @ X).astype(np.int64)  # co-occurrence counts
    rows = []
    S = len(spp)
    for i in range(S):
        if occ[i] < min_obs:
            continue
        for j in range(i + 1, S):
            if occ[j] < min_obs:
                continue
            o = int(co[i, j])
            r = veech_pair(N, int(occ[i]), int(occ[j]), o)
            if r is None:
                continue
            rows.append({
                "a": spp[i], "b": spp[j],
                "N": N, "Na": int(occ[i]), "Nb": int(occ[j]),
                **r,
            })
    return rows


def bh_fdr(rows: list[dict], pkey: str = "p") -> list[dict]:
    if not rows:
        return rows
    order = sorted(range(len(rows)), key=lambda i: rows[i][pkey])
    m = len(rows)
    q = [1.0] * m
    for rank, i in enumerate(order, 1):
        q[i] = min(1.0, rows[i][pkey] * m / rank)
    for k in range(m - 2, -1, -1):
        i, j = order[k], order[k + 1]
        q[i] = min(q[i], q[j])
    out = []
    for i, r in enumerate(rows):
        rr = dict(r)
        rr["q"] = q[i]
        out.append(rr)
    return out


def spatial_subsample(ev_list: list[dict]) -> list[dict]:
    """1 event per cell 0.01° × day (Johnston-style). Prefer longer lists."""
    buckets = collections.defaultdict(list)
    for e in ev_list:
        buckets[(e["cy"], e["cx"], e["day"])].append(e)
    out = []
    for _k, lst in buckets.items():
        lst.sort(key=lambda e: (-e["list_len"], e["obs"]))
        out.append(lst[0])
    return out


def observer_pair_counts(ev_list, spp_set):
    """For each pair, n distinct observers that saw both in same event."""
    pc = collections.defaultdict(set)
    for e in ev_list:
        present = sorted(s for s in e["spp"] if s in spp_set)
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                pc[(present[i], present[j])].add(e["obs"])
    return pc


def save_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


def plot_obs_vs_exp(rows: list[dict], path: Path, title: str) -> None:
    """Simple PNG scatter with PIL (no matplotlib)."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 900, 700
    img = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    margin = 70
    pos = [r for r in rows if r["kind"] == "positive"]
    neg = [r for r in rows if r["kind"] == "negative"]
    rnd = [r for r in rows if r["kind"] == "random"]
    allr = rows
    if not allr:
        img.save(path)
        return
    xs = [r["expected"] for r in allr]
    ys = [r["obs"] for r in allr]
    xmax = max(xs + ys + [1]) * 1.05
    ymax = xmax

    def tx(x):
        return margin + (W - 2 * margin) * (x / xmax)

    def ty(y):
        return H - margin - (H - 2 * margin) * (y / ymax)

    # axes
    dr.line([(margin, H - margin), (W - margin, H - margin)], fill=(0, 0, 0), width=2)
    dr.line([(margin, H - margin), (margin, margin)], fill=(0, 0, 0), width=2)
    # y=x
    dr.line([(tx(0), ty(0)), (tx(xmax), ty(ymax))], fill=(180, 180, 180), width=2)

    def dots(subset, color, r=3):
        for row in subset:
            x, y = tx(row["expected"]), ty(row["obs"])
            dr.ellipse([x - r, y - r, x + r, y + r], fill=color)

    # subsample random for clarity
    if len(rnd) > 4000:
        rnd = random.sample(rnd, 4000)
    dots(rnd, (190, 190, 190), 2)
    dots(neg, (200, 60, 60), 3)
    dots(pos, (40, 110, 180), 3)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
        font_s = font
    dr.text((margin, 20), title, fill=(0, 0, 0), font=font)
    dr.text((W // 2 - 40, H - 40), "esperado (Veech)", fill=(0, 0, 0), font=font_s)
    dr.text((12, H // 2), "obs", fill=(0, 0, 0), font=font_s)
    legend = f"+ {len(pos)}  − {len(neg)}  random {len([r for r in rows if r['kind']=='random'])}"
    dr.text((margin, 45), legend, fill=(60, 60, 60), font=font_s)
    img.save(path)
    log(f"figura {path}")


def classify_interaction(globi_a_b: str, globi_b_a: str) -> str:
    types = []
    for t in (globi_a_b or "", globi_b_a or ""):
        types.append(re.sub(r"[^a-z]", "", t.lower()))
    if any(t in TROPHIC_TYPES for t in types if t):
        return "trophic"
    if any(t in NONTROPHIC_TYPES for t in types if t):
        return "nontrophic"
    if any(types):
        return "other"
    return "none"


def bootstrap_pr(pred_set: set, gold_set: set, n_boot: int = 500):
    """Precision/recall with bootstrap over predicted pairs (Freilich-style reporting)."""
    pred = list(pred_set)
    if not pred:
        return {"precision": 0.0, "recall": 0.0, "precision_ci": (0.0, 0.0), "recall_ci": (0.0, 0.0), "tp": 0, "n_pred": 0, "n_gold": len(gold_set)}
    tp = len(pred_set & gold_set)
    precision = tp / len(pred_set)
    recall = tp / len(gold_set) if gold_set else 0.0
    precs, recs = [], []
    for _ in range(n_boot):
        sample = [pred[i] for i in np.random.randint(0, len(pred), size=len(pred))]
        sset = set(sample)
        tpb = len(sset & gold_set)
        precs.append(tpb / len(sset) if sset else 0.0)
        # recall bootstrap: resample gold
        gold_l = list(gold_set)
        if gold_l:
            gsample = {gold_l[i] for i in np.random.randint(0, len(gold_l), size=len(gold_l))}
            recs.append(len(pred_set & gsample) / len(gsample))
        else:
            recs.append(0.0)
    return {
        "precision": precision,
        "recall": recall,
        "precision_ci": (float(np.percentile(precs, 2.5)), float(np.percentile(precs, 97.5))),
        "recall_ci": (float(np.percentile(recs, 2.5)), float(np.percentile(recs, 97.5))),
        "tp": tp,
        "n_pred": len(pred_set),
        "n_gold": len(gold_set),
    }


def literature_gold() -> dict[tuple[str, str], str]:
    """Known Mediterranean pairs from the article (not GloBI)."""
    pairs = {
        ("peltodoris_atromaculata", "petrosia_ficiformis"): "trophic",
        ("cratena_peregrina", "eudendrium_racemosum"): "trophic",
        ("condylactis_aurantiaca", "periclimenes_scriptus"): "nontrophic",
        ("lysmata_grabhami", "telmatactis_cricoides"): "nontrophic",
        ("electra_posidoniae", "tridentata_perpusilla"): "nontrophic",
        ("felimare_orsinii", "scalarispongia_scalaris"): "trophic",
        ("parazoanthus_axinellae", "spongia_lamella"): "nontrophic",
    }
    out = {}
    for (a, b), k in pairs.items():
        out[tuple(sorted((a, b)))] = k
    return out


def main():
    log("=== v25 correlación benchmark (CPU) ===")
    info = load_catalog()
    log(f"catálogo: {len(info)} spp")

    ev_all = build_events(info)
    ev_ge2 = [e for e in ev_all if e["list_len"] >= 2]
    log(f"eventos >=2 spp: {len(ev_ge2)}")

    # Top species by event frequency (among ge2)
    freq = collections.Counter()
    for e in ev_ge2:
        for s in e["spp"]:
            freq[s] += 1
    top = [s for s, _ in freq.most_common(TOP_SPP)]
    top_set = set(top)
    log(f"top especies: {len(top)} (min freq={freq[top[-1]]})")

    # ---------- 1) Veech on event scale (baseline) ----------
    X0, meta0 = sites_matrix(ev_ge2, top, min_spp=1)
    # sites that have at least one of top spp
    log(f"matriz eventos×top: {X0.shape}")
    veech0 = run_veech_all(X0, top, min_obs=5)
    veech0 = bh_fdr(veech0)
    n_pos = sum(1 for r in veech0 if r["kind"] == "positive")
    n_neg = sum(1 for r in veech0 if r["kind"] == "negative")
    n_pos_q = sum(1 for r in veech0 if r["kind"] == "positive" and r["q"] <= 0.05)
    n_neg_q = sum(1 for r in veech0 if r["kind"] == "negative" and r["q"] <= 0.05)
    log(f"Veech baseline: +{n_pos} (−q05 {n_pos_q})  −{n_neg} (−q05 {n_neg_q})  total pares {len(veech0)}")

    fields_v = ["a", "b", "N", "Na", "Nb", "obs", "expected", "effect", "p_gt", "p_lt", "p", "q", "kind"]
    save_csv(OUT / "v25_veech_eventos_top300_20261011.csv",
             sorted(veech0, key=lambda r: (0 if r["kind"] == "positive" else 1 if r["kind"] == "negative" else 2, r["p"])),
             fields_v)
    plot_obs_vs_exp(veech0, FIG / "fig_v25_veech_obs_vs_esperado.png",
                    "Veech/cooccur: observado frente a esperado (eventos 3 h, top 300)")

    # ---------- 2) Sensitivity / effort filters (Johnston) ----------
    sensitivity = []

    def summarize(label, rows, obs_filter_n=None, pair_obs=None):
        rr = rows
        if pair_obs is not None and obs_filter_n is not None:
            kept = []
            for r in rr:
                k = tuple(sorted((r["a"], r["b"])))
                if len(pair_obs.get(k, ())) >= obs_filter_n:
                    kept.append(r)
            rr = kept
        pos = [r for r in rr if r["kind"] == "positive"]
        neg = [r for r in rr if r["kind"] == "negative"]
        pos_q = [r for r in pos if r["q"] <= 0.05]
        neg_q = [r for r in neg if r["q"] <= 0.05]
        return {
            "filtro": label,
            "n_sitios": rr[0]["N"] if rr else 0,
            "pares_testeados": len(rr),
            "positivos": len(pos),
            "negativos": len(neg),
            "positivos_q05": len(pos_q),
            "negativos_q05": len(neg_q),
        }

    # A: baseline
    sensitivity.append(summarize("A_eventos_ge2_top300", veech0))

    # B: list length — only events with list_len <= Q75 of ge2
    lens = [e["list_len"] for e in ev_ge2]
    q75 = int(np.percentile(lens, 75))
    ev_ll = [e for e in ev_ge2 if e["list_len"] <= q75]
    Xb, _ = sites_matrix(ev_ll, top)
    veech_b = bh_fdr(run_veech_all(Xb, top, min_obs=5))
    sensitivity.append(summarize(f"B_list_len_le_Q75({q75})", veech_b))
    log(f"filtro B list_len<=Q75={q75}: sitios {Xb.shape[0]}")

    # C: spatial subsample 1 event / cell×day
    ev_sp = spatial_subsample(ev_ge2)
    Xs, metas = sites_matrix(ev_sp, top)
    veech_c = bh_fdr(run_veech_all(Xs, top, min_obs=5))
    sensitivity.append(summarize("C_submuestreo_1evento_celda_dia", veech_c))
    log(f"filtro C spatial: sitios {Xs.shape[0]}")

    # D: B+C
    ev_bc = spatial_subsample(ev_ll)
    Xd, _ = sites_matrix(ev_bc, top)
    veech_d = bh_fdr(run_veech_all(Xd, top, min_obs=5))
    sensitivity.append(summarize("D_list_len+submuestreo", veech_d))

    # E: D + >=5 observers per pair
    pair_obs = observer_pair_counts(ev_bc, top_set)
    sensitivity.append(summarize("E_D_mas_ge5_observadores", veech_d, obs_filter_n=5, pair_obs=pair_obs))

    # F: also require effect size obs/expected >= 2 among positives surviving E
    veech_e_rows = []
    for r in veech_d:
        k = tuple(sorted((r["a"], r["b"])))
        if len(pair_obs.get(k, ())) >= 5:
            veech_e_rows.append(r)
    veech_f = [r for r in veech_e_rows if r["kind"] != "positive" or (r["expected"] > 0 and r["obs"] / r["expected"] >= 2)]
    # recount kinds for F
    sensitivity.append({
        "filtro": "F_E_mas_razon_obs_esp_ge2",
        "n_sitios": veech_d[0]["N"] if veech_d else 0,
        "pares_testeados": len(veech_f),
        "positivos": sum(1 for r in veech_f if r["kind"] == "positive"),
        "negativos": sum(1 for r in veech_f if r["kind"] == "negative"),
        "positivos_q05": sum(1 for r in veech_f if r["kind"] == "positive" and r["q"] <= 0.05),
        "negativos_q05": sum(1 for r in veech_f if r["kind"] == "negative" and r["q"] <= 0.05),
    })

    save_csv(OUT / "v25_sensibilidad_johnston_20261011.csv", sensitivity,
             ["filtro", "n_sitios", "pares_testeados", "positivos", "negativos", "positivos_q05", "negativos_q05"])
    log("sensibilidad:")
    for s in sensitivity:
        log(f"  {s}")

    # save survivors of E positives q05
    survivors = [r for r in veech_e_rows if r["kind"] == "positive" and r["q"] <= 0.05]
    save_csv(OUT / "v25_veech_survivors_filtroE_20261011.csv",
             sorted(survivors, key=lambda r: r["p"]), fields_v)

    # ---------- 3) Graphical lasso on event × species ----------
    # Use spatially subsampled matrix for tractability / less hotspot bias
    Xg = Xs.astype(np.float64)
    # drop species with <10 occurrences in this matrix
    occ_g = Xg.sum(axis=0)
    keep_idx = np.where(occ_g >= 10)[0]
    Xg2 = Xg[:, keep_idx]
    spp_g = [top[i] for i in keep_idx]
    log(f"glasso: matriz {Xg2.shape}, alpha={ALPHA}")
    # Standardize lightly: GraphicalLasso assumes centered; binary OK
    try:
        model = GraphicalLasso(alpha=ALPHA, max_iter=400, tol=1e-3)
        model.fit(Xg2)
        prec = model.precision_
        # residual edges: off-diagonal non-zero in precision (conditional dependence)
        edges = []
        S = len(spp_g)
        for i in range(S):
            for j in range(i + 1, S):
                w = float(prec[i, j])
                if abs(w) > 1e-8:
                    edges.append({
                        "a": spp_g[i], "b": spp_g[j],
                        "precision": w,
                        "partial_corr": -w / math.sqrt(prec[i, i] * prec[j, j]),
                        "sign": "positive" if w < 0 else "negative",  # neg precision → positive assoc
                    })
        edges.sort(key=lambda e: -abs(e["partial_corr"]))
        log(f"glasso aristas: {len(edges)}")
    except Exception as ex:
        log(f"glasso FALLÓ: {ex}")
        edges = []
        # fallback: correlation threshold residual after subtracting mean list structure
        C = np.corrcoef(Xg2.T)
        S = len(spp_g)
        for i in range(S):
            for j in range(i + 1, S):
                c = float(C[i, j])
                if abs(c) >= 0.15:
                    edges.append({
                        "a": spp_g[i], "b": spp_g[j],
                        "precision": float("nan"),
                        "partial_corr": c,
                        "sign": "positive" if c > 0 else "negative",
                    })
        edges.sort(key=lambda e: -abs(e["partial_corr"]))
        log(f"fallback corr aristas: {len(edges)}")

    save_csv(OUT / "v25_glasso_red_residual_20261011.csv", edges,
             ["a", "b", "precision", "partial_corr", "sign"])

    # ---------- 4) Freilich validation vs GloBI + literature ----------
    gold_lit = literature_gold()
    gold_all = dict(gold_lit)
    gold_trophic = {k for k, v in gold_lit.items() if v == "trophic"}
    gold_nontrophic = {k for k, v in gold_lit.items() if v == "nontrophic"}

    with open(ART_BF / "globi_pares_completo_20261007.csv", newline="") as f:
        for row in csv.DictReader(f):
            if str(row.get("documentada", "")).lower() != "true":
                continue
            a, b = slug(row["a"]), slug(row["b"])
            k = tuple(sorted((a, b)))
            kind = classify_interaction(row.get("globi_a_b", ""), row.get("globi_b_a", ""))
            if kind == "none":
                kind = "other"
            gold_all[k] = kind
            if kind == "trophic":
                gold_trophic.add(k)
            elif kind == "nontrophic":
                gold_nontrophic.add(k)

    gold_set = set(gold_all)
    log(f"gold GloBI+lit: {len(gold_set)} (troph {len(gold_trophic)}, nontroph {len(gold_nontrophic)})")

    # Predictions: Veech positives q05 after filter E; glasso positive edges top by |partial|
    pred_veech = {tuple(sorted((r["a"], r["b"]))) for r in survivors}
    pred_glasso = {tuple(sorted((e["a"], e["b"]))) for e in edges if e["sign"] == "positive"}
    # top-k glasso by |partial_corr|
    pred_glasso_top200 = {tuple(sorted((e["a"], e["b"]))) for e in edges if e["sign"] == "positive"}
    # restrict to top 200 by strength
    pos_edges = [e for e in edges if e["sign"] == "positive"]
    pred_glasso_top200 = {tuple(sorted((e["a"], e["b"]))) for e in pos_edges[:200]}

    # same-photo candidates from shortlist
    pred_photo = set()
    with open(ART_BF / "copresencia_pares_20261006.csv", newline="") as f:
        for row in csv.DictReader(f):
            hits = int(float(row.get("obs_indep_hits") or 0))
            if hits >= 1:
                pred_photo.add(tuple(sorted((slug(row["a"]), slug(row["b"])))))

    val_rows = []
    for name, pred in [
        ("veech_filtroE_pos_q05", pred_veech),
        ("glasso_pos_top200", pred_glasso_top200),
        ("misma_foto_hits_ge1", pred_photo),
    ]:
        for gname, gset in [
            ("all_gold", gold_set),
            ("trophic", gold_trophic),
            ("nontrophic", gold_nontrophic),
        ]:
            # restrict gold to pairs where both spp in our prediction universe when fairer
            m = bootstrap_pr(pred, gset, n_boot=500)
            val_rows.append({
                "metodo": name,
                "gold": gname,
                "n_pred": m["n_pred"],
                "n_gold": m["n_gold"],
                "tp": m["tp"],
                "precision": round(m["precision"], 4),
                "recall": round(m["recall"], 4),
                "precision_ci_lo": round(m["precision_ci"][0], 4),
                "precision_ci_hi": round(m["precision_ci"][1], 4),
                "recall_ci_lo": round(m["recall_ci"][0], 4),
                "recall_ci_hi": round(m["recall_ci"][1], 4),
            })
            log(f"val {name}/{gname}: P={m['precision']:.3f} R={m['recall']:.3f} tp={m['tp']}")

    save_csv(OUT / "v25_validacion_freilich_globi_20261011.csv", val_rows,
             ["metodo", "gold", "n_pred", "n_gold", "tp", "precision", "recall",
              "precision_ci_lo", "precision_ci_hi", "recall_ci_lo", "recall_ci_hi"])

    # ---------- 5) Three scales ----------
    # Scale foto: already pred_photo; count Veech-like not applicable the same way — report n pairs with hits
    # Scale evento: veech0 / survivors
    # Scale cell×month: aggregate
    month_buckets = collections.defaultdict(set)
    for e in ev_all:
        key = (e["cy"], e["cx"], e["month"])
        month_buckets[key] |= (e["spp"] & top_set)
    month_ev = [{"spp": spp, "list_len": len(spp), "obs": "?", "cy": k[0], "cx": k[1], "day": k[2], "month": k[2], "slot": "m"}
                for k, spp in month_buckets.items() if len(spp) >= 2]
    Xm, _ = sites_matrix(month_ev, top)
    veech_m = bh_fdr(run_veech_all(Xm, top, min_obs=5))
    n_pos_m = sum(1 for r in veech_m if r["kind"] == "positive" and r["q"] <= 0.05)
    n_neg_m = sum(1 for r in veech_m if r["kind"] == "negative" and r["q"] <= 0.05)
    save_csv(OUT / "v25_veech_celda_mes_top300_20261011.csv",
             sorted([r for r in veech_m if r["kind"] != "random"], key=lambda r: r["p"])[:5000],
             fields_v)

    scales = [
        {
            "escala": "misma_foto",
            "n_unidades": "galería (lista corta 138)",
            "pares_con_señal": len(pred_photo),
            "pares_positivos_q05": len(pred_photo),
            "pares_negativos_q05": 0,
            "nota": "obs_indep_hits>=1 en copresencia_pares (no Veech)",
        },
        {
            "escala": "evento_3h",
            "n_unidades": X0.shape[0],
            "pares_con_señal": n_pos + n_neg,
            "pares_positivos_q05": n_pos_q,
            "pares_negativos_q05": n_neg_q,
            "nota": "Veech top300 sobre eventos observador×celda×día×franja3h",
        },
        {
            "escala": "celda_1km_x_mes",
            "n_unidades": Xm.shape[0],
            "pares_con_señal": sum(1 for r in veech_m if r["kind"] != "random"),
            "pares_positivos_q05": n_pos_m,
            "pares_negativos_q05": n_neg_m,
            "nota": "Veech top300 sobre celda 0.01° × mes (sin observador)",
        },
    ]
    save_csv(OUT / "v25_tres_escalas_20261011.csv", scales,
             ["escala", "n_unidades", "pares_con_señal", "pares_positivos_q05", "pares_negativos_q05", "nota"])
    log("escalas:")
    for s in scales:
        log(f"  {s}")

    # Overlap between scales (positive q05 event vs month; photo)
    pos_event = {tuple(sorted((r["a"], r["b"]))) for r in veech0 if r["kind"] == "positive" and r["q"] <= 0.05}
    pos_month = {tuple(sorted((r["a"], r["b"]))) for r in veech_m if r["kind"] == "positive" and r["q"] <= 0.05}
    overlap = {
        "foto_∩_evento": len(pred_photo & pos_event),
        "foto_∩_mes": len(pred_photo & pos_month),
        "evento_∩_mes": len(pos_event & pos_month),
        "foto_∩_evento_∩_mes": len(pred_photo & pos_event & pos_month),
        "glasso∩veechE": len(pred_glasso_top200 & pred_veech),
    }

    summary = {
        "date": "2026-10-11",
        "top_spp": TOP_SPP,
        "glasso_alpha": ALPHA,
        "veech_baseline": {
            "N": int(X0.shape[0]),
            "pares": len(veech0),
            "positivos": n_pos,
            "negativos": n_neg,
            "positivos_q05": n_pos_q,
            "negativos_q05": n_neg_q,
        },
        "list_len_Q75": q75,
        "sensitivity": sensitivity,
        "glasso_edges": len(edges),
        "glasso_pos_edges": sum(1 for e in edges if e["sign"] == "positive"),
        "validation": val_rows,
        "scales": scales,
        "overlap": overlap,
        "gold_n": len(gold_set),
        "citations": {
            "veech": "10.1111/j.1466-8238.2012.00789.x",
            "cooccur": "10.18637/jss.v069.c02",
            "johnston": "10.1111/ddi.13271",
            "harris": "10.1002/ecy.1605",
            "freilich": "10.1002/ecy.2142",
            "blanchet": "10.1111/ele.13525",
        },
    }
    (OUT / "v25_resumen_20261011.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    log("OK resumen → v25_resumen_20261011.json")
    return summary


if __name__ == "__main__":
    main()
