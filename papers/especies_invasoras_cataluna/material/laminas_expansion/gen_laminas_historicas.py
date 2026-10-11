#!/usr/bin/env python3
"""Láminas de expansión estilo mapa histórico (A3) — especies invasoras.

Solo CPU. Reutiliza pobs_key_taxa.csv + tabla_origen_vias_resumen.csv
del análisis origen/vías (Cursor invorigen, 10-oct-2026).
Flechas discontinuas = hipótesis (no confirmadas por lit./datos).
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Polygon as MplPolygon
from matplotlib.lines import Line2D
import numpy as np
import shapefile
from pyproj import Transformer

ROOT = Path("/mnt/docker/biofauna-public/papers/especies_invasoras_cataluna")
ART = Path("/mnt/docker/biofauna/artifacts/invasoras/origen_expansion")
GEO = ART / "geo"
OUT = ROOT / "material" / "laminas_expansion"
OUT.mkdir(parents=True, exist_ok=True)

POBS = ART / "pobs_key_taxa.csv"
TABLA = ROOT / "material" / "tabla_origen_vias_resumen.csv"
FECHAS = ROOT / "material" / "primeras_fechas_20261011.csv"

# ETRS89-LAEA Europe — mapas de España / Med sin deformar
T3035 = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)


def xy(lng, lat):
    return T3035.transform(float(lng), float(lat))

MED = dict(lat=(30.0, 46.5), lng=(-6.5, 37.5))
# Mar Rojo / Golfo de Suez (presencia nativa Pterois)
RED = dict(lat=(12.0, 30.0), lng=(32.0, 45.0))
# Atlántico ibérico / golfo de Vizcaya (NO es Mediterráneo; Magallana/Codium)
ATL_N = dict(lat=(42.0, 48.5), lng=(-10.0, 0.5))

# Periodos (décadas / 5 años) para color de frentes
PERIOD_COLORS = [
    (1990, 1999, "#6b3a2a", "1990–1999"),
    (2000, 2004, "#a0522d", "2000–2004"),
    (2005, 2009, "#cd853f", "2005–2009"),
    (2010, 2014, "#daa520", "2010–2014"),
    (2015, 2019, "#e67e22", "2015–2019"),
    (2020, 2024, "#c0392b", "2020–2024"),
    (2025, 2026, "#7b241c", "2025–2026"),
]

# Especies principales (lámina por especie)
SPECIES = {
    123459: {
        "name": "Pterois miles",
        "common": "pez león",
        "extent": (-5.5, 42.0, 24.5, 42.5),  # lng0,lng1,lat0,lat1 (incluye Mar Rojo N)
        "entry_lit": (34.78, 32.08, "Israel 1991\n(lit.)", False),  # lng, lat, label, hypot
        "entry_bq": (34.771, 32.097, "BQ Med\n2015-08", False),
        "arrows_lit": [  # confirmed literature pathway (not BQ)
            # Suez → Israel (lessepsian) — schematic
            ((33.0, 28.5), (34.78, 32.08), False, "Suez → Israel\n(lessepsiana)"),
            # Israel → Lebanon/Cyprus ~2012
            ((34.78, 32.08), (35.2, 34.0), False, "~2012"),
            ((35.2, 34.0), (33.0, 34.7), False, "Chipre"),
        ],
        "arrows_hyp": [  # secondary / rejected hypotheses
            ((32.5, 29.5), (28.0, 36.5), True, "hipótesis\nacuariofilia"),
            ((34.0, 27.0), (14.0, 36.0), True, "hipótesis\nlastre (no principal)"),
        ],
    },
    734863: {
        "name": "Caulerpa cylindracea",
        "common": "caulerpa cilíndrica",
        "extent": (-6.5, 28.0, 35.0, 45.5),
        "entry_lit": (13.0, 37.5, "Med ~1990s\n(lit. Zenetos)", False),
        "entry_bq": (9.845, 43.050, "BQ Med\n2005-07", False),
        "arrows_lit": [
            ((13.0, 37.5), (9.8, 43.0), False, "→ Córcega/\nCerdeña"),
            ((9.8, 43.0), (1.44, 41.15), False, "→ CAT\n2014"),
        ],
        "arrows_hyp": [],
    },
    107341: {
        "name": "Oculina patagonica",
        "common": "coral Oculina",
        "extent": (-6.5, 20.0, 35.0, 44.5),
        "entry_lit": (5.5, 43.2, "Med 1974\n(Zibrowius)", False),
        "entry_bq": (-0.127, 38.500, "BQ ES\n2010-09", False),
        "arrows_lit": [
            ((5.5, 43.2), (-0.13, 38.5), False, "→ Alicante"),
            ((-0.13, 38.5), (0.76, 40.83), False, "→ CAT\n2011"),
        ],
        "arrows_hyp": [],
    },
    132368: {
        "name": "Lagocephalus sceleratus",
        "common": "pez globo plateado",
        "extent": (-2.0, 37.5, 30.0, 42.5),
        "entry_lit": (33.5, 32.5, "E Med 2000s\n(lit.)", False),
        "entry_bq": (25.474, 36.852, "BQ Med\n2005-06", False),
        "arrows_lit": [
            ((33.0, 28.8), (33.5, 32.5), False, "Suez"),
            ((33.5, 32.5), (25.5, 36.9), False, "→ Egeo"),
            ((25.5, 36.9), (15.0, 37.5), False, "→ centro Med"),
        ],
        "arrows_hyp": [
            ((15.0, 37.5), (2.0, 39.0), True, "hipótesis\navance W"),
        ],
    },
    57779: {
        "name": "Asparagopsis armata",
        "common": "alga harpoon",
        "extent": (-10.0, 20.0, 35.0, 45.0),
        "entry_lit": (3.22, 42.05, "Med histórico\n(fouling)", False),
        "entry_bq": (3.220, 42.046, "BQ CAT\n2008-04", False),
        # Ruta marina por costa (waypoints); nunca cortar Iberia
        "arrows_lit": [
            ((-8.0, 36.0), (-5.6, 36.0), False, "Atlántico"),
            ((-5.6, 36.0), (-4.8, 36.2), False, "Gibraltar"),
            ((-4.8, 36.2), (-1.5, 37.4), False, None),
            ((-1.5, 37.4), (0.8, 39.8), False, None),
            ((0.8, 39.8), (2.2, 41.2), False, None),
            ((2.2, 41.2), (3.22, 42.05), False, "shipping\n→ NW Med"),
        ],
        "arrows_hyp": [
            ((3.22, 42.05), (6.5, 43.0), True, "hipótesis\ndensificación N"),
        ],
        "basin_safe_fronts": True,
    },
    49504: {
        "name": "Callinectes sapidus",
        "common": "cangrejo azul",
        "extent": (-6.0, 12.0, 36.0, 44.0),
        "entry_lit": (-0.7, 37.9, "Segura 2016\n(lit.)", False),
        "entry_bq": (2.126, 41.296, "BQ CAT\n2017-11", False),
        "arrows_lit": [
            # costa mediterránea (mar)
            ((-0.7, 37.9), (0.7, 40.7), False, "→ Delta Ebro"),
            ((0.7, 40.7), (2.13, 41.30), False, "→ Barcelona"),
        ],
        "arrows_hyp": [
            ((2.13, 41.30), (3.1, 42.0), True, "hipótesis\nexpansión local"),
        ],
    },
    605992: {
        "name": "Magallana gigas",
        "common": "ostra del Pacífico",
        "extent": (-10.0, 18.0, 35.5, 46.8),
        # Entrada Med = acuicultura directa (Thau/FR), NO Cantábrico→Pirineos
        "entry_lit": (3.63, 43.40, "Thau (FR)\nacui. Med", False),
        "entry_bq": (3.557, 43.318, "BQ Med verdadero\n2010 Thau", False),
        "extra_entries": [
            (-5.4, 43.5, "acuicultura\nCantábrico (Atl)", False),
            (0.70, 40.70, "Delta Ebro\ncultivo", False),
            (-0.78, 37.72, "Mar Menor\n(hipótesis)", True),
            (12.33, 45.12, "Venecia/\nAdriático", False),
        ],
        # Sin flecha sólida tierra; saltos humanos discontinuos
        "arrows_lit": [],
        # Solo saltos humanos a lo largo de costa Med (mar); Atl y Med = focos
        # acuícolas independientes (sin flecha Cantábrico→Thau).
        "arrows_hyp": [
            ((3.63, 43.40), (0.70, 40.70), True, "fouling / semillas\n→ Delta Ebro"),
            ((3.63, 43.40), (-0.78, 37.72), True, "hipótesis\n→ Mar Menor"),
            ((12.33, 45.12), (9.5, 44.0), True, "acuicultura\nAdriático (local)"),
        ],
        "basin_safe_fronts": True,
        "human_jumps": True,
        "note_banner": "Focos acuícolas independientes (Atl ≠ Med). Sin expansión terrestre.",
    },
    67555: {
        "name": "Codium fragile",
        "common": "alga verde frágil",
        "extent": (-10.0, 15.0, 35.5, 45.5),
        "entry_lit": (3.29, 42.29, "fouling\n(NW Med)", False),
        "entry_bq": (3.286, 42.290, "BQ CAT\n2010-08", False),
        # Solo vía marítima Gibraltar (sin flecha Atl→Med por Francia)
        "arrows_lit": [
            ((-8.5, 36.0), (-5.5, 36.05), False, "Atl→Gibraltar"),
            ((-5.5, 36.05), (3.29, 42.29), False, "shipping\nmarítimo"),
        ],
        "arrows_hyp": [],
        "basin_safe_fronts": True,
    },
}


def in_box(lat, lng, box):
    return box["lat"][0] <= lat <= box["lat"][1] and box["lng"][0] <= lng <= box["lng"][1]


def is_true_med(lat: float, lng: float) -> bool:
    """Mediterráneo real: este de Gibraltar, excluye Cantábrico/Vizcaya."""
    if not in_box(lat, lng, MED):
        return False
    if in_box(lat, lng, ATL_N):
        return False
    # costa atlántica andaluza/portuguesa al oeste de ~−5.3
    if lng < -5.3 and lat < 42.0:
        return False
    return True


def same_marine_basin(lat0, lng0, lat1, lng1) -> bool:
    """True si ambos puntos están en el mismo lado (Atl N vs Med). Evita flechas por tierra."""
    a0, a1 = in_box(lat0, lng0, ATL_N), in_box(lat1, lng1, ATL_N)
    if a0 and a1:
        return True
    if a0 or a1:
        return False
    return is_true_med(lat0, lng0) and is_true_med(lat1, lng1)


def load_tabla():
    out = {}
    with TABLA.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["especie"]] = r
    # overlay min first-dates when disponibles
    if FECHAS.exists():
        with FECHAS.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                sp = r["especie"]
                if sp not in out:
                    out[sp] = {}
                if r.get("primera_mediterraneo"):
                    out[sp]["primera_mediterraneo"] = (
                        f"{r['primera_mediterraneo']} (min fuentes; ver primeras_fechas_20261011.csv)"
                    )
                if r.get("primera_espana"):
                    out[sp]["primera_espana"] = (
                        f"{r['primera_espana']} (min fuentes; ver primeras_fechas_20261011.csv)"
                    )
                if r.get("primera_catalunya"):
                    out[sp]["primera_catalunya"] = (
                        f"{r['primera_catalunya']} (min fuentes; ver primeras_fechas_20261011.csv)"
                    )
    return out


def load_pobs():
    by = defaultdict(list)
    with POBS.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                tid = int(r["taxon_id"])
                lat = float(r["lat"])
                lng = float(r["lng"])
                y = int(r["obs_year"])
            except (TypeError, ValueError):
                continue
            by[tid].append((y, lat, lng))
    return by


def load_coast_land():
    # Natural Earth 10m (no 110m) — costa real
    coast = shapefile.Reader(str(GEO / "ne_10m_coastline"))
    land = shapefile.Reader(str(GEO / "ne_10m_land"))
    return coast.shapes(), land.shapes()


def clip_shape_parts(shape, extent, projected=True):
    """Yield polylines that intersect extent (lng0,lng1,lat0,lat1), optionally in EPSG:3035."""
    lng0, lng1, lat0, lat1 = extent
    pts = shape.points
    parts = list(shape.parts) + [len(pts)]
    pad = 0.5
    for i in range(len(parts) - 1):
        seg = pts[parts[i] : parts[i + 1]]
        if not seg:
            continue
        xs = [p[0] for p in seg]
        ys = [p[1] for p in seg]
        if max(xs) < lng0 - pad or min(xs) > lng1 + pad or max(ys) < lat0 - pad or min(ys) > lat1 + pad:
            continue
        if not projected:
            yield xs, ys
            continue
        px, py = [], []
        for x, y in seg:
            if lng0 - pad <= x <= lng1 + pad and lat0 - pad <= y <= lat1 + pad:
                e, n = xy(x, y)
                px.append(e)
                py.append(n)
        if len(px) >= 2:
            yield px, py


def period_of(year):
    for a, b, c, lab in PERIOD_COLORS:
        if a <= year <= b:
            return a, b, c, lab
    return None


def decade_centroids(pts, extent):
    """pts: list (year, lat, lng) in map extent; return list of (y0,y1,color,lab, mean_lng, mean_lat, n, min_lng)."""
    lng0, lng1, lat0, lat1 = extent
    buckets = defaultdict(list)
    for y, lat, lng in pts:
        if not (lng0 <= lng <= lng1 and lat0 <= lat <= lat1):
            continue
        per = period_of(y)
        if not per:
            continue
        a, b, c, lab = per
        buckets[(a, b, c, lab)].append((lng, lat))
    out = []
    for key in sorted(buckets):
        a, b, c, lab = key
        coords = buckets[key]
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        out.append((a, b, c, lab, float(np.mean(xs)), float(np.mean(ys)), len(coords), float(min(xs))))
    return out


def draw_land_sea(ax, coast_shapes, land_shapes, extent):
    """Mapa en EPSG:3035 (ETRS89-LAEA), costa NE 10m, aspect equal (sin estirar)."""
    lng0, lng1, lat0, lat1 = extent
    corners = [xy(x, y) for x in (lng0, lng1) for y in (lat0, lat1)]
    e0, e1 = min(c[0] for c in corners), max(c[0] for c in corners)
    n0, n1 = min(c[1] for c in corners), max(c[1] for c in corners)
    ax.set_xlim(e0, e1)
    ax.set_ylim(n0, n1)
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor("#c5d6e0")  # sea
    for sh in land_shapes:
        for xs, ys in clip_shape_parts(sh, extent, projected=True):
            ax.fill(xs, ys, facecolor="#e8dcc8", edgecolor="none", zorder=1)
    for sh in coast_shapes:
        for xs, ys in clip_shape_parts(sh, extent, projected=True):
            ax.plot(xs, ys, color="#5c4a32", lw=0.55, zorder=2)
    ax.grid(True, color="#8a7a60", alpha=0.22, lw=0.4, zorder=2)
    ax.set_xlabel("Easting EPSG:3035 (m)", fontsize=9)
    ax.set_ylabel("Northing EPSG:3035 (m)", fontsize=9)
    ax.tick_params(labelsize=7)


def draw_arrow(ax, p0, p1, color, dashed=False, lw=2.2, label=None, label_offset=(0, 0), human_jump=False):
    """Flecha en coords EPSG:3035. p0/p1 = (lng, lat) geográficos → se proyectan."""
    x0, y0 = xy(p0[0], p0[1])
    x1, y1 = xy(p1[0], p1[1])
    dx, dy = x1 - x0, y1 - y0
    dist = math.hypot(dx, dy) or 1.0
    # umbrales en metros (~3.5° ≈ 350 km)
    if human_jump or (dashed and dist > 350_000):
        stub = min(55_000, max(25_000, dist * 0.04))
        ux, uy = dx / dist, dy / dist
        ax.annotate(
            "",
            xy=(x0 + ux * stub, y0 + uy * stub),
            xytext=(x0, y0),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=11),
            zorder=7,
        )
        ax.annotate(
            "",
            xy=(x1, y1),
            xytext=(x1 - ux * stub, y1 - uy * stub),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=13),
            zorder=7,
        )
        if label:
            ox = label_offset[0] * 80_000
            oy = label_offset[1] * 80_000
            ax.text(
                x1 + ox - 15_000,
                y1 + oy + 35_000,
                label,
                fontsize=7.5,
                ha="center",
                va="bottom",
                color="#3e2723",
                zorder=8,
                bbox=dict(
                    boxstyle="round,pad=0.15",
                    fc="#fff8e7",
                    ec="#7f8c8d",
                    ls=(0, (3, 2)),
                    alpha=0.9,
                ),
            )
        return
    shrink = 0.12 if dist > 150_000 else 0.08
    xa, ya = x0 + dx * 0.02, y0 + dy * 0.02
    xb, yb = x1 - dx * shrink, y1 - dy * shrink
    ls = (0, (6, 4)) if dashed else "solid"
    alpha = 0.78 if dashed else 0.95
    ax.plot(
        [xa, xb],
        [ya, yb],
        color=color,
        lw=lw,
        ls=ls,
        solid_capstyle="round",
        zorder=6,
        alpha=alpha,
    )
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(xb, yb),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=lw * 0.9,
            mutation_scale=14,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=7,
    )
    if label:
        ox = label_offset[0] * 80_000
        oy = label_offset[1] * 80_000
        mx = (x0 + x1) / 2 + ox
        my = (y0 + y1) / 2 + oy
        ax.text(
            mx,
            my,
            label,
            fontsize=7,
            ha="center",
            va="center",
            color="#3e2723",
            zorder=8,
            bbox=dict(
                boxstyle="round,pad=0.15",
                fc="#fff8e7",
                ec="#7f8c8d" if dashed else "none",
                ls=(0, (3, 2)) if dashed else "solid",
                alpha=0.82,
            ),
        )


def draw_fronts(ax, buckets, basin_safe=False, connect=True):
    """Frentes en EPSG:3035. buckets traen lng/lat geográficos."""
    if not buckets:
        return
    if connect:
        for i in range(len(buckets) - 1):
            a0, b0, c0, lab0, x0, y0, n0, w0 = buckets[i]
            a1, b1, c1, lab1, x1, y1, n1, w1 = buckets[i + 1]
            # x=lng, y=lat en buckets
            if basin_safe and not same_marine_basin(y0, x0, y1, x1):
                continue
            e0, n0_ = xy(x0, y0)
            e1, n1_ = xy(x1, y1)
            if basin_safe and math.hypot(e1 - e0, n1_ - n0_) > 450_000:
                continue
            lw = 1.6 + min(4.5, math.log10(max(n1, 2)) * 2.4)
            draw_arrow(ax, (x0, y0), (x1, y1), c1, dashed=False, lw=lw)
    for i, (a, b, c, lab, x, y, n, w) in enumerate(buckets):
        ex, ny = xy(x, y)
        ew, _ = xy(w, y)
        half = 70_000 + 15_000 * (i % 3)
        ax.plot([ew, ew], [ny - half, ny + half], color=c, lw=3.2, zorder=5, solid_capstyle="round")
        arc_y = np.linspace(ny - half * 1.3, ny + half * 1.3, 12)
        arc_x = ew + 35_000 * np.sin(np.linspace(0, np.pi, 12))
        ax.plot(arc_x, arc_y, color=c, lw=1.6, alpha=0.55, zorder=4)
        ax.scatter(
            [ex],
            [ny],
            s=45 + min(200, n * 0.45),
            c=c,
            edgecolors="#3e2723",
            lw=0.5,
            zorder=6,
            alpha=0.88,
        )
        dy = 55_000 + 35_000 * (i % 2)
        ax.text(
            ew - 20_000,
            ny + dy,
            str(a),
            fontsize=8.5,
            fontweight="bold",
            color=c,
            ha="right",
            va="bottom",
            zorder=8,
            bbox=dict(boxstyle="round,pad=0.12", fc="#f3ead6", ec=c, alpha=0.85, lw=0.6),
        )


def info_box(ax, meta, name, common, fig):
    """Inset text box with origin / vía / primeras citas."""
    origen = meta.get("origen", "—")
    via = meta.get("via", "—")
    pmed = meta.get("primera_mediterraneo", "—")
    pes = meta.get("primera_espana", "—")
    pcat = meta.get("primera_catalunya", "—")
    tend = meta.get("tendencia", "—")
    causa = meta.get("causa", "—")
    fuente = meta.get("fuente_o_hipotesis", "—")
    # truncate long fields
    def trunc(s, n=110):
        s = (s or "—").replace("\n", " ")
        return s if len(s) <= n else s[: n - 1] + "…"

    text = (
        f"{name} — {common}\n"
        f"Origen: {trunc(origen, 90)}\n"
        f"Vía: {trunc(via, 100)}\n"
        f"1ª Med: {trunc(pmed, 95)}\n"
        f"1ª España: {trunc(pes, 80)}\n"
        f"1ª Cataluña: {trunc(pcat, 80)}\n"
        f"Tendencia: {trunc(tend, 60)}\n"
        f"Causa: {trunc(causa, 90)}\n"
        f"Fuente: {trunc(fuente, 100)}\n"
        f"Flechas discontinuas = hipótesis. Datos: public_observations (SELECT)."
    )
    props = dict(boxstyle="round,pad=0.45", facecolor="#fff8e7", edgecolor="#5c4a32", alpha=0.95, lw=1.0)
    ax.text(
        0.015,
        0.015,
        text,
        transform=ax.transAxes,
        fontsize=7.2,
        va="bottom",
        ha="left",
        family="DejaVu Sans",
        linespacing=1.35,
        bbox=props,
        zorder=20,
    )


def legend_panel(ax):
    handles = [
        Line2D([0], [0], marker="*", color="w", markerfacecolor="#b71c1c", markersize=14, label="Punto de entrada (lit.)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#1565c0", markersize=8, label="1ª obs. BioQuest (caja)"),
        Line2D([0], [0], color="#c0392b", lw=2.2, label="Frente / despliegue (datos o lit.)"),
        Line2D([0], [0], color="#7f8c8d", lw=2.0, ls=(0, (5, 3)), label="Flecha hipótesis"),
    ]
    for a, b, c, lab in PERIOD_COLORS:
        handles.append(Line2D([0], [0], color=c, lw=3, label=lab))
    ax.legend(handles=handles, loc="upper right", fontsize=7, framealpha=0.92, title="Leyenda", title_fontsize=8)


def make_plate(tid, cfg, pts, tabla, coast_shapes, land_shapes):
    name = cfg["name"]
    common = cfg["common"]
    extent = cfg["extent"]
    meta = tabla.get(name, {})

    # A3 landscape inches
    fig = plt.figure(figsize=(16.54, 11.69), dpi=160)
    fig.patch.set_facecolor("#f3ead6")
    ax = fig.add_axes([0.05, 0.08, 0.90, 0.82])

    draw_land_sea(ax, coast_shapes, land_shapes, extent)

    # faint BQ points (context) — proyectados EPSG:3035
    lng0, lng1, lat0, lat1 = extent
    xs, ys, cs = [], [], []
    for y, lat, lng in pts:
        if lng0 <= lng <= lng1 and lat0 <= lat <= lat1:
            per = period_of(y)
            if not per:
                continue
            e, n = xy(lng, lat)
            xs.append(e)
            ys.append(n)
            cs.append(per[2])
    if xs:
        ax.scatter(xs, ys, c=cs, s=8, alpha=0.28, edgecolors="none", zorder=3)

    # BQ fronts / arrows between centroids
    basin_safe = bool(cfg.get("basin_safe_fronts"))
    # For Pterois include Red Sea pts for early periods context but fronts only in Med for westward story
    if tid == 123459:
        med_pts = [p for p in pts if in_box(p[1], p[2], MED) or in_box(p[1], p[2], RED)]
        buckets = decade_centroids(med_pts, extent)
        # prefer Med-only for front arrows after first Med year
        med_only = decade_centroids([p for p in pts if in_box(p[1], p[2], MED)], extent)
        if med_only:
            draw_fronts(ax, med_only, basin_safe=basin_safe)
        else:
            draw_fronts(ax, buckets, basin_safe=basin_safe)
    elif tid == 605992:
        # Magallana: marcas por periodo Atl/Med separados; sin flechas auto
        # (la vía es introducción acuícola / saltos humanos, no frente continuo)
        atl_pts = [(y, lat, lng) for y, lat, lng in pts if in_box(lat, lng, ATL_N)]
        med_pts = [(y, lat, lng) for y, lat, lng in pts if is_true_med(lat, lng)]
        draw_fronts(ax, decade_centroids(atl_pts, extent), basin_safe=True, connect=False)
        draw_fronts(ax, decade_centroids(med_pts, extent), basin_safe=True, connect=False)
    else:
        if basin_safe:
            # solo Med verdadero + Atl N por separado
            atl_pts = [(y, lat, lng) for y, lat, lng in pts if in_box(lat, lng, ATL_N)]
            med_pts = [(y, lat, lng) for y, lat, lng in pts if is_true_med(lat, lng)]
            draw_fronts(ax, decade_centroids(atl_pts, extent), basin_safe=True)
            draw_fronts(ax, decade_centroids(med_pts, extent), basin_safe=True)
        else:
            med_pts = [p for p in pts if in_box(p[1], p[2], MED)]
            buckets = decade_centroids(med_pts, extent)
            draw_fronts(ax, buckets, basin_safe=False)

    # literature / schematic arrows
    human = bool(cfg.get("human_jumps"))
    for (p0, p1, hyp, lab) in cfg.get("arrows_lit", []):
        draw_arrow(ax, p0, p1, "#5d4037", dashed=False, lw=2.0, label=lab)
    for (p0, p1, hyp, lab) in cfg.get("arrows_hyp", []):
        draw_arrow(ax, p0, p1, "#7f8c8d", dashed=True, lw=1.8, label=lab, human_jump=human)

    # entry markers (proyectados)
    elng, elat, elab, _ = cfg["entry_lit"]
    ee, en = xy(elng, elat)
    ax.scatter([ee], [en], marker="*", s=320, c="#b71c1c", edgecolors="#3e2723", lw=0.7, zorder=10)
    ax.annotate(
        elab,
        (ee, en),
        textcoords="offset points",
        xytext=(8, -18),
        fontsize=7.5,
        color="#b71c1c",
        fontweight="bold",
        zorder=11,
        bbox=dict(boxstyle="round,pad=0.15", fc="#fff8e7", ec="#b71c1c", alpha=0.9, lw=0.6),
    )
    blng, blat, blab, _ = cfg["entry_bq"]
    be, bn = xy(blng, blat)
    ax.scatter([be], [bn], marker="o", s=90, c="#1565c0", edgecolors="#0d47a1", lw=0.8, zorder=10)
    ax.annotate(
        blab,
        (be, bn),
        textcoords="offset points",
        xytext=(10, 10),
        fontsize=7.5,
        color="#0d47a1",
        fontweight="bold",
        zorder=11,
        bbox=dict(boxstyle="round,pad=0.15", fc="#e3f2fd", ec="#1565c0", alpha=0.9, lw=0.6),
    )
    for extra in cfg.get("extra_entries", []):
        xlng, xlat, xlab, xhyp = extra
        marker = "D" if xhyp else "P"
        col = "#7f8c8d" if xhyp else "#e65100"
        xe, xn = xy(xlng, xlat)
        ax.scatter([xe], [xn], marker=marker, s=120, c=col, edgecolors="#3e2723", lw=0.6, zorder=10)
        ax.annotate(
            xlab,
            (xe, xn),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=7.5,
            color=col,
            fontweight="bold",
            zorder=11,
            bbox=dict(boxstyle="round,pad=0.12", fc="#fff8e7", ec=col, alpha=0.9, lw=0.5),
        )

    # CAT box proyectado
    cat_ll = [(0.1, 40.45), (3.4, 40.45), (3.4, 42.95), (0.1, 42.95), (0.1, 40.45)]
    cat_xy = [xy(lng, lat) for lng, lat in cat_ll]
    ax.plot(
        [p[0] for p in cat_xy],
        [p[1] for p in cat_xy],
        color="#c0392b",
        lw=1.0,
        ls="--",
        alpha=0.7,
        zorder=4,
        label="caja CAT",
    )

    legend_panel(ax)
    info_box(ax, meta, name, common, fig)

    title = f"Expansión de {name} ({common}) — lámina histórica"
    fig.suptitle(title, fontsize=16, fontweight="bold", color="#3e2723", y=0.965)
    banner = cfg.get("note_banner") or (
        "EPSG:3035 (ETRS89-LAEA) · costa Natural Earth 10m · aspecto 1:1 · "
        "1ªs fechas = min(lit/BQ/presencia) · A3 · 2026-10-11"
    )
    fig.text(
        0.5,
        0.925,
        banner,
        ha="center",
        fontsize=8.5,
        color="#5c4a32",
    )
    fig.text(
        0.5,
        0.02,
        "Fuente de puntos: BioQuest / fauna.public_observations (solo SELECT). "
        "1ªs citas: primeras_fechas_20261011.csv (mínimo de cualquier fuente). "
        "Proyección EPSG:3035 · costa Natural Earth 10m · sin estirar.",
        ha="center",
        fontsize=7,
        color="#5c4a32",
    )

    safe = name.replace(" ", "_")
    out = OUT / f"lamina_expansion_{safe}_A3.png"
    fig.savefig(out, dpi=160, facecolor=fig.get_facecolor())
    out4 = OUT / f"lamina_expansion_{safe}_A4.png"
    # A4: misma composición, raster a tamaño papel (sin aplastar ejes)
    fig.set_size_inches(16.54, 11.69)  # mantener proporción A3-landscape
    fig.savefig(out4, dpi=110, facecolor=fig.get_facecolor())  # ~A4 en px
    plt.close(fig)
    print("wrote", out.name, out4.name, "n_pts=", len(pts))
    return out, out4


def main():
    tabla = load_tabla()
    pobs = load_pobs()
    coast_shapes, land_shapes = load_coast_land()
    written = []
    for tid, cfg in SPECIES.items():
        pts = pobs.get(tid, [])
        written.append(make_plate(tid, cfg, pts, tabla, coast_shapes, land_shapes))
    # index md
    lines = [
        "# Láminas de expansión (estilo mapa histórico)",
        "",
        "**Generado:** 2026-10-11 CEST · Cursor invasoras-fix (EPSG:3035 + NE 10m).",
        "**Alcance:** solo láminas; el análisis origen/vías está en `../ORIGEN_Y_VIAS_EXPANSION.md`.",
        "**Formato:** A3 y A4 PNG imprimibles. Flechas discontinuas = hipótesis.",
        "**Sin GPU.** Proyección **EPSG:3035**; costa Natural Earth **10m**; aspecto equal; puntos `public_observations`.",
        "",
        "| Especie | A3 | A4 |",
        "|---|---|---|",
    ]
    for tid, cfg in SPECIES.items():
        safe = cfg["name"].replace(" ", "_")
        lines.append(
            f"| *{cfg['name']}* | [`lamina_expansion_{safe}_A3.png`](lamina_expansion_{safe}_A3.png) | "
            f"[`lamina_expansion_{safe}_A4.png`](lamina_expansion_{safe}_A4.png) |"
        )
    lines += [
        "",
        "## Convención visual",
        "",
        "- Estrella roja: punto de entrada según bibliografía.",
        "- Círculo azul: primera observación BioQuest en la caja mediterránea (o ES/CAT).",
        "- Flechas sólidas marrón: vía / despliegue confirmado (lit. o secuencia BQ).",
        "- Flechas grises discontinuas: hipótesis (p. ej. lastre o acuariofilia secundaria en *Pterois miles*).",
        "- Color de frentes y centroides BQ por periodo (leyenda en cada lámina).",
        "- Recuadro: origen · vía · 1ª cita Med/ES/CAT · tendencia · causa · fuente.",
        "",
        "Script: [`gen_laminas_historicas.py`](gen_laminas_historicas.py).",
    ]
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("README ok; plates=", len(written))


if __name__ == "__main__":
    main()
