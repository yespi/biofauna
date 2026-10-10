#!/usr/bin/env python3
"""Lámina 5 — póster A3 estilo Carta Marina (Olaus Magnus, 1539).

Mapa antiguo de la costa catalana con 16 nudibranquios como criaturas
de carta náutica: grabado en madera coloreado a mano (vectorial).
CPU only · 300 ppp · márgenes de impresión.
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
from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
COAST = PAPER / "datos/coast-western-med.geojson"
MONTHLY = PAPER / "datos/especies_mensual_normalizado_20261010.csv"
OUT_PNG = PAPER / "LAMINA5_carta_marina_20261010.png"
OUT_PDF = PAPER / "LAMINA5_carta_marina_20261010.pdf"
OUT_SVG = PAPER / "LAMINA5_carta_marina_20261010.svg"
META_JSON = PAPER / "datos/poster_lamina5_meta_20261010.json"

A3_W_IN, A3_H_IN = 16.5354, 11.6929
DPI = 300
MARGIN_IN = 0.3937  # ~10 mm

# Lon/lat span matched to A3 axes aspect so equal-aspect fills the frame
MAP_LON = (0.35, 3.55)  # span 3.20
MAP_LAT = (40.42, 42.60)  # span ≈ 2.18 → Δlon/Δlat ≈ 1.47 ≈ A3 axes

PARCHMENT = "#e8d9b8"
SEA = "#9eb8bc"
LAND = "#c8c6a0"
LAND_EDGE = "#5c2e1f"
INK = "#1a120c"
INK_SOFT = "#3a2a1c"
RED_ACCENT = "#a83a2a"
GOLD = "#c4a35a"
CREAM = "#f2e6c8"
OLIVE = "#7a8a5a"

ZONE_XY = {
    "Cap de Creus": (3.28, 42.32),
    "Illes Medes / Estartit": (3.225, 42.045),
    "Begur–Palamós": (3.15, 41.90),
    "Tossa–Blanes": (2.93, 41.72),
    "Maresme": (2.50, 41.55),
    "Barcelonès": (2.18, 41.38),
    "Garraf": (1.90, 41.25),
    "Costa Daurada N": (1.55, 41.14),
    "Tarragona–Salou": (1.22, 41.08),
    "Delta de l'Ebre": (0.75, 40.70),
}

# name, zone, (dlon, dlat), scale, peak fallback
SPECIES = [
    ("Cratena peregrina", "Tarragona–Salou", (0.22, -0.10), 1.25, "Agosto"),
    ("Flabellina affinis", "Tarragona–Salou", (0.42, 0.14), 1.20, "Julio"),
    ("Peltodoris atromaculata", "Illes Medes / Estartit", (0.28, 0.06), 1.35, "Agosto"),
    ("Felimare picta", "Barcelonès", (0.32, -0.12), 1.30, "Agosto"),
    ("Edmundsella pedata", "Delta de l'Ebre", (0.30, 0.10), 1.15, "Abril"),
    ("Felimare tricolor", "Costa Daurada N", (0.35, 0.06), 1.20, "Junio"),
    ("Calmella cavolini", "Delta de l'Ebre", (0.50, -0.06), 1.10, "Agosto"),
    ("Diaphorodoris papillata", "Illes Medes / Estartit", (0.45, -0.14), 1.05, "Abril"),
    ("Paradoris indecora", "Tossa–Blanes", (0.30, -0.10), 1.15, "Enero"),
    ("Antiopella cristata", "Barcelonès", (0.52, 0.10), 1.25, "Mayo"),
    ("Polycera quadrilineata", "Tossa–Blanes", (0.48, 0.12), 1.10, "Febrero"),
    ("Rudmania krohni", "Illes Medes / Estartit", (0.15, -0.26), 1.05, "Junio"),
    ("Nemesignis banyulensis", "Tarragona–Salou", (0.05, 0.26), 1.10, "Marzo"),
    ("Diaphorodoris alba", "Begur–Palamós", (0.32, 0.04), 1.05, "Mayo"),
    ("Facelina annulicornis", "Cap de Creus", (0.12, -0.18), 1.15, "Enero"),
    ("Felimare fontandraui", "Cap de Creus", (0.26, 0.10), 1.10, "Mayo"),
]

PLACES = [
    (3.20, 42.30, "Promontorium Crucis"),
    (3.12, 42.24, "Rhoda"),
    (3.08, 42.12, "Emporiae"),
    (3.22, 42.05, "Medae insulae"),
    (2.75, 41.95, "Gerunda"),
    (2.12, 41.40, "Barcino"),
    (1.20, 41.10, "Tarraco"),
    (0.52, 40.70, "Dertosa"),
    (0.65, 40.58, "Ebro flumen"),
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


def load_coast_segments():
    geo = json.loads(COAST.read_text())
    segs = []
    for feat in geo["features"]:
        geom = feat["geometry"]
        coords = geom["coordinates"]
        lines = coords if geom["type"] == "MultiLineString" else [coords]
        for line in lines:
            pts = [
                (x, y)
                for x, y in line
                if MAP_LON[0] - 0.4 <= x <= MAP_LON[1] + 0.4
                and MAP_LAT[0] - 0.4 <= y <= MAP_LAT[1] + 0.4
            ]
            if len(pts) >= 2:
                segs.append(np.array(pts))
    return segs


def coast_x_at_lat(lat: float) -> float:
    """Rough west→east land/sea boundary for Catalonia strip."""
    # Cap Creus ~3.3 @42.3 → Delta ~0.7 @40.7
    t = (lat - 40.5) / (42.5 - 40.5)
    return 0.55 + t * 2.55


def parchment_rgba(w, h, seed=1539):
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), dtype=np.float32)
    base[..., 0] = 0.92
    base[..., 1] = 0.86
    base[..., 2] = 0.72
    base += rng.normal(0, 0.025, (h, w, 1)).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    base *= (1.0 - 0.16 * np.clip(r, 0, 1.25) ** 1.8)[..., None]
    for _ in range(50):
        sx = int(rng.integers(0, w))
        sy = int(rng.integers(0, h))
        rad = int(rng.integers(30, 160))
        yy2, xx2 = np.ogrid[-sy : h - sy, -sx : w - sx]
        mask = xx2 * xx2 + yy2 * yy2 <= rad * rad
        base[mask] *= float(rng.uniform(0.93, 1.03))
    base = np.clip(base, 0, 1)
    img = Image.fromarray((base * 255).astype(np.uint8), "RGB")
    return img.filter(ImageFilter.GaussianBlur(0.6))


def draw_sea(ax, rng):
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
    # denser woodcut waves east of coast
    lons = np.linspace(MAP_LON[0], MAP_LON[1], 110)
    for i, lat in enumerate(np.linspace(MAP_LAT[0] + 0.02, MAP_LAT[1] - 0.02, 70)):
        cx = coast_x_at_lat(lat)
        amp = 0.010 + 0.006 * math.sin(i * 0.55)
        ys = lat + amp * np.sin(lons * 9.5 + i * 0.4)
        mask = lons > cx + 0.02
        if mask.sum() < 4:
            continue
        ax.plot(
            lons[mask],
            ys[mask],
            color=INK,
            lw=0.45,
            alpha=0.38,
            solid_capstyle="round",
            zorder=1,
        )
    for _ in range(18):
        cx = rng.uniform(MAP_LON[0] + 0.5, MAP_LON[1] - 0.05)
        cy = rng.uniform(MAP_LAT[0] + 0.12, MAP_LAT[1] - 0.12)
        if cx < coast_x_at_lat(cy) + 0.15:
            continue
        for r in np.linspace(0.025, 0.11, 6):
            t = np.linspace(0, 2.4 * math.pi, 70)
            ax.plot(
                cx + r * np.cos(t) * 1.35,
                cy + r * np.sin(t) * 0.72,
                color=INK,
                lw=0.65,
                alpha=0.50,
                zorder=2,
            )


def draw_rhumb(ax):
    for hx, hy in [(2.35, 41.35), (3.05, 41.85), (1.55, 41.05)]:
        for ang in range(0, 360, 15):
            rad = math.radians(ang)
            ax.plot(
                [hx, hx + 3.0 * math.cos(rad)],
                [hy, hy + 1.7 * math.sin(rad)],
                color=INK,
                lw=0.28,
                alpha=0.14,
                zorder=0.5,
            )


def draw_land(ax, segs):
    # Stable land fill: band west of empirical coast curve (avoids self-intersecting polygons)
    lats = np.linspace(MAP_LAT[0], MAP_LAT[1], 80)
    coast_line = [(coast_x_at_lat(la) - 0.02, la) for la in lats]
    poly = [(MAP_LON[0], MAP_LAT[0])] + coast_line + [
        (MAP_LON[0], MAP_LAT[1]),
        (MAP_LON[0], MAP_LAT[0]),
    ]
    ax.add_patch(
        Polygon(poly, closed=True, facecolor=LAND, edgecolor="none", alpha=0.98, zorder=3)
    )
    # inland hatch
    for lat in np.linspace(MAP_LAT[0], MAP_LAT[1], 45):
        ax.plot(
            [MAP_LON[0], coast_x_at_lat(lat) - 0.08],
            [lat, lat],
            color=INK,
            lw=0.28,
            alpha=0.16,
            zorder=4,
        )
    # forest of little trees
    rng = random.Random(99)
    for _ in range(280):
        la = rng.uniform(MAP_LAT[0] + 0.05, MAP_LAT[1] - 0.05)
        lo = rng.uniform(MAP_LON[0] + 0.05, coast_x_at_lat(la) - 0.14)
        ax.plot(lo, la, marker="^", markersize=2.2, color=OLIVE, alpha=0.4, zorder=4.5)
    # mountains (antique style) — keep clear of calendar SW
    for mx, my, lab, ww, hh in [
        (1.55, 42.35, "Pyrenaei", 0.38, 0.18),
        (2.35, 41.85, "Montseny", 0.26, 0.14),
        (1.75, 41.65, "Montserrat", 0.24, 0.15),
        (2.85, 41.95, "Gavarres", 0.22, 0.11),
        (0.72, 40.95, "Ports de Beseit", 0.30, 0.14),
    ]:
        draw_mountain(ax, mx, my, lab, w=ww, h=hh)
    for cx, cy in [(2.05, 41.55), (1.35, 41.25), (2.55, 42.05)]:
        draw_castle(ax, cx, cy)
    for s in segs:
        ax.plot(s[:, 0], s[:, 1], color=LAND_EDGE, lw=2.4, solid_capstyle="round", zorder=6)
        ax.plot(s[:, 0], s[:, 1], color=RED_ACCENT, lw=0.85, alpha=0.6, zorder=7)
    # Medes
    for dx, dy, rw, rh in [(0, 0, 0.07, 0.04), (0.045, 0.02, 0.05, 0.03), (-0.035, 0.015, 0.045, 0.028)]:
        ax.add_patch(
            Ellipse(
                (3.22 + dx, 42.05 + dy),
                rw,
                rh,
                facecolor=LAND,
                edgecolor=LAND_EDGE,
                lw=0.9,
                zorder=7,
            )
        )


def draw_town(ax, x, y, n=3):
    for i in range(n):
        bx = x + i * 0.038 - 0.035
        ax.add_patch(
            Rectangle((bx, y), 0.030, 0.038, facecolor=CREAM, edgecolor=INK, lw=0.55, zorder=8)
        )
        roof = np.array(
            [[bx - 0.004, y + 0.038], [bx + 0.015, y + 0.060], [bx + 0.034, y + 0.038]]
        )
        ax.add_patch(Polygon(roof, closed=True, facecolor=RED_ACCENT, edgecolor=INK, lw=0.45, zorder=9))


def draw_ship(ax, x, y, scale=1.0, kind="cog"):
    """kind: cog | galleon | galley"""
    s = 0.06 * scale
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
        # oars
        for i in range(5):
            ox = x - 1.5 * s + i * 0.7 * s
            ax.plot([ox, ox + 0.2 * s], [y - 0.5 * s, y - 1.1 * s], color=INK, lw=0.7, zorder=14)
        ax.plot([x - 0.5 * s, x - 0.5 * s], [y, y + 2.0 * s], color=INK, lw=1.0, zorder=16)
        sail = np.array(
            [[x - 0.45 * s, y + 1.9 * s], [x + 1.2 * s, y + 1.2 * s], [x - 0.45 * s, y + 0.5 * s]]
        )
        ax.add_patch(Polygon(sail, closed=True, facecolor="#e8d5a3", edgecolor=INK, lw=0.8, zorder=16))
        return
    # cog / galleon
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
        col = CREAM if mi == 0 else "#f0e0c0"
        ax.add_patch(Polygon(sail, closed=True, facecolor=col, edgecolor=INK, lw=0.85, zorder=16))
    # flag / pirate banner
    top = y + 2.6 * s
    ax.plot([x, x + 0.7 * s], [top, top + 0.15 * s], color=RED_ACCENT, lw=1.4, zorder=17)
    if kind == "galleon":
        # black pirate pennant
        penn = np.array(
            [[x + 0.05 * s, top], [x + 0.75 * s, top + 0.12 * s], [x + 0.05 * s, top + 0.24 * s]]
        )
        ax.add_patch(Polygon(penn, closed=True, facecolor="#1a120c", edgecolor=INK, lw=0.5, zorder=17))


def draw_compass(ax, cx, cy, r=0.22):
    """Large ornamental wind rose."""
    ax.add_patch(Circle((cx, cy), r * 1.18, facecolor=CREAM, edgecolor=INK, lw=1.4, zorder=19, alpha=0.92))
    for i in range(32):
        a0, a1 = i * 11.25, (i + 1) * 11.25
        col = RED_ACCENT if i % 2 == 0 else CREAM
        ax.add_patch(
            Wedge((cx, cy), r, a0, a1, facecolor=col, edgecolor=INK, lw=0.4, zorder=20)
        )
    # fleur tips
    for ang in (90, 0, 270, 180):
        rad = math.radians(ang)
        tip = np.array(
            [
                [cx + (r + 0.02) * math.cos(rad), cy + (r + 0.015) * math.sin(rad)],
                [cx + (r + 0.10) * math.cos(rad) - 0.03 * math.sin(rad),
                 cy + (r + 0.07) * math.sin(rad) + 0.03 * math.cos(rad)],
                [cx + (r + 0.10) * math.cos(rad) + 0.03 * math.sin(rad),
                 cy + (r + 0.07) * math.sin(rad) - 0.03 * math.cos(rad)],
            ]
        )
        ax.add_patch(Polygon(tip, closed=True, facecolor=GOLD, edgecolor=INK, lw=0.5, zorder=21))
    ax.add_patch(Circle((cx, cy), r * 0.28, facecolor=GOLD, edgecolor=INK, lw=1.0, zorder=21))
    ax.add_patch(Circle((cx, cy), r * 0.10, facecolor=INK, zorder=22))
    for lab, ang in [("N", 90), ("E", 0), ("S", 270), ("O", 180)]:
        rad = math.radians(ang)
        ax.text(
            cx + (r + 0.12) * math.cos(rad),
            cy + (r + 0.08) * math.sin(rad),
            lab,
            ha="center",
            va="center",
            fontproperties=_serif(8.5, "bold"),
            color=INK,
            zorder=22,
        )
    ax.text(cx, cy - r - 0.08, "Rosa ventorum", ha="center", va="top",
            fontproperties=_serif(5), color=INK_SOFT, zorder=22)


def draw_wind_face(ax, x, y, label, blow_ang_deg, scale=1.0):
    """Cloud with blowing face (tramontana / llevant / garbí)."""
    s = 0.09 * scale
    # cloud puffs
    for dx, dy, rw in [(-0.6, 0.1, 0.7), (0.0, 0.25, 0.85), (0.55, 0.05, 0.65), (0.15, -0.15, 0.55)]:
        ax.add_patch(
            Ellipse(
                (x + dx * s, y + dy * s), rw * s * 1.6, rw * s,
                facecolor="#efe6d0", edgecolor=INK, lw=0.7, zorder=18, alpha=0.95,
            )
        )
    # face
    ax.add_patch(Circle((x, y), 0.45 * s, facecolor=CREAM, edgecolor=INK, lw=0.9, zorder=19))
    ax.plot(x - 0.12 * s, y + 0.08 * s, marker="o", markersize=2.2, color=INK, zorder=20)
    ax.plot(x + 0.12 * s, y + 0.08 * s, marker="o", markersize=2.2, color=INK, zorder=20)
    # cheek puff + breath lines
    rad = math.radians(blow_ang_deg)
    for k in range(4):
        d = (0.55 + 0.22 * k) * s
        ax.annotate(
            "",
            xy=(x + d * math.cos(rad), y + d * 0.7 * math.sin(rad)),
            xytext=(x + 0.35 * s * math.cos(rad), y + 0.35 * s * 0.7 * math.sin(rad)),
            arrowprops=dict(arrowstyle="-", color=INK, lw=0.7, alpha=0.55),
            zorder=20,
        )
    ax.text(x, y - 0.85 * s, label, ha="center", va="top",
            fontproperties=_serif(5.5, "bold"), color=INK, zorder=20)


def draw_mountain(ax, x, y, label, w=0.28, h=0.16):
    peak = np.array([[x - w / 2, y], [x, y + h], [x + w / 2, y]])
    ax.add_patch(Polygon(peak, closed=True, facecolor="#b8b090", edgecolor=INK, lw=0.9, zorder=5))
    # snow cap hatch
    cap = np.array([[x - w * 0.18, y + h * 0.55], [x, y + h], [x + w * 0.18, y + h * 0.55]])
    ax.add_patch(Polygon(cap, closed=True, facecolor=CREAM, edgecolor=INK, lw=0.5, zorder=5.5))
    ax.text(x, y - 0.03, label, ha="center", va="top",
            fontproperties=_serif(5, "bold"), color=INK, zorder=6,
            path_effects=_stroke(1.5, CREAM))


def draw_castle(ax, x, y):
    ax.add_patch(Rectangle((x - 0.04, y), 0.08, 0.055, facecolor="#d8c8a8", edgecolor=INK, lw=0.6, zorder=8))
    for dx in (-0.04, -0.005, 0.03):
        ax.add_patch(Rectangle((x + dx, y + 0.055), 0.02, 0.018, facecolor="#d8c8a8", edgecolor=INK, lw=0.4, zorder=9))
    ax.add_patch(Polygon(
        [[x - 0.01, y + 0.07], [x + 0.01, y + 0.10], [x + 0.03, y + 0.07]],
        closed=True, facecolor=RED_ACCENT, edgecolor=INK, lw=0.4, zorder=10,
    ))


def draw_friendly_monster(ax, x, y, scale=1.0):
    """Decorative non-nudibranch sea serpent (does not compete with spp labels)."""
    s = 0.08 * scale
    # coiled body
    t = np.linspace(0, 2.2 * math.pi, 80)
    xs = x + 0.55 * s * t * np.cos(t)
    ys = y + 0.35 * s * t * np.sin(t)
    ax.plot(xs, ys, color="#2d6a4f", lw=5.5, solid_capstyle="round", zorder=12, alpha=0.9)
    ax.plot(xs, ys, color=INK, lw=1.0, alpha=0.5, zorder=13)
    # head
    hx, hy = xs[-1], ys[-1]
    ax.add_patch(Ellipse((hx + 0.15 * s, hy), 0.7 * s, 0.5 * s, facecolor="#40916c", edgecolor=INK, lw=1.0, zorder=14))
    ax.plot(hx + 0.25 * s, hy + 0.08 * s, marker="o", markersize=2.5, color=INK, zorder=15)
    ax.text(x, y - 0.55 * s, "belua marina", ha="center", va="top",
            fontproperties=_serif(5), color=INK_SOFT, style="italic", zorder=15)


def draw_scale_bar(ax, x, y):
    """Scala in leguas (decorative)."""
    w, h = 0.85, 0.22
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            facecolor=CREAM, edgecolor=INK, linewidth=1.2, zorder=50, alpha=0.96,
        )
    )
    ax.text(x, y + 0.06, "Scala · leugae", ha="center", va="center",
            fontproperties=_serif(5.5, "bold"), color=INK, zorder=51)
    x0, x1 = x - 0.32, x + 0.32
    seg = (x1 - x0) / 4
    for i in range(4):
        ax.add_patch(
            Rectangle(
                (x0 + i * seg, y - 0.025),
                seg,
                0.045,
                facecolor=INK if i % 2 == 0 else CREAM,
                edgecolor=INK,
                lw=0.5,
                zorder=51,
            )
        )
    ax.text(x0, y - 0.08, "0", ha="center", fontproperties=_serif(4.5), color=INK, zorder=51)
    ax.text(x1, y - 0.08, "10", ha="center", fontproperties=_serif(4.5), color=INK, zorder=51)


def draw_ornate_frame(ax):
    """Decorated outer frame with corner volutes."""
    x0, x1 = MAP_LON[0] + 0.025, MAP_LON[1] - 0.025
    y0, y1 = MAP_LAT[0] + 0.025, MAP_LAT[1] - 0.025
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=INK, lw=2.6, zorder=60))
    ax.add_patch(Rectangle(
        (x0 + 0.035, y0 + 0.035), x1 - x0 - 0.07, y1 - y0 - 0.07,
        fill=False, edgecolor=RED_ACCENT, lw=0.9, zorder=60,
    ))
    # corner flourishes
    for cx, cy, sx, sy in [
        (x0 + 0.08, y0 + 0.08, 1, 1),
        (x1 - 0.08, y0 + 0.08, -1, 1),
        (x0 + 0.08, y1 - 0.08, 1, -1),
        (x1 - 0.08, y1 - 0.08, -1, -1),
    ]:
        t = np.linspace(0, 1.4 * math.pi, 40)
        ax.plot(
            cx + sx * 0.06 * np.cos(t) * t,
            cy + sy * 0.06 * np.sin(t) * t,
            color=GOLD, lw=1.3, zorder=61,
        )


# ── creature drawings ──────────────────────────────────────────────

def _label(ax, x, y, text, s):
    ax.text(
        x,
        y - 1.85 * s,
        text,
        ha="center",
        va="top",
        fontproperties=_serif(6.2, "bold"),
        color=INK,
        style="italic",
        zorder=45,
        bbox=dict(
            boxstyle="round,pad=0.22",
            facecolor=CREAM,
            edgecolor=INK,
            linewidth=0.85,
            alpha=0.96,
        ),
    )


def _aeolid_monster(ax, x, y, s, body, cerata, rhin=None, n=11, head_mouth=True):
    rhin = rhin or body
    # serpentine body (more monster)
    body_pts = []
    for i in range(14):
        t = i / 13
        px = x - 1.9 * s + t * 3.8 * s
        wave = 0.22 * s * math.sin(t * math.pi * 2.2)
        body_pts.append([px, y + wave - 0.35 * s])
    for i in range(13, -1, -1):
        t = i / 13
        px = x - 1.9 * s + t * 3.8 * s
        wave = 0.22 * s * math.sin(t * math.pi * 2.2)
        body_pts.append([px, y + wave + 0.35 * s])
    ax.add_patch(
        Polygon(
            np.array(body_pts), closed=True, facecolor=body, edgecolor=INK, lw=1.35,
            hatch="////", zorder=30,
        )
    )
    # dragonish head
    ax.add_patch(
        Ellipse(
            (x - 1.85 * s, y), 1.0 * s, 0.85 * s, facecolor=body, edgecolor=INK, lw=1.2,
            hatch="////", zorder=31,
        )
    )
    if head_mouth:
        ax.plot(
            [x - 2.2 * s, x - 2.45 * s],
            [y - 0.05 * s, y + 0.15 * s],
            color=INK,
            lw=1.0,
            zorder=32,
        )
        ax.plot(x - 1.7 * s, y + 0.12 * s, marker="o", markersize=2.5, color=INK, zorder=33)
    # tall rhinophores (ears)
    for dx, tip in [(-0.25, 1.35), (0.25, 1.45)]:
        ax.plot(
            [x - 1.85 * s + dx * s, x - 2.05 * s + dx * s],
            [y + 0.25 * s, y + tip * s],
            color=rhin,
            lw=2.8,
            solid_capstyle="round",
            zorder=32,
        )
        ax.plot(
            [x - 1.85 * s + dx * s, x - 2.05 * s + dx * s],
            [y + 0.25 * s, y + tip * s],
            color=INK,
            lw=0.8,
            alpha=0.65,
            zorder=33,
        )
        ax.plot(
            x - 2.05 * s + dx * s,
            y + tip * s,
            marker="o",
            markersize=3.5,
            color=cerata[0],
            markeredgecolor=INK,
            markeredgewidth=0.5,
            zorder=34,
        )
    # wild cerata
    for i in range(n):
        t = i / max(n - 1, 1)
        cx = x - 1.0 * s + t * 2.8 * s
        side = 1 if i % 2 == 0 else -1
        h = (0.85 + 0.45 * abs(math.sin(i * 1.1))) * s
        col = cerata[i % len(cerata)]
        ax.plot(
            [cx, cx + side * 0.12 * s],
            [y + side * 0.15 * s, y + side * h],
            color=col,
            lw=3.4,
            solid_capstyle="round",
            zorder=31,
        )
        ax.plot(
            [cx, cx + side * 0.12 * s],
            [y + side * 0.15 * s, y + side * h],
            color=INK,
            lw=0.75,
            alpha=0.5,
            zorder=32,
        )
        tip = cerata[(i + 1) % len(cerata)]
        ax.plot(
            cx + side * 0.12 * s,
            y + side * h,
            marker="o",
            markersize=3.2,
            color=tip,
            markeredgecolor=INK,
            markeredgewidth=0.4,
            zorder=33,
        )


def _dorid_monster(ax, x, y, s, mantle, spots=None, gill="#ddd", rhin="#eee", stripes=None):
    # plump oval + woodcut hatch
    ax.add_patch(
        Ellipse(
            (x, y), 3.6 * s, 2.3 * s, facecolor=mantle, edgecolor=INK, lw=1.45,
            hatch="xxx", zorder=30,
        )
    )
    if spots:
        rng = random.Random(int(abs(x * 1000 + y * 100)) % 10_000_000)
        n, rad, col = spots
        for _ in range(n):
            sx = x + rng.uniform(-1.2, 1.2) * s
            sy = y + rng.uniform(-0.7, 0.7) * s
            ax.add_patch(
                Ellipse(
                    (sx, sy),
                    rad * s * rng.uniform(0.8, 1.2),
                    rad * 0.8 * s,
                    facecolor=col,
                    edgecolor=INK,
                    lw=0.45,
                    zorder=31,
                )
            )
    if stripes:
        for dy, col, lw in stripes:
            ax.plot(
                [x - 1.45 * s, x + 1.45 * s],
                [y + dy * s, y + dy * s],
                color=col,
                lw=lw,
                zorder=32,
                solid_capstyle="round",
            )
    # rhinophores as horns
    for dx in (-0.4, 0.4):
        ax.plot(
            [x + dx * s, x + dx * s * 1.05],
            [y + 0.55 * s, y + 1.35 * s],
            color=rhin,
            lw=2.6,
            solid_capstyle="round",
            zorder=33,
        )
        ax.plot(
            [x + dx * s, x + dx * s * 1.05],
            [y + 0.55 * s, y + 1.35 * s],
            color=INK,
            lw=0.7,
            alpha=0.6,
            zorder=34,
        )
    # monstrous gill crown
    for ang in range(-70, 80, 14):
        rad = math.radians(ang + 90)
        ax.plot(
            [x + 1.05 * s, x + 1.05 * s + 0.7 * s * math.cos(rad)],
            [y - 0.05 * s, y - 0.05 * s + 0.7 * s * math.sin(rad)],
            color=gill,
            lw=2.0,
            solid_capstyle="round",
            zorder=33,
        )


def draw_species(ax, name, x, y, scale):
    s = 0.078 * scale
    if name == "Cratena peregrina":
        _aeolid_monster(ax, x, y, s, "#f4efe6", ["#e85d04", "#1d4e89", "#e85d04", "#fff"], rhin="#e85d04")
    elif name == "Flabellina affinis":
        _aeolid_monster(ax, x, y, s, "#6a0dad", ["#9b5de5", "#ff6b35", "#c77dff", "#ff9f1c"], rhin="#4a0080")
    elif name == "Peltodoris atromaculata":
        _dorid_monster(ax, x, y, s * 1.15, "#f7f3e8", spots=(10, 0.58, "#3d2314"), gill="#c4a882", rhin="#eee")
    elif name == "Felimare picta":
        _dorid_monster(
            ax, x, y, s, "#1e3a8a",
            gill="#fbbf24", rhin="#fbbf24",
            stripes=[(-0.45, "#fbbf24", 1.6), (0.0, "#fbbf24", 2.0), (0.45, "#fbbf24", 1.6)],
        )
    elif name == "Edmundsella pedata":
        _aeolid_monster(ax, x, y, s, "#e83e8c", ["#ff69b4", "#ff1493", "#ffb6c1", "#fff"], rhin="#ad1457")
    elif name == "Felimare tricolor":
        _dorid_monster(
            ax, x, y, s, "#1e40af",
            gill="#facc15", rhin="#facc15",
            stripes=[(-0.4, "#fff", 1.3), (0.0, "#facc15", 2.1), (0.4, "#fff", 1.3)],
        )
    elif name == "Calmella cavolini":
        _aeolid_monster(ax, x, y, s, "#ff7a18", ["#ff9f1c", "#fff", "#ff6b00", "#ffe5b4"], rhin="#e85d04")
    elif name == "Diaphorodoris papillata":
        _dorid_monster(ax, x, y, s, "#ff8c42", spots=(14, 0.24, "#fff"), gill="#fff", rhin="#fff")
        ax.add_patch(
            Arc((x, y), 3.4 * s, 2.1 * s, theta1=200, theta2=340, color="#6b21a8", lw=2.6, zorder=32)
        )
    elif name == "Paradoris indecora":
        _dorid_monster(ax, x, y, s, "#c4a882", spots=(8, 0.42, "#8b6914"), gill="#a08060", rhin="#ddd")
    elif name == "Antiopella cristata":
        _aeolid_monster(ax, x, y, s, "#e8f4f8", ["#7dd3fc", "#fbbf24", "#38bdf8", "#fde68a"], n=14, rhin="#0284c7")
    elif name == "Polycera quadrilineata":
        ax.add_patch(
            Ellipse((x, y), 3.1 * s, 1.35 * s, facecolor="#f8f4e8", edgecolor=INK, lw=1.3, zorder=30)
        )
        for dy, col in [(-0.28, "#111"), (0.0, "#f5c518"), (0.28, "#111")]:
            ax.plot([x - 1.3 * s, x + 1.3 * s], [y + dy * s, y + dy * s], color=col, lw=1.5, zorder=31)
        for dx in (-1.0, -0.35, 0.35, 1.0):
            ax.plot(
                [x + dx * s, x + dx * s],
                [y + 0.45 * s, y + 1.45 * s],
                color="#f5c518",
                lw=2.4,
                solid_capstyle="round",
                zorder=32,
            )
            ax.plot(
                x + dx * s,
                y + 1.45 * s,
                marker="o",
                markersize=4,
                color="#111",
                markeredgecolor=INK,
                zorder=33,
            )
        # oral tentacles
        for dx in (-0.5, 0.5):
            ax.plot(
                [x - 1.4 * s, x - 1.7 * s + dx * 0.2 * s],
                [y, y + 0.9 * s],
                color="#f5c518",
                lw=2.0,
                zorder=32,
            )
    elif name == "Rudmania krohni":
        _aeolid_monster(ax, x, y, s, "#f0f4f8", ["#ff6b35", "#ff9f1c", "#fff", "#ff6b35"], rhin="#ff6b35")
    elif name == "Nemesignis banyulensis":
        _aeolid_monster(ax, x, y, s, "#ff6b35", ["#ff8c42", "#fff5e6", "#e85d04", "#fff"], rhin="#c2410c")
    elif name == "Diaphorodoris alba":
        _dorid_monster(ax, x, y, s, "#faf7f0", spots=(9, 0.30, "#ff8c42"), gill="#fff", rhin="#ff8c42")
    elif name == "Facelina annulicornis":
        _aeolid_monster(ax, x, y, s, "#f5efe6", ["#d4a574", "#8b4513", "#f5efe6", "#a0522d"], rhin="#8b4513")
        for dx in (-0.2, 0.2):
            for k in range(5):
                yy = y + (0.45 + k * 0.18) * s
                ax.plot(
                    [x - 1.95 * s + dx * s],
                    [yy],
                    marker="s",
                    markersize=2.4,
                    color="#fff" if k % 2 == 0 else "#8b4513",
                    zorder=35,
                )
    elif name == "Felimare fontandraui":
        _dorid_monster(
            ax, x, y, s, "#1e3a8a",
            gill="#facc15", rhin="#facc15",
            stripes=[(0.0, "#facc15", 2.4)],
        )
    else:
        _aeolid_monster(ax, x, y, s, "#ccc", ["#999"])
    _label(ax, x, y, name, s)


def draw_title(ax, x, y):
    """Title cartouche over the open sea (NE), not overlapping the calendar."""
    w, h = 1.40, 0.42
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.035",
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
            boxstyle="round,pad=0.01,rounding_size=0.025",
            facecolor="none",
            edgecolor=RED_ACCENT,
            linewidth=1.0,
            zorder=51,
        )
    )
    ax.text(
        x, y + 0.07, "Nudibranchia Cataloniae",
        ha="center", va="center", fontproperties=_serif(11.5, "bold"), color=INK, zorder=52,
    )
    ax.text(
        x, y - 0.05, "Hic sunt nudibranchia",
        ha="center", va="center", fontproperties=_serif(8), color=RED_ACCENT,
        style="italic", zorder=52,
    )
    ax.text(
        x, y - 0.15, "Costa Catalana · Mare Nostrum",
        ha="center", va="center", fontproperties=_serif(5.5), color=INK_SOFT, zorder=52,
    )


def draw_calendar(ax, x, y, peaks: dict[str, str]):
    """Compact peak-month table in SW margin (over land)."""
    w, h = 1.20, 1.70
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            facecolor=CREAM,
            edgecolor=INK,
            linewidth=1.7,
            zorder=50,
            alpha=0.97,
        )
    )
    ax.text(
        x, y + h / 2 - 0.06, "Calendarium · Menses culminis",
        ha="center", va="top", fontproperties=_serif(6.2, "bold"), color=INK, zorder=51,
    )
    ax.plot(
        [x - w / 2 + 0.06, x + w / 2 - 0.06],
        [y + h / 2 - 0.115, y + h / 2 - 0.115],
        color=INK, lw=0.65, zorder=51,
    )
    ax.text(
        x - w / 2 + 0.06, y + h / 2 - 0.17, "Species",
        ha="left", va="center", fontproperties=_serif(4.6, "bold"), color=INK_SOFT, zorder=51,
    )
    ax.text(
        x + w / 2 - 0.06, y + h / 2 - 0.17, "Pico",
        ha="right", va="center", fontproperties=_serif(4.6, "bold"), color=INK_SOFT, zorder=51,
    )
    for i, (sp, pico) in enumerate(peaks.items()):
        yy = y + h / 2 - 0.26 - i * 0.085
        if i % 2 == 0:
            ax.add_patch(
                Rectangle(
                    (x - w / 2 + 0.04, yy - 0.038),
                    w - 0.08,
                    0.076,
                    facecolor="#e0d0a8",
                    edgecolor="none",
                    alpha=0.45,
                    zorder=50.5,
                )
            )
        short = sp.split()[0][0] + ". " + sp.split()[1]
        ax.text(
            x - w / 2 + 0.07, yy, short,
            ha="left", va="center", fontproperties=_serif(5.0),
            color=INK, style="italic", zorder=51,
        )
        try:
            lab = MES_ABBR[MES_ES.index(pico)]
        except ValueError:
            lab = pico[:3]
        ax.text(
            x + w / 2 - 0.07, yy, lab,
            ha="right", va="center", fontproperties=_serif(5.0, "bold"),
            color=RED_ACCENT, zorder=51,
        )


def build_poster():
    rng = random.Random(1539)
    segs = load_coast_segments()

    peaks = {sp: pico for sp, _, _, _, pico in SPECIES}
    if MONTHLY.exists():
        with MONTHLY.open() as f:
            for row in csv.DictReader(f):
                if row["especie"] in peaks:
                    peaks[row["especie"]] = row["pico_mes_suavizado"]

    fig_w = A3_W_IN
    fig_h = A3_H_IN
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=DPI, facecolor=PARCHMENT)

    left = MARGIN_IN / fig_w
    right = MARGIN_IN / fig_w
    bottom = (MARGIN_IN + 0.18) / fig_h  # room for credit
    top = MARGIN_IN / fig_h
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
    draw_sea(ax, rng)
    draw_land(ax, segs)

    for lon, lat, name in PLACES:
        if any(k in name for k in ("insulae", "flumen", "Promontorium")):
            ax.text(
                lon, lat, name, ha="center", va="bottom",
                fontproperties=_serif(6.5, "bold"), color=INK, zorder=25,
                path_effects=_stroke(2.2, CREAM),
            )
        else:
            draw_town(ax, lon - 0.04, lat - 0.02, n=rng.randint(2, 4))
            ax.text(
                lon, lat + 0.045, name, ha="center", va="bottom",
                fontproperties=_serif(7, "bold"), color=INK, zorder=25,
                path_effects=_stroke(2.4, CREAM),
            )

    for sx, sy, sc, kind in [
        (2.75, 41.32, 1.25, "galleon"),
        (3.40, 41.50, 1.00, "cog"),
        (1.95, 40.95, 1.05, "galley"),
        (2.25, 41.95, 0.9, "cog"),
        (1.05, 40.95, 1.15, "galleon"),
        (3.10, 41.30, 0.85, "cog"),
    ]:
        draw_ship(ax, sx, sy, scale=sc, kind=kind)

    for name, zone, (dx, dy), sc, _ in SPECIES:
        zx, zy = ZONE_XY[zone]
        draw_species(ax, name, zx + dx, zy + dy, sc)

    # decorative extras (addendum Gustavo 20:31) — clear of nudibranch clusters
    draw_wind_face(ax, 2.95, 42.48, "Tramontana", blow_ang_deg=270, scale=1.15)
    draw_wind_face(ax, 3.42, 41.75, "Llevant", blow_ang_deg=180, scale=1.0)
    draw_wind_face(ax, 1.65, 40.72, "Garbí", blow_ang_deg=45, scale=1.05)
    draw_friendly_monster(ax, 3.35, 40.95, scale=1.15)
    draw_compass(ax, 3.15, 40.72, r=0.20)
    draw_scale_bar(ax, 0.85, 40.68)
    draw_title(ax, 2.45, 42.35)
    draw_calendar(ax, 0.78, 41.35, peaks)
    draw_ornate_frame(ax)

    credit = (
        "Inspirado en la Carta Marina de Olaus Magnus, 1539 (dominio público). "
        "Datos: iNaturalist + Minka · BioFauna / fotofauna.yespi.es · 2026"
    )
    fig.text(
        0.5, 0.010, credit, ha="center", va="bottom",
        fontproperties=_serif(5.8), color="#4a3a28",
    )

    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)

    map_img = Image.fromarray(rgba[:, :, :3], "RGB")
    parch = parchment_rgba(w, h)
    map_a = np.asarray(map_img).astype(np.float32) / 255.0
    parch_a = np.asarray(parch).astype(np.float32) / 255.0
    # Soft multiply: keep ink dark, warm paper
    blended = 1.0 - (1.0 - map_a) * (1.0 - 0.22 * (parch_a - 0.5))
    blended = map_a * (0.72 + 0.28 * parch_a)
    grain = np.random.default_rng(7).normal(0, 0.012, blended.shape).astype(np.float32)
    blended = np.clip(blended + grain, 0, 1)
    out = Image.fromarray((blended * 255).astype(np.uint8), "RGB")
    out = ImageEnhance.Contrast(out).enhance(1.10)
    out = ImageEnhance.Color(out).enhance(0.94)

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
  <text x="210" y="280" text-anchor="middle" font-family="DejaVu Serif" font-size="6" fill="#4a3a28">Inspirado en la Carta Marina de Olaus Magnus, 1539 (dominio público)</text>
</svg>
""",
        encoding="utf-8",
    )

    meta = {
        "style": "carta_marina_olaus_magnus_1539",
        "orientation": "A3_landscape",
        "dpi": DPI,
        "size_mm": [420, 297],
        "print_margin_mm": 10,
        "bbox_lon": list(MAP_LON),
        "bbox_lat": list(MAP_LAT),
        "species_n": len(SPECIES),
        "species": [
            {"species": n, "zone": z, "peak": peaks[n], "offset": [dx, dy], "scale": sc}
            for n, z, (dx, dy), sc, _ in SPECIES
        ],
        "credit": "Inspirado en la Carta Marina de Olaus Magnus, 1539 (dominio público)",
        "tools": "matplotlib + Pillow (CPU); sin modelo de imagen; sin GPU",
        "reference_style_only": "ref_carta_marina_gustavo.jpg (no incluida en el póster)",
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S CEST"),
        "png": OUT_PNG.name,
        "pdf": OUT_PDF.name,
        "pixels": list(out.size),
    }
    META_JSON.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK {OUT_PNG} {out.size[0]}x{out.size[1]} @ {DPI}ppi")
    print(f"OK {OUT_PDF}")
    print(f"OK {OUT_SVG}")
    return out


if __name__ == "__main__":
    build_poster()
