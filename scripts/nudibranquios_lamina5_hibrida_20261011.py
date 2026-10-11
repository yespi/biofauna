#!/usr/bin/env python3
"""Lámina 5 — póster A3 híbrido (orden Gustavo 11-oct-2026; anula grabado).

- Tierra: Sentinel-2 cloudless EOX (CC BY 4.0) virada a sepia/pergamino.
- Mar: azul Carta Marina con olas grabadas.
- Nudibranquios: foto real recortada, contorno limpio, sombra suave.
- Rosa portulana 32 puntas + flor de lis al norte.
- Topónimos en caligrafía (sin iconos de pueblo).
- Nubes, galeones, monstruo, cartelas, escala, marco — dentro del marco.
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
from matplotlib.patches import Circle, Ellipse, Polygon, Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
MAT = PAPER / "material"
NE_GEO = MAT / "datos/catalunya_ne10m.geojson"
RECORTES = MAT / "recortes"
MONTHLY = MAT / "datos/especies_mensual_normalizado_20261010.csv"
SAT_MAP = MAT / "datos/mapa_satelite_catalunya_s2cloudless.jpg"
SAT_META = MAT / "datos/mapa_satelite_catalunya_s2cloudless_meta.json"
OUT_PNG = MAT / "LAMINA5_carta_marina_20261010.png"
OUT_PDF = MAT / "LAMINA5_carta_marina_20261010.pdf"
OUT_SVG = MAT / "LAMINA5_carta_marina_20261010.svg"
META_JSON = MAT / "datos/poster_lamina5_meta_20261010.json"

A3_W_IN, A3_H_IN = 16.5354, 11.6929
DPI = 300
MARGIN_IN = 0.42

MAP_LON = (0.55, 3.45)
MAP_LAT = (40.52, 42.55)

PARCHMENT = "#e8d9b8"
SEA = "#6f9eae"
SEA_DEEP = "#4e8294"
LAND_EDGE = "#5a2818"
INK = "#1a120c"
INK_SOFT = "#3a2a1c"
RED_ACCENT = "#a83a2a"
GOLD = "#c4a35a"
CREAM = "#f2e6c8"

# placements tuned clear of compass (SW) and frame
SPECIES = [
    ("Cratena peregrina", (1.22, 41.08), (1.90, 40.82), 1.28, "Agosto", (0.0, -0.05)),
    ("Flabellina affinis", (1.22, 41.08), (2.18, 40.78), 1.22, "Julio", (0.0, -0.05)),
    ("Peltodoris atromaculata", (3.225, 42.045), (2.98, 41.68), 1.28, "Agosto", (0.08, -0.06)),
    ("Felimare picta", (2.18, 41.38), (2.70, 41.25), 1.28, "Agosto", (0.0, -0.05)),
    ("Edmundsella pedata", (0.75, 40.70), (1.30, 40.72), 1.18, "Abril", (0.0, -0.05)),
    ("Felimare tricolor", (1.55, 41.14), (2.05, 41.02), 1.22, "Junio", (0.0, -0.05)),
    ("Calmella cavolini", (0.75, 40.70), (0.92, 40.72), 1.12, "Agosto", (0.08, -0.04)),
    ("Diaphorodoris papillata", (3.225, 42.045), (3.22, 41.42), 1.12, "Abril", (0.0, -0.05)),
    ("Paradoris indecora", (2.93, 41.72), (3.05, 41.28), 1.18, "Enero", (0.0, -0.05)),
    ("Antiopella cristata", (2.18, 41.38), (2.72, 41.50), 1.22, "Mayo", (0.0, -0.05)),
    ("Polycera quadrilineata", (2.93, 41.72), (2.95, 41.08), 1.10, "Febrero", (0.0, -0.05)),
    ("Rudmania krohni", (3.225, 42.045), (2.38, 41.65), 1.08, "Junio", (0.0, -0.05)),
    ("Nemesignis banyulensis", (1.22, 41.08), (1.60, 41.02), 1.12, "Marzo", (0.0, -0.05)),
    ("Diaphorodoris alba", (3.15, 41.90), (2.22, 41.35), 1.08, "Mayo", (0.0, -0.05)),
    ("Facelina annulicornis", (3.28, 42.32), (3.22, 42.00), 1.18, "Enero", (-0.04, -0.05)),
    ("Felimare fontandraui", (3.28, 42.32), (2.65, 42.08), 1.12, "Mayo", (0.0, -0.05)),
]

PLACES = [
    (3.12, 42.26, "Promontorium Crucis"),
    (3.02, 42.06, "Emporiae"),
    (3.16, 41.98, "Medae insulae"),
    (2.72, 41.96, "Gerunda"),
    (2.08, 41.40, "Barcino"),
    (1.20, 41.12, "Tarraco"),
    (0.78, 40.82, "Dertosa"),
    (0.85, 40.64, "Ebro flumen"),
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
        if props.get("source") == "ne_10m_coastline" or geom["type"] in ("LineString", "MultiLineString"):
            coords = geom["coordinates"]
            if geom["type"] == "MultiLineString":
                for line in coords:
                    coasts.append(np.array(line, dtype=float))
            elif geom["type"] == "LineString":
                coasts.append(np.array(coords, dtype=float))
        else:
            lands.append(geom)
    return coasts, lands


def hand_jitter(pts: np.ndarray, amp=0.0025, seed=1539) -> np.ndarray:
    rng = np.random.default_rng(seed + int(abs(pts[0, 0] * 1000)) % 997)
    out = pts.copy()
    for i in range(1, len(out) - 1):
        dx = out[i, 0] - out[i - 1, 0]
        dy = out[i, 1] - out[i - 1, 1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        j = amp * math.sin(i * 0.37) + float(rng.normal(0, amp * 0.35))
        out[i, 0] += nx * j
        out[i, 1] += ny * j * 0.85
    return out


def simplify_line(pts: np.ndarray, step=3) -> np.ndarray:
    if len(pts) <= step:
        return pts
    idx = list(range(0, len(pts), step))
    if idx[-1] != len(pts) - 1:
        idx.append(len(pts) - 1)
    return pts[idx]


def parchment_rgba(w, h, seed=1539):
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), dtype=np.float32)
    base[..., 0], base[..., 1], base[..., 2] = 0.93, 0.87, 0.73
    base += rng.normal(0, 0.012, (h, w, 1)).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    rad = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    base *= (1.0 - 0.08 * np.clip(rad, 0, 1.2) ** 1.7)[..., None]
    return Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8), "RGB").filter(
        ImageFilter.GaussianBlur(0.5)
    )


def build_sepia_land_layer(sat_path: Path, coasts) -> np.ndarray:
    sat = np.asarray(Image.open(sat_path).convert("RGB")).astype(np.float32)
    h, w = sat.shape[:2]
    r, g, b = sat[:, :, 0], sat[:, :, 1], sat[:, :, 2]
    sea_col = ((b > g + 6) & (b > r + 8) & (b > 35)) | ((b > 100) & (g > r + 5) & (b > r + 25))

    pts = []
    for c in coasts:
        for x, y in c:
            if MAP_LON[0] - 0.4 <= x <= MAP_LON[1] + 0.4 and MAP_LAT[0] - 0.4 <= y <= MAP_LAT[1] + 0.4:
                pts.append((float(x), float(y)))
    sea_geo = np.zeros((h, w), dtype=bool)
    if pts:
        arr = np.array(pts)
        order = np.argsort(arr[:, 1])
        clat, clon = arr[order, 1], arr[order, 0]
        # remove duplicate lats for interp
        uniq = np.concatenate([[True], np.diff(clat) > 1e-6])
        clat, clon = clat[uniq], clon[uniq]
        yy, xx = np.mgrid[0:h, 0:w]
        lons = MAP_LON[0] + (xx + 0.5) / w * (MAP_LON[1] - MAP_LON[0])
        lats = MAP_LAT[1] - (yy + 0.5) / h * (MAP_LAT[1] - MAP_LAT[0])
        coast_lon = np.interp(lats, clat, clon, left=clon[0], right=clon[-1])
        sea_geo = lons > (coast_lon + 0.015)

    sea = sea_col | (sea_geo & ((b > r - 5) | (b > 60)))
    m = Image.fromarray(sea.astype(np.uint8) * 255)
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(7))
    m = m.filter(ImageFilter.MaxFilter(5))  # eat dark fringe into sea
    m = m.filter(ImageFilter.GaussianBlur(2.0))
    sea_soft = np.asarray(m).astype(np.float32) / 255.0
    land_a = np.clip(1.0 - sea_soft, 0, 1)

    tr = np.clip(0.393 * r + 0.769 * g + 0.189 * b, 0, 255)
    tg = np.clip(0.349 * r + 0.686 * g + 0.168 * b, 0, 255)
    tb = np.clip(0.272 * r + 0.534 * g + 0.131 * b, 0, 255)
    sep = np.stack([tr, tg, tb], axis=-1)
    wash = np.array([238.0, 222.0, 188.0], dtype=np.float32)
    sep = np.clip(sep * 0.90 + wash * 0.10, 0, 255)
    sep = np.clip(sep * 1.06 + 6, 0, 255)
    return np.dstack([sep, land_a * 255]).astype(np.uint8)


def photo_cutout_shadow(sp: str, size: int = 720) -> Image.Image:
    slug = sp.replace(" ", "_").lower()
    src = RECORTES / f"{slug}_cutout.png"
    if not src.exists():
        src = RECORTES / f"{slug}_cutout_raw.png"
    if not src.exists():
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse((60, 100, size - 60, size - 100), fill=(200, 180, 140, 255))
        return im

    rgba = Image.open(src).convert("RGBA")
    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)

    work = size
    pad = int(work * 0.11)
    bw, bh = rgba.size
    scale = min((work - 2 * pad) / bw, (work - 2 * pad) / bh)
    nw, nh = max(1, int(bw * scale)), max(1, int(bh * scale))
    rgba = rgba.resize((nw, nh), Image.Resampling.LANCZOS)

    r, g, b, a = rgba.split()
    a = a.point(lambda p: 255 if p > 48 else 0)
    # Erode fringe (kills pale halo) then light feather
    a = a.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(3))
    a = a.filter(ImageFilter.GaussianBlur(0.35))
    rgb = ImageEnhance.Contrast(Image.merge("RGB", (r, g, b))).enhance(1.12)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.40)
    rgb = ImageEnhance.Color(rgb).enhance(1.10)
    rgba = Image.merge("RGBA", (*rgb.split(), a))

    canvas = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    ox, oy = (work - nw) // 2, (work - nh) // 2 - int(work * 0.02)

    shadow = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    sh_a = a.point(lambda p: int(p * 0.35) if p > 0 else 0)
    sh_layer = Image.merge(
        "RGBA",
        (
            Image.new("L", (nw, nh), 30),
            Image.new("L", (nw, nh), 22),
            Image.new("L", (nw, nh), 14),
            sh_a,
        ),
    )
    shadow.paste(sh_layer, (ox + int(work * 0.015), oy + int(work * 0.022)), sh_layer)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(7, work // 65)))
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.paste(rgba, (ox, oy), rgba)
    return canvas


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
    for i, alpha in enumerate((0.12, 0.08, 0.05)):
        ax.add_patch(
            Rectangle(
                (MAP_LON[0] + 0.12 * i, MAP_LAT[0]),
                MAP_LON[1] - MAP_LON[0],
                MAP_LAT[1] - MAP_LAT[0],
                facecolor=SEA_DEEP,
                edgecolor="none",
                alpha=alpha,
                zorder=0.2,
            )
        )

    # coast_x helper
    coast_pts = []
    for c in coasts:
        for x, y in c:
            if MAP_LON[0] <= x <= MAP_LON[1] and MAP_LAT[0] <= y <= MAP_LAT[1]:
                coast_pts.append((x, y))

    def coast_x(lat):
        if not coast_pts:
            return 1.5
        return min(coast_pts, key=lambda p: abs(p[1] - lat))[0]

    lons = np.linspace(MAP_LON[0], MAP_LON[1], 180)
    for i, lat in enumerate(np.linspace(MAP_LAT[0] + 0.025, MAP_LAT[1] - 0.025, 110)):
        cx = coast_x(lat)
        amp = 0.008 + 0.0045 * math.sin(i * 0.5)
        ys = lat + amp * np.sin(lons * 13.0 + i * 0.38)
        mask = lons > cx + 0.04
        if mask.sum() < 8:
            continue
        ax.plot(
            lons[mask],
            ys[mask],
            color=INK,
            lw=0.55,
            alpha=0.38,
            solid_capstyle="round",
            zorder=1,
        )

    # few small whirlpools only (open sea)
    rng = random.Random(42)
    for _ in range(4):
        cx = rng.uniform(2.6, 3.25)
        cy = rng.uniform(40.75, 41.5)
        if cx < coast_x(cy) + 0.25:
            continue
        for rad in np.linspace(0.02, 0.07, 3):
            t = np.linspace(0, 2.0 * math.pi, 40)
            ax.plot(
                cx + rad * np.cos(t) * 1.2,
                cy + rad * np.sin(t) * 0.6,
                color=INK,
                lw=0.45,
                alpha=0.35,
                zorder=2,
            )


def draw_rhumb(ax):
    for hx, hy in [(2.60, 41.10)]:
        for ang in np.arange(0, 360, 22.5):
            rad = math.radians(ang)
            ax.plot(
                [hx, hx + 1.4 * math.cos(rad)],
                [hy, hy + 0.85 * math.sin(rad)],
                color=INK,
                lw=0.2,
                alpha=0.09,
                zorder=0.5,
            )


def draw_coastline_only(ax, coasts):
    """Only NE coastline — never province borders."""
    for i, c in enumerate(coasts):
        pts = c[
            (c[:, 0] >= MAP_LON[0] - 0.2)
            & (c[:, 0] <= MAP_LON[1] + 0.2)
            & (c[:, 1] >= MAP_LAT[0] - 0.2)
            & (c[:, 1] <= MAP_LAT[1] + 0.2)
        ]
        if len(pts) < 6:
            continue
        pts = simplify_line(pts, step=2)
        pts = hand_jitter(pts, amp=0.002, seed=2000 + i)
        ax.plot(pts[:, 0], pts[:, 1], color=LAND_EDGE, lw=1.9, solid_capstyle="round", zorder=6)
        ax.plot(pts[:, 0], pts[:, 1], color=RED_ACCENT, lw=0.7, alpha=0.5, zorder=7)


def draw_ship(ax, x, y, scale=1.0, kind="cog"):
    s = 0.045 * scale
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


def _fleur_de_lis(ax, cx, cy, s, z=46):
    petal = np.array(
        [
            [cx, cy + 1.15 * s],
            [cx - 0.22 * s, cy + 0.55 * s],
            [cx - 0.12 * s, cy + 0.15 * s],
            [cx, cy + 0.35 * s],
            [cx + 0.12 * s, cy + 0.15 * s],
            [cx + 0.22 * s, cy + 0.55 * s],
        ]
    )
    ax.add_patch(Polygon(petal, closed=True, facecolor=RED_ACCENT, edgecolor=INK, lw=0.7, zorder=z))
    for sx in (-1, 1):
        side = np.array(
            [
                [cx + sx * 0.08 * s, cy + 0.45 * s],
                [cx + sx * 0.55 * s, cy + 0.75 * s],
                [cx + sx * 0.48 * s, cy + 0.35 * s],
                [cx + sx * 0.22 * s, cy + 0.20 * s],
            ]
        )
        ax.add_patch(Polygon(side, closed=True, facecolor=GOLD, edgecolor=INK, lw=0.55, zorder=z))
    ax.add_patch(
        Rectangle((cx - 0.28 * s, cy + 0.02 * s), 0.56 * s, 0.12 * s, facecolor=INK, edgecolor=INK, lw=0.4, zorder=z + 0.5)
    )
    base = np.array(
        [
            [cx - 0.10 * s, cy + 0.05 * s],
            [cx - 0.18 * s, cy - 0.35 * s],
            [cx, cy - 0.15 * s],
            [cx + 0.18 * s, cy - 0.35 * s],
            [cx + 0.10 * s, cy + 0.05 * s],
        ]
    )
    ax.add_patch(Polygon(base, closed=True, facecolor=RED_ACCENT, edgecolor=INK, lw=0.55, zorder=z))


def draw_compass(ax, cx, cy, r=0.155):
    """32-point portolan rose with fleur-de-lis at north — must fit inside frame."""
    ax.add_patch(Circle((cx, cy), r * 1.42, facecolor=CREAM, edgecolor=INK, lw=1.7, zorder=40, alpha=0.97))
    ax.add_patch(Circle((cx, cy), r * 1.34, facecolor="none", edgecolor=GOLD, lw=1.0, zorder=41))
    ax.add_patch(Circle((cx, cy), r * 1.26, facecolor="none", edgecolor=RED_ACCENT, lw=0.65, zorder=41))

    yscale = 0.72  # visual equal-aspect compensation for lat/lon
    for i in range(32):
        ang = math.radians(90 - i * 11.25)
        if i % 8 == 0:
            r1 = r * 1.10
        elif i % 4 == 0:
            r1 = r * 0.92
        elif i % 2 == 0:
            r1 = r * 0.74
        else:
            r1 = r * 0.55
        r0 = r * 0.16
        perp = ang + math.pi / 2
        half = r * (0.052 if i % 8 == 0 else 0.036 if i % 4 == 0 else 0.026)
        tip = (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang) * yscale)
        base = (cx + r0 * math.cos(ang), cy + r0 * math.sin(ang) * yscale)
        mid = r0 + (r1 - r0) * 0.38
        left = (cx + mid * math.cos(ang) + half * math.cos(perp), cy + mid * math.sin(ang) * yscale + half * math.sin(perp) * yscale)
        right = (cx + mid * math.cos(ang) - half * math.cos(perp), cy + mid * math.sin(ang) * yscale - half * math.sin(perp) * yscale)
        if i % 8 == 0:
            ax.add_patch(Polygon([tip, left, base], closed=True, facecolor=RED_ACCENT, edgecolor=INK, lw=0.35, zorder=42))
            ax.add_patch(Polygon([tip, right, base], closed=True, facecolor=CREAM, edgecolor=INK, lw=0.35, zorder=42))
        else:
            col = GOLD if i % 4 == 0 else (INK_SOFT if i % 2 == 0 else "#8a7355")
            ax.add_patch(Polygon([tip, left, base, right], closed=True, facecolor=col, edgecolor=INK, lw=0.28, zorder=42))

    ax.add_patch(Circle((cx, cy), r * 0.30, facecolor=CREAM, edgecolor=INK, lw=1.0, zorder=43))
    ax.add_patch(Circle((cx, cy), r * 0.20, facecolor=GOLD, edgecolor=INK, lw=0.75, zorder=44))
    ax.add_patch(Circle((cx, cy), r * 0.07, facecolor=INK, zorder=45))
    # Fleur fully inside outer disk
    _fleur_de_lis(ax, cx, cy + r * 1.05 * yscale, s=r * 0.22, z=46)

    for lab, ang_deg in [("E", 0), ("S", 270), ("O", 180)]:
        rad = math.radians(ang_deg)
        ax.text(
            cx + (r * 1.20) * math.cos(rad),
            cy + (r * 1.20) * yscale * math.sin(rad),
            lab,
            ha="center",
            va="center",
            fontproperties=_serif(7.2, "bold"),
            color=INK,
            zorder=47,
            path_effects=_stroke(1.6, CREAM),
        )
    ax.text(
        cx,
        cy - r * 1.48 * yscale,
        "Rosa ventorum",
        ha="center",
        va="top",
        fontproperties=_serif(5.0),
        color=INK_SOFT,
        zorder=47,
    )


def draw_wind_face(ax, x, y, label, blow_ang_deg, scale=1.0):
    s = 0.072 * scale
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
    ax.add_patch(Ellipse((x + 0.05 * s, y - 0.08 * s), 0.18 * s, 0.12 * s, facecolor=INK, zorder=37))
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
        path_effects=_stroke(1.6, CREAM),
    )


def draw_friendly_monster(ax, x, y, scale=1.0):
    s = 0.062 * scale
    t = np.linspace(0, 2.2 * math.pi, 80)
    xs = x + 0.55 * s * t * np.cos(t)
    ys = y + 0.35 * s * t * np.sin(t)
    ax.plot(xs, ys, color="#2d6a4f", lw=5.0, solid_capstyle="round", zorder=12, alpha=0.9)
    ax.plot(xs, ys, color=INK, lw=1.0, alpha=0.5, zorder=13)
    hx, hy = xs[-1], ys[-1]
    ax.add_patch(
        Ellipse((hx + 0.15 * s, hy), 0.7 * s, 0.5 * s, facecolor="#40916c", edgecolor=INK, lw=1.0, zorder=14)
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
        path_effects=_stroke(1.5, CREAM),
    )


def draw_ornate_frame(ax):
    x0, x1 = MAP_LON[0] + 0.03, MAP_LON[1] - 0.03
    y0, y1 = MAP_LAT[0] + 0.03, MAP_LAT[1] - 0.03
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=INK, lw=2.6, zorder=60))
    ax.add_patch(
        Rectangle(
            (x0 + 0.035, y0 + 0.035),
            x1 - x0 - 0.07,
            y1 - y0 - 0.07,
            fill=False,
            edgecolor=RED_ACCENT,
            lw=0.85,
            zorder=60,
        )
    )
    for cx, cy, sx, sy in [
        (x0 + 0.08, y0 + 0.08, 1, 1),
        (x1 - 0.08, y0 + 0.08, -1, 1),
        (x0 + 0.08, y1 - 0.08, 1, -1),
        (x1 - 0.08, y1 - 0.08, -1, -1),
    ]:
        t = np.linspace(0, 1.5 * math.pi, 45)
        ax.plot(
            cx + sx * 0.055 * np.cos(t) * t,
            cy + sy * 0.055 * np.sin(t) * t,
            color=GOLD,
            lw=1.3,
            zorder=61,
        )


def draw_species_photo(ax, name, x, y, scale, label_off=(0.0, -0.05)):
    eng = photo_cutout_shadow(name, size=720)
    w = 0.40 * scale
    h = 0.31 * scale
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
        fontproperties=_serif(5.8, "bold"),
        color=INK,
        style="italic",
        zorder=45,
        bbox=dict(boxstyle="round,pad=0.14", facecolor=CREAM, edgecolor=INK, linewidth=0.65, alpha=0.96),
        clip_on=True,
    )


def draw_calendar_fig(fig, peaks: dict[str, str]):
    ax = fig.add_axes([0.038, 0.36, 0.148, 0.50])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(CREAM)
    for sp in ax.spines.values():
        sp.set_color(INK)
        sp.set_linewidth(1.6)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.add_patch(Rectangle((0.03, 0.03), 0.94, 0.94, fill=False, edgecolor=RED_ACCENT, lw=0.9, zorder=2))
    ax.text(0.5, 0.955, "Calendarium · Menses culminis", ha="center", va="top", fontproperties=_serif(6.5, "bold"), color=INK, zorder=3)
    ax.plot([0.08, 0.92], [0.905, 0.905], color=INK, lw=0.7, zorder=3)
    for i, (sp, pico) in enumerate(peaks.items()):
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
    ax = fig.add_axes([0.36, 0.908, 0.30, 0.062])
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
    # Bottom margin, left of compass — avoid overlap with rose
    ax = fig.add_axes([0.42, 0.042, 0.18, 0.068])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(CREAM)
    for sp in ax.spines.values():
        sp.set_color(INK)
        sp.set_linewidth(1.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.add_patch(Rectangle((0.04, 0.08), 0.92, 0.84, fill=False, edgecolor=RED_ACCENT, lw=0.8))
    ax.text(0.5, 0.78, "Scala · leugae", ha="center", va="center", fontproperties=_serif(6.2, "bold"), color=INK)
    x0, x1, yb = 0.12, 0.88, 0.32
    seg = (x1 - x0) / 4
    for i in range(4):
        ax.add_patch(
            Rectangle((x0 + i * seg, yb), seg, 0.22, facecolor=INK if i % 2 == 0 else CREAM, edgecolor=INK, lw=0.5)
        )
    ax.text(x0, 0.18, "0", ha="center", fontproperties=_serif(5), color=INK)
    ax.text(x1, 0.18, "10", ha="center", fontproperties=_serif(5), color=INK)


def build_poster():
    if not SAT_MAP.exists():
        raise SystemExit(f"Falta satélite: {SAT_MAP}")

    coasts, lands = load_ne()
    peaks = {sp: pico for sp, _, _, _, pico, *_ in SPECIES}
    if MONTHLY.exists():
        with MONTHLY.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["especie"] in peaks:
                    peaks[row["especie"]] = row["pico_mes_suavizado"]

    print("satélite sepia…", flush=True)
    land_rgba = build_sepia_land_layer(SAT_MAP, coasts)

    print("fotos reales…", flush=True)
    for sp, *_ in SPECIES:
        photo_cutout_shadow(sp)
        print(f"  {sp}", flush=True)

    fig = plt.figure(figsize=(A3_W_IN, A3_H_IN), dpi=DPI, facecolor=PARCHMENT)
    left = MARGIN_IN / A3_W_IN
    right = MARGIN_IN / A3_W_IN
    bottom = (MARGIN_IN + 0.18) / A3_H_IN
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
    ax.imshow(
        land_rgba,
        extent=[MAP_LON[0], MAP_LON[1], MAP_LAT[0], MAP_LAT[1]],
        origin="upper",
        zorder=3,
        interpolation="bilinear",
        aspect="auto",
    )
    draw_coastline_only(ax, coasts)

    for lon, lat, name in PLACES:
        ax.text(
            lon,
            lat,
            name,
            ha="center",
            va="center",
            fontproperties=_serif(6.8, "bold"),
            color=INK,
            zorder=25,
            path_effects=_stroke(2.4, CREAM),
        )

    for sx, sy, sc, kind in [
        (3.18, 40.88, 0.95, "galleon"),
        (3.25, 41.20, 0.85, "cog"),
        (1.15, 40.78, 0.88, "galley"),
        (2.55, 40.68, 0.82, "cog"),
        (1.70, 40.66, 0.90, "galleon"),
        (3.12, 41.02, 0.75, "galley"),
    ]:
        draw_ship(ax, sx, sy, scale=sc, kind=kind)

    for name, _zone, (px, py), sc, _pico, lab_off in SPECIES:
        draw_species_photo(ax, name, px, py, sc, label_off=lab_off)

    draw_wind_face(ax, 2.20, 42.38, "Tramontana", blow_ang_deg=270, scale=1.05)
    draw_wind_face(ax, 3.25, 41.58, "Llevant", blow_ang_deg=200, scale=0.92)
    draw_wind_face(ax, 1.40, 40.66, "Garbí", blow_ang_deg=50, scale=0.92)
    draw_wind_face(ax, 0.82, 41.70, "Mestral", blow_ang_deg=320, scale=0.82)
    draw_friendly_monster(ax, 3.18, 41.48, scale=0.95)
    # Compass fully inside frame (inner ≈ 0.58–3.42, 40.55–42.52)
    draw_compass(ax, 2.72, 40.82, r=0.130)

    ax.annotate(
        "Cap de Creus",
        xy=(3.25, 42.26),
        xytext=(3.10, 42.42),
        fontproperties=_serif(6.5, "bold"),
        color=RED_ACCENT,
        arrowprops=dict(arrowstyle="->", color=RED_ACCENT, lw=0.9),
        zorder=40,
        path_effects=_stroke(2.0, CREAM),
    )
    ax.annotate(
        "Delta de l'Ebre",
        xy=(0.88, 40.72),
        xytext=(1.25, 40.60),
        fontproperties=_serif(6.5, "bold"),
        color=RED_ACCENT,
        arrowprops=dict(arrowstyle="->", color=RED_ACCENT, lw=0.9),
        zorder=40,
        path_effects=_stroke(2.0, CREAM),
    )
    draw_ornate_frame(ax)

    draw_title_fig(fig)
    draw_calendar_fig(fig, peaks)
    draw_scale_fig(fig)

    credit = (
        "Carta marina híbrida · mar estilo Olaus Magnus 1539 (dominio público). "
        "Tierra: Sentinel-2 cloudless © EOX (s2maps.eu), CC BY 4.0 "
        "(Contains modified Copernicus Sentinel data). "
        "Nudibranquios: fotos reales CC (lámina 4). Datos: iNaturalist + Minka · BioFauna · 2026"
    )
    fig.text(0.5, 0.010, credit, ha="center", va="bottom", fontproperties=_serif(5.0), color="#4a3a28")

    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)

    map_img = Image.fromarray(rgba[:, :, :3], "RGB")
    parch = parchment_rgba(w, h)
    map_a = np.asarray(map_img).astype(np.float32) / 255.0
    parch_a = np.asarray(parch).astype(np.float32) / 255.0
    blended = np.clip(map_a * 0.92 + parch_a * 0.08, 0, 1)
    out = Image.fromarray((blended * 255).astype(np.uint8), "RGB")
    out = ImageEnhance.Contrast(out).enhance(1.05)
    out = ImageEnhance.Color(out).enhance(0.97)

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT_PNG, "PNG", dpi=(DPI, DPI), compress_level=5)
    out.save(OUT_PDF, "PDF", resolution=DPI)

    OUT_SVG.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">
  <title>Nudibranchia Cataloniae — Carta Marina híbrida</title>
  <desc>Lámina 5 híbrida · PNG/PDF 300 ppp. Script nudibranquios_lamina5_hibrida_20261011.py</desc>
  <rect width="420" height="297" fill="#e8d9b8"/>
  <text x="210" y="145" text-anchor="middle" font-family="DejaVu Serif" font-size="14" fill="#1a120c">Nudibranchia Cataloniae · Hic sunt nudibranchia</text>
  <text x="210" y="165" text-anchor="middle" font-family="DejaVu Serif" font-size="8" fill="#6b3a28">Imprimible: LAMINA5_carta_marina_20261010.png / .pdf (A3 · 300 ppp)</text>
</svg>
""",
        encoding="utf-8",
    )

    sat_meta = json.loads(SAT_META.read_text(encoding="utf-8")) if SAT_META.exists() else {}
    meta = {
        "style": "carta_marina_hibrida_satelite_eox",
        "script": "nudibranquios_lamina5_hibrida_20261011.py",
        "orientation": "A3_landscape",
        "dpi": DPI,
        "size_mm": [420, 297],
        "bbox_lon": list(MAP_LON),
        "bbox_lat": list(MAP_LAT),
        "land": "Sentinel-2 cloudless EOX CC BY 4.0 sepia/parchment",
        "sea": "Carta Marina engraved waves",
        "creatures": "real photo cutouts with soft shadow (no woodcut)",
        "compass": "32-point portolan rose + fleur-de-lis north",
        "places": "calligraphy labels only",
        "satellite_meta": sat_meta,
        "species_n": len(SPECIES),
        "species": [
            {"species": n, "placement": [px, py], "peak": peaks[n], "scale": sc}
            for n, _, (px, py), sc, _, _off in SPECIES
        ],
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S CEST"),
        "png": OUT_PNG.name,
        "pdf": OUT_PDF.name,
        "pixels": list(out.size),
    }
    META_JSON.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    (MAT / "LICENCIAS_POSTER_LAMINA5.md").write_text(
        "\n".join(
            [
                "# Póster A3 — Lámina 5 Carta Marina híbrida",
                f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} CEST",
                "",
                "Mar y ornamentos inspirados en la Carta Marina de Olaus Magnus, 1539 (dominio público).",
                "Tierra: Sentinel-2 cloudless — https://s2maps.eu by EOX IT Services GmbH "
                "(Contains modified Copernicus Sentinel data), licencia **CC BY 4.0**.",
                "Nudibranquios: fotografías reales recortadas (fuentes CC lámina 4), sombra suave.",
                "Rosa de los vientos: portulana de 32 puntas con flor de lis al norte.",
                "Topónimos: caligrafía sobre satélite (sin iconos de pueblo).",
                "Script: `scripts/nudibranquios_lamina5_hibrida_20261011.py`.",
                "",
                "## Especies",
                "",
            ]
            + [f"- *{n}* · pico {peaks[n]}" for n, *_ in SPECIES]
            + [""]
        ),
        encoding="utf-8",
    )
    # Touch LEEME to note new approach
    (MAT / "LEEME_ADDENDUM_LAMINA5.txt").write_text(
        "CAMBIO DE ENFOQUE Gustavo 11-oct-2026: carta marina HÍBRIDA "
        "(satélite sepia EOX + mar Carta Marina + fotos reales nudibranquios + rosa portulana). "
        "Anula el enfoque de grabado woodcut. Script: nudibranquios_lamina5_hibrida_20261011.py\n",
        encoding="utf-8",
    )
    print(f"OK {OUT_PNG} {out.size[0]}x{out.size[1]} @ {DPI}ppi")
    print(f"OK {OUT_PDF}")
    return out


if __name__ == "__main__":
    build_poster()
