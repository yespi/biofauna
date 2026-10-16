#!/usr/bin/env python3
"""P2: tendencia por especie UE con GLMM Poisson-lognormal (intercepto aleatorio de observador) y offset log(esfuerzo del observador en el grupo).
Unidad: observador x año (observadores activos en el grupo ese año; las especies de la lista UE, GBIF iNat RG, Cataluña GADM ESP.6_1).
  y_jt ~ Poisson(mu_jt), log mu_jt = log(n_jt - y_jt) + b0 + b1*(año-centro) + u_j, u_j ~ N(0, s^2)
Verosimilitud marginal por cuadratura Gauss-Hermite (40 nodos) por observador; SE de b1 sandwich agrupado por observador (robusto a sobredispersión).
Comparación: mismo modelo sin efecto aleatorio (s->0) y sensibilidad sin los 3 observadores con más registros de la especie. BH sobre especies estimables.
Salida: glm_tendencias_glmm_20261016.csv"""
import numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp, gammaln
from statsmodels.stats.multitest import multipletests
from pathlib import Path
M = Path(__file__).parent
GH_x, GH_w = np.polynomial.hermite.hermgauss(40)
reg = pd.read_csv(M / "registros_ue_gbif_20261016.csv")
raw = pd.read_pickle("/tmp/obs_year_raw.pkl")  # observador, obs_id (seudónimo)
name2id = dict(zip(raw.observador, raw.obs_id))
reg["obs_id"] = reg.observador.fillna("").map(name2id)
oy = pd.read_csv(M / "observador_anio_grupo_gbif_20261016.csv.gz")

def design(sp, grupo, y0, y1, drop=()):
    g = oy[(oy.grupo == grupo) & oy.year.between(y0, y1)]
    r = reg[(reg.especie == sp) & reg.year.between(y0, y1)]
    ry = r.groupby(["obs_id", "year"]).size().rename("y").reset_index()
    d = g.merge(ry, on=["obs_id", "year"], how="outer").fillna({"y": 0, "n": 0})
    d = d[d.obs_id.notna()]
    d["n"] = np.maximum(d.n, d.y)  # el registro de la especie pertenece al grupo
    d["eff"] = np.maximum(d.n - d.y, 1.0)
    if drop: d = d[~d.obs_id.isin(drop)]
    d = d.sort_values("obs_id").reset_index(drop=True)
    return d, int(r.shape[0]), int(r.year.nunique()), r

def make_ll(d, y0, y1, re=True):
    yy = d.y.values.astype(float); off = np.log(d.eff.values); t = d.year.values - (y0 + y1) / 2.0
    _, idx = np.unique(d.obs_id.values, return_index=True)
    lg = gammaln(yy + 1)
    def per_obs(th):
        b0, b1 = th[0], th[1]
        eta = off + b0 + b1 * t
        if not re:
            ll = yy * eta - np.exp(eta) - lg
            return np.add.reduceat(ll, idx)
        s = np.exp(th[2]); u = np.sqrt(2) * s * GH_x  # nodos
        e = eta[:, None] + u[None, :]
        ll = yy[:, None] * e - np.exp(e) - lg[:, None]
        L = np.add.reduceat(ll, idx, axis=0)  # obs x nodos
        return logsumexp(L, axis=1, b=GH_w / np.sqrt(np.pi))
    return per_obs

def fit(d, y0, y1, re=True):
    f = make_ll(d, y0, y1, re)
    th0 = np.array([np.log(max(d.y.sum(), 1) / d.eff.sum()), 0.0] + ([np.log(0.5)] if re else []))
    nll = lambda th: -f(th).sum()
    r = minimize(nll, th0, method="BFGS", options=dict(gtol=1e-6, maxiter=200))
    th = r.x; k = len(th)
    def grad(fun, x, h=1e-5):
        return np.array([(fun(x + h * e) - fun(x - h * e)) / (2 * h) for e in np.eye(k)])
    S = np.array([[(f(th + 1e-5 * e) - f(th - 1e-5 * e)) / 2e-5 for e in np.eye(k)]]).squeeze(0).T  # obs x k
    Hm = np.zeros((k, k))
    for i, e in enumerate(np.eye(k)):
        Hm[:, i] = (grad(nll, th + 1e-4 * e, 1e-4) - grad(nll, th - 1e-4 * e, 1e-4)) / 2e-4
    Hm = (Hm + Hm.T) / 2
    try:
        Hi = np.linalg.inv(Hm); V = Hi @ (S.T @ S) @ Hi
        se = np.sqrt(V[1, 1]); se_model = np.sqrt(Hi[1, 1])
    except Exception:
        se, se_model = np.nan, np.nan
    return th, se, se_model, bool(np.abs(r.jac).max() < 1e-2)

SP = pd.read_csv(M / "registros_ue_gbif_20261016.csv")[["especie", "grupo"]].drop_duplicates()
allsp = pd.read_json(M / "target_species.json")["name"].tolist()
grp = dict(zip(SP.especie, SP.grupo))
import json
ts = {t["name"]: t for t in json.loads((M / "target_species.json").read_text())}
CLS2G = {"Magnoliopsida":"Plantas","Liliopsida":"Plantas","Polypodiopsida":"Plantas","Aves":"Aves","Mammalia":"Mamíferos","Reptilia":"Herpetofauna","Amphibia":"Herpetofauna","Actinopterygii":"Peces","Insecta":"Insectos"}
def grupo_de(n):
    t = ts[n]
    return CLS2G.get(t.get("class"), "Otros animales (invert. no insectos)" if t.get("kingdom") == "Animalia" else "Otros (hongos, cromistas, etc.)")
rows = []
for y0, y1 in [(2013, 2025), (2016, 2025)]:
    for sp in allsp:
        g = grupo_de(sp)
        d, n, ny, r = design(sp, g, y0, y1)
        row = dict(especie=sp, grupo=g, ventana=f"{y0}-{y1}", n_obs=n, anios_con_obs=ny, n_observadores=int(r.obs_id.nunique()))
        if n >= 10 and ny >= 5:
            top = r.obs_id.value_counts()
            row["top1_pct"] = round(100 * top.iloc[0] / n, 1); row["top3_pct"] = round(100 * top.iloc[:3].sum() / n, 1)
            th, se, sem, ok = fit(d, y0, y1, True)
            th0, se0, _, _ = fit(d, y0, y1, False)
            row.update(RR_anual=np.exp(th[1]), IC95_lo=np.exp(th[1] - 1.96 * se), IC95_hi=np.exp(th[1] + 1.96 * se),
                       p=2 * (1 - __import__("scipy.stats", fromlist=["norm"]).norm.cdf(abs(th[1] / se))), sigma_obs=float(np.exp(th[2])), conv=ok,
                       RR_sinRE=np.exp(th0[1]), p_sinRE=2 * (1 - __import__("scipy.stats", fromlist=["norm"]).norm.cdf(abs(th0[1] / se0))))
            d3, n3, ny3, _ = design(sp, g, y0, y1, drop=tuple(top.index[:3]))
            if n3 >= 10 and (r.obs_id.nunique() > 3):
                th3, se3, _, _ = fit(d3, y0, y1, True)
                row.update(n_sin_top3=int(d3.y.sum()), RR_sin_top3=np.exp(th3[1]), IC_lo_sin_top3=np.exp(th3[1] - 1.96 * se3), IC_hi_sin_top3=np.exp(th3[1] + 1.96 * se3),
                           p_sin_top3=2 * (1 - __import__("scipy.stats", fromlist=["norm"]).norm.cdf(abs(th3[1] / se3))))
        rows.append(row); print(sp, y0, row.get("RR_anual"), flush=True)
r = pd.DataFrame(rows)
for v, gg in r.groupby("ventana"):
    for pc, qc in [("p", "q_BH"), ("p_sinRE", "q_sinRE"), ("p_sin_top3", "q_sin_top3")]:
        ok = gg[pc].notna()
        if ok.any(): r.loc[gg.index[ok], qc] = multipletests(gg.loc[ok, pc], method="fdr_bh")[1]
def clase(q, rr):
    if pd.isna(q): return "no_estimable"
    return "creciente" if (q < .05 and rr > 1) else ("decreciente" if q < .05 else "sin_tendencia_significativa")
r["clase"] = [clase(q, rr) for q, rr in zip(r.q_BH, r.RR_anual)]
r["clase_sin_top3"] = [clase(q, rr) for q, rr in zip(r.q_sin_top3, r.RR_sin_top3)]
r.to_csv(M / "glm_tendencias_glmm_20261016.csv", index=False, float_format="%.4g")
x = r[(r.ventana == "2013-2025") & r.p.notna()].sort_values("q_BH")
pd.set_option("display.width", 250)
print(x[["especie", "n_obs", "n_observadores", "top3_pct", "RR_anual", "IC95_lo", "IC95_hi", "q_BH", "clase", "sigma_obs", "RR_sinRE", "RR_sin_top3", "q_sin_top3"]].to_string())
