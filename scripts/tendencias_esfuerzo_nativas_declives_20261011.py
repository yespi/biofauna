#!/usr/bin/env python3
"""Tendencias normalizadas por esfuerzo (nativas en expansión + declives).

Solo SELECT en postgres-global vía docker. Sin GPU.
Comparte método: tasa = obs_especie_año / esfuerzo_caja_año × 1000;
ratio últimos 5 años / 5 previos; puntos de ruptura heurísticos.
"""
from __future__ import annotations

import csv
import json
import math
import os
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/mnt/docker/biofauna-public")
INV = ROOT / "papers/especies_invasoras_cataluna"
INV_MAT = INV / "material"
DEC = ROOT / "papers/especies_peligro_declives"
DEC_MAT = DEC / "material"
DEC.mkdir(parents=True, exist_ok=True)
(DEC_MAT / "figuras").mkdir(exist_ok=True)
(INV_MAT / "figuras").mkdir(exist_ok=True)

# Caja Cataluña (misma del paper invasoras)
LAT_MIN, LAT_MAX = 40.45, 42.95
LON_MIN, LON_MAX = 0.10, 3.40

# taxon_id iNaturalist (misma clave que public_observations.taxon_id)
# taxon_id = iNat IDs presentes en public_observations (resueltos 11-oct-2026)
NATIVES_EXPAND = [
    ("Pelagia noctiluca", 256089),
    ("Rhizostoma pulmo", 319371),
    ("Cotylorhiza tuberculata", 324852),
    ("Arbacia lixula", 143139),
    ("Paracentrotus lividus", 48032),  # contraste erizos
    ("Thalassoma pavo", 50972),
    ("Sparisoma cretense", 112860),
    ("Sphyraena viridensis", 47260),
    ("Epinephelus costae", 100091),
    ("Caulerpa cylindracea", 734863),  # invasora ya; contraste
]

DECLINES = [
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

# Controles (misma zona/hábitat aproximado; nativos comunes)
CONTROLS = [
    ("Diplodus sargus", 118669),
    ("Diplodus vulgaris", 118667),
    ("Chromis chromis", 118682),
    ("Coris julis", 50968),
    ("Sarpa salpa", 118663),
    ("Symphodus tinca", 52554),
    ("Octopus vulgaris", 49315),
    ("Sepia officinalis", 151429),
    ("Paracentrotus lividus", 48032),
    ("Arbacia lixula", 143139),
]


def sql(q: str) -> list[tuple]:
    r = subprocess.run(
        ["docker", "exec", "-i", "postgres-global", "psql", "-U", "admin_yespi", "-d", "fauna", "-t", "-A", "-F", "\t", "-c", q],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    rows = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(tuple(line.split("\t")))
    return rows


def effort_by_year() -> dict[int, int]:
    q = f"""
    SELECT obs_year, COUNT(*)::bigint
    FROM public_observations
    WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lng BETWEEN {LON_MIN} AND {LON_MAX}
      AND obs_year IS NOT NULL AND obs_year BETWEEN 2005 AND 2026
    GROUP BY 1 ORDER BY 1;
    """
    out = {}
    for y, n in sql(q):
        out[int(y)] = int(n)
    return out


def series_for(taxon_ids: list[int]) -> dict[int, dict[int, int]]:
    """taxon_id -> {year: count} en caja CAT."""
    ids = ",".join(str(i) for i in taxon_ids)
    q = f"""
    SELECT taxon_id, obs_year, COUNT(*)::bigint
    FROM public_observations
    WHERE taxon_id IN ({ids})
      AND lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lng BETWEEN {LON_MIN} AND {LON_MAX}
      AND obs_year IS NOT NULL AND obs_year BETWEEN 2005 AND 2026
    GROUP BY 1,2 ORDER BY 1,2;
    """
    out: dict[int, dict[int, int]] = defaultdict(dict)
    for tid, y, n in sql(q):
        out[int(tid)][int(y)] = int(n)
    return out


def first_obs(taxon_ids: list[int]) -> dict[int, str]:
    ids = ",".join(str(i) for i in taxon_ids)
    q = f"""
    SELECT taxon_id,
           MIN(make_date(obs_year, COALESCE(obs_month,1), COALESCE(obs_day,1)))::text
    FROM public_observations
    WHERE taxon_id IN ({ids})
      AND lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lng BETWEEN {LON_MIN} AND {LON_MAX}
      AND obs_year IS NOT NULL
    GROUP BY 1;
    """
    return {int(t): d for t, d in sql(q)}


def rate_series(counts: dict[int, int], effort: dict[int, int]) -> dict[int, float]:
    return {
        y: (counts.get(y, 0) / effort[y] * 1000.0) if effort.get(y, 0) else 0.0
        for y in sorted(effort)
    }


def window_mean(rates: dict[int, float], y0: int, y1: int) -> float:
    vals = [rates[y] for y in range(y0, y1 + 1) if y in rates]
    return float(np.mean(vals)) if vals else 0.0


def classify_trend(rates: dict[int, float], total_obs: int) -> dict:
    """Ratio 2020-2024 vs 2015-2019; ruptura por máximo drop/rise relativo."""
    recent = window_mean(rates, 2020, 2024)
    prev = window_mean(rates, 2015, 2019)
    older = window_mean(rates, 2010, 2014)
    ratio = (recent / prev) if prev > 1e-9 else (999.0 if recent > 0 else 0.0)
    # rupture: year with largest |Δ rate| relative to previous 3y mean
    years = sorted(rates)
    best_y, best_score = None, 0.0
    for y in years:
        if y < 2012 or y > 2024:
            continue
        base = window_mean(rates, y - 3, y - 1)
        if base < 0.05:  # evita rupturas espurias con denominador ~0
            continue
        score = (rates[y] - base) / base
        if abs(score) > abs(best_score):
            best_score, best_y = score, y

    if total_obs < 8:
        cat = "dato_insuficiente"
    elif ratio >= 1.5 and recent > prev:
        cat = "en_expansion"
    elif ratio <= 0.5 and recent < prev:
        # permanence heuristic
        if recent <= 0.05 * max(older, prev, 1e-9) and window_mean(rates, 2022, 2025) <= 0.05 * max(prev, 1e-9):
            cat = "declive_permanente_candidato"
        elif recent < 0.4 * prev and older > 0 and recent < 0.5 * older:
            cat = "declive_semipermanente_candidato"
        else:
            cat = "declive_temporal_candidato"
    elif ratio <= 0.75 and recent < prev:
        cat = "declive_leve_candidato"
    elif ratio >= 1.2:
        cat = "aumento_leve"
    else:
        cat = "estable_o_sin_patron"

    return {
        "rate_2010_2014": round(older, 4),
        "rate_2015_2019": round(prev, 4),
        "rate_2020_2024": round(recent, 4),
        "ratio_5y": round(ratio, 3) if ratio < 900 else None,
        "rupture_year": best_y,
        "rupture_score": round(best_score, 3),
        "category": cat,
        "n_obs_cat": total_obs,
    }


def plot_species(name: str, rates: dict[int, float], out: Path, color="#1a4f8b"):
    ys = sorted(rates)
    xs = [rates[y] for y in ys]
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=140)
    ax.plot(ys, xs, color=color, lw=1.8, marker="o", ms=3.5)
    ax.axvspan(2015, 2019, color="#ddd", alpha=0.35, label="2015–2019")
    ax.axvspan(2020, 2024, color="#cfe8ff", alpha=0.45, label="2020–2024")
    ax.set_title(f"{name} — tasa / esfuerzo (×1000)", fontsize=11)
    ax.set_xlabel("Año")
    ax.set_ylabel("obs especie / esfuerzo caja × 1000")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_presence_absence(name: str, counts: dict[int, int], out: Path):
    """Mapa temporal simplificado: presencia (1) / ausencia (0) por año."""
    years = list(range(2008, 2027))
    vals = [1 if counts.get(y, 0) > 0 else 0 for y in years]
    fig, ax = plt.subplots(figsize=(7.2, 1.8), dpi=140)
    ax.bar(years, vals, color=["#2a6" if v else "#ccc" for v in vals], width=0.8)
    ax.set_ylim(0, 1.2)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["ausente", "presente"])
    ax.set_title(f"{name} — presencia anual en caja CAT (ciencia ciudadana)", fontsize=10)
    ax.set_xlabel("Año")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def main():
    print("esfuerzo…", flush=True)
    effort = effort_by_year()
    all_taxa = {n: tid for n, tid in NATIVES_EXPAND + DECLINES + CONTROLS}
    tid_list = sorted(set(all_taxa.values()))
    print("series…", flush=True)
    series = series_for(tid_list)
    firsts = first_obs(tid_list)

    # effort CSV
    ef_path = INV / "esfuerzo_bioquest_anual.csv"
    with ef_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "n_obs_caja_cat"])
        for y in sorted(effort):
            w.writerow([y, effort[y]])

    def analyze(group: list[tuple[str, int]], out_csv: Path, fig_dir: Path, prefix: str):
        rows = []
        for name, tid in group:
            counts = series.get(tid, {})
            rates = rate_series(counts, effort)
            meta = classify_trend(rates, sum(counts.values()))
            meta.update(
                {
                    "species": name,
                    "taxon_id": tid,
                    "first_obs_cat": firsts.get(tid, ""),
                    "method": "obs/esfuerzo_caja×1000; ratio 2020-24 / 2015-19",
                }
            )
            rows.append(meta)
            slug = name.replace(" ", "_")
            plot_species(name, rates, fig_dir / f"{prefix}_trend_{slug}.png")
            plot_presence_absence(name, counts, fig_dir / f"{prefix}_presabs_{slug}.png")
            # series csv
            with (fig_dir / f"{prefix}_serie_{slug}.csv").open("w", newline="", encoding="utf-8") as sf:
                sw = csv.writer(sf)
                sw.writerow(["year", "n_obs", "effort", "rate_x1000"])
                for y in sorted(effort):
                    sw.writerow([y, counts.get(y, 0), effort[y], f"{rates[y]:.6f}"])
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            fields = [
                "species",
                "taxon_id",
                "n_obs_cat",
                "first_obs_cat",
                "rate_2010_2014",
                "rate_2015_2019",
                "rate_2020_2024",
                "ratio_5y",
                "rupture_year",
                "rupture_score",
                "category",
                "method",
            ]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k) for k in fields})
        return rows

    print("controles…", flush=True)
    ctrl_rows = analyze(
        CONTROLS,
        DEC_MAT / "controles_tendencias_20261011.csv",
        DEC_MAT / "figuras",
        "control",
    )
    ratios = [r["ratio_5y"] for r in ctrl_rows if isinstance(r.get("ratio_5y"), (int, float))]
    ctrl_mean_ratio = float(np.mean(ratios)) if ratios else float("nan")

    def relative_class(row: dict) -> dict:
        r = row.get("ratio_5y")
        if r is None or not ratios or math.isnan(ctrl_mean_ratio) or ctrl_mean_ratio <= 0:
            row["ratio_vs_controls"] = None
            row["category_vs_controls"] = row["category"]
            return row
        rel = r / ctrl_mean_ratio
        row["ratio_vs_controls"] = round(rel, 3)
        # umbrales relativos al panel de controles (mismo esfuerzo)
        if row["n_obs_cat"] < 8:
            row["category_vs_controls"] = "dato_insuficiente"
        elif rel >= 1.15:
            row["category_vs_controls"] = "expansion_relativa"
        elif rel <= 0.35:
            if row["rate_2020_2024"] <= 0.15 * max(row["rate_2015_2019"], 1e-9):
                row["category_vs_controls"] = "declive_permanente_relativo"
            elif rel <= 0.20:
                row["category_vs_controls"] = "declive_semipermanente_relativo"
            else:
                row["category_vs_controls"] = "declive_temporal_relativo"
        elif rel <= 0.60:
            row["category_vs_controls"] = "declive_leve_relativo"
        elif rel >= 0.90:
            row["category_vs_controls"] = "coherente_con_controles"
        else:
            row["category_vs_controls"] = "por_debajo_de_controles"
        return row

    print("nativas…", flush=True)
    nat_rows = [relative_class(r) for r in analyze(
        NATIVES_EXPAND,
        INV_MAT / "nativas_expansion_tendencias_20261011.csv",
        INV_MAT / "figuras",
        "nativa",
    )]
    # reescribir CSV nativas con columnas relativas
    fields = [
        "species", "taxon_id", "n_obs_cat", "first_obs_cat",
        "rate_2010_2014", "rate_2015_2019", "rate_2020_2024", "ratio_5y",
        "ratio_vs_controls", "rupture_year", "rupture_score",
        "category", "category_vs_controls", "method",
    ]
    with (INV_MAT / "nativas_expansion_tendencias_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in nat_rows:
            w.writerow(r)

    print("declives…", flush=True)
    dec_rows = [relative_class(r) for r in analyze(
        DECLINES,
        DEC_MAT / "declives_tendencias_20261011.csv",
        DEC_MAT / "figuras",
        "declive",
    )]
    with (DEC_MAT / "declives_tendencias_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in dec_rows:
            w.writerow(r)
    with (DEC_MAT / "controles_tendencias_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in ctrl_rows:
            relative_class(r)
            w.writerow(r)

    meta = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S CEST"),
        "effort_years": len(effort),
        "effort_2013": effort.get(2013),
        "effort_2024": effort.get(2024),
        "control_mean_ratio_5y": round(float(ctrl_mean_ratio), 3) if not math.isnan(ctrl_mean_ratio) else None,
        "method_note": "ratio_5y = rate(2020-24)/rate(2015-19); ratio_vs_controls = ratio_5y / media controles",
        "bbox": [LAT_MIN, LAT_MAX, LON_MIN, LON_MAX],
        "n_natives": len(nat_rows),
        "n_declines": len(dec_rows),
        "n_controls": len(ctrl_rows),
    }
    (DEC_MAT / "meta_tendencias_20261011.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (INV_MAT / "meta_nativas_20261011.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print("OK")


if __name__ == "__main__":
    main()
