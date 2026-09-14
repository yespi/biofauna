#!/usr/bin/env python3
"""Ajusta calibración JERÁRQUICA: global + familia + género + especie (shrinkage).

Entrada : dataset/calib_raw.jsonl  (cosechado denso)
          dataset/calibration.json  (modelo logístico global, para p_species base)
Salida  : dataset/calibration_hierarchical.json

Idea:
  - El modelo global da p_species = sigmoid(z).
  - Para cada grupo (especie → género → familia) con >= MIN_N muestras, se calcula
    un UMBRAL propio: el mínimo p_species que alcanza TARGET (80%) de precisión real
    dentro de ese grupo.
  - Shrinkage: el umbral del grupo se mezcla con el umbral global (0.80) ponderado
    por sqrt(n), para que grupos con pocas muestras no produzcan umbrales ruidosos.
  - En producción, identify_service busca umbral en: especie → género → familia → global.
"""
import json, math
from collections import defaultdict

ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
TARGET = 0.80
MIN_N = 10          # mínimo de muestras para calibrar un grupo
SHRINK_K = 30.0     # fuerza del shrinkage hacia el global

def load_global():
    c = json.load(open(f"{ROOT}/dataset/calibration.json"))
    lvl = c.get("levels", {}).get("species", c)
    c["coef"] = lvl.get("coef", c.get("coef"))
    c["mu"] = lvl.get("mu", c.get("mu"))
    c["sd"] = lvl.get("sd", c.get("sd"))
    c["intercept"] = lvl.get("intercept", c.get("intercept"))
    c["features"] = lvl.get("features", c.get("features"))
    return c

def p_global(c, r):
    """Reproduce _calibrate de identify_service.py (nivel species)."""
    try:
        x = [float(r.get(k, 0.0)) for k in c["features"]]
        z = float(sum((xi - mu) / sd * co for xi, mu, sd, co in zip(x, c["mu"], c["sd"], c["coef"])) + c["intercept"])
        return 1.0 / (1.0 + math.exp(-z))
    except Exception:
        return None

def fit_group_threshold(rs, c):
    """Umbral mínimo de p_species que da >= TARGET de precisión en el grupo."""
    pairs = []
    for r in rs:
        p = p_global(c, r)
        if p is None:
            continue
        pairs.append((p, 1 if r.get("ok_species") else 0))
    if len(pairs) < MIN_N:
        return None
    cands = sorted({round(t[0], 2) for t in pairs})
    best = None
    for th in cands:
        above = [t for t in pairs if t[0] >= th]
        if not above:
            continue
        prec = sum(o for _, o in above) / len(above)
        if prec >= TARGET:
            best = th
    if best is None:
        return None
    above = [t for t in pairs if t[0] >= best]
    return {"threshold": best, "n": len(pairs), "precision": round(sum(o for _, o in above) / len(above), 4)}

def shrink(group_thr, n):
    """Mezcla el umbral del grupo con el global (0.80), ponderado por sqrt(n)."""
    w = math.sqrt(n) / (math.sqrt(n) + math.sqrt(SHRINK_K))
    return round(group_thr * w + TARGET * (1 - w), 4)

def main():
    c = load_global()
    rows = [json.loads(l) for l in open(f"{ROOT}/dataset/calib_raw.jsonl") if l.strip()]

    by_sp = defaultdict(list); by_genus = defaultdict(list); by_fam = defaultdict(list)
    for r in rows:
        by_sp[r["true"]].append(r)
        by_genus[r.get("true_genus", "?")].append(r)
        by_fam[r.get("true_family", "?")].append(r)

    out = {"global": {"threshold": TARGET}, "by_species": {}, "by_genus": {}, "by_family": {}}

    for fam, rs in by_fam.items():
        t = fit_group_threshold(rs, c)
        if t:
            out["by_family"][fam] = {"threshold": shrink(t["threshold"], t["n"]),
                                     "n": t["n"], "raw_threshold": t["threshold"],
                                     "precision": t["precision"]}
    for gen, rs in by_genus.items():
        t = fit_group_threshold(rs, c)
        if t:
            out["by_genus"][gen] = {"threshold": shrink(t["threshold"], t["n"]),
                                    "n": t["n"], "raw_threshold": t["threshold"],
                                    "precision": t["precision"]}
    for sp, rs in by_sp.items():
        t = fit_group_threshold(rs, c)
        if t:
            out["by_species"][sp] = {"threshold": shrink(t["threshold"], t["n"]),
                                     "n": t["n"], "raw_threshold": t["threshold"],
                                     "precision": t["precision"]}

    json.dump(out, open(f"{ROOT}/dataset/calibration_hierarchical.json", "w"), indent=1, ensure_ascii=False)
    print(f"especies calibradas: {len(out['by_species'])}")
    print(f"generos calibrados:   {len(out['by_genus'])}")
    print(f"familias calibradas:  {len(out['by_family'])}")
    print("GUARDADO calibration_hierarchical.json")

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
    from calib_lock import calib_write_lock, CalibLockBusy
    try:
        with calib_write_lock("fit_calib_hierarchical.py"):
            main()
    except CalibLockBusy as e:
        print(f"[LOCK] {e}", flush=True)
        sys.exit(3)

