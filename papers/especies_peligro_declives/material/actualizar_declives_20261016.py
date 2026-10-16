#!/usr/bin/env python3
"""Última observación en tabla declives + regenerar filas ARTICULO §3.2 (sin APIs externas)."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pandas as pd

M = Path(__file__).parent
P = M.parent
BOX = (40.45, 42.95, 0.1, 3.4)


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


def fmt_date(y, m, d) -> str:
    if y in (None, "", "None") or pd.isna(y):
        return "sin datos"
    try:
        y = int(float(y))
        if m in (None, "", "None") or pd.isna(m):
            return f"{y}"
        m = int(float(m))
        if d in (None, "", "None") or pd.isna(d):
            return f"{y:04d}-{min(max(m, 1), 12):02d}"
        d = int(float(d))
        return f"{y:04d}-{min(max(m, 1), 12):02d}-{min(max(d, 1), 28):02d}"
    except (ValueError, TypeError):
        return "sin datos"


def main() -> None:
    df = pd.read_csv(M / "declives_tendencias_20261011.csv")
    ids = df["taxon_id"].dropna().astype(int).tolist()
    id_list = ",".join(str(i) for i in ids)
    lat0, lat1, lon0, lon1 = BOX
    sql = f"""
    WITH last AS (
      SELECT taxon_id, MAX(obs_year)::int AS y_max
      FROM public_observations
      WHERE taxon_id IN ({id_list})
        AND lat BETWEEN {lat0} AND {lat1}
        AND lng BETWEEN {lon0} AND {lon1}
      GROUP BY taxon_id
    )
    SELECT o.taxon_id, o.obs_year, o.obs_month, o.obs_day
    FROM public_observations o
    JOIN last l ON l.taxon_id = o.taxon_id AND l.y_max = o.obs_year
    WHERE o.lat BETWEEN {lat0} AND {lat1} AND o.lng BETWEEN {lon0} AND {lon1}
    """
    last = psql(sql)
    if not last.empty:
        last["ultima_obs"] = last.apply(
            lambda r: fmt_date(r.get("obs_year"), r.get("obs_month"), r.get("obs_day")),
            axis=1,
        )
        by_taxon = {
            int(k): v
            for k, v in last.assign(taxon_id=last["taxon_id"].astype(int))
            .groupby("taxon_id")["ultima_obs"]
            .max()
            .items()
        }
    else:
        by_taxon = {}
    df["ultima_obs_catalunya"] = df["taxon_id"].map(
        lambda t: by_taxon.get(int(t), "sin datos") if pd.notna(t) else "sin datos"
    )
    df.to_csv(M / "declives_tendencias_20261016.csv", index=False)

    objetivo = df[df["species"].isin(
        [
            "Pinna nobilis",
            "Pinna rudis",
            "Epinephelus marginatus",
            "Epinephelus costae",
            "Serranus scriba",
            "Serranus cabrilla",
            "Corallium rubrum",
            "Paramuricea clavata",
            "Posidonia oceanica",
            "Cymodocea nodosa",
        ]
    )].copy()

    def cat_human(c: str) -> str:
        return (c or "").replace("_", " ")

    lines = [
        "| Especie | n | Primera obs. | Última obs. | ratio_5y | vs ctrl | Categoría relativa |",
        "|---|---:|---|---|---:|---:|---|",
    ]
    for _, r in objetivo.iterrows():
        sp = r["species"].replace("_", " ")
        lines.append(
            f"| *{sp}* | {int(r['n_obs_cat'])} | {r['first_obs_cat']} | "
            f"{r['ultima_obs_catalunya']} | {r['ratio_5y']:.2f} | "
            f"**{r['ratio_vs_controls']:.2f}** | {cat_human(r['category_vs_controls'])} |"
        )
    table = "\n".join(lines)

    art = (P / "ARTICULO.md").read_text(encoding="utf-8")
    art = re.sub(
        r"### 3\.2 Tabla resumen \(objetivo\)\n\n.*?\n\nCSV completo:",
        "### 3.2 Tabla resumen (objetivo)\n\n"
        + table
        + "\n\n*Última observación:* máximo año/mes/día en `public_observations` dentro de la caja de estudio; "
        "«s. d.» si no hay fila georreferenciada.\n\nCSV completo:",
        art,
        count=1,
        flags=re.DOTALL,
    )
    art = art.replace(
        "declives_tendencias_20261011.csv`](declives_tendencias_20261011.csv)",
        "declives_tendencias_20261016.csv`](material/declives_tendencias_20261016.csv)",
    )
    art = art.replace(
        "controles_tendencias_20261011.csv`](controles_tendencias_20261011.csv)",
        "controles_tendencias_20261011.csv`](material/controles_tendencias_20261011.csv)",
    )
    (P / "ARTICULO.md").write_text(art, encoding="utf-8")
    print("ok", len(objetivo), "species")


if __name__ == "__main__":
    main()
