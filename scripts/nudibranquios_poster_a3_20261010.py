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

# Nombres comunes usados en guías/divulgación mediterránea (CA, ES).
VERNACULAR: dict[str, tuple[str, str]] = {
    "Cratena peregrina": ("Cratena", "Cratena"),
    "Flabellina affinis": ("Flabel·lina violeta", "Flabelina violeta"),
    "Peltodoris atromaculata": ("Vaqueta suïssa", "Vaquita suiza"),
    "Felimare picta": ("Felimare pintada", "Felimare pintada"),
    "Edmundsella pedata": ("Flabel·lina rosa", "Flabelina rosa"),
    "Felimare tricolor": ("Felimare tricolor", "Felimare tricolor"),
    "Calmella cavolini": ("Calmella", "Calmella"),
    "Diaphorodoris papillata": ("Diaphorodoris", "Diaphorodoris"),
    "Paradoris indecora": ("Paradoris", "Paradoris"),
    "Antiopella cristata": ("Antiopella crestada", "Antiopella crestada"),
    "Polycera quadrilineata": ("Polícera de quatre ratlles", "Polícera de cuatro líneas"),
    "Rudmania krohni": ("Rudmania", "Rudmania"),
    "Nemesignis banyulensis": ("Nemesignis de Banyuls", "Nemesignis de Banyuls"),
    "Diaphorodoris alba": ("Diaphorodoris blanca", "Diaphorodoris blanca"),
    "Facelina annulicornis": ("Facelina", "Facelina"),
    "Felimare fontandraui": ("Felimare de Fontandrau", "Felimare de Fontandrau"),
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

# Poblaciones / zonas de buceo (punto + etiqueta; dx/dy en grados, ha relativo al punto)
PLACE_LABELS = [
    # name, lon, lat, dx, dy, ha
    ("Portbou", 3.16, 42.425, -0.18, 0.04, "right"),
    ("Cadaqués", 3.275, 42.288, -0.22, 0.02, "right"),
    ("Roses", 3.175, 42.262, -0.20, -0.02, "right"),
    ("l'Escala", 3.135, 42.125, -0.22, 0.00, "right"),
    ("l'Estartit", 3.20, 42.052, -0.24, 0.00, "right"),
    ("Begur", 3.21, 41.954, -0.18, 0.02, "right"),
    ("Palamós", 3.13, 41.848, -0.20, -0.02, "right"),
    ("Tossa", 2.93, 41.720, -0.18, 0.02, "right"),
    ("Blanes", 2.79, 41.675, -0.18, -0.02, "right"),
    ("Arenys", 2.56, 41.580, -0.18, 0.00, "right"),
    ("Barcelona", 2.175, 41.385, -0.22, 0.00, "right"),
    ("Sitges", 1.825, 41.235, -0.18, 0.00, "right"),
    ("Tarragona", 1.25, 41.115, -0.18, 0.02, "right"),
    ("l'Ametlla", 0.805, 40.885, 0.10, 0.02, "left"),
    ("l'Ampolla", 0.710, 40.812, 0.12, -0.02, "left"),
    ("Delta de l'Ebre", 0.78, 40.70, 0.14, -0.04, "left"),
]

# 16 colores distinguibles (guía + punto de especie); tono saturado sobre satélite oscuro
SPECIES_COLORS = [
    "#ff6b4a",  # 1 Cratena — coral
    "#c44dff",  # 2 Flabellina — violeta
    "#f0f0f0",  # 3 Peltodoris — blanco
    "#3d9bff",  # 4 Felimare picta — azul
    "#ff5aa8",  # 5 Edmundsella — rosa
    "#2ee6c2",  # 6 Felimare tricolor — turquesa
    "#ffb347",  # 7 Calmella — naranja
    "#e8d44d",  # 8 Diaphorodoris papillata — oro
    "#d8b4ff",  # 9 Paradoris — lavanda
    "#7dff7a",  # 10 Antiopella — verde
    "#ff8c42",  # 11 Polycera — naranja vivo
    "#5ec8ff",  # 12 Rudmania — cielo
    "#ff66cc",  # 13 Nemesignis — magenta
    "#b8fff0",  # 14 Diaphorodoris alba — menta
    "#ffd166",  # 15 Facelina — ámbar
    "#4de1ff",  # 16 Felimare fontandraui — cian
]

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


def load_zone_intensity() -> dict[str, float]:
    """Máxima tasa (obs corregida por esfuerzo) por tramo costero."""
    best: dict[str, float] = {}
    with ZONES_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            z = row["tramo"]
            tasa = float(row["tasa"])
            if z not in best or tasa > best[z]:
                best[z] = tasa
    return best


def _hex_rgba(hx: str, a: float = 1.0) -> tuple[float, float, float, float]:
    h = hx.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return (r, g, b, a)


def draw_north_rose(ax, lon: float, lat: float, size_deg: float = 0.14):
    """Rosa de los vientos elegante (N destacado)."""
    s = size_deg
    # anillo exterior
    ax.add_patch(
        mpatches.Circle(
            (lon, lat),
            s * 0.92,
            facecolor=(0.02, 0.05, 0.08, 0.55),
            edgecolor=GOLD,
            linewidth=0.7,
            zorder=9,
        )
    )
    # cruz cardinal fina
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        ax.plot(
            [lon, lon + s * 0.78 * math.sin(rad)],
            [lat, lat + s * 0.78 * math.cos(rad) * 0.72],
            color=(0.85, 0.78, 0.55, 0.55),
            lw=0.45,
            zorder=9.2,
        )
    # flecha norte (triángulo dorado)
    north = np.array(
        [
            [lon, lat + s * 0.78 * 0.72],
            [lon - s * 0.16, lat - s * 0.08],
            [lon + s * 0.16, lat - s * 0.08],
        ]
    )
    ax.add_patch(
        mpatches.Polygon(north, closed=True, facecolor=GOLD, edgecolor="none", zorder=10, alpha=0.95)
    )
    # punta sur más oscura (contraste)
    south = np.array(
        [
            [lon, lat - s * 0.55 * 0.72],
            [lon - s * 0.10, lat + s * 0.02],
            [lon + s * 0.10, lat + s * 0.02],
        ]
    )
    ax.add_patch(
        mpatches.Polygon(south, closed=True, facecolor=(0.55, 0.48, 0.32, 0.85), edgecolor="none", zorder=9.5)
    )
    t = ax.text(
        lon,
        lat + s * 1.05 * 0.72,
        "N",
        fontsize=8.5,
        color=CREAM,
        ha="center",
        va="bottom",
        fontproperties=FONT_SERIF_B,
        zorder=11,
    )
    t.set_path_effects([pe.withStroke(linewidth=2.8, foreground=(0.02, 0.05, 0.08, 0.92))])


def draw_scale_bar(ax, lon0: float, lat0: float, km: float = 50.0):
    """Escala en km (aprox. a latitud media del mapa)."""
    mid_lat = (MAP_LAT[0] + MAP_LAT[1]) / 2
    deg_per_km = 1.0 / (111.32 * math.cos(math.radians(mid_lat)))
    w = km * deg_per_km
    h = 0.018
    # fondo semitransparente
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (lon0 - 0.04, lat0 - 0.055),
            w + 0.08,
            0.11,
            boxstyle="round,pad=0.01",
            facecolor=(0.02, 0.05, 0.08, 0.62),
            edgecolor=(0.83, 0.72, 0.48, 0.45),
            linewidth=0.5,
            zorder=9,
            mutation_aspect=0.6,
        )
    )
    # barra segmentada 0–25–50
    half = w / 2
    ax.add_patch(
        mpatches.Rectangle((lon0, lat0), half, h, facecolor=CREAM, edgecolor="none", zorder=10)
    )
    ax.add_patch(
        mpatches.Rectangle((lon0 + half, lat0), half, h, facecolor=GOLD, edgecolor="none", zorder=10)
    )
    ax.plot([lon0, lon0 + w], [lat0, lat0], color=CREAM, lw=0.8, zorder=10.5)
    for x, lab in ((lon0, "0"), (lon0 + half, "25"), (lon0 + w, "50")):
        ax.plot([x, x], [lat0, lat0 + h * 1.6], color=CREAM, lw=0.7, zorder=10.5)
        t = ax.text(
            x,
            lat0 + h * 2.4,
            lab,
            fontsize=5.2,
            color=CREAM,
            ha="center",
            va="bottom",
            fontproperties=FONT_SANS,
            zorder=11,
        )
        t.set_path_effects([pe.withStroke(linewidth=1.8, foreground=(0, 0, 0, 0.8))])
    t = ax.text(
        lon0 + w / 2,
        lat0 - 0.028,
        "km",
        fontsize=5.5,
        color=GOLD,
        ha="center",
        va="top",
        fontproperties=FONT_SANS,
        zorder=11,
    )
    t.set_path_effects([pe.withStroke(linewidth=1.8, foreground=(0, 0, 0, 0.8))])


def draw_place_labels(ax):
    for name, lo, la, dx, dy, ha in PLACE_LABELS:
        ax.plot(
            lo,
            la,
            "o",
            markersize=3.2,
            color=CREAM,
            markeredgecolor=GOLD,
            markeredgewidth=0.55,
            zorder=8.5,
            alpha=0.95,
        )
        t = ax.text(
            lo + dx,
            la + dy,
            name,
            fontsize=6.5,
            color=CREAM,
            ha=ha,
            va="center",
            fontproperties=FONT_SANS,
            zorder=8.6,
            alpha=0.98,
        )
        t.set_path_effects([pe.withStroke(linewidth=2.8, foreground=(0, 0, 0, 0.88))])


def draw_hot_zones(ax, intensities: dict[str, float]):
    """Puntos luminosos = zonas calientes; tamaño/brillo ∝ tasa corregida por esfuerzo."""
    if not intensities:
        return
    vmax = max(intensities.values()) or 1.0
    for zone, (lo, la) in ZONE_XY.items():
        tasa = intensities.get(zone, 0.0)
        if tasa <= 0:
            continue
        t = float(np.clip(tasa / vmax, 0.15, 1.0))
        # halo exterior
        ax.plot(
            lo,
            la,
            "o",
            markersize=14 + 28 * t,
            color=(0.35 + 0.2 * t, 0.75 + 0.2 * t, 1.0, 0.10 + 0.18 * t),
            markeredgewidth=0,
            zorder=4.5,
        )
        ax.plot(
            lo,
            la,
            "o",
            markersize=7 + 14 * t,
            color=(0.45 + 0.35 * t, 0.85 + 0.12 * t, 1.0, 0.22 + 0.45 * t),
            markeredgewidth=0,
            zorder=4.7,
        )


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


def build_poster(
    spp: list[dict],
    photos: dict[str, dict],
    hot: dict[str, str],
    zone_int: dict[str, float] | None = None,
):
    # A3 apaisado mm → inches (costa N–S como franja central)
    fig_w, fig_h = 16.54, 11.69
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=300, facecolor=BG)
    zone_int = zone_int or {}

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

    # ——— Mapa satélite central (deja franja inferior para leyenda) ———
    map_l, map_b, map_w, map_h = 0.348, 0.168, 0.304, 0.695
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

    # zonas calientes luminosas (tamaño ∝ intensidad corregida por esfuerzo)
    draw_hot_zones(ax_map, zone_int)
    # poblaciones y zonas de buceo
    draw_place_labels(ax_map)
    # rosa de los vientos + escala
    draw_north_rose(ax_map, lon=1.05, lat=42.28, size_deg=0.16)
    draw_scale_bar(ax_map, lon0=0.78, lat0=40.95, km=50.0)

    ax_map.text(
        0.5,
        0.012,
        "Sentinel-2 cloudless · EOX",
        transform=ax_map.transAxes,
        fontsize=4.6,
        color=(1, 1, 1, 0.50),
        ha="center",
        va="bottom",
        fontproperties=FONT_SANS,
        zorder=6,
    )

    # puntos de especie (color propio) sobre las zonas
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
        col = SPECIES_COLORS[i % len(SPECIES_COLORS)]
        rgba = _hex_rgba(col, 0.98)
        ax_map.plot(
            lo,
            la,
            "o",
            markersize=16,
            color=_hex_rgba(col, 0.22),
            markeredgewidth=0,
            zorder=6,
        )
        ax_map.plot(
            lo,
            la,
            "o",
            markersize=11.5,
            color=rgba,
            markeredgecolor=(0.05, 0.08, 0.12, 0.95),
            markeredgewidth=0.9,
            zorder=7,
        )
        lum = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
        num_col = "#061018" if lum > 0.55 else "#f4f0e6"
        ax_map.text(
            lo,
            la,
            str(i + 1),
            ha="center",
            va="center",
            fontsize=6.6,
            color=num_col,
            fontweight="bold",
            zorder=8,
            fontproperties=FONT_SANS,
        )

    # ——— Fichas especie (sin tarjeta blanca): 8 izq + 8 der ———
    # Márgenes impresión ≈ 12 mm (A3). Nombres grandes (legibles ~1 m en A3).
    left_col_x = 0.028
    right_col_x = 0.662
    col_w = 0.308
    row0_y = 0.082
    row_h = 0.094
    gap = 0.0048

    slot_xy: dict[int, tuple[float, float, float, float]] = {}
    anchor_fig: dict[int, tuple[float, float]] = {}

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

        # Imagen hacia el mapa; texto exterior amplio
        if side == 0:
            img_box = [x + col_w * 0.42, y + row_h * 0.22, col_w * 0.56, row_h * 0.74]
            text_x = 0.02
            text_ha = "left"
            cal_box = [x + 0.01, y + 0.008, col_w * 0.40, row_h * 0.16]
            anchor_fig[i] = (x + col_w * 0.98, y + row_h * 0.55)
        else:
            img_box = [x + col_w * 0.02, y + row_h * 0.22, col_w * 0.56, row_h * 0.74]
            text_x = 0.98
            text_ha = "right"
            cal_box = [x + col_w * 0.58, y + 0.008, col_w * 0.40, row_h * 0.16]
            anchor_fig[i] = (x + col_w * 0.02, y + row_h * 0.55)

        ax_img = fig.add_axes(img_box, zorder=4)
        ax_img.set_facecolor("none")
        ax_img.imshow(load_species_image(s["species"], photos[s["species"]]["path"], (720, 540)))
        ax_img.set_xticks([])
        ax_img.set_yticks([])
        for spn in ax_img.spines.values():
            spn.set_visible(False)

        sp_col = SPECIES_COLORS[i % len(SPECIES_COLORS)]
        ax_c.text(
            text_x,
            0.92,
            str(i + 1),
            fontsize=10.0,
            color=sp_col,
            ha=text_ha,
            va="center",
            fontproperties=FONT_SERIF_B,
            alpha=0.98,
        )
        # Nombre científico grande + nombre común debajo
        ax_c.text(
            text_x,
            0.70,
            s["species"],
            fontsize=13.5,
            color=CREAM,
            fontproperties=FONT_SERIF_BI,
            ha=text_ha,
            va="center",
        )
        vern = VERNACULAR.get(s["species"])
        if vern:
            ca, es = vern
            common = ca if ca == es else f"{ca}  ·  {es}"
            ax_c.text(
                text_x,
                0.40,
                common,
                fontsize=8.6,
                color=GOLD,
                fontproperties=FONT_SANS,
                ha=text_ha,
                va="center",
            )

        ax_cal = fig.add_axes(cal_box, zorder=4)
        draw_month_dots(ax_cal, s["months"])

    # Líneas guía del color de cada especie → punto exacto del mapa
    fig.canvas.draw()
    for i, s in enumerate(spp):
        lo, la = marker_pos[i]
        end = anchor_fig[i]
        col = _hex_rgba(SPECIES_COLORS[i % len(SPECIES_COLORS)], 0.72)
        con = ConnectionPatch(
            xyA=(lo, la),
            xyB=end,
            coordsA=ax_map.transData,
            coordsB=fig.transFigure,
            axesA=ax_map,
            axesB=ax_bg,
            color=col,
            linewidth=1.15,
            linestyle="-",
            zorder=5.5,
            connectionstyle="arc3,rad=0.0",
            clip_on=False,
        )
        fig.add_artist(con)

    # ——— Leyenda (bajo el mapa) ———
    ax_leg = fig.add_axes([map_l, 0.072, map_w, 0.088], zorder=3)
    ax_leg.set_xlim(0, 1)
    ax_leg.set_ylim(0, 1)
    ax_leg.axis("off")
    ax_leg.set_facecolor("none")
    ax_leg.add_patch(
        mpatches.FancyBboxPatch(
            (0.01, 0.04),
            0.98,
            0.92,
            boxstyle="round,pad=0.015",
            facecolor=(0.03, 0.07, 0.11, 0.78),
            edgecolor=(0.83, 0.72, 0.48, 0.40),
            linewidth=0.55,
            transform=ax_leg.transAxes,
            zorder=0,
        )
    )
    ax_leg.text(
        0.04,
        0.82,
        "Llegenda",
        fontsize=6.8,
        color=GOLD,
        fontproperties=FONT_SERIF_B,
        ha="left",
        va="center",
    )
    # zonas calientes (tamaño)
    for j, (ms, lab) in enumerate(((5.5, "baixa"), (9.0, ""), (13.5, "alta"))):
        x = 0.07 + j * 0.055
        ax_leg.plot(
            x,
            0.48,
            "o",
            markersize=ms,
            color=(0.45, 0.85, 1.0, 0.35 + 0.2 * j),
            markeredgewidth=0,
            transform=ax_leg.transAxes,
            zorder=2,
        )
    ax_leg.text(
        0.26,
        0.48,
        "Zones calentes: mida/brillantor =\nintensitat d'obs. corregida per esforç",
        fontsize=4.6,
        color=CREAM,
        fontproperties=FONT_SANS,
        ha="left",
        va="center",
        linespacing=1.25,
    )
    # calendario 12 puntos
    for j in range(12):
        t = j / 11
        ax_leg.plot(
            0.07 + j * 0.018,
            0.18,
            "o",
            markersize=2.2 + 2.8 * t,
            color=(0.25 + 0.55 * t, 0.65 + 0.3 * t, 0.9, 0.25 + 0.7 * t),
            markeredgewidth=0,
            transform=ax_leg.transAxes,
            zorder=2,
        )
    ax_leg.text(
        0.30,
        0.18,
        "12 punts = mesos (G→D); brillantor = activitat",
        fontsize=4.6,
        color=CREAM,
        fontproperties=FONT_SANS,
        ha="left",
        va="center",
    )
    # línea guía + punto especie
    ax_leg.plot(
        [0.62, 0.72],
        [0.55, 0.55],
        color=_hex_rgba("#ff6b4a", 0.85),
        lw=1.3,
        transform=ax_leg.transAxes,
        zorder=2,
        solid_capstyle="round",
    )
    ax_leg.plot(
        0.72,
        0.55,
        "o",
        markersize=7,
        color="#ff6b4a",
        markeredgecolor="#061018",
        markeredgewidth=0.5,
        transform=ax_leg.transAxes,
        zorder=3,
    )
    ax_leg.text(
        0.75,
        0.55,
        "Línia + punt numerat =\nespècie (color propi)",
        fontsize=4.6,
        color=CREAM,
        fontproperties=FONT_SANS,
        ha="left",
        va="center",
        linespacing=1.25,
    )
    ax_leg.text(
        0.62,
        0.20,
        "Punts crema = poblacions / zones de busseig",
        fontsize=4.5,
        color=MUTED,
        fontproperties=FONT_SANS,
        ha="left",
        va="center",
    )

    # Créditos
    sat_cite = (
        "Mapa: Sentinel-2 cloudless – https://s2maps.eu by EOX IT Services GmbH "
        "(Contains modified Copernicus Sentinel data) · CC BY 4.0"
    )
    ax_bg.text(
        0.5,
        0.048,
        "Fotos CC0 / CC BY / CC BY-SA (crèdit a LICENCIAS_POSTER_LAMINA4.md). "
        "Dades: iNaturalist + Minka · BioFauna / FotoFauna · 2026-10-10",
        fontsize=4.8,
        color=MUTED,
        fontproperties=FONT_SANS,
        ha="center",
        va="center",
    )
    ax_bg.text(
        0.5,
        0.028,
        sat_cite + "  ·  A3 · 300 ppp",
        fontsize=4.2,
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
    zone_int = load_zone_intensity()
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
    png, pdf = build_poster(spp, photos, hot, zone_int=zone_int)
    print("PNG", png, png.stat().st_size)
    print("PDF", pdf, pdf.stat().st_size)
    im = Image.open(png)
    print("pixels", im.size, "expected ~4962×3508")


if __name__ == "__main__":
    main()
