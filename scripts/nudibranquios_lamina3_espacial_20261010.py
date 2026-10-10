#!/usr/bin/env python3
"""Lámina 3 — distribución espacial de nudibranquios (Cataluña + Mediterráneo español).

Solo SELECT en postgres-global (fauna.public_observations). Sin GPU.
Coordenadas públicas tal cual están en la tabla (las ocultas/ofuscadas sin
ubicación no entran en public_observations).
"""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Nunca GPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import to_rgba
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
COAST = PAPER / "datos/coast-western-med.geojson"

CAT_LAT = (40.45, 42.95)
CAT_LON = (0.10, 3.40)
# Costa mediterránea española (península + Baleares, sin Canarias)
ESMED_LAT = (35.80, 43.20)
ESMED_LON = (-5.60, 4.50)

NUDI_ORDERS = {"Nudibranchia", "Doridida", "Dendronotida"}

# Tramos de costa catalana (cajas lat/lng; orden N→S)
COAST_ZONES: list[tuple[str, float, float, float, float]] = [
    ("Cap de Creus", 42.20, 42.55, 3.05, 3.40),
    ("Illes Medes / Estartit", 42.00, 42.20, 3.10, 3.35),
    ("Begur–Palamós", 41.80, 42.00, 3.00, 3.30),
    ("Tossa–Blanes", 41.65, 41.80, 2.75, 3.10),
    ("Maresme", 41.45, 41.65, 2.25, 2.75),
    ("Barcelonès", 41.30, 41.45, 2.05, 2.30),
    ("Garraf", 41.18, 41.32, 1.68, 2.05),
    ("Costa Daurada N", 41.10, 41.18, 1.30, 1.75),
    ("Tarragona–Salou", 40.95, 41.12, 0.90, 1.35),
    ("Delta de l'Ebre", 40.50, 40.95, 0.40, 1.05),
]

DIVE_SITES = [
    ("Cap de Creus", 42.32, 3.28),
    ("Illes Medes", 42.045, 3.225),
    ("Tossa", 41.72, 2.935),
    ("Garraf", 41.25, 1.90),
    ("Tarragona", 41.08, 1.22),
]

# Paleta distintiva (12 spp.)
PALETTE = [
    "#e41a1c",
    "#377eb8",
    "#4daf4a",
    "#984ea3",
    "#ff7f00",
    "#a65628",
    "#f781bf",
    "#999999",
    "#66c2a5",
    "#fc8d62",
    "#8da0cb",
    "#e78ac3",
]


def psql_csv(sql: str) -> list[list[str]]:
    cmd = [
        "docker",
        "exec",
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
        sql,
    ]
    out = subprocess.check_output(cmd, text=True, errors="replace").strip()
    if not out:
        return []
    return [line.split("\t") for line in out.split("\n")]


def load_nudi_names() -> list[str]:
    ts = json.load(open(ROOT / "dataset/target_species.json"))
    return sorted({x["name"] for x in ts if x.get("order") in NUDI_ORDERS})


def top_species_from_csv(n: int = 12) -> list[str]:
    path = PAPER / "datos/especies_mensual_normalizado_20261010.csv"
    spp = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            spp.append(row["especie"])
            if len(spp) >= n:
                break
    return spp


def sql_in(names: list[str]) -> str:
    return ", ".join("'" + n.replace("'", "''") + "'" for n in names)


def fetch_points(names: list[str], lat_b, lon_b) -> list[tuple[str, float, float, int | None, float | None]]:
    """SELECT público: lat/lng ya son las coordenadas publicadas (sin ocultas)."""
    sql = f"""
SELECT taxon_name, lat, lng, obs_year, depth_m
FROM public_observations
WHERE lat IS NOT NULL AND lng IS NOT NULL
  AND lat BETWEEN {lat_b[0]} AND {lat_b[1]}
  AND lng BETWEEN {lon_b[0]} AND {lon_b[1]}
  AND taxon_name IN ({sql_in(names)});
"""
    rows = psql_csv(sql)
    out = []
    for r in rows:
        try:
            name, la, lo = r[0], float(r[1]), float(r[2])
            yr = int(r[3]) if r[3] not in ("", "\\N", None) else None
            dep = float(r[4]) if len(r) > 4 and r[4] not in ("", "\\N", None) else None
            out.append((name, la, lo, yr, dep))
        except (ValueError, IndexError):
            continue
    return out


def fetch_all_nudi_zone_effort(nudi_names: list[str]) -> dict[str, int]:
    """Esfuerzo = total nudibranquios georreferenciados por tramo (caja CAT)."""
    sql = f"""
SELECT lat, lng
FROM public_observations
WHERE lat IS NOT NULL AND lng IS NOT NULL
  AND lat BETWEEN {CAT_LAT[0]} AND {CAT_LAT[1]}
  AND lng BETWEEN {CAT_LON[0]} AND {CAT_LON[1]}
  AND taxon_name IN ({sql_in(nudi_names)});
"""
    effort = {z[0]: 0 for z in COAST_ZONES}
    effort["Fuera de tramos"] = 0
    for r in psql_csv(sql):
        try:
            la, lo = float(r[0]), float(r[1])
        except ValueError:
            continue
        z = assign_zone(la, lo)
        effort[z] += 1
    return effort


def assign_zone(lat: float, lon: float) -> str:
    for name, la0, la1, lo0, lo1 in COAST_ZONES:
        if la0 <= lat <= la1 and lo0 <= lon <= lo1:
            return name
    return "Fuera de tramos"


def load_coast_lines(lon_b, lat_b) -> list[np.ndarray]:
    g = json.loads(COAST.read_text(encoding="utf-8"))
    segs = []
    for feat in g["features"]:
        geom = feat["geometry"]
        coords = geom["coordinates"]
        if geom["type"] == "LineString":
            coords = [coords]
        for line in coords:
            arr = np.array(line, dtype=float)  # lon, lat
            if arr.size < 4:
                continue
            m = (
                (arr[:, 0] >= lon_b[0] - 0.3)
                & (arr[:, 0] <= lon_b[1] + 0.3)
                & (arr[:, 1] >= lat_b[0] - 0.3)
                & (arr[:, 1] <= lat_b[1] + 0.3)
            )
            if m.sum() < 2:
                continue
            # Keep contiguous runs
            idx = np.where(m)[0]
            # split on gaps
            breaks = np.where(np.diff(idx) > 1)[0]
            starts = np.r_[0, breaks + 1]
            ends = np.r_[breaks + 1, len(idx)]
            for s, e in zip(starts, ends):
                chunk = arr[idx[s:e]]
                if len(chunk) >= 2:
                    segs.append(chunk)
    return segs


def italic_name(sp: str) -> str:
    """Etiqueta con cursiva real (matplotlib fontstyle)."""
    return sp


def draw_coast(ax, lon_b, lat_b, lw=0.7, color="#1e3a5f"):
    for seg in load_coast_lines(lon_b, lat_b):
        ax.plot(seg[:, 0], seg[:, 1], color=color, lw=lw, zorder=2, solid_capstyle="round")


def draw_dive_labels(ax, sites=DIVE_SITES, fontsize=7):
    for name, la, lo in sites:
        if not (ax.get_xlim()[0] <= lo <= ax.get_xlim()[1] and ax.get_ylim()[0] <= la <= ax.get_ylim()[1]):
            # set after xlim; check bounds passed
            pass
        ax.plot(lo, la, marker="*", color="#111", markersize=7, zorder=6)
        t = ax.annotate(
            name,
            (lo, la),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=fontsize,
            color="#111",
            zorder=7,
            fontweight="medium",
        )
        t.set_path_effects([pe.withStroke(linewidth=2.5, foreground="white")])


def hex_dominant(ax, points_by_sp: dict[str, np.ndarray], colors: dict[str, str], gridsize: int, extent):
    """Hexágonos coloreados por especie dominante; alpha ~ intensidad."""
    from matplotlib.patches import RegularPolygon

    all_xy, all_lab = [], []
    for sp, xy in points_by_sp.items():
        if len(xy) == 0:
            continue
        all_xy.append(xy)
        all_lab.append(np.full(len(xy), sp, dtype=object))
    if not all_xy:
        return
    xy = np.vstack(all_xy)
    labs = np.concatenate(all_lab)

    # Rejilla hexagonal axial (flat-top approx. via offset rows)
    xmin, xmax, ymin, ymax = extent
    nx = max(int(gridsize), 8)
    dx = (xmax - xmin) / nx
    dy = dx * np.sqrt(3) / 2
    ny = max(int((ymax - ymin) / dy) + 1, 8)

    buckets: dict[tuple[int, int], Counter] = defaultdict(Counter)
    for (lo, la), sp in zip(xy, labs):
        row = int((la - ymin) / dy)
        col = int((lo - xmin) / dx - (0.5 if row % 2 else 0.0))
        if 0 <= row < ny and 0 <= col < nx + 1:
            buckets[(col, row)][sp] += 1

    max_n = max((sum(c.values()) for c in buckets.values()), default=1)
    rad = dx / np.sqrt(3) * 1.05
    for (col, row), c in buckets.items():
        if not c:
            continue
        cx = xmin + (col + (0.5 if row % 2 else 0.0)) * dx + dx / 2
        cy = ymin + row * dy + dy / 2
        if not (xmin <= cx <= xmax and ymin <= cy <= ymax):
            continue
        dom = c.most_common(1)[0][0]
        tot = sum(c.values())
        alpha = 0.28 + 0.67 * (tot / max_n)
        col_rgba = to_rgba(colors.get(dom, "#888"), alpha=min(alpha, 0.95))
        ax.add_patch(
            RegularPolygon(
                (cx, cy),
                numVertices=6,
                radius=rad,
                orientation=np.radians(30),
                facecolor=col_rgba,
                edgecolor=(1, 1, 1, 0.35),
                linewidth=0.2,
                zorder=3,
            )
        )


def scatter_alpha(ax, points_by_sp, colors, s=6, alpha=0.22):
    for sp, xy in points_by_sp.items():
        if len(xy) == 0:
            continue
        ax.scatter(
            xy[:, 0],
            xy[:, 1],
            s=s,
            c=colors[sp],
            alpha=alpha,
            edgecolors="none",
            zorder=4,
            rasterized=True,
        )


def map_panel(ax, points, species, colors, lon_b, lat_b, title, gridsize, mode="hex"):
    by_sp = {sp: [] for sp in species}
    for name, la, lo, *_ in points:
        if name in by_sp:
            by_sp[name].append((lo, la))
    by_sp_arr = {sp: np.array(v) if v else np.zeros((0, 2)) for sp, v in by_sp.items()}

    ax.set_facecolor("#e8f1f8")
    draw_coast(ax, lon_b, lat_b)
    extent = (lon_b[0], lon_b[1], lat_b[0], lat_b[1])
    if mode == "hex":
        hex_dominant(ax, by_sp_arr, colors, gridsize=gridsize, extent=extent)
        scatter_alpha(ax, by_sp_arr, colors, s=3.5, alpha=0.10)
    else:
        # Fondo de densidad hexagonal + puntos con transparencia
        all_xy = np.vstack([v for v in by_sp_arr.values() if len(v)]) if any(len(v) for v in by_sp_arr.values()) else np.zeros((0, 2))
        if len(all_xy):
            ax.hexbin(
                all_xy[:, 0],
                all_xy[:, 1],
                gridsize=gridsize,
                extent=extent,
                cmap="Blues",
                mincnt=1,
                alpha=0.35,
                linewidths=0.1,
                zorder=2,
            )
        scatter_alpha(ax, by_sp_arr, colors, s=7, alpha=0.30)

    ax.set_xlim(lon_b)
    ax.set_ylim(lat_b)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Longitud (°E)", fontsize=8)
    ax.set_ylabel("Latitud (°N)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_title(title, fontsize=10, color="#5c1a00", loc="left", pad=6)

    if lon_b[1] - lon_b[0] < 5:
        for name, la, lo in DIVE_SITES:
            if lon_b[0] <= lo <= lon_b[1] and lat_b[0] <= la <= lat_b[1]:
                ax.plot(lo, la, marker="*", color="#111", markersize=8, zorder=6)
                t = ax.annotate(
                    name,
                    (lo, la),
                    textcoords="offset points",
                    xytext=(6, 4),
                    fontsize=6.5,
                    color="#111",
                    zorder=7,
                )
                t.set_path_effects([pe.withStroke(linewidth=2.2, foreground="white")])


def build_lamina(species: list[str], pts_cat, pts_es, effort_zone, nudi_names):
    colors = {sp: PALETTE[i % len(PALETTE)] for i, sp in enumerate(species)}

    # --- aggregates ---
    zone_sp = defaultdict(lambda: Counter())
    year_sp = defaultdict(lambda: Counter())
    depths = []
    for name, la, lo, yr, dep in pts_cat:
        z = assign_zone(la, lo)
        zone_sp[z][name] += 1
        if yr and 2005 <= yr <= 2026:
            year_sp[yr][name] += 1
        if dep is not None:
            depths.append((name, dep))

    zones_ord = [z[0] for z in COAST_ZONES] + ["Fuera de tramos"]
    # Hotspot: n_sp / effort_zone
    hotspot = {}  # sp -> list of (zone, rate, n)
    for sp in species:
        rows = []
        for z in zones_ord:
            if z == "Fuera de tramos":
                continue
            n = zone_sp[z].get(sp, 0)
            e = max(effort_zone.get(z, 0), 1)
            if n >= 5 and e >= 30:
                rows.append((z, n / e, n, e))
        rows.sort(key=lambda x: -x[1])
        hotspot[sp] = rows[:3]

    fig = plt.figure(figsize=(16.54, 11.69), dpi=300, facecolor="white")
    gs = GridSpec(
        3,
        3,
        figure=fig,
        height_ratios=[1.15, 1.0, 0.95],
        width_ratios=[1.15, 1.15, 0.95],
        left=0.05,
        right=0.98,
        top=0.92,
        bottom=0.06,
        wspace=0.28,
        hspace=0.38,
    )

    ax_cat = fig.add_subplot(gs[0, 0])
    ax_es = fig.add_subplot(gs[0, 1])
    ax_leg = fig.add_subplot(gs[0, 2])
    ax_heat = fig.add_subplot(gs[1, 0:2])
    ax_mix = fig.add_subplot(gs[1, 2])
    ax_year = fig.add_subplot(gs[2, 0])
    ax_hot = fig.add_subplot(gs[2, 1])
    ax_dep = fig.add_subplot(gs[2, 2])

    map_panel(
        ax_cat,
        pts_cat,
        species,
        colors,
        CAT_LON,
        CAT_LAT,
        "A · Cataluña — hexágonos por especie dominante",
        gridsize=28,
        mode="hex",
    )
    map_panel(
        ax_es,
        pts_es,
        species,
        colors,
        ESMED_LON,
        ESMED_LAT,
        "B · Mediterráneo español — puntos (α) + costa",
        gridsize=40,
        mode="scatter",
    )
    # Baleares / Levante dive cue labels (sparse)
    for name, la, lo in [
        ("Cabo de Gata", 36.72, -2.19),
        ("Cabo de Palos", 37.63, -0.69),
        ("Mallorca", 39.55, 2.65),
        ("Menorca", 39.95, 4.10),
        ("Costa Brava", 42.0, 3.2),
    ]:
        if ESMED_LON[0] <= lo <= ESMED_LON[1] and ESMED_LAT[0] <= la <= ESMED_LAT[1]:
            ax_es.plot(lo, la, "k.", markersize=3, zorder=5)
            t = ax_es.annotate(name, (lo, la), textcoords="offset points", xytext=(4, 3), fontsize=5.5, color="#222")
            t.set_path_effects([pe.withStroke(linewidth=2, foreground="white")])

    # Legend
    ax_leg.axis("off")
    ax_leg.set_title("Especies (top 12)", fontsize=10, color="#5c1a00", loc="left")
    handles = []
    for sp in species:
        handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=colors[sp],
                markersize=8,
                label=italic_name(sp),
            )
        )
    leg = ax_leg.legend(
        handles=handles,
        loc="upper left",
        fontsize=7.5,
        frameon=False,
        labelspacing=0.55,
        handletextpad=0.4,
    )
    for text, sp in zip(leg.get_texts(), species):
        text.set_fontstyle("italic")
        text.set_text(sp)
    ax_leg.text(
        0.0,
        0.02,
        "Hexágono = especie dominante\n"
        "Intensidad ∝ nº obs. en la celda\n"
        "★ zonas de buceo de referencia\n"
        "Coords. públicas (SELECT);\n"
        "ocultas/ofuscadas no figurán.",
        transform=ax_leg.transAxes,
        fontsize=6.5,
        color="#444",
        va="bottom",
    )

    # Heatmap zone × species
    mat = np.zeros((len(species), len(zones_ord)))
    for j, z in enumerate(zones_ord):
        for i, sp in enumerate(species):
            mat[i, j] = zone_sp[z].get(sp, 0)
    # row-normalize for readability
    row_max = mat.max(axis=1, keepdims=True)
    row_max[row_max == 0] = 1
    mat_n = mat / row_max
    im = ax_heat.imshow(mat_n, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1, interpolation="nearest")
    ax_heat.set_yticks(range(len(species)))
    ax_heat.set_yticklabels(species, fontstyle="italic", fontsize=7)
    ax_heat.set_xticks(range(len(zones_ord)))
    ax_heat.set_xticklabels(zones_ord, rotation=35, ha="right", fontsize=6.5)
    ax_heat.set_title("C · Observaciones por tramo de costa × especie (fila normalizada)", fontsize=9, color="#5c1a00", loc="left")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = int(mat[i, j])
            if v >= 8:
                ax_heat.text(j, i, str(v), ha="center", va="center", fontsize=5.2, color="#222" if mat_n[i, j] < 0.55 else "white")

    # Species mix stacked (proportion of top12 in zone)
    bottom = np.zeros(len(zones_ord))
    totals_z = np.array([sum(zone_sp[z].get(sp, 0) for sp in species) for z in zones_ord], dtype=float)
    totals_z[totals_z == 0] = 1
    x = np.arange(len(zones_ord))
    for sp in species:
        vals = np.array([zone_sp[z].get(sp, 0) for z in zones_ord], dtype=float) / totals_z
        ax_mix.bar(x, vals, bottom=bottom, color=colors[sp], width=0.85, linewidth=0)
        bottom += vals
    ax_mix.set_xticks(x)
    ax_mix.set_xticklabels(zones_ord, rotation=40, ha="right", fontsize=5.5)
    ax_mix.set_ylim(0, 1)
    ax_mix.set_ylabel("Proporción", fontsize=7)
    ax_mix.set_title("D · Mezcla de especies por tramo", fontsize=9, color="#5c1a00", loc="left")
    ax_mix.tick_params(labelsize=6)

    # Year trends (lines)
    years = sorted(y for y in year_sp if 2012 <= y <= 2026)
    for sp in species[:8]:  # top 8 lines to avoid clutter
        ys = [year_sp[y].get(sp, 0) for y in years]
        ax_year.plot(years, ys, color=colors[sp], lw=1.4, marker="o", markersize=2.5, alpha=0.9)
    ax_year.set_title("E · Tendencia anual (8 spp. más frecuentes)", fontsize=9, color="#5c1a00", loc="left")
    ax_year.set_xlabel("Año", fontsize=7)
    ax_year.set_ylabel("Obs.", fontsize=7)
    ax_year.tick_params(labelsize=6)
    ax_year.grid(True, axis="y", alpha=0.25)

    # Hotspots normalized
    ax_hot.axis("off")
    ax_hot.set_title("F · Zonas calientes (obs. spp / nudis del tramo)", fontsize=9, color="#5c1a00", loc="left")
    y = 0.96
    ax_hot.text(
        0.0,
        y,
        "Dónde se ve más cada especie, normalizado por esfuerzo local\n(total de nudibranquios del tramo). Mín. 5 obs. y 30 nudis.",
        transform=ax_hot.transAxes,
        fontsize=6.2,
        color="#444",
        va="top",
    )
    y -= 0.12
    for sp in species:
        tops = hotspot.get(sp) or []
        if not tops:
            continue
        bits = "; ".join(f"{z} ({r:.0%}, n={n})" for z, r, n, e in tops[:2])
        ax_hot.text(0.0, y, sp, transform=ax_hot.transAxes, fontsize=6.5, fontstyle="italic", color=colors[sp], va="top", fontweight="medium")
        y -= 0.045
        ax_hot.text(0.02, y, bits, transform=ax_hot.transAxes, fontsize=5.8, color="#333", va="top")
        y -= 0.055
        if y < 0.02:
            break

    # Depth
    ax_dep.axis("off")
    ax_dep.set_title("G · Profundidad", fontsize=9, color="#5c1a00", loc="left")
    n_dep = len(depths)
    if n_dep >= 20:
        ax_dep.axis("on")
        vals = [d for _, d in depths]
        ax_dep.hist(vals, bins=12, color="#377eb8", alpha=0.75, edgecolor="white")
        ax_dep.set_xlabel("Profundidad (m)", fontsize=7)
        ax_dep.set_ylabel("Obs.", fontsize=7)
    else:
        ax_dep.text(
            0.0,
            0.7,
            f"Sin datos de profundidad útiles\n"
            f"en public_observations para estas\n"
            f"especies en la caja catalana\n"
            f"(depth_m relleno: {n_dep} / {len(pts_cat)}).\n\n"
            "El campo existe en BioQuest\n"
            "(API /academy/depth) pero aún\n"
            "casi vacío para nudibranquios.",
            transform=ax_dep.transAxes,
            fontsize=7.5,
            color="#444",
            va="top",
        )

    fig.suptitle(
        "Lámina 3 · Distribución espacial de nudibranquios (Cataluña y Mediterráneo español)",
        fontsize=13,
        color="#5c1a00",
        x=0.05,
        ha="left",
        y=0.97,
    )
    fig.text(
        0.05,
        0.015,
        "Fuente: public_observations (Minka + iNaturalist), solo SELECT · Costa: coast-western-med.geojson (BioQuest) · "
        f"Generado {datetime.now().strftime('%Y-%m-%d %H:%M')} CEST · sin GPU",
        fontsize=6,
        color="#666",
    )

    png = PAPER / "LAMINA3_distribucion_espacial_20261010.png"
    pdf = PAPER / "LAMINA3_distribucion_espacial_20261010.pdf"
    fig.savefig(png, dpi=300, facecolor="white")
    fig.savefig(pdf, dpi=300, facecolor="white")
    plt.close(fig)
    return png, pdf, mat, zones_ord, hotspot, year_sp, n_dep


def write_csvs(species, zones_ord, zone_sp_mat, hotspot, year_sp, effort_zone):
    datos = PAPER / "datos"
    # zone × species counts
    with open(datos / "distribucion_zona_especie_20261010.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["especie"] + zones_ord)
        # rebuild from hotspot context — pass matrix
        pass
    # rewrite properly below in main

    with open(datos / "esfuerzo_nudi_por_tramo_20261010.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tramo", "obs_nudibranquios"])
        for z in zones_ord:
            w.writerow([z, effort_zone.get(z, 0)])

    with open(datos / "zonas_calientes_normalizado_20261010.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["especie", "tramo", "tasa", "n_especie", "esfuerzo_nudi"])
        for sp, rows in hotspot.items():
            for z, r, n, e in rows:
                w.writerow([sp, z, round(r, 4), n, e])

    years = sorted(y for y in year_sp if 2010 <= y <= 2026)
    with open(datos / "tendencia_anual_top12_20261010.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["especie"] + years)
        for sp in species:
            w.writerow([sp] + [year_sp[y].get(sp, 0) for y in years])


def patch_articulo(png_name: str, n_cat: int, n_es: int, n_dep: int, hotspot: dict, species: list[str]):
    path = PAPER / "ARTICULO_20261010.md"
    md = path.read_text(encoding="utf-8")

    # Update resumen mention of two laminas → three
    md = md.replace(
        "Incluimos dos láminas imprimibles A3 (calendario por familias y rosas mensuales)",
        "Incluimos tres láminas imprimibles A3 (calendario por familias, rosas mensuales y distribución espacial)",
    )

    # Methods figures list
    if "Lámina 3:" not in md:
        md = md.replace(
            "- Lámina 2: `LAMINA2_rosas_estaciones_20261010.png` (PNG 300 ppp + PDF, A3).\n"
            "- Script: `scripts/nudibranquios_articulo_generar_20261010.py`.",
            "- Lámina 2: `LAMINA2_rosas_estaciones_20261010.png` (PNG 300 ppp + PDF, A3).\n"
            f"- Lámina 3: `{png_name}` (PNG 300 ppp + PDF, A3): mapas Cataluña / Mediterráneo español, "
            "obs. por tramo × especie, mezcla, tendencia anual y zonas calientes normalizadas por esfuerzo.\n"
            "- Scripts: `scripts/nudibranquios_articulo_generar_20261010.py` (láminas 1–2) y "
            "`scripts/nudibranquios_lamina3_espacial_20261010.py` (lámina 3).",
        )

    # Methods coords paragraph
    if "### 2.4 Distribución espacial" not in md:
        insert_after = "### 2.3 Figuras y reproducibilidad"
        block = """### 2.4 Distribución espacial

- **Coordenadas:** `lat`/`lng` de `public_observations` (solo `SELECT`). Son las coordenadas **públicas** ya almacenadas; las observaciones con ubicación oculta u ofuscada sin punto publicable no figuran en la tabla y, por tanto, no se dibujan. No se intenta «desofuscar» nada.
- **Mapas:** costa occidental mediterránea (`datos/coast-western-med.geojson`, BioQuest). En Cataluña, hexágonos coloreados por la especie dominante del top-12 (intensidad ∝ conteo); en el Mediterráneo español, puntos semitransparentes. Marcamos zonas de buceo de referencia (Cap de Creus, Illes Medes, Tossa, Garraf, Tarragona).
- **Tramos de costa:** cajas lat/lng a lo largo de la costa catalana (Cap de Creus → Delta de l'Ebre), análogas a los gráficos regionales del Atlas BioQuest (sin polígonos de comarca).
- **Esfuerzo espacial:** denominador = total de nudibranquios georreferenciados del tramo. Tasa = obs. de la especie / esfuerzo.
- **Profundidad:** el campo `depth_m` existe, pero en esta extracción está vacío para los nudibranquios de la caja (0 registros con profundidad).

"""
        # Insert before 2.3 or after 2.3 section — put after 2.2 / before 2.3 figures is ok; after 2.3 better
        # Find end of 2.3 (before ## 3)
        md = md.replace("## 3. Resultados", block + "## 3. Resultados")

    section = f"""
### 3.5 Distribución espacial (Lámina 3)

La **Lámina 3** sitúa las **{len(species)}** especies más registradas sobre la costa: **{n_cat:,}** puntos en la caja catalana y **{n_es:,}** en el Mediterráneo español (misma lista de especies; coordenadas públicas). Los hexágonos de Cataluña muestran la especie dominante por celda; el panel B evita el solapamiento con transparencia. Los paneles C–D resumen observaciones y mezcla por tramo de costa; el E, la tendencia anual (estilo Atlas BioQuest); el F señala **zonas calientes** normalizadas por el total de nudibranquios del tramo.

"""
    # hotspot highlights for top 3 spp
    highlights = []
    for sp in species[:6]:
        tops = hotspot.get(sp) or []
        if tops:
            z, r, n, e = tops[0]
            highlights.append(f"*{sp}* → {z} ({r:.0%} del esfuerzo local, n={n})")
    if highlights:
        section += "Ejemplos de zonas calientes (máxima tasa local): " + "; ".join(highlights) + ".\n\n"
    section += (
        f"Profundidad: sin señal útil (`depth_m` nulo en {n_cat - n_dep:,}/{n_cat:,} obs. de la caja).\n\n"
        f"![Lámina 3 — distribución espacial]({png_name})\n"
    )

    if "### 3.5 Distribución espacial" in md:
        md = re.sub(
            r"### 3\.5 Distribución espacial \(Lámina 3\).*?(?=## 4\.|\Z)",
            section.strip() + "\n\n",
            md,
            flags=re.S,
        )
    else:
        md = md.replace("## 4. Discusión", section + "\n## 4. Discusión")

    # Discussion tweak
    if "Lámina 3" not in md.split("## 4. Discusión")[1][:800]:
        md = md.replace(
            "**Cobertura geográfica.** La caja incluye tramos fuera de Cataluña administrativa; localidades dominantes (Costa Brava, Barcelona, Tarragona) reflejan clubs de buceo más que ausencia en el Ebro.",
            "**Cobertura geográfica.** La caja incluye tramos fuera de Cataluña administrativa; localidades dominantes (Costa Brava, Barcelona, Tarragona) reflejan clubs de buceo más que ausencia en el Ebro. La Lámina 3 cuantifica ese sesgo por tramo y lo normaliza por esfuerzo (nudibranquios del tramo).",
        )

    path.write_text(md, encoding="utf-8")
    return path


def patch_readme():
    path = PAPER / "README.md"
    txt = path.read_text(encoding="utf-8")
    row = (
        "| [`LAMINA3_distribucion_espacial_20261010.pdf`](LAMINA3_distribucion_espacial_20261010.pdf) · "
        "[`.png`](LAMINA3_distribucion_espacial_20261010.png) | "
        "Distribución espacial A3: mapas CAT/Med-ES, tramos, tendencia, zonas calientes |\n"
    )
    if "LAMINA3_distribucion" not in txt:
        txt = txt.replace(
            "| [`LAMINA2_rosas_estaciones_20261010.pdf`](LAMINA2_rosas_estaciones_20261010.pdf) · [`.png`](LAMINA2_rosas_estaciones_20261010.png) | Rosas radiales (12 spp.) + panel estacional |\n",
            "| [`LAMINA2_rosas_estaciones_20261010.pdf`](LAMINA2_rosas_estaciones_20261010.pdf) · [`.png`](LAMINA2_rosas_estaciones_20261010.png) | Rosas radiales (12 spp.) + panel estacional |\n"
            + row,
        )
    if "nudibranquios_lamina3" not in txt:
        txt = txt.replace(
            "```bash\npapers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_articulo_generar_20261010.py\n```",
            "```bash\npapers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_articulo_generar_20261010.py\npapers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_lamina3_espacial_20261010.py\n```",
        )
    path.write_text(txt, encoding="utf-8")


def main():
    PAPER.mkdir(parents=True, exist_ok=True)
    (PAPER / "datos").mkdir(exist_ok=True)
    if not COAST.exists():
        src = Path("/mnt/docker/bioquest/webapp/public/data/coast-western-med.geojson")
        COAST.write_bytes(src.read_bytes())

    species = top_species_from_csv(12)
    nudi_names = load_nudi_names()
    print(f"Top especies: {species}", flush=True)

    print("SELECT puntos Cataluña…", flush=True)
    pts_cat = fetch_points(species, CAT_LAT, CAT_LON)
    print(f"  {len(pts_cat)} puntos", flush=True)
    print("SELECT puntos Mediterráneo español…", flush=True)
    pts_es = fetch_points(species, ESMED_LAT, ESMED_LON)
    print(f"  {len(pts_es)} puntos", flush=True)
    print("Esfuerzo por tramo (todos los nudis del catálogo)…", flush=True)
    effort_zone = fetch_all_nudi_zone_effort(nudi_names)
    print(effort_zone, flush=True)

    png, pdf, mat, zones_ord, hotspot, year_sp, n_dep = build_lamina(
        species, pts_cat, pts_es, effort_zone, nudi_names
    )

    # zone×species CSV
    zone_sp = defaultdict(lambda: Counter())
    for name, la, lo, *_ in pts_cat:
        zone_sp[assign_zone(la, lo)][name] += 1
    with open(PAPER / "datos/distribucion_zona_especie_20261010.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["especie"] + zones_ord)
        for i, sp in enumerate(species):
            w.writerow([sp] + [int(mat[i, j]) for j in range(len(zones_ord))])

    write_csvs(species, zones_ord, mat, hotspot, year_sp, effort_zone)
    patch_articulo(png.name, len(pts_cat), len(pts_es), n_dep, hotspot, species)
    patch_readme()

    meta = {
        "generated": datetime.now().isoformat(),
        "species": species,
        "n_points_cat": len(pts_cat),
        "n_points_esmed": len(pts_es),
        "n_depth": n_dep,
        "effort_zone": effort_zone,
        "files": [str(png), str(pdf)],
        "gpu": False,
    }
    (PAPER / "meta_lamina3_20261010.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(json.dumps(meta, indent=2, ensure_ascii=False))
    print("OK", png)


if __name__ == "__main__":
    main()
