#!/usr/bin/env python3
"""Póster A3 estilo museo/película — nudibranquios comunes de Cataluña.

Fondo negro abisal · recortes sobre negro con halo · mapa Sentinel-2 cloudless
(EOX, CC BY 4.0) como pieza central · zonas calientes luminosas · tipografía serif.
300 ppp. Sin GPU.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import patheffects as pe
from matplotlib.font_manager import FontProperties
from matplotlib.patches import ConnectionPatch
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
FOTOS = PAPER / "fotos"
FOTOS_LG = PAPER / "fotos_poster"
RECORTES = PAPER / "recortes"
COAST = PAPER / "datos/coast-western-med.geojson"
META_JSON = PAPER / "datos/fotos_meta_20261010.json"
MONTHLY = PAPER / "datos/especies_mensual_normalizado_20261010.csv"
ZONES_CSV = PAPER / "datos/zonas_calientes_normalizado_20261010.csv"
SAT_MAP = PAPER / "datos/mapa_satelite_catalunya_s2cloudless.jpg"
SAT_META = PAPER / "datos/mapa_satelite_catalunya_s2cloudless_meta.json"

# Encuadre satélite (debe coincidir con el mosaico descargado)
MAP_LAT = (40.52, 42.55)
MAP_LON = (0.55, 3.45)
CAT_LAT = (40.45, 42.95)
CAT_LON = (0.10, 3.40)
MED_LAT = (35.0, 45.5)
MED_LON = (-6.0, 16.0)

LICENSE_OK = re.compile(r"^(cc0|cc-by|cc-by-sa)(-[0-9.]+)?$", re.I)
USER_AGENT = "BioFaunaNudibranchPoster/2026-10 (yespi.es; educational; contact gustavo.zafra@gmail.com)"
MES = ["G", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
MES_KEYS = [
    "suav_Enero",
    "suav_Febrero",
    "suav_Marzo",
    "suav_Abril",
    "suav_Mayo",
    "suav_Junio",
    "suav_Julio",
    "suav_Agosto",
    "suav_Septiembre",
    "suav_Octubre",
    "suav_Noviembre",
    "suav_Diciembre",
]

# Solo nombres comunes asentados en guías/divulgación local — no inventar.
VERNACULAR: dict[str, tuple[str, str] | None] = {
    "Peltodoris atromaculata": ("Vaqueta suïssa", "Vaquita suiza"),
    "Flabellina affinis": ("Flabel·lina violeta", "Flabelina violeta"),
}

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

FALLBACK_ZONES = ["Maresme", "Garraf", "Costa Daurada N", "Tossa–Blanes"]

BG = "#020508"
ABYSS = "#050c14"
GOLD = "#d4b87a"
CREAM = "#e8e0d0"
MUTED = "#8a9aaa"
GLOW = "#7ec8e3"

FONT_SERIF = FontProperties(fname="/usr/share/fonts/truetype/freefont/FreeSerif.ttf")
FONT_SERIF_B = FontProperties(fname="/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf")
FONT_SERIF_I = FontProperties(fname="/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf")
FONT_SERIF_BI = FontProperties(fname="/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf")
FONT_SANS = FontProperties(fname="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def http_json(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except Exception:
        return None


def http_bytes(url: str, timeout: int = 40) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception:
        return None


def ok_license(lic: str) -> bool:
    s = (lic or "").strip().lower().replace("_", "-")
    if "nc" in s or "nd" in s:
        return False
    return bool(LICENSE_OK.match(s)) or s in {"cc0", "cc-by", "cc-by-sa"}


def load_top(n: int = 16) -> list[dict]:
    rows = []
    with MONTHLY.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            vals = [float(row[k]) for k in MES_KEYS]
            rows.append(
                {
                    "species": row["especie"],
                    "family": row["familia"],
                    "total": int(row["total_obs"]),
                    "months": np.array(vals, dtype=float),
                    "peak": row["pico_mes_suavizado"],
                }
            )
            if len(rows) >= n:
                break
    return rows


def load_hot_zone(species: list[str]) -> dict[str, str]:
    best: dict[str, tuple[float, str]] = {}
    with ZONES_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sp = row["especie"]
            if sp not in species:
                continue
            tasa = float(row["tasa"])
            if sp not in best or tasa > best[sp][0]:
                best[sp] = (tasa, row["tramo"])
    return {sp: z for sp, (_, z) in best.items()}


def catalog_taxon_ids() -> dict[str, dict]:
    cat = {s["name"]: s for s in json.load(open(ROOT / "dataset/catalog.json"))["species"]}
    out = {}
    for name, s in cat.items():
        out[name] = {"inat": s.get("inat_taxon"), "minka": s.get("minka_taxon")}
    return out


def _inat_search(tid: int, bbox=None) -> list[dict]:
    params = {
        "taxon_id": tid,
        "quality_grade": "research",
        "photos": "true",
        "per_page": 30,
        "order_by": "votes",
    }
    if bbox:
        (la0, la1), (lo0, lo1) = bbox
        params.update({"swlat": la0, "swlng": lo0, "nelat": la1, "nelng": lo1})
    url = "https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(params)
    data = http_json(url)
    if not data:
        return []
    out = []
    for obs in data.get("results") or []:
        lic = (obs.get("license_code") or "").lower()
        if not ok_license(lic):
            continue
        photos = obs.get("photos") or []
        if not photos:
            continue
        purl = (photos[0].get("url") or "").replace("square", "large").replace("medium", "large")
        if not purl:
            continue
        out.append(
            {
                "url": purl,
                "author": (obs.get("user") or {}).get("name")
                or (obs.get("user") or {}).get("login")
                or "?",
                "license": lic,
                "date": (obs.get("observed_on") or "")[:10],
                "place": obs.get("place_guess") or "",
                "uri": obs.get("uri") or f"https://www.inaturalist.org/observations/{obs.get('id')}",
            }
        )
    return out


def _minka_search(mid: int | None, name: str) -> list[dict]:
    if mid:
        q = urllib.parse.urlencode({"taxon_id": mid, "quality_grade": "research", "per_page": 20})
    else:
        q = urllib.parse.urlencode({"q": name, "quality_grade": "research", "per_page": 20})
    data = http_json(f"https://minka-sdg.org/observations.json?{q}")
    if not data:
        return []
    results = data if isinstance(data, list) else (data.get("results") or [])
    out = []
    for obs in results:
        lic = (obs.get("license_code") or obs.get("license") or "").lower()
        if not ok_license(lic):
            continue
        photos = obs.get("photos") or []
        if not photos:
            continue
        purl = photos[0].get("large_url") or photos[0].get("url") or ""
        purl = purl.replace("square", "large").replace("medium", "large")
        if not purl:
            continue
        user = obs.get("user") or {}
        out.append(
            {
                "url": purl,
                "author": user.get("name") or user.get("login") or "?",
                "license": lic,
                "date": (obs.get("observed_on") or "")[:10],
                "place": obs.get("place_guess") or "",
                "uri": obs.get("uri") or f"https://minka-sdg.org/observations/{obs.get('id')}",
            }
        )
    return out


def credits_from_recortes(sp: str) -> dict:
    meta_p = RECORTES / "meta_recortes_20261010.json"
    if not meta_p.exists():
        return {}
    try:
        for it in json.loads(meta_p.read_text(encoding="utf-8")).get("items") or []:
            if it.get("species") == sp and it.get("author"):
                return {
                    "author": it.get("author") or "?",
                    "license": it.get("license") or "",
                    "uri": it.get("uri") or "",
                }
    except Exception:
        pass
    return {}


def ensure_large_photo(sp: str, prev: dict, taxa: dict) -> dict:
    FOTOS_LG.mkdir(parents=True, exist_ok=True)
    slug = sp.replace(" ", "_").lower()
    dest = FOTOS_LG / f"{slug}_large.jpg"
    thumb = FOTOS / f"{slug}_thumb.jpg"

    def entry(path: Path, meta: dict, source: str) -> dict:
        return {
            "species": sp,
            "path": path,
            "author": meta.get("author") or "?",
            "license": meta.get("license") or "",
            "date": meta.get("date") or "",
            "place": meta.get("place") or "",
            "uri": meta.get("uri") or "",
            "source": source,
        }

    if dest.exists() and dest.stat().st_size > 20000:
        meta = {**prev, **credits_from_recortes(sp)}
        return entry(dest, meta, "cache_large")

    tid = (taxa.get(sp) or {}).get("inat")
    mid = (taxa.get(sp) or {}).get("minka")
    for bbox in [(CAT_LAT, CAT_LON), (MED_LAT, MED_LON), None]:
        if tid:
            cands = _inat_search(int(tid), bbox)
            time.sleep(0.4)
            for c in cands[:4]:
                blob = http_bytes(c["url"])
                if blob and len(blob) > 15000:
                    dest.write_bytes(blob)
                    return entry(dest, c, "inat_large")
    if mid:
        cands = _minka_search(int(mid), sp)
        time.sleep(0.4)
        for c in cands[:4]:
            blob = http_bytes(c["url"])
            if blob and len(blob) > 15000:
                dest.write_bytes(blob)
                return entry(dest, c, "minka_large")

    if thumb.exists() and thumb.stat().st_size > 8000:
        dest.write_bytes(thumb.read_bytes())
        return entry(dest, prev, "thumb_fallback")

    raise FileNotFoundError(f"Sin foto CC para {sp}")


def cutout_path(sp: str) -> Path | None:
    p = RECORTES / f"{sp.replace(' ', '_').lower()}_cutout.png"
    return p if p.exists() and p.stat().st_size > 8000 else None


def museum_rgba(path: Path, size: tuple[int, int]) -> np.ndarray:
    """Recorte centrado + contraste/saturación + halo suave (estudio museo)."""
    tw, th = size
    im = Image.open(path).convert("RGBA")
    rgb = im.convert("RGB")
    alpha = im.split()[-1]
    rgb = ImageEnhance.Color(rgb).enhance(1.28)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.18)
    rgb = ImageEnhance.Brightness(rgb).enhance(1.06)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.15)
    im = Image.merge("RGBA", (*rgb.split(), alpha))

    w, h = im.size
    scale = min(tw / w, th / h) * 0.94
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)

    # Halo: blur de alpha tintado (brillo de estudio)
    glow_a = im.split()[-1].filter(ImageFilter.GaussianBlur(radius=max(10, min(nw, nh) // 14)))
    glow_rgb = Image.new("RGB", (nw, nh), (110, 190, 220))
    glow = Image.merge("RGBA", (*glow_rgb.split(), glow_a.point(lambda a: int(a * 0.55))))

    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ox, oy = (tw - nw) // 2, (th - nh) // 2
    gw, gh = int(nw * 1.14), int(nh * 1.14)
    glow_big = glow.resize((gw, gh), Image.Resampling.LANCZOS)
    canvas.paste(glow_big, (ox - (gw - nw) // 2, oy - (gh - nh) // 2), glow_big)
    canvas.paste(im, (ox, oy), im)
    return np.asarray(canvas)


def load_species_image(sp: str, path: Path, size: tuple[int, int]) -> np.ndarray:
    cp = cutout_path(sp)
    if cp is not None:
        return museum_rgba(cp, size)
    # fallback rectangular con viñeta negra
    im = Image.open(path).convert("RGB")
    tw, th = size
    w, h = im.size
    scale = max(tw / w, th / h)
    nw, nh = int(w * scale), int(h * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    im = im.crop((left, top, left + tw, top + th))
    im = ImageEnhance.Color(im).enhance(1.2)
    im = ImageEnhance.Contrast(im).enhance(1.15)
    arr = np.asarray(im.convert("RGBA"))
    yy, xx = np.mgrid[0:th, 0:tw]
    cx, cy = tw / 2, th / 2
    r = np.sqrt(((xx - cx) / (tw * 0.48)) ** 2 + ((yy - cy) / (th * 0.48)) ** 2)
    arr[..., 3] = (np.clip(1.0 - r, 0, 1) * 255).astype(np.uint8)
    return arr


def draw_month_dots(ax, months: np.ndarray):
    """12 puntos brillantes discretos: intensidad = pico fenológico suavizado."""
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 1)
    ax.set_facecolor("none")
    ax.axis("off")
    for sp in ax.spines.values():
        sp.set_visible(False)
    peak = float(months.max()) if months.max() > 0 else 1.0
    for i, v in enumerate(months):
        t = float(np.clip(v / peak, 0, 1))
        r = 0.14 + 0.12 * t
        col = (0.25 + 0.55 * t, 0.65 + 0.3 * t, 0.9 + 0.1 * t, 0.18 + 0.82 * t)
        ax.add_patch(
            mpatches.Circle(
                (i + 0.5, 0.5),
                r,
                facecolor=col,
                edgecolor="none",
                zorder=2,
            )
        )
        if t > 0.75:
            ax.add_patch(
                mpatches.Circle(
                    (i + 0.5, 0.5),
                    r * 2.2,
                    facecolor=(0.55, 0.9, 1.0, 0.14 * t),
                    edgecolor="none",
                    zorder=1,
                )
            )


def _place_for_species(sp: str, hot: dict[str, str], fb_i: list[int]) -> str:
    z = hot.get(sp)
    if z:
        return z
    place = FALLBACK_ZONES[fb_i[0] % len(FALLBACK_ZONES)]
    fb_i[0] += 1
    return place


def build_poster(spp: list[dict], photos: dict[str, dict], hot: dict[str, str]):
    # A3 apaisado mm → inches (costa N–S como franja central)
    fig_w, fig_h = 16.54, 11.69
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=300, facecolor=BG)

    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis("off")
    # Gradiente abisal vertical (más profundo en bordes)
    for a in np.linspace(0, 1, 60):
        t = abs(a - 0.48)
        c = (0.012 + 0.018 * (1 - t), 0.028 + 0.05 * (1 - t), 0.05 + 0.07 * (1 - t), 1)
        ax_bg.add_patch(mpatches.Rectangle((0, a), 1, 1 / 60 + 0.002, facecolor=c, edgecolor="none"))

    # Título museo
    ax_bg.text(
        0.5,
        0.965,
        "Nudibranquis de Catalunya",
        fontsize=26,
        color=CREAM,
        fontproperties=FONT_SERIF_B,
        ha="center",
        va="center",
        zorder=3,
    )
    ax_bg.text(
        0.5,
        0.932,
        "Nudibranquios de Cataluña",
        fontsize=14,
        color=GOLD,
        fontproperties=FONT_SERIF_I,
        ha="center",
        va="center",
        zorder=3,
    )
    ax_bg.text(
        0.5,
        0.905,
        "Les 16 espècies més freqüents · Guia visual · BioFauna 2026",
        fontsize=7.2,
        color=MUTED,
        fontproperties=FONT_SANS,
        ha="center",
        va="center",
        zorder=3,
    )
    # línea dorada fina
    ax_bg.plot([0.22, 0.78], [0.888, 0.888], color=GOLD, lw=0.6, alpha=0.55, solid_capstyle="round")

    # ——— Mapa satélite central ———
    map_l, map_b, map_w, map_h = 0.348, 0.100, 0.304, 0.76
    ax_map = fig.add_axes([map_l, map_b, map_w, map_h], zorder=2)
    sat = np.asarray(Image.open(SAT_MAP).convert("RGB"))
    # Viñeta suave hacia negro en bordes del mapa
    sat_f = sat.astype(np.float32)
    hh, ww = sat_f.shape[:2]
    yy = np.linspace(0, 1, hh)[:, None]
    xx = np.linspace(0, 1, ww)[None, :]
    edge = np.minimum(np.minimum(xx, 1 - xx) / 0.08, np.minimum(yy, 1 - yy) / 0.06)
    edge = np.clip(edge, 0, 1)[..., None]
    sat_f = sat_f * (0.55 + 0.45 * edge)
    ax_map.imshow(
        sat_f.astype(np.uint8),
        extent=[MAP_LON[0], MAP_LON[1], MAP_LAT[0], MAP_LAT[1]],
        origin="upper",
        aspect="auto",
        zorder=1,
        interpolation="bilinear",
    )
    ax_map.set_xlim(MAP_LON[0], MAP_LON[1])
    ax_map.set_ylim(MAP_LAT[0], MAP_LAT[1])
    ax_map.set_xticks([])
    ax_map.set_yticks([])
    for spn in ax_map.spines.values():
        spn.set_color(GOLD)
        spn.set_linewidth(0.9)
        spn.set_alpha(0.5)

    # etiquetas de costa discretas
    labels = {
        "Cap de Creus": (3.05, 42.38),
        "Medes": (2.85, 42.08),
        "Barcelona": (1.75, 41.42),
        "Tarragona": (0.95, 41.12),
        "Delta de l'Ebre": (0.72, 40.68),
    }
    for name, (lo, la) in labels.items():
        t = ax_map.text(
            lo,
            la,
            name,
            fontsize=5.2,
            color=CREAM,
            ha="center",
            va="center",
            fontproperties=FONT_SANS,
            zorder=5,
            alpha=0.9,
        )
        t.set_path_effects([pe.withStroke(linewidth=2.0, foreground=(0, 0, 0, 0.75))])

    ax_map.text(
        0.5,
        0.015,
        "Sentinel-2 cloudless · EOX",
        transform=ax_map.transAxes,
        fontsize=4.8,
        color=(1, 1, 1, 0.55),
        ha="center",
        va="bottom",
        fontproperties=FONT_SANS,
        zorder=6,
    )

    # anclas por zona + marcadores luminosos
    zone_counts: dict[str, int] = defaultdict(int)
    marker_pos: dict[int, tuple[float, float]] = {}
    fb_i = [0]
    for i, s in enumerate(spp):
        place = _place_for_species(s["species"], hot, fb_i)
        k = zone_counts[place]
        zone_counts[place] += 1
        base = ZONE_XY.get(place, (2.2, 41.4))
        ang = k * 2.1 + i * 0.08
        r = 0.028 + 0.012 * k
        lo = base[0] + r * math.cos(ang)
        la = base[1] + r * math.sin(ang) * 0.7
        marker_pos[i] = (lo, la)
        # halo + punto
        ax_map.plot(lo, la, "o", markersize=14, color=(0.4, 0.85, 1.0, 0.18), markeredgewidth=0, zorder=6)
        ax_map.plot(
            lo,
            la,
            "o",
            markersize=7.5,
            color=(0.85, 0.95, 1.0, 0.95),
            markeredgecolor=GOLD,
            markeredgewidth=0.7,
            zorder=7,
        )
        ax_map.text(
            lo,
            la,
            str(i + 1),
            ha="center",
            va="center",
            fontsize=4.8,
            color="#0a1520",
            fontweight="bold",
            zorder=8,
            fontproperties=FONT_SANS,
        )

    # ——— Fichas especie (sin tarjeta blanca): 8 izq + 8 der ———
    # Márgenes impresión ≈ 12 mm (A3)
    left_col_x = 0.032
    right_col_x = 0.668
    col_w = 0.300
    row0_y = 0.085
    row_h = 0.093
    gap = 0.0055

    slot_xy: dict[int, tuple[float, float, float, float]] = {}

    for i, s in enumerate(spp):
        side = 0 if i < 8 else 1
        row = i if i < 8 else i - 8
        x = left_col_x if side == 0 else right_col_x
        y = row0_y + (7 - row) * (row_h + gap)
        slot_xy[i] = (x, y, col_w, row_h)

        ax_c = fig.add_axes([x, y, col_w, row_h], zorder=3)
        ax_c.set_xlim(0, 1)
        ax_c.set_ylim(0, 1)
        ax_c.axis("off")
        ax_c.set_facecolor("none")

        ax_c.text(
            0.02 if side == 0 else 0.98,
            0.90,
            str(i + 1),
            fontsize=7.2,
            color=GOLD,
            ha="left" if side == 0 else "right",
            va="center",
            fontproperties=FONT_SERIF_B,
            alpha=0.85,
        )

        # Imagen grande hacia el mapa; texto compacto al borde exterior
        if side == 0:
            img_box = [x + col_w * 0.30, y + row_h * 0.04, col_w * 0.68, row_h * 0.92]
            text_x = 0.03
            text_ha = "left"
            cal_box = [x + 0.008, y + 0.01, col_w * 0.27, row_h * 0.18]
        else:
            img_box = [x + col_w * 0.02, y + row_h * 0.04, col_w * 0.68, row_h * 0.92]
            text_x = 0.97
            text_ha = "right"
            cal_box = [x + col_w * 0.71, y + 0.01, col_w * 0.27, row_h * 0.18]

        ax_img = fig.add_axes(img_box, zorder=4)
        ax_img.set_facecolor("none")
        ax_img.imshow(load_species_image(s["species"], photos[s["species"]]["path"], (720, 540)))
        ax_img.set_xticks([])
        ax_img.set_yticks([])
        for spn in ax_img.spines.values():
            spn.set_visible(False)

        vern = VERNACULAR.get(s["species"])
        name_y = 0.58 if vern else 0.52
        ax_c.text(
            text_x,
            name_y,
            s["species"],
            fontsize=6.6,
            color=CREAM,
            fontproperties=FONT_SERIF_BI,
            ha=text_ha,
            va="center",
        )
        if vern:
            ca, es = vern
            ax_c.text(
                text_x,
                0.38,
                f"{ca}  ·  {es}",
                fontsize=4.3,
                color=MUTED,
                fontproperties=FONT_SANS,
                ha=text_ha,
                va="center",
            )

        ax_cal = fig.add_axes(cal_box, zorder=4)
        draw_month_dots(ax_cal, s["months"])

    # Líneas finas luminosas mapa → especie
    for i, s in enumerate(spp):
        lo, la = marker_pos[i]
        # punto en figura vía transformación mapa
        disp = ax_map.transData.transform((lo, la))
        fig_pt = fig.transFigure.inverted().transform(disp)
        sx, sy, sw, sh = slot_xy[i]
        side = 0 if i < 8 else 1
        if side == 0:
            end = (sx + sw * 0.92, sy + sh * 0.5)
        else:
            end = (sx + sw * 0.08, sy + sh * 0.5)
        # curva suave con ConnectionPatch
        con = ConnectionPatch(
            xyA=fig_pt,
            xyB=end,
            coordsA="figure fraction",
            coordsB="figure fraction",
            axesA=ax_bg,
            axesB=ax_bg,
            color=(0.55, 0.85, 0.95, 0.28),
            linewidth=0.55,
            linestyle="-",
            zorder=1.5,
            connectionstyle="arc3,rad=0.08" if side == 0 else "arc3,rad=-0.08",
        )
        fig.add_artist(con)

    # Créditos
    sat_cite = (
        "Mapa: Sentinel-2 cloudless – https://s2maps.eu by EOX IT Services GmbH "
        "(Contains modified Copernicus Sentinel data) · CC BY 4.0"
    )
    ax_bg.text(
        0.5,
        0.052,
        "Fotos CC0 / CC BY / CC BY-SA (crèdit a LICENCIAS_POSTER_LAMINA4.md). "
        "Dades: iNaturalist + Minka · BioFauna / FotoFauna · 2026-10-10",
        fontsize=5.0,
        color=MUTED,
        fontproperties=FONT_SANS,
        ha="center",
        va="center",
    )
    ax_bg.text(
        0.5,
        0.032,
        sat_cite + "  ·  A3 · 300 ppp  ·  Punts = mesos pic",
        fontsize=4.4,
        color=(0.45, 0.55, 0.62, 1),
        fontproperties=FONT_SANS,
        ha="center",
        va="center",
    )

    out_png = PAPER / "LAMINA4_poster_guia_20261010.png"
    out_pdf = PAPER / "LAMINA4_poster_guia_20261010.pdf"
    fig.savefig(out_png, dpi=300, facecolor=fig.get_facecolor())
    fig.savefig(out_pdf, dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_png, out_pdf


def write_meta(photos: dict[str, dict], spp: list[dict], hot: dict[str, str]):
    sat = {}
    if SAT_META.exists():
        sat = json.loads(SAT_META.read_text(encoding="utf-8"))
    lines = [
        "# Póster A3 — nudibranquios Cataluña (estilo museo / película)",
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} CEST",
        "",
        "Solo CC0 / CC BY / CC BY-SA. Fotos reales (no generadas).",
        "Fondo negro abisal · recortes con halo · sin tarjetas blancas.",
        "",
        "## Mapa",
        "",
        sat.get(
            "source",
            "Sentinel-2 cloudless – https://s2maps.eu by EOX IT Services GmbH "
            "(Contains modified Copernicus Sentinel data)",
        ),
        f"Licencia mapa: {sat.get('license', 'CC BY 4.0')}",
        f"Archivo: `{SAT_MAP.name}` · zoom {sat.get('zoom', '?')}",
        "",
        "## Especies y créditos",
        "",
    ]
    for i, s in enumerate(spp):
        ph = photos[s["species"]]
        vern = VERNACULAR.get(s["species"])
        vern_s = f"CA: {vern[0]} · ES: {vern[1]}" if vern else "sense nom comú establert (només científic)"
        lines.append(
            f"{i+1}. *{s['species']}* — {vern_s} · zona: {hot.get(s['species'],'?')} · "
            f"{ph['author']} · {ph['license']} · {ph['source']}"
            + (f" · {ph['uri']}" if ph.get("uri") else "")
        )
    (PAPER / "LICENCIAS_POSTER_LAMINA4.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    slim = []
    for i, s in enumerate(spp):
        vern = VERNACULAR.get(s["species"])
        slim.append(
            {
                "n": i + 1,
                "species": s["species"],
                "ca": vern[0] if vern else None,
                "es": vern[1] if vern else None,
                "zone": hot.get(s["species"]),
                **{k: photos[s["species"]].get(k) for k in ("author", "license", "uri", "source")},
                "file": str(photos[s["species"]]["path"].name),
            }
        )
    meta_out = {
        "style": "museum_movie_poster",
        "orientation": "A3_landscape",
        "dpi": 300,
        "map": sat,
        "species": slim,
    }
    (PAPER / "datos/poster_lamina4_meta_20261010.json").write_text(
        json.dumps(meta_out, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main():
    if not SAT_MAP.exists():
        raise SystemExit(f"Falta mapa satélite: {SAT_MAP}")
    spp = load_top(16)
    names = [s["species"] for s in spp]
    hot = load_hot_zone(names)
    prev_list = json.load(open(META_JSON)) if META_JSON.exists() else []
    prev = {p["species"]: p for p in prev_list}
    taxa = catalog_taxon_ids()
    photos = {}
    for s in spp:
        sp = s["species"]
        print(f"foto: {sp} …", flush=True)
        photos[sp] = ensure_large_photo(sp, prev.get(sp) or {}, taxa)
        print(f"  → {photos[sp]['source']} · {photos[sp]['author']} · {photos[sp]['license']}", flush=True)
    write_meta(photos, spp, hot)
    png, pdf = build_poster(spp, photos, hot)
    print("PNG", png, png.stat().st_size)
    print("PDF", pdf, pdf.stat().st_size)
    im = Image.open(png)
    print("pixels", im.size, "expected ~4962×3508")


if __name__ == "__main__":
    main()
