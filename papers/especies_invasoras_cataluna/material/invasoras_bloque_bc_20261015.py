#!/usr/bin/env python3
"""Tablas B/C, figuras y análisis P1/P3/P6 con datos locales (postgres + CSV). Sin GPU, sin APIs iNat/Minka."""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

M = Path(__file__).parent
P = M.parent
F = M / "figuras"

BOX = (40.45, 42.95, 0.1, 3.4)  # lat_min, lat_max, lng_min, lng_max


def psql(sql: str) -> pd.DataFrame:
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


def effort_by_group():
    ts = json.loads((M / "target_species.json").read_text())
    taxa = {t["inat_taxon"]: t for t in ts}
    sql = f"""
    SELECT taxon_id::text, source, obs_year::text AS year, COUNT(*)::text AS n
    FROM public_observations
    WHERE lat BETWEEN {BOX[0]} AND {BOX[1]} AND lng BETWEEN {BOX[2]} AND {BOX[3]}
      AND obs_year BETWEEN 2005 AND 2025
      AND quality_grade = 'research'
    GROUP BY 1,2,3;
    """
    df = psql(sql)
    if df.empty:
        return
    df["n"] = df["n"].astype(int)
    df["year"] = df["year"].astype(int)
    df["taxon_id"] = df["taxon_id"].astype(int)
    df["grupo"] = df["taxon_id"].map(
        lambda i: taxa.get(i, {}).get("kingdom", "Desconocido")
    )
    # coarse iconic groups
    def iconic(row):
        t = taxa.get(int(row["taxon_id"]), {})
        k, c = t.get("kingdom", ""), t.get("class", "")
        if k == "Plantae":
            return "Plantae"
        if c == "Aves":
            return "Aves"
        if c == "Mammalia":
            return "Mammalia"
        if c in ("Actinopterygii", "Elasmobranchii"):
            return "Actinopterygii"
        if k == "Animalia":
            return "Invertebrados"
        return "Otros"

    df["iconic"] = df.apply(iconic, axis=1)
    g = df.groupby(["year", "iconic"], as_index=False)["n"].sum()
    g.to_csv(M / "esfuerzo_por_grupo_20261015.csv", index=False)
    pivot = g.pivot(index="year", columns="iconic", values="n").fillna(0)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for col in pivot.columns:
        ax.plot(pivot.index, pivot[col], marker="o", ms=3, label=col)
    ax.set_yscale("log")
    ax.set_xlabel("Año")
    ax.set_ylabel("Observaciones research-grade (caja CAT)")
    ax.set_title("Esfuerzo por grupo taxonómico (taxones del catálogo en public_observations)")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(F / "esfuerzo_por_grupo_20261015.png", dpi=160)
    plt.close(fig)


def dedup_overlap():
    sql = f"""
    WITH c AS (
      SELECT taxon_id, obs_year,
             ROUND(lat::numeric, 3) AS rlat, ROUND(lng::numeric, 3) AS rlng,
             COUNT(*) FILTER (WHERE source='inat') AS n_inat,
             COUNT(*) FILTER (WHERE source='minka') AS n_minka
      FROM public_observations
      WHERE lat BETWEEN {BOX[0]} AND {BOX[1]} AND lng BETWEEN {BOX[2]} AND {BOX[3]}
        AND quality_grade='research'
      GROUP BY 1,2,3,4
    )
    SELECT
      SUM(n_inat + n_minka) AS suma_bruta,
      SUM(CASE WHEN n_inat>0 AND n_minka>0 THEN GREATEST(n_inat,n_minka) ELSE n_inat+n_minka END) AS suma_dedup_celda
    FROM c;
    """
    df = psql(sql)
    df.to_csv(M / "dedup_inat_minka_caja_20261015.csv", index=False)


def absence_power():
    pres = pd.read_csv(M / "presencia_cat_es.csv")
    easin = pd.read_csv(M / "concordancia_easin_20261015.csv")
    eff = pd.read_csv(M / "esfuerzo_bioquest_anual.csv")
    e2024 = float(eff.loc[eff.year == 2024, "n_obs_caja_cat"].iloc[0])
    rows = []
    for _, r in pres.iterrows():
        if r["presencia_catalunya"] != "no":
            continue
        if r["presencia_espana"] != "sí":
            continue
        n_es = int(r["obs_espana"] or 0)
        if n_es < 1:
            continue
        # crude: expected in CAT ~ n_es * (eff_cat / eff_spain proxy) — use obs ratio from presencia
        # Spain total effort unknown; use n_es as rate proxy: lambda = n_es * (e2024 / 1e6) heuristic
        lam = max(n_es * (e2024 / 500_000), 0.01)
        p0 = math.exp(-lam)
        rows.append(
            {
                "especie": r["especie"],
                "obs_espana": n_es,
                "lambda_esperado_cat_aprox": round(lam, 3),
                "P_cero_obs_CAT_si_presente": round(p0, 4),
                "ausencia_informativa": "sí" if p0 < 0.05 else "no",
            }
        )
    pd.DataFrame(rows).to_csv(M / "potencia_ausencia_cat_20261015.csv", index=False)


def fig_heatmap():
    sql = f"""
    SELECT FLOOR((lng - {BOX[2]}) / 0.09)::int AS gx,
           FLOOR((lat - {BOX[0]}) / 0.09)::int AS gy,
           COUNT(*)::int AS n
    FROM public_observations
    WHERE lat BETWEEN {BOX[0]} AND {BOX[1]} AND lng BETWEEN {BOX[2]} AND {BOX[3]}
      AND quality_grade='research' AND obs_year BETWEEN 2018 AND 2024
    GROUP BY 1,2;
    """
    df = psql(sql)
    if df.empty:
        return
    df["gx"] = df["gx"].astype(int)
    df["gy"] = df["gy"].astype(int)
    df["n"] = df["n"].astype(int)
    w, h = df.gx.max() + 1, df.gy.max() + 1
    grid = np.zeros((h, w))
    for _, r in df.iterrows():
        grid[r.gy, r.gx] = np.log10(r.n + 1)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(grid, origin="lower", cmap="YlOrRd", aspect="auto")
    ax.set_title("Fig. 1. Densidad de esfuerzo (log10 obs), caja CAT 2018–2024")
    ax.set_xlabel("celda ~10 km (aprox.)")
    ax.set_ylabel("celda ~10 km (aprox.)")
    fig.tight_layout()
    fig.savefig(F / "area_estudio_esfuerzo_heatmap_20261015.png", dpi=160)
    plt.close(fig)


def fig_composition():
    pres = pd.read_csv(M / "presencia_cat_es.csv")
    pres = pres[pres.categoria != "ausente"]
    cat_map = {
        "ocasional_o_puntual": "ocasional",
        "recurrente": "recurrente",
        "llegada_reciente_serie_insuficiente": "llegada reciente",
    }
    pres["cat"] = pres["categoria"].map(cat_map).fillna(pres["categoria"])
    g = pres.groupby(["grupo_taxonomico", "cat"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4))
    g.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
    ax.set_title("Fig. 3. Taxones UE con registro en Cataluña por grupo y categoría")
    ax.set_xlabel("Grupo taxonómico")
    ax.set_ylabel("N taxones")
    ax.legend(title="Categoría", fontsize=7)
    fig.tight_layout()
    fig.savefig(F / "composicion_ue_cat_20261015.png", dpi=160)
    plt.close(fig)


def fig_marine_delay():
    mar = pd.read_csv(M / "marinas_weitzmann_comparativa_20261010.csv")
    mar = mar[mar["primera_inat_cat"].notna() & (mar["primera_inat_cat"] != "")]
    # literature years hardcoded where known from paper
    lit = {
        "Oculina patagonica": 2011,
        "Caulerpa cylindracea": 2014,
        "Callinectes sapidus": 2012,
        "Bursatella leachii": 2007,
    }
    rows = []
    for _, r in mar.iterrows():
        sp = r["especie"]
        if sp not in lit:
            continue
        cit = lit[sp]
        iyr = int(str(r["primera_inat_cat"])[:4])
        rows.append({"especie": sp, "lit": cit, "inat": iyr})
    if not rows:
        return
    d = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    y = np.arange(len(d))
    for i, row in d.iterrows():
        ax.plot([row["lit"], row["inat"]], [i, i], "k-", lw=1)
        ax.scatter([row["lit"], row["inat"]], [i, i], c=["#2980b9", "#e67e22"])
    ax.set_yticks(y)
    ax.set_yticklabels(d.especie, style="italic", fontsize=8)
    ax.set_xlabel("Año")
    ax.set_title("Fig. 7. Primera cita publicada (aprox.) frente a primer registro iNaturalist en Cataluña")
    fig.tight_layout()
    fig.savefig(F / "marinas_retraso_ciudadano_20261015.png", dpi=160)
    plt.close(fig)


def write_tablas():
    t1 = """# Tabla 1. Fuentes de datos

| Plataforma | Ámbito | Periodo | Filtros | Descarga | Licencia |
|---|---|---|---|---|---|
| iNaturalist | place Cataluña (61614) / España (6774) | 2005–2026 | research grade; cautivas excluidas (no auditado) | oct-2026 | CC BY / CC BY-NC |
| Minka | caja 0,1–3,4° E; 40,45–42,95° N | 2005–2026 | research grade | oct-2026 | según observador |
| BioQuest (`public_observations`) | misma caja | 2005–2026 | research grade | oct-2026 | uso interno / agregados |
| EASIN | España | consulta 15-oct-2026 | fichas oficiales UE | API apixg | uso científico |
| WoRMS | taxones acuáticos | 15-oct-2026 | REST | REST | CC BY |
"""
    (P / "TABLA_1_FUENTES.md").write_text(t1, encoding="utf-8")

    pres = pd.read_csv(M / "presencia_cat_es.csv")
    glm = pd.read_csv(M / "glm_tendencias_20261015.csv")
    glm = glm[glm.ventana == "2013-2025"][["especie", "RR_anual", "IC95_lo", "IC95_hi", "q_BH", "clase"]]
    pres_cat = pres[pres.presencia_catalunya == "sí"].copy()
    pres_cat = pres_cat.merge(glm, on="especie", how="left")
    lines = [
        "# Tabla 3. Presencia en Cataluña, tendencia y primer registro ciudadano\n\n",
        "| Especie | Obs | Celdas UTM 10 km | Primer registro ciudadano | Categoría | RR anual (IC 95 %) | q (FDR) |\n",
        "|---|---:|---:|---|---|---:|---:|\n",
    ]
    cat_h = {
        "ocasional_o_puntual": "ocasional",
        "llegada_reciente_serie_insuficiente": "llegada reciente",
    }
    for _, r in pres_cat.sort_values("obs_catalunya", ascending=False).iterrows():
        cat = cat_h.get(r["categoria"], r["categoria"])
        pr = r.get("primera_obs_catalunya", "") or "—"
        if pd.notna(r.get("RR_anual")):
            rr = f"{r['RR_anual']:.2f} ({r['IC95_lo']:.2f}–{r['IC95_hi']:.2f})"
            q = f"{r['q_BH']:.3f}" if pd.notna(r["q_BH"]) else "—"
        else:
            rr, q = "—", "—"
        loc = r.get("localidades_catalunya")
        loc_s = int(loc) if pd.notna(loc) else "—"
        lines.append(
            f"| *{r['especie']}* | {int(r['obs_catalunya'])} | {loc_s} | {pr} | {cat} | {rr} | {q} |\n"
        )
    (P / "TABLA_3_PRESENCIA_TENDENCIAS.md").write_text("".join(lines), encoding="utf-8")

    easin = pd.read_csv(M / "concordancia_easin_20261015.csv")
    n_easin_es = (easin.EASIN_presente_ES == True).sum()
    n_cc_es = (easin.ciudadana_ES == "sí").sum()
    both = ((easin.EASIN_presente_ES == True) & (easin.ciudadana_ES == "sí")).sum()
    only_e = ((easin.EASIN_presente_ES == True) & (easin.ciudadana_ES != "sí")).sum()
    only_c = ((easin.EASIN_presente_ES != True) & (easin.ciudadana_ES == "sí")).sum()
    t4 = f"""# Tabla 4. Concordancia de presencia (EASIN España frente a ciencia ciudadana)

Escala **país** (EASIN no sustituye EXOCAT en Cataluña; EXOCAT pendiente de descarga manual).

|  | Ciudadana: presente ES | Ciudadana: ausente ES |
|---|---:|---:|
| EASIN: presente ES | {both} | {only_e} |
| EASIN: ausente ES | {only_c} | — |

El desglose por especie figura en la Tabla S4. Falsos ausentes ciudadanos (EASIN sí, ciudadana no): {only_e} taxones. Registros ciudadanos sin respaldo EASIN: {only_c} (*Mulinia lateralis*, *Andropogon virginicus*).
"""
    (P / "TABLA_4_CONCORDANCIA_EASIN.md").write_text(t4, encoding="utf-8")

    # Tabla S2 full effort
    eff = pd.read_csv(M / "esfuerzo_bioquest_anual.csv")
    s2 = "# Tabla S2. Esfuerzo anual (base BioQuest, caja CAT)\n\n| Año | Observaciones |\n|---|---:|\n"
    for _, r in eff.iterrows():
        s2 += f"| {int(r.year)} | {int(r.n_obs_caja_cat)} |\n"
    s2 += "\nDesglose por grupo taxonómico (research grade, taxones del catálogo en la caja): ver Fig. 2 (cont.) y Tabla S2 (nota).\n"
    (P / "SUPLEMENTO_TABLA_S2.md").write_text(s2, encoding="utf-8")

    pres_cat2 = pres[pres.presencia_catalunya == "sí"].merge(
        easin[["especie", "EASIN_vias_CBD"]], on="especie", how="left"
    )
    t2 = [
        "# Tabla 2. Origen, hábitat, vía y primer registro (taxones presentes en Cataluña)\n\n",
        "| Especie | Hábitat | Origen | Vía principal (EASIN/CBD) | Primer registro ciudadano | Categoría |\n",
        "|---|---|---|---|---|---|\n",
    ]
    for _, r in pres_cat2.sort_values("obs_catalunya", ascending=False).iterrows():
        hab = (r.get("habitat_tags") or r.get("medio") or "").replace(",", "+")
        orig = r.get("origen_nativo_probable") or "—"
        via = (r.get("via_entrada") or r.get("EASIN_vias_CBD") or "—")
        if isinstance(via, str) and len(via) > 80:
            via = via.split(";")[0] + "…"
        pr = r.get("primera_obs_catalunya") or "—"
        cat = cat_h.get(r["categoria"], r["categoria"])
        t2.append(f"| *{r['especie']}* | {hab} | {orig} | {via} | {pr} | {cat} |\n")
    (P / "TABLA_2_ORIGEN_VIAS_CAT.md").write_text("".join(t2), encoding="utf-8")

    s4 = "# Tabla S4. Concordancia EASIN–ciudadana por especie\n\n"
    s4 += "| Especie | EASIN ES | Ciudadana ES | Ciudadana CAT |\n|---|---|---|---|\n"
    for _, r in easin.sort_values("especie").iterrows():
        e = "sí" if r.EASIN_presente_ES == True or str(r.EASIN_presente_ES).lower() == "true" else "no"
        s4 += f"| *{r.especie}* | {e} | {r.ciudadana_ES} | {r.ciudadana_CAT} |\n"
    (P / "SUPLEMENTO_TABLA_S4_EASIN.md").write_text(s4, encoding="utf-8")

    canon = {
        "taxones_ue": 114,
        "presentes_cat": int((pres.presencia_catalunya == "sí").sum()),
        "presentes_es": int((pres.presencia_espana == "sí").sum()),
        "ausentes_cat": int((pres.categoria == "ausente").sum()),
        "esfuerzo_2013": int(eff.loc[eff.year == 2013, "n_obs_caja_cat"].iloc[0]),
        "esfuerzo_2024": int(eff.loc[eff.year == 2024, "n_obs_caja_cat"].iloc[0]),
        "esfuerzo_2025": int(eff.loc[eff.year == 2025, "n_obs_caja_cat"].iloc[0]) if (eff.year == 2025).any() else None,
        "easin_concordancia": {
            "ambos": int(both),
            "solo_easin": int(only_e),
            "solo_ciudadana": int(only_c),
        },
    }
    (M / "cifras_canonicas_20261015.json").write_text(json.dumps(canon, indent=2), encoding="utf-8")

    canon_md = f"""# Cifras canónicas (15-oct-2026)

| Concepto | Valor |
|---|---:|
| Taxones lista UE | 114 |
| Presentes en Cataluña | {canon['presentes_cat']} |
| Presentes en España (ciudadana) | {canon['presentes_es']} |
| Ausentes en Cataluña | {canon['ausentes_cat']} |
| Esfuerzo BioQuest 2013 / 2024 / 2025 | {canon['esfuerzo_2013']} / {canon['esfuerzo_2024']} / {canon['esfuerzo_2025']} |
| EASIN∩ciudadana ES | {canon['easin_concordancia']['ambos']} |
| Solo EASIN | {canon['easin_concordancia']['solo_easin']} |
| Solo ciudadana | {canon['easin_concordancia']['solo_ciudadana']} |
| Solape iNat–Minka (dedup celdas, caja) | ~0,4 % (372.987 frente a 374.348 brutas) |
"""
    (M / "cifras_canonicas_20261015.md").write_text(canon_md, encoding="utf-8")


def main():
    effort_by_group()
    dedup_overlap()
    absence_power()
    fig_heatmap()
    fig_composition()
    fig_marine_delay()
    write_tablas()
    print("OK bloque_bc")


if __name__ == "__main__":
    main()
