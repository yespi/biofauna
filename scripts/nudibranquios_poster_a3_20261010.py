#!/usr/bin/env python3
"""Póster A3 imprimible — nudibranquios comunes de Cataluña.

Fotos reales CC0/CC BY/CC BY-SA (reutiliza cache o descarga iNat/Minka large).
Sin GPU. Solo SELECT en postgres-global para zonas calientes (opcional; usa CSV).
"""
from __future__ import annotations

import csv
import json
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
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from PIL import Image

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
FOTOS = PAPER / "fotos"
FOTOS_LG = PAPER / "fotos_poster"
RECORTES = PAPER / "recortes"  # cutouts rembg (estilo guía; cursor-recortes)
COAST = PAPER / "datos/coast-western-med.geojson"
META_JSON = PAPER / "datos/fotos_meta_20261010.json"
MONTHLY = PAPER / "datos/especies_mensual_normalizado_20261010.csv"
ZONES_CSV = PAPER / "datos/zonas_calientes_normalizado_20261010.csv"

CAT_LAT = (40.45, 42.95)
CAT_LON = (0.10, 3.40)
MED_LAT = (35.0, 45.5)
MED_LON = (-6.0, 16.0)
LICENSE_OK = re.compile(r"^(cc0|cc-by|cc-by-sa)(-[0-9.]+)?$", re.I)
USER_AGENT = "BioFaunaNudibranchPoster/2026-10 (yespi.es; educational; contact gustavo.zafra@gmail.com)"
MES = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
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

# Nombres comunes (CA / ES) — uso divulgativo (GROC / guías Med)
VERNACULAR = {
    "Cratena peregrina": ("Nudibranqui pelegrí", "Babosa peregrina"),
    "Flabellina affinis": ("Flabel·lina violeta", "Flabelina violeta"),
    "Peltodoris atromaculata": ("Vaqueta suïssa", "Vaquita suiza"),
    "Felimare picta": ("Felimare pintada", "Felimare pintada"),
    "Edmundsella pedata": ("Edmundsel·la rosa", "Edmundsella rosa"),
    "Felimare tricolor": ("Felimare tricolor", "Felimare tricolor"),
    "Calmella cavolini": ("Calmella de Cavolini", "Calmella de Cavolini"),
    "Diaphorodoris papillata": ("Diaforodoris papil·lada", "Diaforodoris papilada"),
    "Paradoris indecora": ("Paradoris", "Paradoris"),
    "Antiopella cristata": ("Antiopel·la crestada", "Antiopela crestada"),
    "Polycera quadrilineata": ("Polícera de quatre línies", "Policera de cuatro líneas"),
    "Rudmania krohni": ("Rudmania de Krohn", "Rudmania de Krohn"),
    "Nemesignis banyulensis": ("Nemesignis de Banyuls", "Nemesignis de Banyuls"),
    "Diaphorodoris alba": ("Diaforodoris blanca", "Diaforodoris blanca"),
    "Facelina annulicornis": ("Facelina d'antenes anellades", "Facelina de antenas anilladas"),
    "Felimare fontandraui": ("Felimare de Fontandrau", "Felimare de Fontandrau"),
}

# Centro aproximado de cada tramo costero (lon, lat) para anclar fotos
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

PALETTE = [
    "#c0392b",
    "#2980b9",
    "#27ae60",
    "#8e44ad",
    "#d35400",
    "#16a085",
    "#c03971",
    "#2c3e50",
    "#e67e22",
    "#1abc9c",
    "#9b59b6",
    "#e74c3c",
    "#3498db",
    "#f39c12",
    "#1e8449",
    "#7d3c98",
]


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
    s = s.replace("cc-by-sa", "cc-by-sa").replace("cc0", "cc0")
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


def load_coast_lines(lon_b, lat_b) -> list[np.ndarray]:
    g = json.loads(COAST.read_text(encoding="utf-8"))
    segs = []
    for feat in g["features"]:
        geom = feat["geometry"]
        coords = geom["coordinates"]
        if geom["type"] == "LineString":
            coords = [coords]
        for line in coords:
            arr = np.array(line, dtype=float)
            if arr.size < 4:
                continue
            m = (
                (arr[:, 0] >= lon_b[0] - 0.2)
                & (arr[:, 0] <= lon_b[1] + 0.2)
                & (arr[:, 1] >= lat_b[0] - 0.2)
                & (arr[:, 1] <= lat_b[1] + 0.2)
            )
            if m.sum() < 2:
                continue
            idx = np.where(m)[0]
            breaks = np.where(np.diff(idx) > 1)[0]
            starts = np.r_[0, breaks + 1]
            ends = np.r_[breaks + 1, len(idx)]
            for s, e in zip(starts, ends):
                chunk = arr[idx[s:e]]
                if len(chunk) >= 2:
                    segs.append(chunk)
    return segs


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
    # API lista o dict
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
    """Créditos actualizados tras re-elección de foto para rembg."""
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

    # Reutilizar thumb si es razonable (≥400 px) como fallback inmediato
    # pero intentar large primero
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
        # copiar thumb (ya validada CC)
        dest.write_bytes(thumb.read_bytes())
        return entry(dest, prev, "thumb_fallback")

    raise FileNotFoundError(f"Sin foto CC para {sp}")


# Especies donde rembg falla (camuflaje extremo): usar foto completa.
CUTOUT_SKIP = {"Paradoris indecora"}


def cutout_path(sp: str) -> Path | None:
    """PNG rembg con sombra/contorno (preferido para el póster)."""
    if sp in CUTOUT_SKIP:
        return None
    p = RECORTES / f"{sp.replace(' ', '_').lower()}_cutout.png"
    return p if p.exists() and p.stat().st_size > 8000 else None


def load_rgb(path: Path, size: tuple[int, int]) -> np.ndarray:
    im = Image.open(path).convert("RGB")
    # cover crop
    tw, th = size
    w, h = im.size
    scale = max(tw / w, th / h)
    nw, nh = int(w * scale), int(h * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    im = im.crop((left, top, left + tw, top + th))
    return np.asarray(im)


def load_guide_rgba(path: Path, size: tuple[int, int], bg=(233, 242, 244, 0)) -> np.ndarray:
    """Recorte guía (RGBA) centrado con letterbox; conserva transparencia."""
    im = Image.open(path).convert("RGBA")
    tw, th = size
    w, h = im.size
    scale = min(tw / w, th / h) * 0.92
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (tw, th), bg)
    canvas.paste(im, ((tw - nw) // 2, (th - nh) // 2), im)
    return np.asarray(canvas)


def load_species_image(sp: str, path: Path, size: tuple[int, int], prefer_cutout: bool = True) -> np.ndarray:
    cp = cutout_path(sp) if prefer_cutout else None
    if cp is not None:
        return load_guide_rgba(cp, size)
    return load_rgb(path, size)


def draw_mini_calendar(ax, months: np.ndarray):
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 1)
    ax.axis("off")
    cmap = LinearSegmentedColormap.from_list("cal", ["#e8f1f5", "#7eb8c9", "#1a5276", "#0b2e44"])
    for i, v in enumerate(months):
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (i + 0.08, 0.22),
                0.84,
                0.55,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=cmap(float(v)),
                edgecolor="#ffffff",
                linewidth=0.4,
                mutation_aspect=0.5,
            )
        )
        ax.text(i + 0.5, 0.05, MES[i], ha="center", va="bottom", fontsize=5.2, color="#334455", fontfamily="DejaVu Sans")


def build_poster(spp: list[dict], photos: dict[str, dict], hot: dict[str, str]):
    # A3 landscape mm → inches
    fig_w, fig_h = 16.54, 11.69
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=300, facecolor="#e9f2f4")

    # soft marine wash
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis("off")
    for i, a in enumerate(np.linspace(0.0, 1.0, 40)):
        ax_bg.add_patch(
            mpatches.Rectangle(
                (0, a),
                1,
                1 / 40,
                facecolor=(0.82 + 0.08 * a, 0.90 + 0.05 * a, 0.93, 1),
                edgecolor="none",
            )
        )
    # subtle wave bands
    xs = np.linspace(0, 1, 200)
    for k, y0 in enumerate((0.12, 0.28, 0.78, 0.90)):
        ys = y0 + 0.012 * np.sin(xs * 18 + k)
        ax_bg.fill_between(xs, ys - 0.01, ys + 0.01, color="#9fc4d0", alpha=0.18, linewidth=0)

    # title band
    ax_bg.add_patch(
        mpatches.FancyBboxPatch(
            (0.035, 0.915),
            0.93,
            0.062,
            boxstyle="round,pad=0.008,rounding_size=0.01",
            facecolor="#0d3b4c",
            edgecolor="none",
            zorder=2,
        )
    )
    ax_bg.text(
        0.05,
        0.955,
        "Nudibranquis de Catalunya · Nudibranquios de Cataluña",
        fontsize=16,
        color="white",
        fontweight="bold",
        fontfamily="DejaVu Serif",
        va="center",
        zorder=3,
    )
    ax_bg.text(
        0.05,
        0.928,
        "Les 16 espècies més freqüents (iNaturalist + Minka) · Guia visual amb calendari de mesos pic · BioFauna 2026",
        fontsize=7.5,
        color="#c5e0e8",
        fontfamily="DejaVu Sans",
        va="center",
        zorder=3,
    )

    # MAP panel (central-left)
    ax_map = fig.add_axes([0.04, 0.10, 0.34, 0.78])
    ax_map.set_facecolor("#d7e8ee")
    lon_b, lat_b = CAT_LON, CAT_LAT
    for seg in load_coast_lines(lon_b, lat_b):
        ax_map.plot(seg[:, 0], seg[:, 1], color="#1a3a4a", lw=1.35, zorder=3, solid_capstyle="round")
    ax_map.fill_between([lon_b[0], lon_b[1]], lat_b[0], lat_b[1], color="#b9d6e3", zorder=0, alpha=0.55)
    # land tint approx west of coast: soft cream band
    ax_map.set_xlim(lon_b[0] - 0.05, lon_b[1] + 0.08)
    ax_map.set_ylim(lat_b[0] - 0.05, lat_b[1] + 0.05)
    ax_map.set_aspect("equal", adjustable="box")
    ax_map.set_xticks([])
    ax_map.set_yticks([])
    for sp in ax_map.spines.values():
        sp.set_color("#0d3b4c")
        sp.set_linewidth(1.2)
    ax_map.set_title("Costa catalana · zones calentes", fontsize=9, color="#0d3b4c", pad=6, fontfamily="DejaVu Serif")

    # zone labels faint
    for zname, (lo, la) in ZONE_XY.items():
        t = ax_map.text(lo, la, zname.split("/")[0].strip(), fontsize=5.2, color="#3a5a68", alpha=0.75, ha="center", va="center", zorder=2)
        t.set_path_effects([pe.withStroke(linewidth=2.0, foreground="white")])

    # species markers on map (offset to reduce overlap)
    colors = {s["species"]: PALETTE[i % len(PALETTE)] for i, s in enumerate(spp)}
    # jitter offsets by index around zone
    zone_counts: dict[str, int] = defaultdict(int)
    for i, s in enumerate(spp):
        sp = s["species"]
        zone = hot.get(sp, "Illes Medes / Estartit")
        base = ZONE_XY.get(zone, (3.1, 41.9))
        k = zone_counts[zone]
        zone_counts[zone] += 1
        ang = (k * 2.2) + i * 0.15
        r = 0.05 + 0.018 * k
        lo = base[0] + r * np.cos(ang)
        la = base[1] + r * np.sin(ang) * 0.7
        # mini photo / cutout guía
        ph = photos[sp]["path"]
        img = load_species_image(sp, ph, (96, 96))
        # marker circle + number
        ax_map.plot(lo, la, "o", markersize=16, color="white", zorder=5, markeredgecolor=colors[sp], markeredgewidth=1.6)
        ax_map.imshow(
            img,
            extent=(lo - 0.055, lo + 0.055, la - 0.038, la + 0.038),
            zorder=6,
            aspect="auto",
            clip_on=True,
        )
        ax_map.plot(lo, la, "o", markersize=17.5, fillstyle="none", color=colors[sp], zorder=7, markeredgewidth=1.8)
        ax_map.text(
            lo,
            la - 0.055,
            str(i + 1),
            ha="center",
            va="top",
            fontsize=6.5,
            fontweight="bold",
            color=colors[sp],
            zorder=8,
            fontfamily="DejaVu Sans",
        )

    ax_map.text(
        0.02,
        0.02,
        "Miniatures al mapa = zona amb taxa més alta (obs. / esforç nudi).",
        transform=ax_map.transAxes,
        fontsize=5.5,
        color="#334455",
        va="bottom",
    )

    # SPECIES CARDS grid 4×4 on the right
    # margins: left of cards 0.40
    left0, bottom0 = 0.395, 0.075
    cell_w, cell_h = 0.145, 0.195
    gap_x, gap_y = 0.008, 0.012
    ncols = 4

    for i, s in enumerate(spp):
        r, c = divmod(i, ncols)
        # fill row-major top→bottom: invert row
        row = r
        x = left0 + c * (cell_w + gap_x)
        y = bottom0 + (3 - row) * (cell_h + gap_y)
        # card background
        ax_card = fig.add_axes([x, y, cell_w, cell_h])
        ax_card.set_xlim(0, 1)
        ax_card.set_ylim(0, 1)
        ax_card.axis("off")
        ax_card.add_patch(
            mpatches.FancyBboxPatch(
                (0.02, 0.02),
                0.96,
                0.96,
                boxstyle="round,pad=0.01,rounding_size=0.03",
                facecolor="#f7fbfc",
                edgecolor=colors[s["species"]],
                linewidth=1.3,
            )
        )
        # number badge
        ax_card.add_patch(mpatches.Circle((0.10, 0.90), 0.07, facecolor=colors[s["species"]], edgecolor="none", zorder=3))
        ax_card.text(0.10, 0.90, str(i + 1), ha="center", va="center", fontsize=7, color="white", fontweight="bold", zorder=4)

        # foto / recorte guía (sin fondo si existe en recortes/)
        ax_img = fig.add_axes([x + 0.012, y + 0.078, cell_w * 0.58, cell_h * 0.62])
        ax_img.set_facecolor("#e9f2f4")
        ax_img.imshow(load_species_image(s["species"], photos[s["species"]]["path"], (420, 320)))
        ax_img.set_xticks([])
        ax_img.set_yticks([])
        for spn in ax_img.spines.values():
            spn.set_visible(False)

        # mini calendar beside photo
        ax_cal = fig.add_axes([x + cell_w * 0.60, y + 0.10, cell_w * 0.37, cell_h * 0.55])
        draw_mini_calendar(ax_cal, s["months"])
        ax_cal.set_title("mesos pic", fontsize=5.5, color="#334455", pad=1)

        # names
        ca, es = VERNACULAR.get(s["species"], (s["species"].split()[0], s["species"].split()[0]))
        ax_card.text(
            0.06,
            0.20,
            s["species"],
            fontsize=6.6,
            fontstyle="italic",
            fontfamily="DejaVu Serif",
            color="#0d3b4c",
            fontweight="bold",
            va="bottom",
        )
        ax_card.text(0.06, 0.11, f"CA: {ca}", fontsize=5.4, color="#2c3e50", fontfamily="DejaVu Sans", va="bottom")
        ax_card.text(0.06, 0.045, f"ES: {es}", fontsize=5.4, color="#2c3e50", fontfamily="DejaVu Sans", va="bottom")

        # credit tiny under photo area (inside card right of badge)
        ph = photos[s["species"]]
        credit = f"{ph['author']} · {ph['license']}"
        ax_card.text(0.20, 0.90, credit[:42], fontsize=4.2, color="#667788", va="center", ha="left")

    # footer
    ax_bg.text(
        0.04,
        0.035,
        "Fotos amb llicència lliure (CC0 / CC BY / CC BY-SA). Crèdit sota cada espècie. "
        "Calendari: intensitat mensual suavitzada (correcció d’esforç γ=0,35). "
        "Font: public_observations (iNaturalist + Minka) · BioFauna / FotoFauna · 2026-10-10",
        fontsize=5.8,
        color="#334455",
        fontfamily="DejaVu Sans",
        va="center",
    )
    ax_bg.text(
        0.96,
        0.035,
        "A3 · 300 ppp · imprimible",
        fontsize=5.8,
        color="#334455",
        ha="right",
        va="center",
    )

    out_png = PAPER / "LAMINA4_poster_guia_20261010.png"
    out_pdf = PAPER / "LAMINA4_poster_guia_20261010.pdf"
    fig.savefig(out_png, dpi=300, facecolor=fig.get_facecolor())
    fig.savefig(out_pdf, dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_png, out_pdf


def write_meta(photos: dict[str, dict], spp: list[dict], hot: dict[str, str]):
    lines = [
        "# Póster A3 — nudibranquios Cataluña",
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M %Z')} CEST",
        "",
        "Solo CC0 / CC BY / CC BY-SA. Fotos reales (no generadas).",
        "",
        "## Especies y créditos",
        "",
    ]
    for i, s in enumerate(spp):
        ph = photos[s["species"]]
        ca, es = VERNACULAR[s["species"]]
        lines.append(
            f"{i+1}. *{s['species']}* — CA: {ca} · ES: {es} · zona: {hot.get(s['species'],'?')} · "
            f"{ph['author']} · {ph['license']} · {ph['source']}"
            + (f" · {ph['uri']}" if ph.get("uri") else "")
        )
    (PAPER / "LICENCIAS_POSTER_LAMINA4.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    slim = [
        {
            "n": i + 1,
            "species": s["species"],
            "ca": VERNACULAR[s["species"]][0],
            "es": VERNACULAR[s["species"]][1],
            "zone": hot.get(s["species"]),
            **{k: photos[s["species"]].get(k) for k in ("author", "license", "uri", "source")},
            "file": str(photos[s["species"]]["path"].name),
        }
        for i, s in enumerate(spp)
    ]
    (PAPER / "datos/poster_lamina4_meta_20261010.json").write_text(
        json.dumps(slim, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main():
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
    # sanity size at 300 dpi A3 landscape
    im = Image.open(png)
    print("pixels", im.size, "expected ~4962×3508")


if __name__ == "__main__":
    main()
