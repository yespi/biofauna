#!/usr/bin/env python3
"""Lámina 5 — póster A3 estilo Carta Marina (Olaus Magnus, 1539).

Costa REAL de Catalunya (Natural Earth 10m, trazo único desde polígonos).
16 nudibranquios: grabados (SD1.5+Canny + polish flat-pastel/hatch) desde recorte.
300 ppp · márgenes · ref_carta_marina_gustavo.jpg (estilo).
"""
from __future__ import annotations

import csv
import json
import math
import os
import random
from datetime import datetime
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from matplotlib.font_manager import FontProperties
from matplotlib.patches import (
    Arc,
    Circle,
    Ellipse,
    FancyBboxPatch,
    Polygon,
    Rectangle,
    Wedge,
)
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
MAT = PAPER / "material"
NE_GEO = MAT / "datos/catalunya_ne10m.geojson"
RECORTES = MAT / "recortes"
MONTHLY = MAT / "datos/especies_mensual_normalizado_20261010.csv"
OUT_PNG = MAT / "LAMINA5_carta_marina_20261010.png"
OUT_PDF = MAT / "LAMINA5_carta_marina_20261010.pdf"
OUT_SVG = MAT / "LAMINA5_carta_marina_20261010.svg"
META_JSON = MAT / "datos/poster_lamina5_meta_20261010.json"
ENGRAVE_DIR = MAT / "datos/engravings_lamina5"

A3_W_IN, A3_H_IN = 16.5354, 11.6929
DPI = 300
MARGIN_IN = 0.45  # ~11.5 mm

# Encuadre: costa catalana completa (Cap de Creus → Delta Ebre)
MAP_LON = (0.20, 3.70)
MAP_LAT = (40.35, 42.80)

PARCHMENT = "#e8d9b8"
SEA = "#a8c0c4"
LAND = "#d2c9a4"
LAND_EDGE = "#6b2e1f"
INK = "#1a120c"
INK_SOFT = "#3a2a1c"
RED_ACCENT = "#a83a2a"
GOLD = "#c4a35a"
CREAM = "#f2e6c8"
OLIVE = "#6e8250"

# name, zone_xy, sea placement (lon, lat), scale, peak fallback, label_offset (dx, dy)
SPECIES = [
    ("Cratena peregrina", (1.22, 41.08), (1.95, 40.82), 1.15, "Agosto", (0.0, -0.06)),
    ("Flabellina affinis", (1.22, 41.08), (2.50, 40.78), 1.10, "Julio", (0.0, -0.06)),
    ("Peltodoris atromaculata", (3.225, 42.045), (3.28, 41.82), 1.15, "Agosto", (0.18, -0.10)),
    ("Felimare picta", (2.18, 41.38), (2.68, 41.18), 1.15, "Agosto", (0.0, -0.09)),
    ("Edmundsella pedata", (0.75, 40.70), (1.40, 40.62), 1.00, "Abril", (0.0, -0.08)),
    ("Felimare tricolor", (1.55, 41.14), (2.12, 41.02), 1.05, "Junio", (0.0, -0.08)),
    ("Calmella cavolini", (0.75, 40.70), (1.00, 40.58), 0.95, "Agosto", (0.12, -0.07)),
    ("Diaphorodoris papillata", (3.225, 42.045), (3.38, 41.52), 0.95, "Abril", (0.0, -0.09)),
    ("Paradoris indecora", (2.93, 41.72), (3.18, 41.36), 1.00, "Enero", (0.0, -0.09)),
    ("Antiopella cristata", (2.18, 41.38), (2.85, 41.55), 1.05, "Mayo", (0.0, -0.08)),
    ("Polycera quadrilineata", (2.93, 41.72), (2.92, 41.16), 0.95, "Febrero", (0.0, -0.08)),
    ("Rudmania krohni", (3.225, 42.045), (2.48, 41.75), 0.90, "Junio", (0.0, -0.08)),
    ("Nemesignis banyulensis", (1.22, 41.08), (1.70, 41.05), 0.95, "Marzo", (0.0, -0.08)),
    ("Diaphorodoris alba", (3.15, 41.90), (2.30, 41.45), 0.90, "Mayo", (0.0, -0.08)),
    ("Facelina annulicornis", (3.28, 42.32), (3.38, 42.12), 1.00, "Enero", (0.0, -0.09)),
    ("Felimare fontandraui", (3.28, 42.32), (2.75, 42.20), 0.95, "Mayo", (0.0, -0.08)),
]

PLACES = [
    (3.18, 42.28, "Promontorium Crucis"),
    (3.08, 42.10, "Emporiae"),
    (3.22, 42.05, "Medae insulae"),
    (2.82, 41.98, "Gerunda"),
    (2.12, 41.42, "Barcino"),
    (1.25, 41.12, "Tarraco"),
    (0.55, 40.72, "Dertosa"),
    (0.72, 40.55, "Ebro flumen"),
]

MES_ABBR = ["Ian", "Feb", "Mar", "Apr", "Mai", "Iun", "Iul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def _serif(size=9, weight="normal"):
    return FontProperties(family="DejaVu Serif", size=size, weight=weight)


def _stroke(lw=2.0, color=CREAM):
    return [pe.withStroke(linewidth=lw, foreground=color)]


def load_ne():
    geo = json.loads(NE_GEO.read_text(encoding="utf-8"))
    coasts, lands = [], []
    for feat in geo["features"]:
        geom = feat["geometry"]
        props = feat.get("properties") or {}
        if props.get("source") == "ne_10m_coastline" or geom["type"] == "LineString":
            coords = geom["coordinates"]
            if geom["type"] == "MultiLineString":
                for line in coords:
                    coasts.append(np.array(line, dtype=float))
            else:
                coasts.append(np.array(coords, dtype=float))
        else:
            lands.append(geom)
    return coasts, lands


def hand_jitter(pts: np.ndarray, amp=0.012, seed=1539) -> np.ndarray:
    """Irregular «a mano» stroke along a polyline."""
    rng = np.random.default_rng(seed + int(abs(pts[0, 0] * 1000)) % 997)
    out = pts.copy()
    n = len(out)
    for i in range(n):
        if i == 0 or i == n - 1:
            continue
        dx = out[i, 0] - out[i - 1, 0]
        dy = out[i, 1] - out[i - 1, 1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        j = amp * math.sin(i * 0.37) + float(rng.normal(0, amp * 0.35))
        out[i, 0] += nx * j
        out[i, 1] += ny * j * 0.85
    return out


def simplify_line(pts: np.ndarray, step=6) -> np.ndarray:
    if len(pts) <= step:
        return pts
    idx = list(range(0, len(pts), step))
    if idx[-1] != len(pts) - 1:
        idx.append(len(pts) - 1)
    return pts[idx]


def parchment_rgba(w, h, seed=1539):
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), dtype=np.float32)
    base[..., 0] = 0.93
    base[..., 1] = 0.87
    base[..., 2] = 0.73
    base += rng.normal(0, 0.022, (h, w, 1)).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    base *= (1.0 - 0.14 * np.clip(r, 0, 1.2) ** 1.7)[..., None]
    # fold lines
    for x in np.linspace(0.2, 0.8, 3):
        xi = int(x * w)
        base[:, max(0, xi - 1) : xi + 2] *= 0.96
    for y in np.linspace(0.25, 0.75, 2):
        yi = int(y * h)
        base[max(0, yi - 1) : yi + 2, :] *= 0.97
    for _ in range(40):
        sx = int(rng.integers(0, w))
        sy = int(rng.integers(0, h))
        rad = int(rng.integers(40, 180))
        yy2, xx2 = np.ogrid[-sy : h - sy, -sx : w - sx]
        mask = xx2 * xx2 + yy2 * yy2 <= rad * rad
        base[mask] *= float(rng.uniform(0.94, 1.02))
    base = np.clip(base, 0, 1)
    img = Image.fromarray((base * 255).astype(np.uint8), "RGB")
    return img.filter(ImageFilter.GaussianBlur(0.5))


def woodcut_from_cutout(sp: str, size: int = 520) -> Image.Image:
    """Load polished engraving cache; fallback placeholder if missing."""
    ENGRAVE_DIR.mkdir(parents=True, exist_ok=True)
    slug = sp.replace(" ", "_").lower()
    cache = ENGRAVE_DIR / f"{slug}_woodcut.png"
    if cache.exists():
        im = Image.open(cache).convert("RGBA")
        if im.size != (size, size):
            im = im.resize((size, size), Image.Resampling.LANCZOS)
        return im
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((40, 80, size - 40, size - 80), fill=(200, 180, 140, 255), outline=(26, 18, 12, 255))
    im.save(cache)
    return im

def draw_sea_waves(ax, coasts):
    ax.add_patch(
        Rectangle(
            (MAP_LON[0], MAP_LAT[0]),
            MAP_LON[1] - MAP_LON[0],
            MAP_LAT[1] - MAP_LAT[0],
            facecolor=SEA,
            edgecolor="none",
            zorder=0,
        )
    )
    # Approximate coast x for wave masking
    coast_pts = []
    for c in coasts:
        for x, y in c:
            if MAP_LON[0] <= x <= MAP_LON[1] and MAP_LAT[0] <= y <= MAP_LAT[1]:
                coast_pts.append((x, y))
    coast_pts = sorted(coast_pts, key=lambda p: p[1])

    def coast_x(lat):
        if not coast_pts:
            return 1.5
        # nearest
        best = min(coast_pts, key=lambda p: abs(p[1] - lat))
        return best[0]

    lons = np.linspace(MAP_LON[0], MAP_LON[1], 140)
    for i, lat in enumerate(np.linspace(MAP_LAT[0] + 0.03, MAP_LAT[1] - 0.03, 85)):
        cx = coast_x(lat)
        amp = 0.008 + 0.005 * math.sin(i * 0.6)
        ys = lat + amp * np.sin(lons * 11 + i * 0.45)
        mask = lons > cx + 0.03
        if mask.sum() < 5:
            continue
        ax.plot(
            lons[mask],
            ys[mask],
            color=INK,
            lw=0.38,
            alpha=0.32,
            solid_capstyle="round",
            zorder=1,
        )
    # whirlpools
    rng = random.Random(42)
    for _ in range(10):
        cx = rng.uniform(2.2, 3.5)
        cy = rng.uniform(40.6, 42.2)
        if cx < coast_x(cy) + 0.2:
            continue
        for r in np.linspace(0.03, 0.12, 5):
            t = np.linspace(0, 2.3 * math.pi, 60)
            ax.plot(
                cx + r * np.cos(t) * 1.3,
                cy + r * np.sin(t) * 0.7,
                color=INK,
                lw=0.55,
                alpha=0.45,
                zorder=2,
            )


def draw_little_tree(ax, x, y, s=0.025):
    ax.plot([x, x], [y, y + s * 0.35], color=INK, lw=0.55, zorder=4.6, solid_capstyle="round")
    ax.add_patch(
        Ellipse(
            (x, y + s * 0.55),
            s * 0.85,
            s * 0.70,
            facecolor=OLIVE,
            edgecolor=INK,
            lw=0.35,
            alpha=0.85,
            zorder=4.7,
        )
    )


def _land_exteriors(lands):
    exteriors = []
    for geom in lands:
        gtype = geom["type"]
        if gtype == "Polygon":
            polys = [geom["coordinates"]]
        elif gtype == "MultiPolygon":
            polys = geom["coordinates"]
        else:
            continue
        for poly in polys:
            if poly:
                exteriors.append(np.array(poly[0], dtype=float))
    return exteriors


def draw_land(ax, coasts, lands):
    exteriors = _land_exteriors(lands)
    for exterior in exteriors:
        ax.add_patch(
            Polygon(exterior, closed=True, facecolor=LAND, edgecolor="none", alpha=0.98, zorder=3)
        )

    rng = random.Random(99)
    forest_patches = [
        (1.20, 1.70, 42.15, 42.45, 55),
        (2.20, 2.60, 41.70, 41.95, 40),
        (1.55, 1.95, 41.45, 41.70, 35),
        (2.70, 3.05, 41.85, 42.10, 30),
        (0.35, 0.80, 40.80, 41.15, 35),
        (0.90, 1.50, 41.20, 41.55, 25),
    ]
    for lo0, lo1, la0, la1, n in forest_patches:
        for _ in range(n):
            draw_little_tree(ax, rng.uniform(lo0, lo1), rng.uniform(la0, la1), s=rng.uniform(0.018, 0.032))

    for mx, my, lab, ww, hh in [
        (1.40, 42.38, "Pyrenaei", 0.55, 0.20),
        (2.40, 41.80, "Montseny", 0.36, 0.16),
        (1.78, 41.60, "Montserrat", 0.32, 0.17),
        (2.88, 41.93, "Gavarres", 0.30, 0.13),
        (0.55, 40.95, "Ports de Beseit", 0.38, 0.15),
    ]:
        draw_mountain(ax, mx, my, lab, w=ww, h=hh)

    for cx, cy in [(2.05, 41.55), (1.40, 41.28), (2.60, 42.05), (0.90, 41.15)]:
        draw_castle(ax, cx, cy)

    # ONE coast stroke from land exteriors (fixes ghost line NE Creus/Roses)
    for i, exterior in enumerate(exteriors):
        pts = exterior[
            (exterior[:, 0] >= MAP_LON[0] - 0.15)
            & (exterior[:, 0] <= MAP_LON[1] + 0.15)
            & (exterior[:, 1] >= MAP_LAT[0] - 0.15)
            & (exterior[:, 1] <= MAP_LAT[1] + 0.15)
        ]
        if len(pts) < 8:
            continue
        step = 2 if pts[:, 0].max() > 2.9 and pts[:, 1].max() > 41.9 else 4
        pts = simplify_line(pts, step=step)
        pts = hand_jitter(pts, amp=0.0035, seed=1539 + i)
        ax.plot(pts[:, 0], pts[:, 1], color=LAND_EDGE, lw=2.4, solid_capstyle="round", zorder=6)
        ax.plot(pts[:, 0], pts[:, 1], color=RED_ACCENT, lw=0.9, alpha=0.65, zorder=7)

    for dx, dy, rw, rh in [(0, 0, 0.06, 0.035), (0.04, 0.018, 0.045, 0.028), (-0.03, 0.012, 0.04, 0.025)]:
        ax.add_patch(
            Ellipse((3.22 + dx, 42.05 + dy), rw, rh, facecolor=LAND, edgecolor=LAND_EDGE, lw=0.9, zorder=7)
        )

def draw_rhumb(ax):
    for hx, hy in [(2.40, 41.30), (3.10, 41.70)]:
        for ang in range(0, 360, 15):
            rad = math.radians(ang)
            ax.plot(
                [hx, hx + 2.8 * math.cos(rad)],
                [hy, hy + 1.6 * math.sin(rad)],
                color=INK,
                lw=0.25,
                alpha=0.12,
                zorder=0.5,
            )


def draw_town(ax, x, y, n=3):
    for i in range(n):
        bx = x + i * 0.036 - 0.035
        ax.add_patch(
            Rectangle((bx, y), 0.028, 0.036, facecolor=CREAM, edgecolor=INK, lw=0.55, zorder=8)
        )
        roof = np.array(
            [[bx - 0.004, y + 0.036], [bx + 0.014, y + 0.058], [bx + 0.032, y + 0.036]]
        )
        ax.add_patch(Polygon(roof, closed=True, facecolor=RED_ACCENT, edgecolor=INK, lw=0.45, zorder=9))


def draw_ship(ax, x, y, scale=1.0, kind="cog"):
    s = 0.055 * scale
    if kind == "galley":
        hull = np.array(
            [
                [x - 3.2 * s, y],
                [x - 2.6 * s, y - 0.55 * s],
                [x + 2.8 * s, y - 0.45 * s],
                [x + 3.4 * s, y + 0.1 * s],
                [x + 2.4 * s, y + 0.35 * s],
                [x - 2.4 * s, y + 0.4 * s],
            ]
        )
        ax.add_patch(Polygon(hull, closed=True, facecolor="#6b3e1f", edgecolor=INK, lw=1.0, zorder=15))
        for i in range(5):
            ox = x - 1.5 * s + i * 0.7 * s
            ax.plot([ox, ox + 0.2 * s], [y - 0.5 * s, y - 1.1 * s], color=INK, lw=0.7, zorder=14)
        ax.plot([x - 0.5 * s, x - 0.5 * s], [y, y + 2.0 * s], color=INK, lw=1.0, zorder=16)
        sail = np.array(
            [[x - 0.45 * s, y + 1.9 * s], [x + 1.2 * s, y + 1.2 * s], [x - 0.45 * s, y + 0.5 * s]]
        )
        ax.add_patch(Polygon(sail, closed=True, facecolor="#e8d5a3", edgecolor=INK, lw=0.8, zorder=16))
        return
    hull = np.array(
        [
            [x - 2.5 * s, y],
            [x - 2.0 * s, y - 0.8 * s],
            [x + 2.0 * s, y - 0.8 * s],
            [x + 2.6 * s, y],
            [x + 1.7 * s, y + 0.42 * s],
            [x - 1.7 * s, y + 0.42 * s],
        ]
    )
    ax.add_patch(Polygon(hull, closed=True, facecolor="#7a4a22", edgecolor=INK, lw=1.0, zorder=15))
    masts = [0.0] if kind == "cog" else [-0.7, 0.5]
    for mi, mx in enumerate(masts):
        ax.plot([x + mx * s, x + mx * s], [y, y + (2.6 - 0.3 * mi) * s], color=INK, lw=1.15, zorder=16)
        sail = np.array(
            [
                [x + mx * s + 0.05 * s, y + (2.5 - 0.3 * mi) * s],
                [x + mx * s + 1.6 * s, y + (1.6 - 0.2 * mi) * s],
                [x + mx * s + 0.05 * s, y + (0.55 - 0.1 * mi) * s],
            ]
        )
        ax.add_patch(
            Polygon(sail, closed=True, facecolor=CREAM if mi == 0 else "#f0e0c0", edgecolor=INK, lw=0.85, zorder=16)
        )
    top = y + 2.6 * s
    ax.plot([x, x + 0.7 * s], [top, top + 0.15 * s], color=RED_ACCENT, lw=1.4, zorder=17)
    if kind == "galleon":
        penn = np.array(
            [[x + 0.05 * s, top], [x + 0.75 * s, top + 0.12 * s], [x + 0.05 * s, top + 0.24 * s]]
        )
        ax.add_patch(Polygon(penn, closed=True, facecolor="#1a120c", edgecolor=INK, lw=0.5, zorder=17))


def draw_compass(ax, cx, cy, r=0.18):
    ax.add_patch(Circle((cx, cy), r * 1.22, facecolor=CREAM, edgecolor=INK, lw=1.5, zorder=40, alpha=0.95))
    for i in range(32):
        a0, a1 = i * 11.25, (i + 1) * 11.25
        col = RED_ACCENT if i % 2 == 0 else CREAM
        ax.add_patch(Wedge((cx, cy), r, a0, a1, facecolor=col, edgecolor=INK, lw=0.35, zorder=41))
    for ang in (90, 0, 270, 180):
        rad = math.radians(ang)
        tip = np.array(
            [
                [cx + (r + 0.015) * math.cos(rad), cy + (r + 0.012) * math.sin(rad)],
                [
                    cx + (r + 0.09) * math.cos(rad) - 0.028 * math.sin(rad),
                    cy + (r + 0.06) * math.sin(rad) + 0.028 * math.cos(rad),
                ],
                [
                    cx + (r + 0.09) * math.cos(rad) + 0.028 * math.sin(rad),
                    cy + (r + 0.06) * math.sin(rad) - 0.028 * math.cos(rad),
                ],
            ]
        )
        ax.add_patch(Polygon(tip, closed=True, facecolor=GOLD, edgecolor=INK, lw=0.5, zorder=42))
    ax.add_patch(Circle((cx, cy), r * 0.28, facecolor=GOLD, edgecolor=INK, lw=1.0, zorder=42))
    ax.add_patch(Circle((cx, cy), r * 0.10, facecolor=INK, zorder=43))
    for lab, ang in [("N", 90), ("E", 0), ("S", 270), ("O", 180)]:
        rad = math.radians(ang)
        ax.text(
            cx + (r + 0.11) * math.cos(rad),
            cy + (r + 0.07) * math.sin(rad),
            lab,
            ha="center",
            va="center",
            fontproperties=_serif(8, "bold"),
            color=INK,
            zorder=43,
        )
    ax.text(
        cx,
        cy - r - 0.07,
        "Rosa ventorum",
        ha="center",
        va="top",
        fontproperties=_serif(5),
        color=INK_SOFT,
        zorder=43,
    )


def draw_wind_face(ax, x, y, label, blow_ang_deg, scale=1.0):
    s = 0.085 * scale
    for dx, dy, rw in [(-0.6, 0.1, 0.7), (0.0, 0.25, 0.85), (0.55, 0.05, 0.65), (0.15, -0.15, 0.55)]:
        ax.add_patch(
            Ellipse(
                (x + dx * s, y + dy * s),
                rw * s * 1.6,
                rw * s,
                facecolor="#efe6d0",
                edgecolor=INK,
                lw=0.7,
                zorder=35,
                alpha=0.95,
            )
        )
    ax.add_patch(Circle((x, y), 0.45 * s, facecolor=CREAM, edgecolor=INK, lw=0.9, zorder=36))
    ax.plot(x - 0.12 * s, y + 0.08 * s, marker="o", markersize=2.2, color=INK, zorder=37)
    ax.plot(x + 0.12 * s, y + 0.08 * s, marker="o", markersize=2.2, color=INK, zorder=37)
    # pursed mouth
    ax.add_patch(
        Ellipse((x + 0.05 * s, y - 0.08 * s), 0.18 * s, 0.12 * s, facecolor=INK, zorder=37)
    )
    rad = math.radians(blow_ang_deg)
    for k in range(5):
        d0 = (0.5 + 0.08 * k) * s
        d1 = (0.75 + 0.28 * k) * s
        ax.plot(
            [x + d0 * math.cos(rad), x + d1 * math.cos(rad)],
            [y + d0 * 0.65 * math.sin(rad), y + d1 * 0.65 * math.sin(rad)],
            color=INK,
            lw=0.7,
            alpha=0.5,
            zorder=37,
        )
    ax.text(
        x,
        y - 0.9 * s,
        label,
        ha="center",
        va="top",
        fontproperties=_serif(5.5, "bold"),
        color=INK,
        zorder=37,
    )


def draw_mountain(ax, x, y, label, w=0.28, h=0.16):
    """Several separate engraved peaks (not one triangle/trapezoid)."""
    peak_specs = [
        (x - w * 0.32, h * 0.72, w * 0.38),
        (x - w * 0.02, h * 1.00, w * 0.42),
        (x + w * 0.28, h * 0.78, w * 0.36),
        (x + w * 0.48, h * 0.55, w * 0.28),
    ]
    for px, ph, pw in peak_specs:
        left, right, tip = px - pw / 2, px + pw / 2, (px, y + ph)
        # asymmetric ridge for engraving look
        mid_l = (px - pw * 0.18, y + ph * 0.55)
        mid_r = (px + pw * 0.22, y + ph * 0.48)
        poly = [(left, y), mid_l, tip, mid_r, (right, y)]
        ax.add_patch(Polygon(poly, closed=True, facecolor="#c2b696", edgecolor=INK, lw=0.95, zorder=5))
        # slope hatching
        for i in range(6):
            t = 0.2 + i * 0.12
            ax.plot(
                [left + pw * 0.15 * t, px - pw * 0.02],
                [y + ph * t * 0.7, y + ph * (0.35 + t * 0.45)],
                color=INK,
                lw=0.35,
                alpha=0.45,
                zorder=5.2,
            )
        cap = np.array(
            [[px - pw * 0.10, y + ph * 0.72], [px, y + ph], [px + pw * 0.10, y + ph * 0.72]]
        )
        ax.add_patch(Polygon(cap, closed=True, facecolor=CREAM, edgecolor=INK, lw=0.45, zorder=5.5))
    rng = random.Random(int(abs(x * 1000) + abs(y * 100)))
    for _ in range(14):
        draw_little_tree(
            ax,
            rng.uniform(x - w * 0.48, x + w * 0.52),
            y - rng.uniform(0.005, 0.05),
            s=rng.uniform(0.016, 0.028),
        )
    ax.text(
        x,
        y - 0.05,
        label,
        ha="center",
        va="top",
        fontproperties=_serif(5, "bold"),
        color=INK,
        zorder=6,
        path_effects=_stroke(1.5, CREAM),
    )

def draw_castle(ax, x, y):
    ax.add_patch(
        Rectangle((x - 0.04, y), 0.08, 0.055, facecolor="#d8c8a8", edgecolor=INK, lw=0.6, zorder=8)
    )
    for dx in (-0.04, -0.005, 0.03):
        ax.add_patch(
            Rectangle(
                (x + dx, y + 0.055), 0.02, 0.018, facecolor="#d8c8a8", edgecolor=INK, lw=0.4, zorder=9
            )
        )
    ax.add_patch(
        Polygon(
            [[x - 0.01, y + 0.07], [x + 0.01, y + 0.10], [x + 0.03, y + 0.07]],
            closed=True,
            facecolor=RED_ACCENT,
            edgecolor=INK,
            lw=0.4,
            zorder=10,
        )
    )


def draw_friendly_monster(ax, x, y, scale=1.0):
    s = 0.075 * scale
    t = np.linspace(0, 2.2 * math.pi, 80)
    xs = x + 0.55 * s * t * np.cos(t)
    ys = y + 0.35 * s * t * np.sin(t)
    ax.plot(xs, ys, color="#2d6a4f", lw=5.2, solid_capstyle="round", zorder=12, alpha=0.9)
    ax.plot(xs, ys, color=INK, lw=1.0, alpha=0.5, zorder=13)
    hx, hy = xs[-1], ys[-1]
    ax.add_patch(
        Ellipse(
            (hx + 0.15 * s, hy), 0.7 * s, 0.5 * s, facecolor="#40916c", edgecolor=INK, lw=1.0, zorder=14
        )
    )
    ax.plot(hx + 0.25 * s, hy + 0.08 * s, marker="o", markersize=2.5, color=INK, zorder=15)
    ax.text(
        x,
        y - 0.5 * s,
        "belua marina",
        ha="center",
        va="top",
        fontproperties=_serif(5),
        color=INK_SOFT,
        style="italic",
        zorder=15,
    )


def draw_scale_bar(ax, x, y):
    w, h = 0.80, 0.20
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            facecolor=CREAM,
            edgecolor=INK,
            linewidth=1.2,
            zorder=50,
            alpha=0.96,
        )
    )
    ax.text(
        x,
        y + 0.055,
        "Scala · leugae",
        ha="center",
        va="center",
        fontproperties=_serif(5.2, "bold"),
        color=INK,
        zorder=51,
    )
    x0, x1 = x - 0.30, x + 0.30
    seg = (x1 - x0) / 4
    for i in range(4):
        ax.add_patch(
            Rectangle(
                (x0 + i * seg, y - 0.02),
                seg,
                0.04,
                facecolor=INK if i % 2 == 0 else CREAM,
                edgecolor=INK,
                lw=0.5,
                zorder=51,
            )
        )
    ax.text(x0, y - 0.07, "0", ha="center", fontproperties=_serif(4.2), color=INK, zorder=51)
    ax.text(x1, y - 0.07, "10", ha="center", fontproperties=_serif(4.2), color=INK, zorder=51)


def draw_ornate_frame(ax):
    x0, x1 = MAP_LON[0] + 0.04, MAP_LON[1] - 0.04
    y0, y1 = MAP_LAT[0] + 0.04, MAP_LAT[1] - 0.04
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=INK, lw=2.8, zorder=60))
    ax.add_patch(
        Rectangle(
            (x0 + 0.04, y0 + 0.04),
            x1 - x0 - 0.08,
            y1 - y0 - 0.08,
            fill=False,
            edgecolor=RED_ACCENT,
            lw=0.9,
            zorder=60,
        )
    )
    # Corner volutes — small, keep clear of Cap de Creus (NE)
    for cx, cy, sx, sy, amp in [
        (x0 + 0.08, y0 + 0.08, 1, 1, 0.05),
        (x1 - 0.08, y0 + 0.08, -1, 1, 0.05),
        (x0 + 0.08, y1 - 0.08, 1, -1, 0.05),
        (x1 - 0.12, y1 - 0.14, -1, -1, 0.035),  # NE smaller / inset
    ]:
        t = np.linspace(0, 1.2 * math.pi, 36)
        ax.plot(
            cx + sx * amp * np.cos(t) * t,
            cy + sy * amp * np.sin(t) * t,
            color=GOLD,
            lw=1.1,
            zorder=61,
        )


def draw_title(ax, x, y):
    """Title cartouche over open sea / north margin — must stay inside ylim."""
    w, h = 1.20, 0.34
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            facecolor=CREAM,
            edgecolor=INK,
            linewidth=2.0,
            zorder=50,
            alpha=0.97,
        )
    )
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2 + 0.03, y - h / 2 + 0.03),
            w - 0.06,
            h - 0.06,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            facecolor="none",
            edgecolor=RED_ACCENT,
            linewidth=1.0,
            zorder=51,
        )
    )
    # volutes
    for sx in (-1, 1):
        t = np.linspace(0, 1.2 * math.pi, 30)
        ax.plot(
            x + sx * (w / 2 + 0.02) + sx * 0.04 * np.cos(t) * t,
            y + 0.04 * np.sin(t) * t,
            color=GOLD,
            lw=1.2,
            zorder=51,
        )
    ax.text(
        x,
        y + 0.07,
        "Nudibranchia Cataloniae",
        ha="center",
        va="center",
        fontproperties=_serif(11, "bold"),
        color=INK,
        zorder=52,
    )
    ax.text(
        x,
        y - 0.04,
        "Hic sunt nudibranchia",
        ha="center",
        va="center",
        fontproperties=_serif(7.5),
        color=RED_ACCENT,
        style="italic",
        zorder=52,
    )
    ax.text(
        x,
        y - 0.14,
        "Costa Catalana · Mare Nostrum",
        ha="center",
        va="center",
        fontproperties=_serif(5.2),
        color=INK_SOFT,
        zorder=52,
    )


def draw_calendar(ax, x, y, peaks: dict[str, str]):
    """Peak-month table fully inside land / frame / ylim."""
    w, h = 1.00, 1.40
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.018,rounding_size=0.028",
            facecolor=CREAM,
            edgecolor=INK,
            linewidth=1.7,
            zorder=50,
            alpha=0.97,
        )
    )
    # volute corners
    for sx, sy in [(-1, 1), (1, 1), (-1, -1), (1, -1)]:
        t = np.linspace(0, math.pi, 20)
        ax.plot(
            x + sx * (w / 2 - 0.02) + sx * 0.03 * np.cos(t),
            y + sy * (h / 2 - 0.02) + sy * 0.03 * np.sin(t),
            color=GOLD,
            lw=1.0,
            zorder=51,
        )
    ax.text(
        x,
        y + h / 2 - 0.055,
        "Calendarium · Menses culminis",
        ha="center",
        va="top",
        fontproperties=_serif(5.8, "bold"),
        color=INK,
        zorder=51,
    )
    ax.plot(
        [x - w / 2 + 0.05, x + w / 2 - 0.05],
        [y + h / 2 - 0.10, y + h / 2 - 0.10],
        color=INK,
        lw=0.6,
        zorder=51,
    )
    for i, (sp, pico) in enumerate(peaks.items()):
        yy = y + h / 2 - 0.18 - i * 0.072
        if i % 2 == 0:
            ax.add_patch(
                Rectangle(
                    (x - w / 2 + 0.035, yy - 0.032),
                    w - 0.07,
                    0.064,
                    facecolor="#e0d0a8",
                    edgecolor="none",
                    alpha=0.4,
                    zorder=50.5,
                )
            )
        short = sp.split()[0][0] + ". " + sp.split()[1]
        ax.text(
            x - w / 2 + 0.055,
            yy,
            short,
            ha="left",
            va="center",
            fontproperties=_serif(4.6),
            color=INK,
            style="italic",
            zorder=51,
            clip_on=True,
        )
        try:
            lab = MES_ABBR[MES_ES.index(pico)]
        except ValueError:
            lab = pico[:3]
        ax.text(
            x + w / 2 - 0.055,
            yy,
            lab,
            ha="right",
            va="center",
            fontproperties=_serif(4.6, "bold"),
            color=RED_ACCENT,
            zorder=51,
            clip_on=True,
        )


def draw_species_engraving(ax, name, x, y, scale, label_off=(0.0, -0.06)):
    eng = woodcut_from_cutout(name, size=520)
    w = 0.46 * scale
    h = 0.36 * scale
    ax.imshow(
        np.asarray(eng),
        extent=[x - w / 2, x + w / 2, y - h / 2, y + h / 2],
        zorder=30,
        interpolation="bilinear",
        aspect="auto",
    )
    ax.text(
        x + label_off[0],
        y - h / 2 + label_off[1],
        name,
        ha="center",
        va="top",
        fontproperties=_serif(5.6, "bold"),
        color=INK,
        style="italic",
        zorder=45,
        bbox=dict(boxstyle="round,pad=0.16", facecolor=CREAM, edgecolor=INK, linewidth=0.7, alpha=0.96),
        clip_on=True,
    )

def draw_calendar_fig(fig, peaks: dict[str, str]):
    """Calendar as figure inset — never clipped by map equal-aspect."""
    ax = fig.add_axes([0.045, 0.38, 0.155, 0.48])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(CREAM)
    for sp in ax.spines.values():
        sp.set_color(INK)
        sp.set_linewidth(1.6)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.add_patch(
        Rectangle((0.03, 0.03), 0.94, 0.94, fill=False, edgecolor=RED_ACCENT, lw=0.9, zorder=2)
    )
    ax.text(
        0.5,
        0.955,
        "Calendarium · Menses culminis",
        ha="center",
        va="top",
        fontproperties=_serif(6.5, "bold"),
        color=INK,
        zorder=3,
    )
    ax.plot([0.08, 0.92], [0.905, 0.905], color=INK, lw=0.7, zorder=3)
    items = list(peaks.items())
    for i, (sp, pico) in enumerate(items):
        yy = 0.86 - i * 0.048
        if i % 2 == 0:
            ax.add_patch(Rectangle((0.06, yy - 0.02), 0.88, 0.042, facecolor="#e0d0a8", edgecolor="none", alpha=0.45, zorder=1))
        short = sp.split()[0][0] + ". " + sp.split()[1]
        ax.text(0.10, yy, short, ha="left", va="center", fontproperties=_serif(5.4), color=INK, style="italic", zorder=3)
        try:
            lab = MES_ABBR[MES_ES.index(pico)]
        except ValueError:
            lab = pico[:3]
        ax.text(0.90, yy, lab, ha="right", va="center", fontproperties=_serif(5.4, "bold"), color=RED_ACCENT, zorder=3)


def draw_title_fig(fig):
    ax = fig.add_axes([0.38, 0.905, 0.28, 0.065])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(CREAM)
    for sp in ax.spines.values():
        sp.set_color(INK)
        sp.set_linewidth(1.8)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.add_patch(Rectangle((0.03, 0.08), 0.94, 0.84, fill=False, edgecolor=RED_ACCENT, lw=0.9))
    ax.text(0.5, 0.62, "Nudibranchia Cataloniae", ha="center", va="center", fontproperties=_serif(10.5, "bold"), color=INK)
    ax.text(0.5, 0.28, "Hic sunt nudibranchia · Costa Catalana", ha="center", va="center", fontproperties=_serif(6.2), color=RED_ACCENT, style="italic")


def draw_scale_fig(fig):
    """Scale cartouche in the bottom page margin (cream strip under the map)."""
    ax = fig.add_axes([0.38, 0.028, 0.24, 0.055])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(CREAM)
    for sp in ax.spines.values():
        sp.set_color(INK)
        sp.set_linewidth(1.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.add_patch(Rectangle((0.04, 0.08), 0.92, 0.84, fill=False, edgecolor=RED_ACCENT, lw=0.8))
    for sx, sy in [(-1, 1), (1, 1), (-1, -1), (1, -1)]:
        t = np.linspace(0, math.pi, 16)
        ax.plot(0.5 + sx * 0.46 + sx * 0.04 * np.cos(t), 0.5 + sy * 0.40 + sy * 0.04 * np.sin(t), color=GOLD, lw=0.9, zorder=2)
    ax.text(0.5, 0.78, "Scala · leugae", ha="center", va="center", fontproperties=_serif(6.2, "bold"), color=INK)
    x0, x1, yb = 0.12, 0.88, 0.32
    seg = (x1 - x0) / 4
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * seg, yb), seg, 0.22, facecolor=INK if i % 2 == 0 else CREAM, edgecolor=INK, lw=0.5))
    ax.text(x0, 0.18, "0", ha="center", fontproperties=_serif(5), color=INK)
    ax.text(x1, 0.18, "10", ha="center", fontproperties=_serif(5), color=INK)


def build_poster():
    coasts, lands = load_ne()
    peaks = {sp: pico for sp, _, _, _, pico, *_ in SPECIES}
    if MONTHLY.exists():
        with MONTHLY.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["especie"] in peaks:
                    peaks[row["especie"]] = row["pico_mes_suavizado"]

    # Pre-build engravings
    print("engravings…", flush=True)
    for sp, *_ in SPECIES:
        woodcut_from_cutout(sp)
        print(f"  {sp}", flush=True)

    fig = plt.figure(figsize=(A3_W_IN, A3_H_IN), dpi=DPI, facecolor=PARCHMENT)
    left = MARGIN_IN / A3_W_IN
    right = MARGIN_IN / A3_W_IN
    bottom = (MARGIN_IN + 0.42) / A3_H_IN  # room for scale cartouche in cream margin
    top = MARGIN_IN / A3_H_IN
    ax = fig.add_axes([left, bottom, 1 - left - right, 1 - bottom - top])
    ax.set_xlim(MAP_LON)
    ax.set_ylim(MAP_LAT)
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor(SEA)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    draw_rhumb(ax)
    draw_sea_waves(ax, coasts)
    draw_land(ax, coasts, lands)

    for lon, lat, name in PLACES:
        if any(k in name for k in ("insulae", "flumen", "Promontorium")):
            ax.text(
                lon,
                lat,
                name,
                ha="center",
                va="bottom",
                fontproperties=_serif(6.2, "bold"),
                color=INK,
                zorder=25,
                path_effects=_stroke(2.2, CREAM),
            )
        else:
            draw_town(ax, lon - 0.04, lat - 0.02, n=random.Random(int(lon * 100)).randint(2, 4))
            ax.text(
                lon,
                lat + 0.04,
                name,
                ha="center",
                va="bottom",
                fontproperties=_serif(6.5, "bold"),
                color=INK,
                zorder=25,
                path_effects=_stroke(2.2, CREAM),
            )

    # Ships fully inside ornate frame (inner ≈ 0.28–3.62 / 40.43–42.72)
    for sx, sy, sc, kind in [
        (3.05, 40.98, 0.88, "galleon"),
        (3.12, 41.22, 0.78, "cog"),
        (1.35, 40.82, 0.82, "galley"),
        (2.55, 40.78, 0.78, "cog"),
        (2.05, 40.70, 0.82, "galleon"),
        (2.95, 41.10, 0.72, "galley"),
    ]:
        draw_ship(ax, sx, sy, scale=sc, kind=kind)

    for name, _zone, (px, py), sc, _pico, lab_off in SPECIES:
        draw_species_engraving(ax, name, px, py, sc, label_off=lab_off)

    # Decorations — all inside frame; scale in left margin cartouche
    draw_wind_face(ax, 2.55, 42.52, "Tramontana", blow_ang_deg=270, scale=1.10)
    draw_wind_face(ax, 3.38, 41.65, "Llevant", blow_ang_deg=200, scale=0.95)
    draw_wind_face(ax, 1.40, 40.62, "Garbí", blow_ang_deg=50, scale=1.00)
    draw_wind_face(ax, 0.58, 41.82, "Mestral", blow_ang_deg=320, scale=0.88)
    draw_friendly_monster(ax, 3.28, 41.55, scale=1.00)
    draw_compass(ax, 2.55, 40.95, r=0.125)
    ax.annotate(
        "Cap de Creus",
        xy=(3.28, 42.28),
        xytext=(3.38, 42.50),
        fontproperties=_serif(6.5, "bold"),
        color=RED_ACCENT,
        arrowprops=dict(arrowstyle="->", color=RED_ACCENT, lw=0.9),
        zorder=40,
        path_effects=_stroke(2.0, CREAM),
    )
    ax.annotate(
        "Delta de l'Ebre",
        xy=(0.78, 40.68),
        xytext=(1.15, 40.52),
        fontproperties=_serif(6.5, "bold"),
        color=RED_ACCENT,
        arrowprops=dict(arrowstyle="->", color=RED_ACCENT, lw=0.9),
        zorder=40,
        path_effects=_stroke(2.0, CREAM),
    )
    draw_ornate_frame(ax)

    # Title + calendar in figure coords (never clipped by equal-aspect)
    draw_title_fig(fig)
    draw_calendar_fig(fig, peaks)
    draw_scale_fig(fig)

    credit = (
        "Inspirado en la Carta Marina de Olaus Magnus, 1539 (dominio público). "
        "Costa: Natural Earth 10m. Criaturas: grabado (SD1.5+Canny + polish pastel/hatch). "
        "Datos: iNaturalist + Minka · BioFauna · 2026"
    )
    fig.text(0.5, 0.012, credit, ha="center", va="bottom", fontproperties=_serif(5.4), color="#4a3a28")

    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)

    map_img = Image.fromarray(rgba[:, :, :3], "RGB")
    parch = parchment_rgba(w, h)
    map_a = np.asarray(map_img).astype(np.float32) / 255.0
    parch_a = np.asarray(parch).astype(np.float32) / 255.0
    blended = map_a * (0.80 + 0.20 * parch_a)
    # Very light parchment only — heavy grain made creatures look photographic
    grain = np.random.default_rng(7).normal(0, 0.003, blended.shape).astype(np.float32)
    blended = np.clip(blended + grain, 0, 1)
    out = Image.fromarray((blended * 255).astype(np.uint8), "RGB")
    out = ImageEnhance.Contrast(out).enhance(1.08)
    out = ImageEnhance.Color(out).enhance(0.92)

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT_PNG, "PNG", dpi=(DPI, DPI))
    out.save(OUT_PDF, "PDF", resolution=DPI)

    OUT_SVG.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">
  <title>Nudibranchia Cataloniae — Carta Marina</title>
  <desc>Lámina 5 · ver PNG/PDF 300 ppp. Script nudibranquios_lamina5_carta_marina_20261010.py</desc>
  <rect width="420" height="297" fill="#e8d9b8"/>
  <text x="210" y="145" text-anchor="middle" font-family="DejaVu Serif" font-size="14" fill="#1a120c">Nudibranchia Cataloniae · Hic sunt nudibranchia</text>
  <text x="210" y="165" text-anchor="middle" font-family="DejaVu Serif" font-size="8" fill="#6b3a28">Imprimible: LAMINA5_carta_marina_20261010.png / .pdf (A3 · 300 ppp)</text>
</svg>
""",
        encoding="utf-8",
    )

    meta = {
        "style": "carta_marina_olaus_magnus_1539",
        "orientation": "A3_landscape",
        "dpi": DPI,
        "size_mm": [420, 297],
        "print_margin_mm": round(MARGIN_IN * 25.4, 1),
        "bbox_lon": list(MAP_LON),
        "bbox_lat": list(MAP_LAT),
        "coast_source": "Natural Earth 10m coastline + admin_1 Catalonia provinces",
        "creatures": "SD1.5 ControlNet-Canny img2img + flat-pastel/hatch polish from real cutouts",
        "gpu": "used then unloaded (scripts/nudibranquios_lamina5_engrave_gpu_20261011.py)",
        "species_n": len(SPECIES),
        "species": [
            {"species": n, "placement": [px, py], "peak": peaks[n], "scale": sc, "label_offset": list(off)}
            for n, _, (px, py), sc, _, off in SPECIES
        ],
        "credit": "Inspirado en la Carta Marina de Olaus Magnus, 1539 (dominio público)",
        "reference_style_only": "ref_carta_marina_gustavo.jpg (no incluida en el póster)",
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S CEST"),
        "png": OUT_PNG.name,
        "pdf": OUT_PDF.name,
        "pixels": list(out.size),
    }
    META_JSON.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lic = MAT / "LICENCIAS_POSTER_LAMINA5.md"
    lic.write_text(
        "\n".join(
            [
                "# Póster A3 — Lámina 5 Carta Marina",
                f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} CEST",
                "",
                "Estilo inspirado en la Carta Marina de Olaus Magnus, 1539 (dominio público).",
                "Costa: Natural Earth 10m (public domain).",
                "Criaturas: grabado (SD1.5 img2img + ControlNet Canny + polish pastel/hatch) desde recortes CC lámina 4.",
                "Referencia de estilo (no incluida): `ref_carta_marina_gustavo.jpg`.",
                "",
                "## Especies",
                "",
            ]
            + [f"- *{n}* · pico {peaks[n]}" for n, *_ in SPECIES]
            + [""]
        ),
        encoding="utf-8",
    )
    print(f"OK {OUT_PNG} {out.size[0]}x{out.size[1]} @ {DPI}ppi")
    print(f"OK {OUT_PDF}")
    return out


if __name__ == "__main__":
    build_poster()
