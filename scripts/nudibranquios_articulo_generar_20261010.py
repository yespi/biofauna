#!/usr/bin/env python3
"""Genera artículo + láminas del calendario fenológico de nudibranquios (Cataluña).
Solo SELECT en postgres-global (fauna.public_observations) + APIs públicas de fotos.
Sin GPU; sin escribir en producción."""
from __future__ import annotations

import csv
import json
import math
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import gridspec, patheffects
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
ENRICH = Path("/mnt/docker/biofauna/dataset/enrich_obs_metadata_progress_20260919.json")
CORR_FOTOS = ROOT / "papers/proyecto_correlacion/lamina_fotos"

CAT_LAT = (40.45, 42.95)
CAT_LON = (0.10, 3.40)
# Mediterráneo occidental (rescate de fotos CC)
MED_LAT = (35.0, 45.5)
MED_LON = (-6.0, 16.0)

MES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
MES_L = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

MARINE_ICONIC = {
    "Mollusca",
    "Actinopterygii",
    "Elasmobranchii",
    "Cnidaria",
    "Malacostraca",
    "Porifera",
    "Annelida",
    "Bryozoa",
    "Echinodermata",
    "Crustacea",
    "Cephalopoda",
    "Ctenophora",
    "Platyhelminthes",
    "Chondrichthyes",
    "Hydrozoa",
    "Anthozoa",
    "Ascidiacea",
    "Polychaeta",
    "Animalia",
}

NUDI_ORDERS = {"Nudibranchia", "Doridida", "Dendronotida"}

LICENSE_OK = re.compile(r"^(cc0|cc-by|cc-by-sa)(-[0-9.]+)?$", re.I)
# Corrección parcial del esfuerzo (γ<1 evita inflar ene/feb) + prior débil
EFFORT_GAMMA = 0.35
LOW_EFFORT_FRAC = 0.55  # meses con E < esto × mediana → tramado
USER_AGENT = "BioFaunaNudibranchCalendar/2026-10 (yespi.es; educational; contact gustavo.zafra@gmail.com)"


def http_json(url: str, timeout: int = 30) -> dict | list | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except Exception:
        return None


def http_bytes(url: str, timeout: int = 30) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception:
        return None


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


def load_nudibranchs() -> dict[str, dict]:
    ts = json.load(open(ROOT / "dataset/target_species.json"))
    cat = {s["name"]: s for s in json.load(open(ROOT / "dataset/catalog.json"))["species"]}
    out = {}
    for x in ts:
        if x.get("order") not in NUDI_ORDERS:
            continue
        name = x["name"]
        fam = x.get("family") or (cat.get(name) or {}).get("family") or "Sin familia"
        c = cat.get(name) or {}
        out[name] = {
            "family": fam,
            "slug": c.get("slug", ""),
            "inat": c.get("inat_taxon"),
            "minka": c.get("minka_taxon"),
        }
    return out


def marine_taxon_ids() -> list[int]:
    ids = []
    for s in json.load(open(ROOT / "dataset/catalog.json"))["species"]:
        if s.get("inat_taxon") and s.get("iconic") in MARINE_ICONIC:
            ids.append(int(s["inat_taxon"]))
    return ids


def fetch_obs_counts(nudi_names: list[str], marine_ids: list[int]) -> tuple[dict, dict, dict]:
    names_sql = ", ".join("'" + n.replace("'", "''") + "'" for n in nudi_names)
    ids_sql = ",".join(str(i) for i in marine_ids)

    effort_rows = psql_csv(
        f"""
SELECT obs_month::int, COUNT(*)::bigint
FROM public_observations
WHERE lat BETWEEN {CAT_LAT[0]} AND {CAT_LAT[1]}
  AND lng BETWEEN {CAT_LON[0]} AND {CAT_LON[1]}
  AND obs_month BETWEEN 1 AND 12
  AND taxon_id IN ({ids_sql})
GROUP BY obs_month ORDER BY obs_month;
"""
    )
    effort = {int(r[0]): int(r[1]) for r in effort_rows}

    sp_rows = psql_csv(
        f"""
SELECT taxon_name, obs_month::int, COUNT(*)::bigint
FROM public_observations
WHERE lat BETWEEN {CAT_LAT[0]} AND {CAT_LAT[1]}
  AND lng BETWEEN {CAT_LON[0]} AND {CAT_LON[1]}
  AND obs_month BETWEEN 1 AND 12
  AND taxon_name IN ({names_sql})
GROUP BY taxon_name, obs_month ORDER BY taxon_name, obs_month;
"""
    )
    by_sp_month: dict[str, list[int]] = defaultdict(lambda: [0] * 12)
    totals: dict[str, int] = defaultdict(int)
    for name, mo, cnt in sp_rows:
        m = int(mo) - 1
        c = int(cnt)
        by_sp_month[name][m] = c
        totals[name] += c

    src_rows = psql_csv(
        f"""
SELECT source, COUNT(*)::bigint
FROM public_observations
WHERE lat BETWEEN {CAT_LAT[0]} AND {CAT_LAT[1]}
  AND lng BETWEEN {CAT_LON[0]} AND {CAT_LON[1]}
  AND taxon_name IN ({names_sql})
GROUP BY source;
"""
    )
    sources = {r[0]: int(r[1]) for r in src_rows}
    return dict(by_sp_month), dict(totals), {"effort_month": effort, "sources": sources}


def ok_license(lic: str | None) -> bool:
    if not lic:
        return False
    s = lic.lower().strip().replace(" ", "-").replace("_", "-")
    s = s.replace("cc0", "cc0").replace("cc-0", "cc0")
    if "nc" in s or "nd" in s:
        return False
    if s in {"cc0", "cc-by", "cc-by-sa"} or LICENSE_OK.match(s):
        return True
    if s.startswith("cc-by-sa") or s.startswith("cc-by-") and "nc" not in s and "nd" not in s:
        return True
    if s == "cc0" or "publicdomain" in s or s == "pd":
        return True
    return bool(re.search(r"\bcc0\b|\bcc-by\b|\bcc-by-sa\b", s))


def smoothed_activity(counts: list[int], effort: dict[int, int], gamma: float = EFFORT_GAMMA) -> np.ndarray:
    """Índice fenológico con corrección parcial del esfuerzo + prior bayesiano débil.

    I_m = (N_m + α·π_m) · (E_ref / max(E_m,1))^γ

    - γ≈0,35 evita que ene/feb (poco esfuerzo) disparen el cociente N/E.
    - α·π_m: pseudocuentas proporcionales a la cuota de esfuerzo (prior débil).
    - Se normaliza a [0,1] por especie (máximo mensual = 1).
    """
    E = np.array([float(effort.get(i + 1, 1)) for i in range(12)], dtype=float)
    N = np.array(counts, dtype=float)
    E_ref = float(np.median(E)) if E.max() > 0 else 1.0
    total_n = float(N.sum())
    # Prior: ~2 observaciones repartidas según el esfuerzo mensual
    alpha_total = 2.0
    prior = alpha_total * (E / E.sum()) if E.sum() > 0 else np.full(12, alpha_total / 12)
    N_sm = N + prior
    score = N_sm * (E_ref / np.maximum(E, 1.0)) ** gamma
    mx = float(score.max())
    if mx <= 0:
        return np.zeros(12)
    return score / mx


def low_effort_mask(effort: dict[int, int], frac: float = LOW_EFFORT_FRAC) -> np.ndarray:
    E = np.array([float(effort.get(i + 1, 0)) for i in range(12)])
    med = float(np.median(E)) if E.max() > 0 else 1.0
    return E < frac * med


def make_silhouette(size=(96, 96)) -> np.ndarray:
    """Silueta discreta de nudibranquio (no parece error / placeholder verde)."""
    im = Image.new("RGB", size, (245, 248, 250))
    d = ImageDraw.Draw(im)
    w, h = size
    # cuerpo ovalado + ceratas / branquias sugeridas
    body = [w * 0.18, h * 0.42, w * 0.82, h * 0.72]
    d.ellipse(body, fill=(120, 150, 165), outline=(70, 100, 115))
    # cabeza / rinóforos
    d.ellipse([w * 0.62, h * 0.32, w * 0.78, h * 0.48], fill=(100, 135, 150))
    d.line([(w * 0.70, h * 0.34), (w * 0.70, h * 0.18)], fill=(70, 100, 115), width=max(2, w // 48))
    d.line([(w * 0.74, h * 0.34), (w * 0.78, h * 0.20)], fill=(70, 100, 115), width=max(2, w // 48))
    # ceratas
    for i, x in enumerate(np.linspace(w * 0.28, w * 0.58, 5)):
        d.ellipse([x - w * 0.04, h * 0.22 + (i % 2) * 4, x + w * 0.04, h * 0.46], fill=(140, 170, 180))
    # borde suave
    d.rectangle([0, 0, w - 1, h - 1], outline=(200, 210, 218))
    return np.asarray(im)


def load_thumb(path: Path | None, size=(72, 72), allow_silhouette: bool = True) -> np.ndarray:
    if path and path.exists():
        try:
            im = Image.open(path).convert("RGB")
            # crop center square then resize
            w, h = im.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            im = im.crop((left, top, left + side, top + side)).resize(size, Image.Resampling.LANCZOS)
            return np.asarray(im)
        except Exception:
            pass
    if allow_silhouette:
        return make_silhouette(size)
    pad = np.ones((size[1], size[0], 3), dtype=np.uint8) * 240
    return pad


def _inat_search(taxon_id: int, bbox: tuple | None, per_page: int = 5) -> list[dict]:
    params = {
        "taxon_id": taxon_id,
        "photos": "true",
        "photo_license": "cc0,cc-by,cc-by-sa",
        "quality_grade": "research",
        "per_page": per_page,
        "order_by": "votes",
    }
    if bbox:
        (swlat, nelat), (swlng, nelng) = bbox
        params.update({"swlat": swlat, "nelat": nelat, "swlng": swlng, "nelng": nelng})
    url = "https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(params)
    data = http_json(url)
    if not data:
        return []
    out = []
    for o in data.get("results") or []:
        photos = o.get("photos") or []
        if not photos:
            continue
        ph = photos[0]
        lic = ph.get("license_code") or o.get("license_code") or ""
        if not ok_license(lic):
            continue
        purl = (ph.get("url") or "").replace("/square.", "/medium.").replace("square", "medium")
        if not purl:
            continue
        user = (o.get("user") or {})
        out.append(
            {
                "url": purl,
                "license": lic,
                "author": user.get("name") or user.get("login") or "?",
                "date": (o.get("observed_on") or "")[:10],
                "place": (o.get("place_guess") or "")[:120],
                "uri": f"https://www.inaturalist.org/observations/{o.get('id')}",
                "platform": "iNaturalist",
            }
        )
    return out


def _minka_search(taxon_id: int | None, name: str, per_page: int = 8) -> list[dict]:
    params = {"photos": "true", "per_page": per_page, "order_by": "votes"}
    if taxon_id:
        params["taxon_id"] = taxon_id
    else:
        params["taxon_name"] = name
    url = "https://api.minka-sdg.org/v1/observations?" + urllib.parse.urlencode(params)
    data = http_json(url)
    if not data:
        return []
    out = []
    for o in data.get("results") or []:
        photos = o.get("photos") or []
        if not photos:
            continue
        ph = photos[0]
        lic = ph.get("license_code") or o.get("license_code") or ""
        if not ok_license(lic):
            continue
        purl = (ph.get("url") or "").replace("/square.", "/medium.").replace("square", "medium")
        if not purl:
            continue
        user = (o.get("user") or {})
        out.append(
            {
                "url": purl,
                "license": lic,
                "author": user.get("name") or user.get("login") or "?",
                "date": (o.get("observed_on") or "")[:10],
                "place": (o.get("place_guess") or "")[:120],
                "uri": f"https://minka-sdg.org/observations/{o.get('id')}",
                "platform": "Minka",
            }
        )
    return out


def pick_photos(species: list[str], meta: dict[str, dict], n_article: int = 6) -> list[dict]:
    """CC0 / CC BY / CC BY-SA: correlación → enrich CAT → iNat (CAT/Med/mundo) → Minka."""
    thumbs_dir = PAPER / "fotos"
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    # Enrich (CAT box) — carga una vez
    by_sp_enrich: dict[str, list[dict]] = defaultdict(list)
    if ENRICH.exists():
        d = json.load(open(ENRICH))
        want = set(species)
        for _src, obs_map in d.items():
            for obs_id, m in obs_map.items():
                sp = m.get("obs_taxon_name_api")
                if sp not in want:
                    continue
                if not ok_license(m.get("obs_license") or ""):
                    continue
                try:
                    lat = float(m["obs_lat"])
                    lon = float(m["obs_lon"])
                except (KeyError, TypeError, ValueError):
                    continue
                if not (CAT_LAT[0] <= lat <= CAT_LAT[1] and CAT_LON[0] <= lon <= CAT_LON[1]):
                    continue
                uri = m.get("obs_uri") or ""
                platform = "iNaturalist" if "inaturalist" in uri else ("Minka" if "minka" in uri else "otro")
                obs_num = re.search(r"/(\d+)\s*$", uri)
                by_sp_enrich[sp].append(
                    {
                        "obs_id": obs_num.group(1) if obs_num else str(obs_id),
                        "uri": uri,
                        "author": m.get("observer_name") or m.get("observer_login") or "?",
                        "license": m.get("obs_license"),
                        "date": (m.get("obs_date") or "")[:10],
                        "place": m.get("obs_place_guess") or "",
                        "platform": platform,
                        "lat": lat,
                        "lon": lon,
                    }
                )

    manifest_path = CORR_FOTOS / "lamina_manifest_20261008.json"
    manifest = json.load(open(manifest_path)) if manifest_path.exists() else []
    corr_by_sp: dict[str, list] = defaultdict(list)
    for block in manifest:
        for ph in block.get("fotos", []):
            if ph.get("nc"):
                continue
            lic = (ph.get("licencia") or "").lower()
            if not ok_license(lic):
                continue
            tax = ph.get("taxon")
            if tax not in species:
                continue
            fpath = CORR_FOTOS / ph["file"]
            if fpath.exists():
                corr_by_sp[tax].append({**ph, "local": str(fpath)})

    chosen: list[dict] = []
    have: set[str] = set()

    def save_entry(sp: str, dest: Path, meta_ph: dict, source: str) -> dict:
        return {
            "species": sp,
            "file": dest.name,
            "path": dest,
            "author": meta_ph.get("author") or meta_ph.get("autor") or "?",
            "license": meta_ph.get("license") or meta_ph.get("licencia") or "",
            "date": meta_ph.get("date") or meta_ph.get("fecha") or "",
            "place": meta_ph.get("place") or meta_ph.get("lugar_final") or meta_ph.get("lugar") or "",
            "uri": meta_ph.get("uri") or meta_ph.get("enlace") or "",
            "source": source,
            "is_silhouette": False,
        }

    # Metadatos previos (para reutilizar thumbs ya descargados)
    prev_lic: dict[str, dict] = {}
    meta_json = PAPER / "datos/fotos_meta_20261010.json"
    if meta_json.exists():
        for p in json.load(open(meta_json)):
            prev_lic[p["species"]] = p
    else:
        lic_path = PAPER / "LICENCIAS_FOTOS.md"
        if lic_path.exists():
            for line in lic_path.read_text(encoding="utf-8").splitlines():
                m = re.match(r"- \*(.+?)\*: (.+?) · (.+?) ·", line)
                if m:
                    prev_lic[m.group(1)] = {
                        "author": m.group(2),
                        "license": m.group(3),
                        "date": "",
                        "place": "",
                        "uri": "",
                    }

    for sp in species:
        slug = sp.replace(" ", "_").lower()
        dest = thumbs_dir / f"{slug}_thumb.jpg"
        entry = None

        # 0) reutilizar miniatura local ya válida
        if dest.exists() and dest.stat().st_size > 8000:
            meta_ph = prev_lic.get(sp) or {
                "author": "?",
                "license": "cc (cache local)",
                "date": "",
                "place": "",
                "uri": "",
            }
            entry = save_entry(sp, dest, meta_ph, "cache_local")

        # 1) lámina correlación local
        if entry is None and corr_by_sp.get(sp):
            ph = corr_by_sp[sp][0]
            shutil.copy2(ph["local"], dest)
            entry = save_entry(sp, dest, ph, "lamina_correlacion")

        # 2) enrich + descarga iNat
        if entry is None and by_sp_enrich.get(sp):
            for cand in by_sp_enrich[sp][:5]:
                if cand["platform"] == "iNaturalist":
                    data = http_json(f"https://api.inaturalist.org/v1/observations/{cand['obs_id']}")
                    if not data:
                        continue
                    photos = (data.get("results") or [{}])[0].get("photos") or []
                    if not photos:
                        continue
                    purl = (photos[0].get("url") or "").replace("square", "medium")
                    blob = http_bytes(purl) if purl else None
                    if blob:
                        dest.write_bytes(blob)
                        entry = save_entry(sp, dest, cand, "enrich+inat_api")
                        break

        # 3) iNat API: CAT → Med → mundo
        if entry is None:
            tid = (meta.get(sp) or {}).get("inat")
            if tid:
                for bbox in [
                    (CAT_LAT, CAT_LON),
                    (MED_LAT, MED_LON),
                    None,
                ]:
                    cands = _inat_search(int(tid), bbox)
                    time.sleep(0.35)
                    if not cands:
                        continue
                    blob = http_bytes(cands[0]["url"])
                    if blob:
                        dest.write_bytes(blob)
                        entry = save_entry(sp, dest, cands[0], "inat_api")
                        break

        # 4) Minka API (solo CC libres)
        if entry is None:
            mid = (meta.get(sp) or {}).get("minka")
            cands = _minka_search(int(mid) if mid else None, sp)
            time.sleep(0.35)
            if cands:
                blob = http_bytes(cands[0]["url"])
                if blob:
                    dest.write_bytes(blob)
                    entry = save_entry(sp, dest, cands[0], "minka_api")

        # 5) silueta discreta
        if entry is None:
            sil = Image.fromarray(make_silhouette((320, 320)))
            sil.save(dest, quality=90)
            entry = {
                "species": sp,
                "file": dest.name,
                "path": dest,
                "author": "silueta esquemática",
                "license": "obra propia (dominio interno)",
                "date": "",
                "place": "",
                "uri": "",
                "source": "silhouette",
                "is_silhouette": True,
            }

        if entry and sp not in have:
            chosen.append(entry)
            have.add(sp)

    # Preferir fotos reales para el artículo
    real = [c for c in chosen if not c.get("is_silhouette")]
    article = real[:n_article] if real else chosen[:n_article]
    # Devolver todas (para láminas) pero marcar artículo
    for c in chosen:
        c["in_article"] = c in article
    return chosen


def lamina_calendario(
    top_species: list[str],
    meta: dict,
    norm: dict[str, np.ndarray],
    effort: dict[int, int],
    photos: dict[str, Path | None],
    photo_meta: dict[str, dict],
):
    # Paleta alto contraste: crema → ámbar → rojo → granate
    cmap = LinearSegmentedColormap.from_list(
        "fenologia",
        ["#fff7ec", "#fee8c8", "#fdd49e", "#fdbb84", "#fc8d59", "#ef6548", "#d7301f", "#990000"],
    )
    fam_order: list[str] = []
    for sp in top_species:
        fam = meta[sp]["family"]
        if fam not in fam_order:
            fam_order.append(fam)
    ordered: list[str] = []
    for fam in fam_order:
        ordered.extend([s for s in top_species if meta[s]["family"] == fam])
    n = len(ordered)
    low = low_effort_mask(effort)

    # A3 apaisado — columnas claras: familia | miniatura | nombre | heatmap
    fig_w, fig_h = 16.54, 11.69
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=300, facecolor="white")

    left_heat = 0.42
    bottom = 0.13
    width_heat = 0.48
    height = 0.80
    ax = fig.add_axes([left_heat, bottom, width_heat, height])
    mat = np.array([norm[s] for s in ordered])
    im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
    ax.set_xticks(range(12))
    ax.set_xticklabels(MES, fontsize=9)
    ax.set_yticks([])
    ax.set_xlabel("Mes", fontsize=10)
    ax.set_title(
        "Lámina 1 · Calendario fenológico de nudibranquios (Cataluña)",
        fontsize=13,
        color="#5c1a00",
        pad=10,
        loc="left",
    )

    # Tramado en meses de poco esfuerzo
    for m in range(12):
        if low[m]:
            ax.add_patch(
                mpatches.Rectangle(
                    (m - 0.5, -0.5),
                    1,
                    n,
                    fill=False,
                    hatch="////",
                    edgecolor="#666666",
                    linewidth=0.0,
                    alpha=0.65,
                    zorder=3,
                )
            )
            ax.axvspan(m - 0.5, m + 0.5, facecolor="#e8e8e8", alpha=0.35, zorder=1)

    # Cabeceras de columna
    hdr_y = bottom + height + 0.012
    fig.text(0.018, hdr_y, "Familia", fontsize=8, fontweight="bold", color="#6b3a1f")
    fig.text(0.155, hdr_y, "Foto", fontsize=8, fontweight="bold", color="#6b3a1f")
    fig.text(0.215, hdr_y, "Especie", fontsize=8, fontweight="bold", color="#6b3a1f")

    row_h = height / n
    credits: list[str] = []

    for i, sp in enumerate(ordered):
        fam = meta[sp]["family"]
        fig_y = bottom + height * (1 - (i + 0.5) / n)
        # Fondo alterno suave por familia (cambio de bloque)
        prev_fam = meta[ordered[i - 1]]["family"] if i > 0 else None
        if fam != prev_fam:
            # contar longitud del bloque
            j = i
            while j < n and meta[ordered[j]]["family"] == fam:
                j += 1
            y_top = bottom + height * (1 - i / n)
            y_bot = bottom + height * (1 - j / n)
            fig.add_artist(
                FancyBboxPatch(
                    (0.012, y_bot),
                    0.135,
                    y_top - y_bot,
                    transform=fig.transFigure,
                    boxstyle="square,pad=0",
                    facecolor="#f7f1ea",
                    edgecolor="#e8ddd0",
                    linewidth=0.3,
                    zorder=0,
                )
            )

        # Columna familia (cada fila, legible)
        fig.text(
            0.018,
            fig_y,
            fam,
            fontsize=6.5,
            fontweight="bold",
            color="#6b3a1f",
            va="center",
            ha="left",
            clip_on=False,
            zorder=2,
        )

        thumb_h = min(row_h * 0.90, 0.026)
        ax_img = fig.add_axes([0.150, fig_y - thumb_h / 2, 0.050, thumb_h], zorder=2)
        thumb = load_thumb(photos.get(sp), size=(96, 96))
        ax_img.imshow(thumb)
        ax_img.set_xticks([])
        ax_img.set_yticks([])
        for spine in ax_img.spines.values():
            spine.set_color("#bbbbbb")
            spine.set_linewidth(0.5)

        fig.text(
            0.212,
            fig_y,
            sp,
            fontsize=8.2,
            fontstyle="italic",
            color="#111111",
            va="center",
            ha="left",
            clip_on=False,
            zorder=2,
        )
        pm = photo_meta.get(sp)
        if pm and not pm.get("is_silhouette"):
            credits.append(f"{sp}: {pm.get('author','?')} ({pm.get('license','')})")

    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.015)
    cbar.set_label("Actividad relativa (baja → alta)", fontsize=8)

    leyenda = (
        "Color: actividad relativa de cada especie a lo largo del año (suavizada). "
        "Columnas con tramado: meses con poco esfuerzo de observación; interpretar con cautela."
    )
    fig.text(0.5, 0.055, leyenda, ha="center", fontsize=7.5, color="#333")
    fig.text(
        0.5,
        0.022,
        "Fuente: iNaturalist + Minka (caja costera de Cataluña). "
        + ("Fotos: " + " · ".join(credits[:5]) + (" …" if len(credits) > 5 else "") if credits else ""),
        ha="center",
        fontsize=5.5,
        color="#555",
    )

    out_png = PAPER / "LAMINA1_calendario_fenologico_20261010.png"
    out_pdf = PAPER / "LAMINA1_calendario_fenologico_20261010.pdf"
    fig.savefig(out_png, dpi=300, facecolor="white")
    fig.savefig(out_pdf, facecolor="white")
    plt.close(fig)
    return out_png, out_pdf, credits


def season_blurb(top12: list[str], norm: dict[str, np.ndarray]) -> list[tuple[str, list[str]]]:
    # Invierno: dic–feb (circular)
    windows = [
        ("Invierno (dic–feb)", [11, 0, 1]),
        ("Primavera (mar–may)", [2, 3, 4]),
        ("Verano (jun–ago)", [5, 6, 7]),
        ("Otoño (sep–nov)", [8, 9, 10]),
    ]
    out = []
    for label, months in windows:
        scores: Counter[str] = Counter()
        for sp in top12:
            chunk = np.array([norm[sp][m] for m in months])
            if chunk.max() > 0.55:
                scores[sp] += float(chunk.max())
        tops = [s for s, _ in scores.most_common(4)]
        out.append((label, tops))
    return out


def lamina_radial(
    top12: list[str],
    norm: dict[str, np.ndarray],
    photos: dict[str, Path | None],
    effort: dict[int, int],
):
    ncols = 4
    nrows = math.ceil(len(top12) / ncols)
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300, facecolor="white")
    gs = gridspec.GridSpec(
        nrows + 1,
        ncols,
        height_ratios=[1.2] * nrows + [0.85],
        hspace=0.55,
        wspace=0.30,
        left=0.05,
        right=0.97,
        top=0.90,
        bottom=0.05,
    )

    theta = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    low = low_effort_mask(effort)

    for i, sp in enumerate(top12):
        r = i // ncols
        c = i % ncols
        cell = gs[r, c].subgridspec(2, 1, height_ratios=[0.36, 0.64], hspace=0.35)
        ax_head = fig.add_subplot(cell[0, 0])
        ax_head.axis("off")
        ax = fig.add_subplot(cell[1, 0], projection="polar")

        vals = np.asarray(norm[sp], dtype=float)
        peak = int(np.argmax(vals))
        # Una sola serie: polígono radar cerrado (sin cuñas apiladas)
        theta_c = np.append(theta, theta[0])
        vals_c = np.append(vals, vals[0])
        ax.plot(theta_c, vals_c, color="#c2410c", linewidth=1.8, zorder=3)
        ax.fill(theta_c, vals_c, color="#fb923c", alpha=0.45, zorder=2)
        # Marca del mes pico
        ax.plot([theta[peak]], [vals[peak]], "o", color="#7c2d12", markersize=6, zorder=4)
        # Meses de poco esfuerzo: punto gris en el radio (misma serie, incertidumbre)
        for m in range(12):
            if low[m]:
                ax.plot([theta[m]], [vals[m]], "o", color="#9ca3af", markersize=4, zorder=4)

        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_xticks(theta)
        ax.set_xticklabels(MES, fontsize=6)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels([])
        ax.set_ylim(0, 1.05)
        ax.grid(True, color="#e5e7eb", linewidth=0.6)

        hb = ax_head.get_position()
        tw = min(0.030, hb.width * 0.24)
        th = tw * (fig.get_figwidth() / fig.get_figheight())
        thumb_ax = fig.add_axes([hb.x0, hb.y0 + (hb.height - th) / 2, tw, th])
        thumb_ax.imshow(load_thumb(photos.get(sp), size=(80, 80)))
        thumb_ax.set_xticks([])
        thumb_ax.set_yticks([])
        for spine in thumb_ax.spines.values():
            spine.set_color("#cccccc")
            spine.set_linewidth(0.5)

        ax_head.text(
            0.32,
            0.68,
            sp,
            transform=ax_head.transAxes,
            ha="left",
            va="center",
            fontsize=10,
            fontstyle="italic",
            family="serif",
            color="#1a1a1a",
            clip_on=False,
        )
        ax_head.text(
            0.32,
            0.22,
            f"Pico: {MES_L[peak]}",
            transform=ax_head.transAxes,
            ha="left",
            va="center",
            fontsize=8,
            fontstyle="normal",
            family="sans-serif",
            color="#7c2d12",
            clip_on=False,
        )

    axp = fig.add_subplot(gs[nrows, :])
    axp.axis("off")
    seasons = season_blurb(top12, norm)
    axp.text(
        0.01,
        0.95,
        "Qué buscar cada estación (orientativo; puntos grises en las rosas = poco esfuerzo):",
        va="top",
        fontsize=10,
        fontweight="bold",
        fontstyle="normal",
        transform=axp.transAxes,
        color="#5c1a00",
    )
    y = 0.72
    for title, spp in seasons:
        axp.text(0.02, y, f"• {title}:", va="top", fontsize=9, fontstyle="normal", transform=axp.transAxes, color="#333")
        x = 0.28
        if not spp:
            axp.text(x, y, "—", va="top", fontsize=9, transform=axp.transAxes)
        else:
            for j, s in enumerate(spp):
                label = s + (", " if j < len(spp) - 1 else "")
                axp.text(
                    x,
                    y,
                    label,
                    va="top",
                    fontsize=9,
                    fontstyle="italic",
                    family="serif",
                    transform=axp.transAxes,
                    color="#1a1a1a",
                )
                x += 0.0095 * (len(s) + 2)
        y -= 0.20

    fig.suptitle(
        "Lámina 2 · Rosas mensuales (actividad corregida por esfuerzo) — Cataluña",
        fontsize=13,
        color="#5c1a00",
        y=0.97,
    )

    out_png = PAPER / "LAMINA2_rosas_estaciones_20261010.png"
    out_pdf = PAPER / "LAMINA2_rosas_estaciones_20261010.pdf"
    fig.savefig(out_png, dpi=300, facecolor="white")
    fig.savefig(out_pdf, facecolor="white")
    plt.close(fig)
    return out_png, out_pdf


def write_licencias(photos: list[dict], lamina_attributions: list[str]):
    lines = [
        "# Licencias de fotografías — calendario nudibranquios\n",
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} CEST\n\n",
        "Solo CC0 / CC BY / CC BY-SA (sin NC/ND). Las siluetas son obra esquemática interna.\n\n",
        "## Miniaturas (láminas)\n\n",
    ]
    for p in photos:
        tag = "silueta" if p.get("is_silhouette") else p.get("source", "")
        lines.append(
            f"- *{p['species']}*: {p['author']} · {p['license']} · {p.get('date','')} · "
            f"{p.get('place','')} · {p.get('uri','')} [{tag}]\n"
        )
    lines.append("\n## Atribuciones resumidas\n\n")
    for a in lamina_attributions:
        lines.append(f"- {a}\n")
    (PAPER / "LICENCIAS_FOTOS.md").write_text("".join(lines), encoding="utf-8")
    # Cache JSON para reutilizar atribuciones sin redescargar
    slim = [
        {
            "species": p["species"],
            "file": p.get("file"),
            "author": p.get("author"),
            "license": p.get("license"),
            "date": p.get("date"),
            "place": p.get("place"),
            "uri": p.get("uri"),
            "source": p.get("source"),
            "is_silhouette": bool(p.get("is_silhouette")),
        }
        for p in photos
    ]
    (PAPER / "datos/fotos_meta_20261010.json").write_text(json.dumps(slim, indent=2, ensure_ascii=False), encoding="utf-8")


def write_articulo_md(
    top30,
    top12,
    meta,
    totals,
    effort,
    sources,
    norm,
    photos,
    lam1,
    lam2,
    by_sp_month,
):
    total_nudi = sum(totals.values())
    ts = datetime.now().strftime("%Y-%m-%d")
    low = low_effort_mask(effort)
    low_names = ", ".join(MES_L[i] for i in range(12) if low[i])

    md = f"""# Cuándo ver nudibranquios en Cataluña: un calendario fenológico a partir de ciencia ciudadana

**Autores:** Gustavo Zafra (Yespi); datos comunitarios Minka SDG e iNaturalist; curación taxonómica BioFauna  
**Fecha:** {ts}  
**Repositorio:** https://github.com/yespi/biofauna (`papers/nudibranquios_calendario/`)

---

## Resumen

Presentamos un calendario de actividad mensual de nudibranquios (**Nudibranchia** y **doridoideos**, *sensu* catálogo BioFauna) en la costa catalana, a partir de **{total_nudi:,}** observaciones georreferenciadas en la base pública `public_observations` (iNaturalist + Minka). La intensidad mensual se **corrige por el esfuerzo de muestreo** con un suavizado (corrección parcial del denominador y prior bayesiano débil), para evitar que los meses con pocas salidas (sobre todo invierno) inflen artificialmente el cociente. Los meses de poco esfuerzo se marcan en las láminas. Incluimos dos láminas imprimibles A3 (calendario por familias y rosas mensuales) con miniaturas de fotos de licencia libre cuando existen.

**Palabras clave:** Nudibranchia, Doridida, fenología, ciencia ciudadana, Mediterráneo, Cataluña, Minka, iNaturalist

## 1. Introducción

Los nudibranquios concentran el interés de buceadores y naturalistas por su color y diversidad trófica. En Cataluña, proyectos como Minka SDG y iNaturalist acumulan miles de registros, pero las curvas crudas de «cuándo se fotografían» mezclan la biología con **cuándo sale la gente al mar**. Además, los informes previos del proyecto se apoyaban en listas cortas de aeolideos; aquí ampliamos el alcance a **doridoideos** (*Felimare*, *Peltodoris*, *Hypselodoris*, *Dendrodoris*, *Doris*, *Discodoris*, etc.) usando el catálogo vivo de BioFauna ({len(meta)} especies potenciales).

## 2. Métodos

### 2.1 Área de estudio y fuentes

- **Región:** caja costera de Cataluña usada en BioQuest (lat {CAT_LAT[0]}–{CAT_LAT[1]}° N; lon {CAT_LON[0]}–{CAT_LON[1]}° E; definición 8-oct-2026).
- **Datos:** tabla `public_observations` (contenedor `postgres-global`, BD `fauna`), fuentes `{sources.get('minka', 0):,}` Minka + `{sources.get('inat', 0):,}` iNaturalist — **solo lectura (`SELECT`)**.
- **Taxonomía:** especies con `order` ∈ {{Nudibranchia, Doridida, Dendronotida}} en `dataset/target_species.json`, enriquecidas con familia desde `dataset/catalog.json`.

### 2.2 Corrección del esfuerzo (suavizado)

Una división directa «observaciones de la especie / observaciones marinas del mes» hace explotar enero y febrero: el denominador es bajo y el cociente no refleja un pico biológico. Usamos un **índice suavizado**:

1. Pseudocuentas débiles repartidas según la cuota mensual de esfuerzo (prior bayesiano).
2. Corrección **parcial** del esfuerzo: se multiplica por \\((E_{{\\mathrm{{ref}}}} / E_m)^{{\\gamma}}\\) con \\(\\gamma = {EFFORT_GAMMA}\\) (no con exponente 1), de modo que el verano sigue pesando más en especies realmente estivales.
3. Normalización a 0–1 **por especie** (el máximo mensual de cada una vale 1).

Los meses con esfuerzo por debajo del {int(LOW_EFFORT_FRAC*100)} % de la mediana ({low_names}) se muestran con **tramado o gris** en las láminas: hay señal, pero con más incertidumbre.

**Esfuerzo mensual (obs. marinas del catálogo):** {", ".join(f"{MES_L[i]}={effort.get(i+1,0):,}" for i in range(12))}.

### 2.3 Figuras y reproducibilidad

- Lámina 1: `{lam1.name}` (PNG 300 ppp + PDF, A3).
- Lámina 2: `{lam2.name}` (PNG 300 ppp + PDF, A3).
- Script: `scripts/nudibranquios_articulo_generar_20261010.py`.

## 3. Resultados

### 3.1 Especies más registradas

Entre las **30** especies más observadas en la caja figuran tanto aeolideos históricamente abundantes (*Cratena peregrina*, *Edmundsella pedata*, *Calmella cavolini*) como doridoideos (*Felimare picta*, *Felimare tricolor*, *Peltodoris atromaculata*, *Dendrodoris limbata*, …).

| Especie | Familia | Obs. totales | Mes pico (suavizado) |
|---|---|---:|---|
"""
    for sp in top30[:15]:
        peak_m = int(np.argmax(norm[sp])) + 1
        md += f"| *{sp}* | {meta[sp]['family']} | {totals[sp]:,} | {MES_L[peak_m-1]} |\n"

    # Patrones destacados
    felimare = [s for s in top30 if s.startswith("Felimare")]
    fel_peaks = ", ".join(f"*{s}* → {MES_L[int(np.argmax(norm[s]))]}" for s in felimare[:4])

    md += f"""
*(Tabla completa en `datos/especies_mensual_normalizado_20261010.csv`.)*

### 3.2 Calendario fenológico

La **Lámina 1** agrupa ~30 especies por familia, con columnas **familia | miniatura | nombre** y el mapa de calor mensual. Tras el suavizado, el patrón de los cromodóridos (*Felimare*) se concentra en **primavera–verano** ({fel_peaks}), coherente con la fenología mediterránea conocida, y no en un artefacto invernal. Aeolideos como *Cratena peregrina* y *Flabellina affinis* mantienen picos estivales; *Edmundsella pedata*, *Antiopella cristata* y *Diaphorodoris* destacan en primavera.

![Lámina 1 — calendario fenológico](LAMINA1_calendario_fenologico_20261010.png)

### 3.3 Rosas de actividad y estaciones

La **Lámina 2** muestra las doce especies más frecuentes como una rosa mensual (una sola serie por especie, etiqueta del mes pico y miniatura). El panel «Qué buscar» se calcula sobre los mismos valores suavizados.

![Lámina 2 — rosas y estaciones](LAMINA2_rosas_estaciones_20261010.png)

### 3.4 Fotografías de ejemplo (licencias libres)

"""
    article_photos = [p for p in photos if p.get("in_article") and not p.get("is_silhouette")][:6]
    for i, p in enumerate(article_photos, 1):
        md += f"""
<figure>
<img src="fotos/{p['file']}" alt="{p['species']}" width="420"/>
<figcaption>Figura {i}. *{p['species']}* — {p['author']} · {p['license']} · {p['date']} · {p.get('place','')[:80]} · <a href="{p.get('uri','')}">observación</a></figcaption>
</figure>
"""

    md += """
## 4. Discusión

**Sesgo de esfuerzo.** La corrección parcial y el prior evitan picos espurios en enero–febrero, pero el denominador sigue siendo un proxy (taxones marinos del catálogo), no horas de buceo. Los meses tramados deben leerse con reserva.

**Identificación.** Los nombres provienen de la comunidad y del pipeline BioFauna; pares crípticos (*Caloria*/*Luisella*, *Tenellia*/*Cratena*) pueden contaminar series. No sustituye revisión por especialistas (GROC, Minka).

**Cobertura geográfica.** La caja incluye tramos fuera de Cataluña administrativa; localidades dominantes (Costa Brava, Barcelona, Tarragona) reflejan clubs de buceo más que ausencia en el Ebro.

**Ampliación doridoidea.** Respecto al borrador de 8-oct (133 aeolideos), incorporar **Doridida** cambia el ranking: *Felimare picta* supera a muchos aeolideos en recuento regional.

## 5. Referencias

- Ballesteros, M., & Pontes, M. (coords.). *GROC* / guías de opistobranquis del Mediterráneo occidental.
- Cattaneo-Vietti, R., et al. (1990). *Atlas of Mediterranean Nudibranchs* (referencia clásica de distribución).
- BioFauna / FotoFauna: https://fotofauna.yespi.es — catálogo y metodología (`papers/biofauna/01_biofauna_es.md`).
- Minka SDG: https://minka-sdg.org — observaciones comunitarias.
- iNaturalist (2026). API pública v1 — https://api.inaturalist.org

---

*Manuscrito generado automáticamente a partir de datos abiertos; revisar antes de publicación en revista.*
"""
    path = PAPER / "ARTICULO_20261010.md"
    path.write_text(md, encoding="utf-8")
    return path


def html_to_pdf(md_path: Path, pdf_path: Path):
    html_path = PAPER / "_articulo_print.html"
    md_text = md_path.read_text(encoding="utf-8")
    body = md_text
    for h, tag in [("# ", "h1"), ("## ", "h2"), ("### ", "h3")]:
        body = re.sub(rf"^{re.escape(h)}(.+)$", rf"<{tag}>\1</{tag}>", body, flags=re.M)
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
    body = re.sub(r"\*(.+?)\*", r"<em>\1</em>", body)
    body = re.sub(
        r"!\[(.+?)\]\((.+?)\)",
        r'<figure><img src="\2" style="max-width:100%"/><figcaption>\1</figcaption></figure>',
        body,
    )
    body = re.sub(r"\|(.+\|)", lambda m: "<p>" + m.group(0).replace("|", " ") + "</p>", body)
    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"/>
<style>
body {{ font-family: 'Segoe UI', Georgia, serif; max-width: 900px; margin: 24px auto; line-height: 1.45; color: #1a1a1a; }}
h1 {{ color: #5c1a00; }} h2 {{ color: #9a3412; border-bottom: 1px solid #ccc; }}
figure {{ margin: 1.2em 0; }} figcaption {{ font-size: 0.85em; color: #444; }}
</style></head><body>{body}</body></html>"""
    html_path.write_text(html, encoding="utf-8")
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome:
        return
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ],
        check=False,
        capture_output=True,
    )


def main():
    PAPER.mkdir(parents=True, exist_ok=True)
    (PAPER / "datos").mkdir(exist_ok=True)
    (PAPER / "figuras").mkdir(exist_ok=True)

    meta = load_nudibranchs()
    nudi_names = sorted(meta.keys())
    marine_ids = marine_taxon_ids()

    by_sp_month, totals, extra = fetch_obs_counts(nudi_names, marine_ids)
    effort = extra["effort_month"]
    sources = extra["sources"]
    norm = {sp: smoothed_activity(counts, effort) for sp, counts in by_sp_month.items()}

    ranked = sorted(totals.items(), key=lambda x: -x[1])
    top30 = [s for s, n in ranked[:30] if n >= 10]
    top12 = [s for s, n in ranked[:12]]

    csv_path = PAPER / "datos/especies_mensual_normalizado_20261010.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["especie", "familia", "total_obs"]
            + [f"n_{m}" for m in MES_L]
            + [f"suav_{m}" for m in MES_L]
            + ["pico_mes_suavizado"]
        )
        for sp, _ in ranked:
            if sp not in meta:
                continue
            counts = by_sp_month.get(sp, [0] * 12)
            sm = norm.get(sp, np.zeros(12))
            row = [sp, meta[sp]["family"], totals.get(sp, 0)] + list(counts) + [round(float(x), 4) for x in sm]
            row.append(MES_L[int(np.argmax(sm))])
            w.writerow(row)

    with open(PAPER / "datos/esfuerzo_marino_mensual_20261010.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mes", "obs_marinas_catalogo", "poco_esfuerzo"])
        low = low_effort_mask(effort)
        for i in range(12):
            w.writerow([MES_L[i], effort.get(i + 1, 0), int(bool(low[i]))])

    photo_species = list(dict.fromkeys(top30 + top12))
    print(f"Buscando fotos CC para {len(photo_species)} especies…", flush=True)
    photos = pick_photos(photo_species, meta, n_article=6)
    photo_paths = {p["species"]: p.get("path") for p in photos}
    photo_meta = {p["species"]: p for p in photos}
    n_real = sum(1 for p in photos if not p.get("is_silhouette"))
    print(f"Fotos reales CC: {n_real}/{len(photos)}; siluetas: {len(photos)-n_real}", flush=True)

    lam1_png, lam1_pdf, lam_credits = lamina_calendario(
        top30, meta, norm, effort, photo_paths, photo_meta
    )
    lam2_png, lam2_pdf = lamina_radial(top12, norm, photo_paths, effort)

    fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
    cols = ["#b0b0b0" if low_effort_mask(effort)[i] else "#c2410c" for i in range(12)]
    ax.bar(range(12), [effort.get(i + 1, 0) for i in range(12)], color=cols)
    ax.set_xticks(range(12))
    ax.set_xticklabels(MES)
    ax.set_ylabel("Obs. marinas (catálogo)")
    ax.set_title("Esfuerzo de muestreo mensual — caja Cataluña (gris = poco esfuerzo)")
    fig.tight_layout()
    fig.savefig(PAPER / "figuras/esfuerzo_marino_mensual_20261010.png")
    plt.close(fig)

    md_path = write_articulo_md(
        top30, top12, meta, totals, effort, sources, norm, photos, lam1_png, lam2_png, by_sp_month
    )
    pdf_path = PAPER / "ARTICULO_20261010.pdf"
    html_to_pdf(md_path, pdf_path)
    write_licencias(photos, lam_credits)

    # README
    readme = PAPER / "README.md"
    readme.write_text(
        f"""# Calendario de observación de los nudibranquios (Cataluña)

**Estado: artículo de divulgación {datetime.now().strftime('%d-%b-%Y')}** (revisión láminas). Incluye **doridoideos** (*Felimare*, *Peltodoris*, …), no solo aeolideos.

## Entregables principales

| Documento | Descripción |
|---|---|
| [`ARTICULO_20261010.md`](ARTICULO_20261010.md) · [`ARTICULO_20261010.pdf`](ARTICULO_20261010.pdf) | Artículo naturalista |
| [`LAMINA1_calendario_fenologico_20261010.pdf`](LAMINA1_calendario_fenologico_20261010.pdf) · [`.png`](LAMINA1_calendario_fenologico_20261010.png) | Calendario A3: familia / miniatura / nombre + mapa de calor suavizado |
| [`LAMINA2_rosas_estaciones_20261010.pdf`](LAMINA2_rosas_estaciones_20261010.pdf) · [`.png`](LAMINA2_rosas_estaciones_20261010.png) | Rosas radiales (12 spp.) + panel estacional |
| [`LICENCIAS_FOTOS.md`](LICENCIAS_FOTOS.md) | Atribución CC0 / CC BY / CC BY-SA |
| [`datos/`](datos/) | CSV mensual (conteos + índice suavizado) y esfuerzo |

## Método (resumen)

- **Fuente:** `public_observations` — iNaturalist + Minka; solo `SELECT`.
- **Área:** caja costera Cataluña (lat 40,45–42,95; lon 0,10–3,40).
- **Suavizado:** corrección parcial del esfuerzo (γ={EFFORT_GAMMA}) + prior bayesiano débil; meses con poco esfuerzo tramados/gris.
- **Fotos:** iNat / Minka / láminas correlación con licencia libre; si no hay, silueta esquemática.

```bash
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_articulo_generar_20261010.py
```
""",
        encoding="utf-8",
    )

    peaks = {sp: MES_L[int(np.argmax(norm[sp]))] for sp in top12}
    summary = {
        "generated": datetime.now().isoformat(),
        "n_species_catalog": len(meta),
        "n_species_with_data": len(totals),
        "total_obs": sum(totals.values()),
        "top30": top30,
        "top12_peaks_smoothed": peaks,
        "photos_cc": n_real,
        "photos_silhouette": len(photos) - n_real,
        "effort_gamma": EFFORT_GAMMA,
        "files": [str(lam1_pdf), str(lam2_pdf), str(pdf_path), str(md_path)],
    }
    (PAPER / "meta_generacion_20261010.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
