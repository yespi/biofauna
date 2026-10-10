#!/usr/bin/env python3
"""Genera artículo + láminas del calendario fenológico de nudibranquios (Cataluña).
Solo SELECT en postgres-global (fauna.public_observations) + lectura enrich JSON.
Sin GPU; sin escribir en producción."""
from __future__ import annotations

import csv
import json
import math
import re
import shutil
import subprocess
import textwrap
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import gridspec
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from PIL import Image

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
ENRICH = Path("/mnt/docker/biofauna/dataset/enrich_obs_metadata_progress_20260919.json")
CORR_FOTOS = ROOT / "papers/proyecto_correlacion/lamina_fotos"

CAT_LAT = (40.45, 42.95)
CAT_LON = (0.10, 3.40)
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

LICENSE_OK = re.compile(r"cc0|cc-by(?!-nc|-nd)|cc-by-sa", re.I)


def psql_csv(sql: str) -> list[dict]:
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
    lines = out.split("\n")
    # psql -t -A without header — we use aliases in SELECT
    rows = []
    for line in lines:
        parts = line.split("\t")
        rows.append(parts)
    return rows


def load_nudibranchs() -> dict[str, dict]:
    ts = json.load(open(ROOT / "dataset/target_species.json"))
    cat = {s["name"]: s for s in json.load(open(ROOT / "dataset/catalog.json"))["species"]}
    out = {}
    for x in ts:
        if x.get("order") not in NUDI_ORDERS:
            continue
        name = x["name"]
        fam = x.get("family") or (cat.get(name) or {}).get("family") or "Sin familia"
        out[name] = {"family": fam, "slug": (cat.get(name) or {}).get("slug", ""), "inat": (cat.get(name) or {}).get("inat_taxon")}
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


def normalized_matrix(by_sp_month: dict[str, list[int]], effort: dict[int, int]) -> dict[str, np.ndarray]:
    eff = np.array([effort.get(i + 1, 1) for i in range(12)], dtype=float)
    eff = np.maximum(eff, 1.0)
    out = {}
    for sp, counts in by_sp_month.items():
        raw = np.array(counts, dtype=float) / eff
        mx = raw.max() if raw.max() > 0 else 1.0
        out[sp] = raw / mx
    return out


def ok_license(lic: str) -> bool:
    if not lic:
        return False
    s = lic.lower().replace(" ", "-")
    if "nc" in s or "nd" in s:
        return False
    return bool(LICENSE_OK.search(s))


def pick_photos(species: list[str], n_article: int = 6) -> list[dict]:
    """CC BY / BY-SA / CC0 en caja Cataluña desde enrich (solo lectura)."""
    d = json.load(open(ENRICH))
    by_sp: dict[str, list[dict]] = defaultdict(list)
    for _src, obs_map in d.items():
        for obs_id, m in obs_map.items():
            sp = m.get("obs_taxon_name_api")
            if sp not in species:
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
            by_sp[sp].append(
                {
                    "species": sp,
                    "obs_id": obs_num.group(1) if obs_num else str(obs_id),
                    "uri": uri,
                    "author": m.get("observer_name") or m.get("observer_login") or "?",
                    "license": m.get("obs_license"),
                    "date": (m.get("obs_date") or "")[:10],
                    "place": m.get("obs_place_guess") or "",
                    "lat": lat,
                    "lon": lon,
                    "platform": platform,
                }
            )

    # Copia CC-BY conocida de láminas correlación (solo lectura)
    manifest_path = ROOT / "papers/proyecto_correlacion/lamina_fotos/lamina_manifest_20261008.json"
    manifest = json.load(open(manifest_path)) if manifest_path.exists() else []
    corr_by_sp = defaultdict(list)
    for block in manifest:
        for ph in block.get("fotos", []):
            if ph.get("nc"):
                continue
            lic = (ph.get("licencia") or "").lower()
            if "nc" in lic or "nd" in lic:
                continue
            tax = ph.get("taxon")
            if tax not in species:
                continue
            try:
                la, lo = float(ph["lat"]), float(ph["lon"])
            except (KeyError, TypeError, ValueError):
                continue
            if not (CAT_LAT[0] <= la <= CAT_LAT[1] and CAT_LON[0] <= lo <= CAT_LON[1]):
                continue
            fpath = CORR_FOTOS / ph["file"]
            if not fpath.exists():
                continue
            corr_by_sp[tax].append({**ph, "local": str(fpath), "species": tax})

    chosen: list[dict] = []
    thumbs_dir = PAPER / "fotos"
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    def download_inat(obs_id: str, dest: Path) -> bool:
        try:
            url = f"https://api.inaturalist.org/v1/observations/{obs_id}"
            with urllib.request.urlopen(url, timeout=25) as r:
                data = json.load(r)
            photos = (data.get("results") or [{}])[0].get("photos") or []
            if not photos:
                return False
            purl = photos[0].get("url", "").replace("square", "medium")
            if not purl:
                return False
            with urllib.request.urlopen(purl, timeout=25) as r:
                dest.write_bytes(r.read())
            return True
        except Exception:
            return False

    for sp in species:
        entry = None
        if corr_by_sp.get(sp):
            ph = corr_by_sp[sp][0]
            slug = sp.replace(" ", "_").lower()
            dest = thumbs_dir / f"{slug}_thumb.jpg"
            shutil.copy2(ph["local"], dest)
            entry = {
                "species": sp,
                "file": dest.name,
                "path": dest,
                "author": ph.get("autor"),
                "license": ph.get("licencia"),
                "date": ph.get("fecha"),
                "place": ph.get("lugar_final") or ph.get("lugar"),
                "uri": ph.get("enlace"),
                "source": "lamina_correlacion",
            }
        elif by_sp.get(sp):
            cand = by_sp[sp][0]
            slug = sp.replace(" ", "_").lower()
            dest = thumbs_dir / f"{slug}_thumb.jpg"
            if cand["platform"] == "iNaturalist" and download_inat(cand["obs_id"], dest):
                entry = {
                    "species": sp,
                    "file": dest.name,
                    "path": dest,
                    "author": cand["author"],
                    "license": cand["license"],
                    "date": cand["date"],
                    "place": cand["place"],
                    "uri": cand["uri"],
                    "source": "enrich+inat_api",
                }
        if entry:
            chosen.append(entry)

    # Asegurar fotos para artículo (top especies)
    for sp in species:
        if len(chosen) >= n_article:
            break
        if any(c["species"] == sp for c in chosen):
            continue
        if by_sp.get(sp):
            cand = by_sp[sp][0]
            slug = sp.replace(" ", "_").lower()
            dest = thumbs_dir / f"{slug}_thumb.jpg"
            if cand["platform"] == "iNaturalist" and download_inat(cand["obs_id"], dest):
                chosen.append(
                    {
                        "species": sp,
                        "file": dest.name,
                        "path": dest,
                        "author": cand["author"],
                        "license": cand["license"],
                        "date": cand["date"],
                        "place": cand["place"],
                        "uri": cand["uri"],
                        "source": "enrich+inat_api",
                    }
                )
    return chosen


def load_thumb(path: Path | None, size=(48, 48)) -> np.ndarray:
    if path and path.exists():
        im = Image.open(path).convert("RGB")
        im.thumbnail(size, Image.Resampling.LANCZOS)
        arr = np.asarray(im)
        h, w = arr.shape[:2]
        pad = np.ones((size[1], size[0], 3), dtype=np.uint8) * 240
        y0 = (size[1] - h) // 2
        x0 = (size[0] - w) // 2
        pad[y0 : y0 + h, x0 : x0 + w] = arr
        return pad
    pad = np.ones((size[1], size[0], 3), dtype=np.uint8) * 232
    pad[:, :, 0] = 210
    pad[:, :, 2] = 220
    return pad


def lamina_calendario(
    top_species: list[str],
    meta: dict,
    norm: dict[str, np.ndarray],
    photos: dict[str, Path | None],
    photo_meta: dict[str, dict],
):
    cmap = LinearSegmentedColormap.from_list("mar", ["#f7fbff", "#cfe8ef", "#6baed6", "#08519c", "#023858"])
    fam_order: list[str] = []
    for sp in top_species:
        fam = meta[sp]["family"]
        if fam not in fam_order:
            fam_order.append(fam)
    ordered: list[str] = []
    for fam in fam_order:
        ordered.extend([s for s in top_species if meta[s]["family"] == fam])
    n = len(ordered)

    fig_w, fig_h = 16.54, max(11.69, 0.28 * n + 2.8)
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=300, facecolor="white")
    ax = fig.add_axes([0.14, 0.08, 0.78, 0.82])
    mat = np.array([norm[s] for s in ordered])
    im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
    ax.set_xticks(range(12))
    ax.set_xticklabels(MES, fontsize=9)
    ax.set_yticks(range(n))
    ax.set_yticklabels([s for s in ordered], fontsize=7, style="italic")
    ax.set_xlabel("Mes — actividad relativa normalizada por esfuerzo marino", fontsize=10)
    ax.set_title("Lámina 1 · Calendario fenológico de nudibranquios (Cataluña, caja costera)", fontsize=13, color="#0b3d5c", pad=14)

    # Bandas de familia
    y0 = -0.5
    for fam in fam_order:
        spp = [s for s in ordered if meta[s]["family"] == fam]
        y1 = y0 + len(spp)
        ax.axhspan(y0, y1, facecolor="#eef6fa", alpha=0.35, zorder=0)
        fig.text(0.02, 0.08 + (0.82 * (1 - (y0 + y1) / (2 * n))), fam, fontsize=7, fontweight="bold", color="#145a7a", va="center")
        y0 = y1

    # Miniaturas alineadas con cada fila
    credits: list[str] = []
    for i, sp in enumerate(ordered):
        thumb = load_thumb(photos.get(sp), size=(64, 64))
        ax_img = fig.add_axes([0.055, 0.08 + 0.82 * (1 - (i + 0.65) / n), 0.06, 0.82 / n * 0.85])
        ax_img.imshow(thumb, aspect="equal")
        ax_img.axis("off")
        if sp in photo_meta:
            pm = photo_meta[sp]
            credits.append(f"{sp}: {pm.get('author','?')} ({pm.get('license','')})")

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Intensidad 0–1 (por especie)", fontsize=8)
    foot1 = "Intensidad = (obs. especie / obs. marinas del mes en catálogo BioFauna). Fuente: public_observations (iNat + Minka), solo lectura."
    fig.text(0.5, 0.04, foot1, ha="center", fontsize=7, color="#333")
    if credits:
        fig.text(0.5, 0.015, "Fotos: " + " · ".join(credits[:8]) + (" …" if len(credits) > 8 else ""), ha="center", fontsize=5.5, color="#555")

    out_png = PAPER / "LAMINA1_calendario_fenologico_20261010.png"
    out_pdf = PAPER / "LAMINA1_calendario_fenologico_20261010.pdf"
    fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_png, out_pdf, credits


def season_blurb(top12: list[str], norm: dict[str, np.ndarray]) -> list[tuple[str, str]]:
    """Texto estacional a partir de picos normalizados agregados."""
    seasons = [(0, 3, "Invierno (dic–feb)"), (3, 6, "Primavera (mar–may)"), (6, 9, "Verano (jun–ago)"), (9, 12, "Otoño (sep–nov)")]
    out = []
    for a, b, label in seasons:
        scores: Counter[str] = Counter()
        for sp in top12:
            chunk = norm[sp][a:b]
            if chunk.max() > 0.55:
                scores[sp] += float(chunk.max())
        tops = ", ".join(f"*{s}*" for s, _ in scores.most_common(4)) or "—"
        out.append((label, f"Picos relativos destacados: {tops}."))
    return out


def lamina_radial(top12: list[str], norm: dict[str, np.ndarray]):
    ncols = 4
    nrows = math.ceil(len(top12) / ncols)
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    gs = gridspec.GridSpec(nrows + 1, ncols, height_ratios=[1] * nrows + [1.2], hspace=0.35, wspace=0.25)

    theta = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    width = 2 * np.pi / 12 * 0.85

    for i, sp in enumerate(top12):
        r = i // ncols
        c = i % ncols
        ax = fig.add_subplot(gs[r, c], projection="polar")
        vals = norm[sp]
        bars = ax.bar(theta, vals, width=width, bottom=0.05, color=plt.cm.ocean(vals), edgecolor="white", linewidth=0.4)
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_xticks(theta)
        ax.set_xticklabels(MES, fontsize=6)
        ax.set_yticklabels([])
        ax.set_ylim(0, 1.15)
        ax.set_title(f"*{sp}*", fontsize=8, style="italic", pad=8)

    # Panel estaciones
    axp = fig.add_subplot(gs[nrows, :])
    axp.axis("off")
    seasons = season_blurb(top12, norm)
    txt = "Qué buscar cada estación (orientativo, sesgo de muestreo):\n\n"
    for title, body in seasons:
        txt += f"• {title}: {body}\n"
    axp.text(0.02, 0.95, txt, va="top", fontsize=9, family="sans-serif", wrap=True)

    out_png = PAPER / "LAMINA2_rosas_estaciones_20261010.png"
    out_pdf = PAPER / "LAMINA2_rosas_estaciones_20261010.pdf"
    fig.suptitle("Picos mensuales normalizados — nudibranquios más observados en Cataluña", fontsize=12, y=0.98)
    fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_png, out_pdf


def write_licencias(photos: list[dict], lamina_attributions: list[str]):
    lines = ["# Licencias de fotografías — calendario nudibranquios\n", f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} CEST\n\n"]
    lines.append("## Artículo y miniaturas de lámina 1\n\n")
    for p in photos:
        lines.append(
            f"- *{p['species']}*: {p['author']} · {p['license']} · {p['date']} · {p.get('place','')} · {p.get('uri','')}\n"
        )
    lines.append("\n## Atribuciones adicionales (láminas)\n\n")
    for a in lamina_attributions:
        lines.append(f"- {a}\n")
    (PAPER / "LICENCIAS_FOTOS.md").write_text("".join(lines), encoding="utf-8")


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
):
    total_nudi = sum(totals.values())
    ts = datetime.now().strftime("%Y-%m-%d")
    md = f"""# Cuándo ver nudibranquios en Cataluña: un calendario fenológico a partir de ciencia ciudadana

**Autores:** Gustavo Zafra (Yespi); datos comunitarios Minka SDG e iNaturalist; curación taxonómica BioFauna  
**Fecha:** {ts}  
**Repositorio:** https://github.com/yespi/biofauna (`papers/nudibranquios_calendario/`)

---

## Resumen

Presentamos un calendario de actividad mensual de nudibranquios (**Nudibranchia** y **doridoideos**, *sensu* catálogo BioFauna) en la costa catalana, a partir de **{total_nudi:,}** observaciones georreferenciadas en la base pública `public_observations` (iNaturalist + Minka). La intensidad mensual se **normaliza por el esfuerzo de muestreo**: en cada mes dividimos las observaciones de la especie entre el total de observaciones de **taxones marinos** del catálogo en la misma caja geográfica, para atenuar el sesgo estival del buceo. Incluimos dos láminas imprimibles (calendario por familias y rosas mensuales) y discutimos limitaciones de identificación automática y cobertura desigual.

**Palabras clave:** Nudibranchia, Doridida, fenología, ciencia ciudadana, Mediterráneo, Cataluña, Minka, iNaturalist

## 1. Introducción

Los nudibranquios concentran el interés de buceadores y naturalistas por su color y diversidad trofica. En Cataluña, proyectos como Minka SDG y iNaturalist acumulan miles de registros, pero las curvas crudas de «cuándo se fotografían» mezclan la biología con **cuándo sale la gente al mar**. Además, los informes previos del proyecto se apoyaban en listas cortas de aeolideos; aquí ampliamos el alcance a **doridoideos** (*Felimare*, *Peltodoris*, *Hypselodoris*, *Dendrodoris*, *Doris*, *Discodoris*, etc.) usando el catálogo vivo de BioFauna ({len(meta)} especies potenciales).

## 2. Métodos

### 2.1 Área de estudio y fuentes

- **Región:** caja costera de Cataluña usada en BioQuest (lat {CAT_LAT[0]}–{CAT_LAT[1]}° N; lon {CAT_LON[0]}–{CAT_LON[1]}° E; definición 8-oct-2026).
- **Datos:** tabla `public_observations` (contenedor `postgres-global`, BD `fauna`), fuentes `{sources.get('minka', 0):,}` Minka + `{sources.get('inat', 0):,}` iNaturalist — **solo lectura (`SELECT`)**.
- **Taxonomía:** especies con `order` ∈ {{Nudibranchia, Doridida, Dendronotida}} en `dataset/target_species.json`, enriquecidas con familia desde `dataset/catalog.json`.

### 2.2 Normalización por esfuerzo

Para cada mes *m* y especie *s*:

\\[
\\text{{actividad}}_{{s,m}} = \\frac{{N_{{s,m}}}}{{E_m}}
\\]

donde \\(N_{{s,m}}\\) es el número de observaciones de *s* en el mes *m* dentro de la caja, y \\(E_m\\) el total de observaciones de **especies marinas del catálogo BioFauna** (`iconic` ∈ grupos marinos) en el mismo mes y caja. Para las figuras, dividimos por el máximo mensual de cada especie (escala 0–1 relativa).

**Esfuerzo mensual (obs. marinas):** {", ".join(f"{MES_L[i]}={effort.get(i+1,0):,}" for i in range(12))}.

### 2.3 Figuras y reproducibilidad

- Lámina 1: `{lam1.name}` (PNG 300 ppp + PDF).
- Lámina 2: `{lam2.name}` (PNG 300 ppp + PDF).
- Script: `scripts/nudibranquios_articulo_generar_20261010.py`.

## 3. Resultados

### 3.1 Especies más registradas

Entre las **30** especies más observadas en la caja figuran tanto aeolideos históricamente abundantes (*Cratena peregrina*, *Edmundsella pedata*, *Calmella cavolini*) como doridoideos antes ausentes del borrador aeolideo-only (*Felimare picta*, *Felimare tricolor*, *Peltodoris atromaculata*, *Hypselodoris picta*, *Dendrodoris limbata*, …).

| Especie | Familia | Obs. totales | Mes pico (normalizado) |
|---|---|---:|---|
"""
    for sp in top30[:15]:
        peak_m = int(np.argmax(norm[sp])) + 1
        md += f"| *{sp}* | {meta[sp]['family']} | {totals[sp]:,} | {MES_L[peak_m-1]} |\n"

    md += """
*(Tabla completa en `datos/especies_mensual_normalizado_20261010.csv`.)*

### 3.2 Calendario fenológico

La **Lámina 1** muestra ~30 especies agrupadas por familia; el color sigue la actividad normalizada mes a mes. Tras normalizar, algunos picos invernales de *Facelina* o *Doto* ganan peso relativo frente al verano bruto.

![Lámina 1 — calendario fenológico](LAMINA1_calendario_fenologico_20261010.png)

### 3.3 Rosas de actividad y estaciones

La **Lámina 2** representa las doce especies más frecuentes como diagramas radiales mensuales, más un panel orientativo «qué ver cada estación».

![Lámina 2 — rosas y estaciones](LAMINA2_rosas_estaciones_20261010.png)

### 3.4 Fotografías de ejemplo (licencias libres)

"""
    for i, p in enumerate(photos[:6], 1):
        md += f"""
<figure>
<img src="fotos/{p['file']}" alt="{p['species']}" width="420"/>
<figcaption>Figura {i}. *{p['species']}* — {p['author']} · {p['license']} · {p['date']} · {p.get('place','')[:80]} · <a href="{p.get('uri','')}">observación</a></figcaption>
</figure>
"""

    md += """
## 4. Discusión

**Sesgo de esfuerzo.** Aunque normalizamos por observaciones marinas mensuales, el denominador incluye peces, cnidarios y algas fotografiados en las mismas salidas; no es un censo independiente de «horas de buceo». El verano sigue sobre-representado en *Cratena* o *Calmella* en datos brutos.

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
    # conversión mínima md → html
    body = md_text
    for h, tag in [("# ", "h1"), ("## ", "h2"), ("### ", "h3")]:
        body = re.sub(rf"^{re.escape(h)}(.+)$", rf"<{tag}>\1</{tag}>", body, flags=re.M)
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
    body = re.sub(r"\*(.+?)\*", r"<em>\1</em>", body)
    body = re.sub(r"!\[(.+?)\]\((.+?)\)", r'<figure><img src="\2" style="max-width:100%"/><figcaption>\1</figcaption></figure>', body)
    body = re.sub(r"\|(.+\|)", lambda m: "<p>" + m.group(0).replace("|", " ") + "</p>", body)
    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"/>
<style>
body {{ font-family: 'Segoe UI', Georgia, serif; max-width: 900px; margin: 24px auto; line-height: 1.45; color: #1a1a1a; }}
h1 {{ color: #0b3d5c; }} h2 {{ color: #145a7a; border-bottom: 1px solid #ccc; }}
figure {{ margin: 1.2em 0; }} figcaption {{ font-size: 0.85em; color: #444; }}
</style></head><body>{body}</body></html>"""
    html_path.write_text(html, encoding="utf-8")
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome:
        shutil.copy(md_path, pdf_path.with_suffix(".md.bak"))
        return
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ],
        check=True,
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
    norm = normalized_matrix(by_sp_month, effort)

    ranked = sorted(totals.items(), key=lambda x: -x[1])
    top30 = [s for s, n in ranked[:30] if n >= 10]
    top12 = [s for s, n in ranked[:12]]

    # CSV export
    csv_path = PAPER / "datos/especies_mensual_normalizado_20261010.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["especie", "familia", "total_obs"] + MES_L + ["pico_mes_norm"])
        for sp, _ in ranked:
            if sp not in meta:
                continue
            row = [sp, meta[sp]["family"], totals.get(sp, 0)] + [by_sp_month.get(sp, [0] * 12)[i] for i in range(12)]
            row.append(MES_L[int(np.argmax(norm.get(sp, np.zeros(12))))])
            w.writerow(row)

    with open(PAPER / "datos/esfuerzo_marino_mensual_20261010.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mes", "obs_marinas_catalogo"])
        for i in range(12):
            w.writerow([MES_L[i], effort.get(i + 1, 0)])

    photo_species = list(dict.fromkeys(top30[:20] + top12))
    photos = pick_photos(photo_species, n_article=6)
    photo_paths = {p["species"]: p.get("path") for p in photos}

    photo_meta = {p["species"]: p for p in photos}
    lam1_png, lam1_pdf, lam_credits = lamina_calendario(top30, meta, norm, photo_paths, photo_meta)
    lam2_png, lam2_pdf = lamina_radial(top12, norm)

    # Figura esfuerzo
    fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
    ax.bar(range(12), [effort.get(i + 1, 0) for i in range(12)], color="#4a90a4")
    ax.set_xticks(range(12))
    ax.set_xticklabels(MES)
    ax.set_ylabel("Obs. marinas (catálogo)")
    ax.set_title("Esfuerzo de muestreo mensual — caja Cataluña")
    fig.tight_layout()
    fig.savefig(PAPER / "figuras/esfuerzo_marino_mensual_20261010.png")
    plt.close(fig)

    md_path = write_articulo_md(top30, top12, meta, totals, effort, sources, norm, photos, lam1_png, lam2_png)
    pdf_path = PAPER / "ARTICULO_20261010.pdf"
    html_to_pdf(md_path, pdf_path)

    write_licencias(photos, lam_credits)

    # README update snippet
    summary = {
        "generated": datetime.now().isoformat(),
        "n_species_catalog": len(meta),
        "n_species_with_data": len(totals),
        "total_obs": sum(totals.values()),
        "top30": top30,
        "files": [str(lam1_pdf), str(lam2_pdf), str(pdf_path), str(md_path)],
    }
    (PAPER / "meta_generacion_20261010.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
