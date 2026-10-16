#!/usr/bin/env python3
"""GLM NB2: obs especie ~ año centrado + offset(log esfuerzo caja), FDR BH.

Ventana 2013–2025 (excluye 2026 incompleto). Esfuerzo = todas las obs en caja CAT.
Uso: /tmp/rev/venv/bin/python glm_tendencias_declives_20261016.py
"""
from __future__ import annotations

import subprocess
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

warnings.filterwarnings("ignore")

M = Path(__file__).parent
LAT_MIN, LAT_MAX = 40.45, 42.95
LON_MIN, LON_MAX = 0.10, 3.40
Y0, Y1 = 2013, 2025

SPECIES = [
    ("Pinna nobilis", 118945),
    ("Pinna rudis", 292173),
    ("Epinephelus marginatus", 100119),
    ("Epinephelus costae", 100091),
    ("Serranus scriba", 118674),
    ("Serranus cabrilla", 118675),
    ("Corallium rubrum", 483326),
    ("Paramuricea clavata", 338005),
    ("Posidonia oceanica", 118943),
    ("Cymodocea nodosa", 131135),
]


def sql(q: str) -> list[tuple[str, ...]]:
    r = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "postgres-global",
            "psql",
            "-U",
            "admin_yespi",
            "-d",
            "fauna",
            "-t",
            "-A",
            "-F",
            "\t",
            "-c",
            q,
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    rows = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if line:
            rows.append(tuple(line.split("\t")))
    return rows


def effort_by_year() -> pd.Series:
    q = f"""
    SELECT obs_year, COUNT(*)::bigint
    FROM public_observations
    WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lng BETWEEN {LON_MIN} AND {LON_MAX}
      AND obs_year BETWEEN {Y0} AND {Y1}
    GROUP BY 1 ORDER BY 1;
    """
    d = {int(y): int(n) for y, n in sql(q)}
    yrs = np.arange(Y0, Y1 + 1)
    return pd.Series([d.get(int(y), 0) for y in yrs], index=yrs, dtype=float)


def counts_for(taxon_id: int) -> pd.Series:
    q = f"""
    SELECT obs_year, COUNT(*)::bigint
    FROM public_observations
    WHERE taxon_id = {taxon_id}
      AND lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lng BETWEEN {LON_MIN} AND {LON_MAX}
      AND obs_year BETWEEN {Y0} AND {Y1}
    GROUP BY 1 ORDER BY 1;
    """
    d = {int(y): int(n) for y, n in sql(q)}
    yrs = np.arange(Y0, Y1 + 1)
    return pd.Series([d.get(int(y), 0) for y in yrs], index=yrs, dtype=int)


def main() -> None:
    eff = effort_by_year()
    res = []
    for sp, tid in SPECIES:
        o = counts_for(tid)
        yrs = o.index.values.astype(float)
        n, ny = int(o.sum()), int((o > 0).sum())
        row = dict(species=sp, taxon_id=tid, n_obs=n, anios_con_obs=ny)
        if n >= 20 and ny >= 5 and eff.min() > 0:
            X = sm.add_constant(yrs - yrs.mean())
            try:
                m = sm.NegativeBinomial(
                    o.values, X, offset=np.log(eff.values)
                ).fit(disp=0, maxiter=250)
                b, se, p = m.params[1], m.bse[1], m.pvalues[1]
            except Exception:
                m = sm.GLM(
                    o.values,
                    X,
                    family=sm.families.Poisson(),
                    offset=np.log(eff.values),
                ).fit(cov_type="HC0")
                b, se, p = m.params[1], m.bse[1], m.pvalues[1]
            row.update(
                RR_anual=float(np.exp(b)),
                IC95_lo=float(np.exp(b - 1.96 * se)),
                IC95_hi=float(np.exp(b + 1.96 * se)),
                p=float(p),
            )
        res.append(row)
    r = pd.DataFrame(res)
    ok = r.p.notna()
    if ok.any():
        r.loc[ok, "q_BH"] = multipletests(r.p[ok], method="fdr_bh")[1]
    r["clase"] = np.where(
        r.q_BH.isna(),
        "no estimable",
        np.where(
            (r.q_BH < 0.05) & (r.RR_anual < 1),
            "decreciente (q<0,05)",
            np.where(
                (r.q_BH < 0.05) & (r.RR_anual > 1),
                "creciente (q<0,05)",
                "sin tendencia significativa",
            ),
        ),
    )
    out = M / "glm_tendencias_declives_20261016.csv"
    r.to_csv(out, index=False, float_format="%.4g")
    print(r.to_string())
    print("wrote", out)


if __name__ == "__main__":
    main()
