#!/usr/bin/env python3
"""GLM binomial negativa (NB2) obs ~ año + offset(log esfuerzo), FDR BH. Sin GPU, sin APIs.
Esfuerzo = total BioQuest en caja CAT (serie_anual_normalizada.csv); NO por grupo (limitación documentada en el paper).
Uso: /tmp/rev/venv/bin/python glm_tendencias_20261015.py"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings("ignore")
M = Path(__file__).parent
ue = {x["name"] for x in json.load(open(M / "target_species.json"))}
df = pd.read_csv(M / "serie_anual_normalizada.csv")
df = df[df.region == "Catalunya"]

def fit(g, y0, y1):
    g = g[(g.year >= y0) & (g.year <= y1)]
    yrs = np.arange(y0, y1 + 1)
    g = g.set_index("year").reindex(yrs)
    eff = df[df.especie == g.attrs.get("sp", "")]  # placeholder
    return g

res = []
eff_year = df.groupby("year").esfuerzo_bioquest_caja.max()
for sp, g in df.groupby("especie"):
    for (y0, y1) in [(2013, 2025), (2016, 2025)]:
        yrs = np.arange(y0, y1 + 1)
        o = g.set_index("year").obs.reindex(yrs).fillna(0).astype(int)
        e = eff_year.reindex(yrs).astype(float)
        n, ny = int(o.sum()), int((o > 0).sum())
        row = dict(especie=sp, UE=sp in ue, ventana=f"{y0}-{y1}", n_obs=n, anios_con_obs=ny)
        if n >= 10 and ny >= 5:
            X = sm.add_constant((yrs - yrs.mean()).astype(float))
            try:
                m = sm.NegativeBinomial(o.values, X, offset=np.log(e.values)).fit(disp=0, maxiter=200)
                b, se, p, alpha = m.params[1], m.bse[1], m.pvalues[1], m.params[-1]
            except Exception:
                m = sm.GLM(o.values, X, family=sm.families.Poisson(), offset=np.log(e.values)).fit(cov_type="HC0")
                b, se, p, alpha = m.params[1], m.bse[1], m.pvalues[1], np.nan
            row.update(RR_anual=np.exp(b), IC95_lo=np.exp(b - 1.96 * se), IC95_hi=np.exp(b + 1.96 * se), p=p, alpha=alpha)
        res.append(row)
r = pd.DataFrame(res)
for v, gg in r.groupby("ventana"):
    ok = gg.p.notna()
    r.loc[gg.index[ok], "q_BH"] = multipletests(gg.p[ok], method="fdr_bh")[1]
r["clase"] = np.where(r.q_BH.isna(), "no_estimable", np.where((r.q_BH < .05) & (r.RR_anual > 1), "creciente", np.where((r.q_BH < .05), "decreciente", "sin_tendencia_significativa")))
r.to_csv(M / "glm_tendencias_20261015.csv", index=False, float_format="%.4g")
print(r[r.p.notna()].sort_values(["ventana", "q_BH"]).to_string())
