#!/usr/bin/env python3
"""FASE 2 · paso 2 — AJUSTE de la calibración de confianza.

Entrada : dataset/calib_raw.jsonl  (lo produce harvest_calib.py, out-of-sample real)
Salida  : dataset/calibration.json (coeficientes + tabla de fiabilidad + umbrales)

Qué hace: aprende P(el top-1 de especie es correcto | features del kNN). Hoy la API
devuelve la similitud coseno como "confidence", que NO es una probabilidad — por eso un
0.938 puede ser un error. Tras esto, "0.90" querrá decir 90% de acierto real.

Modelos comparados en HELD-OUT (split por especie, sin fugas):
  raw       : p = s1 (lo que hace hoy la API)          <- baseline a batir
  platt_s1  : logística sobre s1 (recalibra la escala)
  full      : logística sobre todas las features del kNN (margen, votos, share, nref...)
  full+iso  : isotónica encima de `full` (no paramétrica; solo si hay muestras de sobra)

Selección por **NLL** (regla de puntuación propia: penaliza a la vez la mala
discriminación y el exceso de confianza — justo nuestro fallo: 0.938 y equivocado).
ECE/Brier/AUC se reportan como diagnóstico.

Se calibran TRES niveles, porque Minka acepta identificaciones a género y a familia:
  species / genus / family = P(el taxón del top-1 sea correcto a ese nivel).
El punto de auto-publicación seguro suele estar en género, no en especie.
Al final, la tabla que importa: umbral -> cobertura y PRECISIÓN REAL.
"""
import json, sys, time
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss

ROOT = Path("/work")
RAW = ROOT / "dataset/calib_raw.jsonl"
OUT = ROOT / "dataset/calibration.json"
SEED = 7
FEATS = ["s1", "s2", "margin", "votes1", "share1", "lognref1", "meansim",
         "kclasses", "same_genus_12", "same_family_12"]

log = lambda *a: print(*a, flush=True)


def load():
    recs = []
    for ln in RAW.read_text().splitlines():
        try:
            recs.append(json.loads(ln))
        except Exception:
            pass
    tgt = json.loads((ROOT / "dataset/target_species.json").read_text())
    import re
    sl = lambda n: re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")
    meta = {sl(s["name"]): s for s in tgt}
    for r in recs:
        t1 = meta.get(r["top"][0], {})
        r["ok_genus"] = bool(r.get("true_genus")) and t1.get("genus") == r["true_genus"]
        r["ok_family"] = bool(r.get("true_family")) and t1.get("family") == r["true_family"]
    return recs


def featurize(recs, target="ok_species"):
    X = np.array([[r["s1"], r["s2"], r["margin"], r["votes1"], r["share1"],
                   np.log1p(r["nref1"]), r["meansim"], r["kclasses"],
                   float(r["same_genus_12"]), float(r["same_family_12"])]
                  for r in recs], dtype="float64")
    y = np.array([1 if r[target] else 0 for r in recs], dtype="int32")
    return X, y


def ece(p, y, bins=15):
    """Expected Calibration Error: |confianza declarada - acierto real| ponderado."""
    e, n = 0.0, len(y)
    edges = np.linspace(0, 1, bins + 1)
    for i in range(bins):
        m = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= 1.0)
        if m.sum() == 0:
            continue
        e += m.sum() / n * abs(p[m].mean() - y[m].mean())
    return e


def evaluate(name, p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    try:
        auc = roc_auc_score(y, p)
    except ValueError:
        auc = float("nan")
    return {"model": name, "ece": round(ece(p, y), 4),
            "brier": round(brier_score_loss(y, p), 4),
            "nll": round(log_loss(y, p, labels=[0, 1]), 4), "auc": round(auc, 4)}


def reliability(p, y, bins=10):
    out, edges = [], np.linspace(0, 1, bins + 1)
    for i in range(bins):
        m = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= 1.0)
        if m.sum() == 0:
            continue
        out.append({"bin": f"{edges[i]:.1f}-{edges[i+1]:.1f}", "n": int(m.sum()),
                    "declarada": round(float(p[m].mean()), 3),
                    "real": round(float(y[m].mean()), 3)})
    return out


def op_table(p, y, ths=(0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.98), n_bootstrap=1000):
    """Lo accionable: si auto-publico a partir de X, ¿qué precisión y cobertura tengo?
    3.0.e: añade CIs por bootstrap (1000 remuestreos)."""
    rows = []
    n = len(y)
    rng = np.random.RandomState(7)
    for t in ths:
        m = p >= t
        n_pos = int(m.sum())
        prec = round(float(y[m].mean()), 3) if n_pos else None
        # Bootstrap CI para la precision
        ci_low = ci_high = None
        if n_pos >= 10 and prec is not None:
            boots = []
            for _ in range(n_bootstrap):
                idx = rng.choice(n, n, replace=True)
                bm = p[idx] >= t
                if bm.sum():
                    boots.append(float(y[idx][bm].mean()))
            if boots:
                boots.sort()
                ci_low = round(boots[int(0.025 * len(boots))], 3)
                ci_high = round(boots[int(0.975 * len(boots))], 3)
        rows.append({"umbral": t, "cobertura": round(float(m.mean()), 3),
                     "n": n_pos,
                     "precision_real": prec,
                     "ci_95": [ci_low, ci_high] if ci_low is not None else None})
    return rows


def fit_level(recs, tr, te, target, label):
    """Ajusta y elige el mejor calibrador para un nivel taxonómico. -> bloque JSON."""
    Xtr, ytr = featurize(tr, target)
    Xte, yte = featurize(te, target)
    if len(set(ytr)) < 2 or len(set(yte)) < 2:
        log(f"\n[{label}] una sola clase en fit o test — no se puede calibrar")
        return None
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9

    cands = {"raw": (np.clip(Xte[:, 0], 0, 1), None)}
    lr1 = LogisticRegression(C=1.0, max_iter=2000).fit(Xtr[:, :1], ytr)
    cands["platt_s1"] = (lr1.predict_proba(Xte[:, :1])[:, 1], lr1)
    lrf = LogisticRegression(C=1.0, max_iter=5000).fit((Xtr - mu) / sd, ytr)
    cands["full"] = (lrf.predict_proba((Xte - mu) / sd)[:, 1], lrf)
    # 3.0.e: isotonica eliminada — fragil en la cola con n~590 held-out.
    # La logistica sola ("full") es mas fiable donde auto-publicamos (p>=0.90).

    log(f"\n[{label}] modelos (held-out; NLL decide, ECE = deshonestidad)")
    mets = [evaluate(nm, p, yte) for nm, (p, _) in cands.items()]
    for m in mets:
        log(f"  {m['model']:10s} NLL={m['nll']:.4f}  ECE={m['ece']:.4f}  "
            f"Brier={m['brier']:.4f}  AUC={m['auc']:.4f}")
    best = min(mets, key=lambda m: m["nll"])["model"]
    log(f"  -> elegido: {best}")

    p = cands[best][0]
    log(f"  fiabilidad (declarada vs real):")
    for r in reliability(p, yte):
        log(f"    {r['bin']}  n={r['n']:4d}  declarada={r['declarada']:.3f}  "
            f"real={r['real']:.3f}")
    log(f"  operativa (auto-publicar por encima del umbral):")
    for r in op_table(p, yte):
        log(f"    p>={r['umbral']:.2f}  cobertura={r['cobertura']:.3f} "
            f"(n={r['n']:4d})  precision_real={r['precision_real']}")
    ths = {}
    for tgt in (0.90, 0.95, 0.98):
        pick = None
        for r in op_table(p, yte, ths=np.round(np.arange(0.5, 0.995, 0.01), 3)):
            if r["n"] >= 30 and r["precision_real"] is not None and r["precision_real"] >= tgt:
                pick = r["umbral"]; break
        ths[f"p{int(tgt*100)}"] = pick
    log(f"  umbrales para precisión objetivo: {ths}"
        + ("   <- ninguno alcanzable con muestra suficiente" if not any(ths.values()) else ""))

    # reajuste final sobre TODOS los datos, para producción
    Xa, ya = featurize(recs, target)
    blk = {"target": target, "model": best, "metrics": mets,
           "reliability": reliability(p, yte), "operating_points": op_table(p, yte),
           "thresholds": ths, "base_rate": round(float(ya.mean()), 4)}
    if best == "raw":
        blk["kind"] = "identity"
    elif best == "platt_s1":
        m = LogisticRegression(C=1.0, max_iter=2000).fit(Xa[:, :1], ya)
        blk.update(kind="logistic", features=["s1"], coef=m.coef_[0].tolist(),
                   intercept=float(m.intercept_[0]), mu=[0.0], sd=[1.0])
    else:
        mu2, sd2 = Xa.mean(0), Xa.std(0) + 1e-9
        m = LogisticRegression(C=1.0, max_iter=5000).fit((Xa - mu2) / sd2, ya)
        blk.update(kind="logistic", features=FEATS, coef=m.coef_[0].tolist(),
                   intercept=float(m.intercept_[0]), mu=mu2.tolist(), sd=sd2.tolist())
        if best == "full+iso":
            iso2 = IsotonicRegression(out_of_bounds="clip").fit(
                m.predict_proba((Xa - mu2) / sd2)[:, 1], ya)
            blk["isotonic"] = {"x": iso2.X_thresholds_.tolist(),
                               "y": iso2.y_thresholds_.tolist()}
            blk["kind"] = "logistic+isotonic"
    return blk


def main():
    if not RAW.exists():
        log(f"falta {RAW} — corre antes harvest_calib.py"); sys.exit(2)
    recs = load()
    log(f"[datos] {len(recs)} muestras out-of-sample · "
        f"{len({r['true'] for r in recs})} especies")
    acc = np.mean([r["ok_species"] for r in recs])
    log(f"[realidad] acierto ESPECIE top-1 = {100*acc:.1f}%  |  "
        f"género {100*np.mean([r['ok_genus'] for r in recs]):.1f}%  |  "
        f"familia {100*np.mean([r['ok_family'] for r in recs]):.1f}%")
    for t in sorted({r.get("tier", 9) for r in recs}):
        s = [r for r in recs if r.get("tier", 9) == t]
        tier_acc = np.mean([r['ok_species'] for r in s])
        tier_gen = np.mean([r['ok_genus'] for r in s])
        tier_fam = np.mean([r['ok_family'] for r in s])
        log(f"    tier {t}: n={len(s)}  especie={100*tier_acc:.0f}%  genero={100*tier_gen:.0f}%  familia={100*tier_fam:.0f}%")

    # split POR ESPECIE: ninguna especie aparece en fit y en test a la vez
    rng = np.random.RandomState(SEED)
    sps = sorted({r["true"] for r in recs})
    rng.shuffle(sps)
    test_sp = set(sps[:max(1, int(0.3 * len(sps)))])
    tr = [r for r in recs if r["true"] not in test_sp]
    te = [r for r in recs if r["true"] in test_sp]
    log(f"[split] fit {len(tr)} muestras / test {len(te)} (por especie, sin solape)")
    if len(te) < 50 or len(set(np.array([r['ok_species'] for r in te]))) < 2:
        log("!! test demasiado pequeño o de una sola clase — cosecha más antes de fiarte")

    levels = {}
    for target, label in (("ok_species", "species"), ("ok_genus", "genus"),
                          ("ok_family", "family")):
        blk = fit_level(recs, tr, te, target, label)
        if blk:
            levels[label] = blk

    # 3.0.e: acierto por tier
    tier_acc = {}
    for t in sorted({r.get("tier", 9) for r in recs}):
        s = [r for r in recs if r.get("tier", 9) == t]
        tier_acc[str(t)] = {"n": len(s),
            "species": round(float(np.mean([r['ok_species'] for r in s])), 4),
            "genus": round(float(np.mean([r['ok_genus'] for r in s])), 4),
            "family": round(float(np.mean([r['ok_family'] for r in s])), 4)}

    payload = {"created": datetime.now().isoformat(timespec="seconds"),
               "n_samples": len(recs), "n_species": len({r["true"] for r in recs}),
               "tier_acc": tier_acc,
               "field_acc": {"species": round(float(acc), 4),
                             "genus": round(float(np.mean([r["ok_genus"] for r in recs])), 4),
                             "family": round(float(np.mean([r["ok_family"] for r in recs])), 4)},
               "features": FEATS, "levels": levels,
               # el servicio lee estos alias para el nivel de especie
               "note": "P(el taxón del top-1 sea correcto a ese nivel). Ajustado "
                       "OUT-OF-SAMPLE: fotos excluidas por obs id contra _manifest.jsonl. "
                       "Ver YOLOFAUNA.md sec. L."}
    if "species" in levels:
        sp = levels["species"]
        payload.update(kind=sp.get("kind"), model=sp.get("model"),
                       features=sp.get("features", FEATS), coef=sp.get("coef"),
                       intercept=sp.get("intercept"), mu=sp.get("mu"), sd=sp.get("sd"))
        if "isotonic" in sp:
            payload["isotonic"] = sp["isotonic"]
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1))
    log(f"\nGUARDADO {OUT} (species kind={payload.get('kind')}, "
        f"niveles={list(levels)})")


if __name__ == "__main__":
    main()
