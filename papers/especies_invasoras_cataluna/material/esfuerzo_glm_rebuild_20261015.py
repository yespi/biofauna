#!/usr/bin/env python3
"""Esfuerzo = todas las obs research-grade iNat+Minka en caja CAT, menos la especie (offset).
Regenera esfuerzo_cat_total_anual.csv, actualiza serie y glm_tendencias_20261015.csv."""
from __future__ import annotations

import json
import subprocess
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

warnings.filterwarnings("ignore")

M = Path(__file__).parent
BOX = (40.45, 42.95, 0.1, 3.4)  # lat_min, lat_max, lng_min, lng_max


def psql_df(sql: str) -> pd.DataFrame:
    cmd = [
        "docker",
        "exec",
        "postgres-global",
        "psql",
        "-U",
        "admin_yespi",
        "-d",
        "fauna",
        "-A",
        "-F",
        ",",
        "-c",
        sql,
    ]
    out = subprocess.check_output(cmd, text=True)
    lines = [ln for ln in out.strip().splitlines() if ln and not ln.startswith("(")]
    if len(lines) < 2:
        return pd.DataFrame()
    header = lines[0].split(",")
    rows = [ln.split(",") for ln in lines[1:]]
    return pd.DataFrame(rows, columns=header)


def main():
    sql_total = f"""
    SELECT obs_year::int AS year, COUNT(*)::bigint AS n_total
    FROM public_observations
    WHERE quality_grade = 'research'
      AND lat BETWEEN {BOX[0]} AND {BOX[1]}
      AND lng BETWEEN {BOX[2]} AND {BOX[3]}
      AND obs_year BETWEEN 2005 AND 2026
    GROUP BY 1 ORDER BY 1;
    """
    tot = psql_df(sql_total)
    tot["year"] = tot["year"].astype(int)
    tot["n_total"] = tot["n_total"].astype(int)
    tot.to_csv(M / "esfuerzo_cat_total_anual_20261015.csv", index=False)

    ts = json.loads((M / "target_species.json").read_text())
    ue = {
        t["name"]: int(t["inat_taxon"])
        for t in ts
        if t.get("inat_taxon") is not None
    }
    ids = ",".join(str(i) for i in ue.values())
    sql_sp = f"""
    SELECT taxon_id::int, obs_year::int AS year, COUNT(*)::int AS n
    FROM public_observations
    WHERE quality_grade = 'research'
      AND lat BETWEEN {BOX[0]} AND {BOX[1]}
      AND lng BETWEEN {BOX[2]} AND {BOX[3]}
      AND taxon_id = ANY(ARRAY[{ids}]::int[])
      AND obs_year BETWEEN 2005 AND 2026
    GROUP BY 1,2;
    """
    sp = psql_df(sql_sp)
    if sp.empty:
        raise SystemExit("sin series por especie")
    sp["taxon_id"] = sp["taxon_id"].astype(int)
    sp["year"] = sp["year"].astype(int)
    sp["n"] = sp["n"].astype(int)
    tid_to_name = {v: k for k, v in ue.items()}
    sp["especie"] = sp["taxon_id"].map(tid_to_name)

    eff = tot.set_index("year")["n_total"]
    serie = pd.read_csv(M / "serie_anual_normalizada.csv")
    serie = serie[serie.region == "Catalunya"].copy()
    # refresh obs from DB for UE species
    for especie, g in sp.groupby("especie"):
        idx = serie["especie"] == especie
        if not idx.any():
            continue
        for _, r in g.iterrows():
            m = idx & (serie["year"] == r["year"])
            if m.any():
                serie.loc[m, "obs"] = r["n"]
    serie["esfuerzo_total_caja"] = serie["year"].map(eff)
    serie["esfuerzo_offset"] = np.maximum(
        serie["esfuerzo_total_caja"] - serie["obs"].fillna(0).astype(int), 1
    )
    serie["esfuerzo_bioquest_caja"] = serie["esfuerzo_offset"]
    serie["obs_por_1000_esfuerzo"] = (
        serie["obs"].fillna(0) / serie["esfuerzo_offset"] * 1000
    )
    serie.to_csv(M / "serie_anual_normalizada.csv", index=False)

    eff_out = tot.copy()
    eff_out.columns = ["year", "n_obs_caja_cat"]
    eff_out.to_csv(M / "esfuerzo_bioquest_anual.csv", index=False)

    res = []
    for sp_name, gdf in serie.groupby("especie"):
        is_ue = sp_name in ue
        for (y0, y1) in [(2013, 2025), (2016, 2025)]:
            yrs = np.arange(y0, y1 + 1)
            sub = gdf.set_index("year").reindex(yrs)
            o = sub["obs"].fillna(0).astype(int)
            e = sub["esfuerzo_offset"].astype(float)
            n, ny = int(o.sum()), int((o > 0).sum())
            row = {
                "especie": sp_name,
                "UE": is_ue,
                "ventana": f"{y0}-{y1}",
                "n_obs": n,
                "anios_con_obs": ny,
            }
            if is_ue and n >= 10 and ny >= 5:
                X = sm.add_constant((yrs - yrs.mean()).astype(float))
                try:
                    m = sm.NegativeBinomial(
                        o.values, X, offset=np.log(e.values)
                    ).fit(disp=0, maxiter=250)
                    b, se, p, alpha = (
                        m.params[1],
                        m.bse[1],
                        m.pvalues[1],
                        m.params[-1],
                    )
                except Exception:
                    m = sm.GLM(
                        o.values,
                        X,
                        family=sm.families.Poisson(),
                        offset=np.log(e.values),
                    ).fit(cov_type="HC0")
                    b, se, p, alpha = m.params[1], m.bse[1], m.pvalues[1], np.nan
                row.update(
                    RR_anual=np.exp(b),
                    IC95_lo=np.exp(b - 1.96 * se),
                    IC95_hi=np.exp(b + 1.96 * se),
                    p=p,
                    alpha=alpha,
                )
            res.append(row)

    r = pd.DataFrame(res)
    for v, gg in r.groupby("ventana"):
        ok = gg.p.notna()
        if ok.any():
            r.loc[gg.index[ok], "q_BH"] = multipletests(gg.p[ok], method="fdr_bh")[1]
    r["clase"] = np.where(
        r.q_BH.isna(),
        "no_estimable",
        np.where(
            (r.q_BH < 0.05) & (r.RR_anual > 1),
            "creciente",
            np.where((r.q_BH < 0.05), "decreciente", "sin_tendencia_significativa"),
        ),
    )
    r.to_csv(M / "glm_tendencias_20261015.csv", index=False, float_format="%.4g")
    ue13 = r[(r.UE == True) & (r.ventana == "2013-2025") & r.p.notna()]
    print("UE 2013-2025 estimables:", len(ue13))
    print(ue13.sort_values("q_BH")[["especie", "RR_anual", "q_BH", "clase"]].head(12))


if __name__ == "__main__":
    main()
