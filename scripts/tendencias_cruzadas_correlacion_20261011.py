#!/mnt/docker/biofauna/venv_det_20261005/bin/python
"""Tendencias cruzadas, comunidades y cascadas (paper correlación v26).

Solo SELECT en postgres-global. Sin GPU. Método alineado con BENCHMARK_PAPERS
(Isaac/Barve esfuerzo relativo; Johnston; Blanchet: correlación ≠ causalidad).

Salidas en papers/proyecto_correlacion/experimentos/ y figuras/cruzadas/.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import subprocess
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
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/proyecto_correlacion"
MAT = PAPER / "material"
OUT = MAT / "experimentos"
FIG = MAT / "figuras" / "cruzadas"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

CATALOG = Path("/mnt/docker/biofauna/dataset/target_species.json")

LAT_MIN, LAT_MAX = 40.45, 42.95
LON_MIN, LON_MAX = 0.10, 3.40
YEAR0, YEAR1 = 2010, 2025
MIN_YEARS = 8
MIN_OBS_SPP = 40
MIN_EFFORT_YEAR = 80
TOP_CLUSTER_SPP = 120
TOP_PAIRS = 20
FDR_Q = 0.05

# Zonas operativas (costa catalana N→S; lat bands + lon costa)
ZONES = {
    "Costa_Brava": (41.70, 42.95, 2.70, 3.40),
    "Barcelona": (41.20, 41.70, 1.65, 2.80),
    "Tarragona_Ebro": (40.45, 41.20, 0.10, 1.75),
}

# Pares de prueba (ejemplos de Gustavo; no son hallazgos a priori)
TEST_PAIRS = [
    ("Pinna nobilis", "Pinna rudis"),
    ("Pelagia noctiluca", "Paracentrotus lividus"),
    ("Pelagia noctiluca", "Arbacia lixula"),
    ("Epinephelus marginatus", "Octopus vulgaris"),
    ("Epinephelus costae", "Octopus vulgaris"),
]

# Detonantes documentados (fecha = bibliografía; ver Crossref en biblio)
DETONATORS = [
    {
        "id": "pinna_mm_spain",
        "label": "Pinna nobilis MM (España)",
        "year": 2016,
        "species_trigger": "Pinna nobilis",
        "zones_impact": ["Costa_Brava", "Barcelona", "Tarragona_Ebro"],
        "zones_control": [],  # evento regional; contraste = antes/después
        "note": "Inicio documentado en España otoño 2016 (Vázquez-Luis 2017); no 2014",
    },
    {
        "id": "mhw_2003",
        "label": "Ola de calor marina 2003",
        "year": 2003,
        "species_trigger": None,
        "zones_impact": ["Costa_Brava", "Barcelona", "Tarragona_Ebro"],
        "zones_control": [],
        "note": "Fuera de ventana 2010–2025 para series densas; se reporta solo si hay datos",
    },
    {
        "id": "mhw_2015",
        "label": "Ola de calor marina 2015",
        "year": 2015,
        "species_trigger": None,
        "zones_impact": ["Costa_Brava", "Barcelona", "Tarragona_Ebro"],
        "zones_control": [],
        "note": "Garrabou et al. 2022 (contexto MHW Med)",
    },
    {
        "id": "mhw_2022",
        "label": "Ola de calor marina 2022",
        "year": 2022,
        "species_trigger": None,
        "zones_impact": ["Costa_Brava", "Barcelona", "Tarragona_Ebro"],
        "zones_control": [],
        "note": "Garrabou et al. 2022 + episodios posteriores",
    },
    {
        "id": "rugulopteryx",
        "label": "Rugulopteryx okamurae (llegada)",
        "year": 2015,
        "species_trigger": "Rugulopteryx okamurae",
        "zones_impact": ["Costa_Brava", "Barcelona", "Tarragona_Ebro"],
        "zones_control": [],
        "note": "Usar primera obs CAT en datos si disponible; año lit. Med occidental ~2015+",
    },
    {
        "id": "pelagia_bloom",
        "label": "Años bloom Pelagia (proxy pico)",
        "year": None,  # se calcula del pico de tasa
        "species_trigger": "Pelagia noctiluca",
        "zones_impact": ["Costa_Brava", "Barcelona", "Tarragona_Ebro"],
        "zones_control": [],
        "note": "Año = máximo de proporción esfuerzo-corregida en caja CAT",
    },
    {
        "id": "vnn_meros",
        "label": "VNN / betanodavirus en meros",
        "year": 2020,
        "species_trigger": "Epinephelus marginatus",
        "zones_impact": ["Costa_Brava", "Barcelona", "Tarragona_Ebro"],
        "zones_control": [],
        "note": "Ancla bibliográfica Med español: Peñalver et al. 2020 (Cabo de Palos). "
        "Brotes previos: Haddad-Boubaker et al. 2014 (E. costae y E. marginatus). "
        "No se halló en Crossref un brote publicado 2023+ en Cataluña; 2023+ = hipótesis sin DOI.",
    },
]

EXCLUDE_CLASSES = {
    "Aves",
    "Mammalia",
    "Insecta",
    "Arachnida",
    "Amphibia",
    "Reptilia",
    "Magnoliopsida",
    "Liliopsida",
}
# fanerógamas marinas (sí Liliopsida pero las queremos)
KEEP_NAMES = {
    "Posidonia oceanica",
    "Cymodocea nodosa",
    "Zostera marina",
    "Zostera noltei",
    "Nanozostera noltei",
}
MARINE_PHYLA = {
    "Mollusca",
    "Cnidaria",
    "Porifera",
    "Echinodermata",
    "Bryozoa",
    "Annelida",
    "Rhodophyta",
    "Ochrophyta",
    "Chlorophyta",
    "Ctenophora",
    "Platyhelminthes",
    "Chordata",
    "Arthropoda",  # crustáceos marinos en catálogo BF
    "Foraminifera",
    "Brachiopoda",
}


def log(msg: str) -> None:
    print(msg, flush=True)


def sql(q: str, timeout: int = 600) -> list[tuple]:
    r = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
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
            q,
        ],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-1200:])
    rows = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(tuple(line.split("\t")))
    return rows


def zone_of(lat: float, lon: float) -> str | None:
    for z, (la0, la1, lo0, lo1) in ZONES.items():
        if la0 <= lat < la1 and lo0 <= lon <= lo1:
            return z
    # borde norte Costa Brava inclusive
    if 41.70 <= lat <= LAT_MAX and 2.70 <= lon <= 3.40:
        return "Costa_Brava"
    return None


def load_marine_catalog() -> dict[str, dict]:
    cat = json.loads(CATALOG.read_text())
    out = {}
    for s in cat:
        name = (s.get("name") or "").strip()
        if " " not in name:
            continue
        if name in KEEP_NAMES:
            out[name] = s
            continue
        if s.get("realm") in ("terrestrial", "aves"):
            continue
        cls = s.get("class_name") or ""
        if cls in EXCLUDE_CLASSES and name not in KEEP_NAMES:
            continue
        ph = s.get("phylum") or ""
        if ph in MARINE_PHYLA or name in KEEP_NAMES:
            out[name] = s
    return out


def bh_fdr(pvals: list[float]) -> list[float]:
    n = len(pvals)
    if n == 0:
        return []
    order = np.argsort(pvals)
    q = np.empty(n, dtype=float)
    prev = 1.0
    for i in range(n - 1, -1, -1):
        idx = order[i]
        rank = i + 1
        val = pvals[idx] * n / rank
        prev = min(prev, val)
        q[idx] = prev
    return [float(min(1.0, x)) for x in q]


def crossref_works(query: str, rows: int = 5) -> list[dict]:
    q = urllib.parse.quote(query)
    url = f"https://api.crossref.org/works?query={q}&rows={rows}&select=DOI,title,author,published,container-title,issued"
    req = urllib.request.Request(url, headers={"User-Agent": "BioFaunaPapers/1.0 (mailto:yespi@yespi.es)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        log(f"crossref fail {query[:60]}: {e}")
        return []
    return data.get("message", {}).get("items", [])


def verify_doi(doi: str) -> dict | None:
    doi = doi.strip().removeprefix("https://doi.org/")
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(url, headers={"User-Agent": "BioFaunaPapers/1.0 (mailto:yespi@yespi.es)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()).get("message")
    except Exception:
        return None


def globi_interactions(name: str, limit: int = 40) -> list[dict]:
    """Devuelve lista de dicts {target, type}. Tolera formatos GloBI columns/data."""
    q = urllib.parse.quote(name)
    urls = [
        f"https://api.globalbioticinteractions.org/interaction?sourceTaxon={q}&limit={limit}&type=json",
        f"https://api.globalbioticinteractions.org/taxon/{q}/interactsWith?type=json&limit={limit}",
    ]
    data = None
    for url in urls:
        req = urllib.request.Request(url, headers={"User-Agent": "BioFaunaPapers/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode())
            break
        except Exception:
            continue
    if data is None:
        return []
    out: list[dict] = []
    if isinstance(data, dict) and "columns" in data and "data" in data:
        cols = data["columns"]
        for row in data["data"]:
            if not isinstance(row, (list, tuple)):
                continue
            d = {cols[i]: row[i] for i in range(min(len(cols), len(row)))}
            tgt = d.get("target_taxon_name") or d.get("target") or ""
            if isinstance(tgt, list):
                tgt = " ".join(str(x) for x in tgt if not str(x).isdigit())
            typ = d.get("interaction_type") or d.get("type") or ""
            out.append({"target": str(tgt), "type": str(typ)})
        return out
    if isinstance(data, list):
        for it in data:
            if isinstance(it, dict):
                tgt = it.get("target_taxon_name") or it.get("target") or it.get("object") or ""
                if isinstance(tgt, dict):
                    tgt = tgt.get("name") or ""
                if isinstance(tgt, list):
                    tgt = " ".join(str(x) for x in tgt if not str(x).isdigit())
                out.append({"target": str(tgt), "type": str(it.get("interaction_type") or it.get("type") or "")})
        return out
    return out

def fetch_counts() -> tuple[dict, dict, dict]:
    """effort[zone][year], counts[tid][zone][year], names[tid]->canonical."""
    log("SQL: effort zone×year…")
    # Pull all rows aggregated in SQL with CASE zones
    q_eff = f"""
    SELECT
      CASE
        WHEN lat >= 41.70 AND lng BETWEEN 2.70 AND 3.40 THEN 'Costa_Brava'
        WHEN lat >= 41.20 AND lat < 41.70 AND lng BETWEEN 1.65 AND 2.80 THEN 'Barcelona'
        WHEN lat < 41.20 AND lng BETWEEN 0.10 AND 1.75 THEN 'Tarragona_Ebro'
        ELSE NULL
      END AS zona,
      obs_year,
      COUNT(*)::bigint
    FROM public_observations
    WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lng BETWEEN {LON_MIN} AND {LON_MAX}
      AND obs_year BETWEEN {YEAR0} AND {YEAR1}
    GROUP BY 1,2
    HAVING CASE
        WHEN lat >= 41.70 AND lng BETWEEN 2.70 AND 3.40 THEN 'Costa_Brava'
        WHEN lat >= 41.20 AND lat < 41.70 AND lng BETWEEN 1.65 AND 2.80 THEN 'Barcelona'
        WHEN lat < 41.20 AND lng BETWEEN 0.10 AND 1.75 THEN 'Tarragona_Ebro'
        ELSE NULL
      END IS NOT NULL
    ORDER BY 1,2;
    """
    # HAVING can't reference CASE alias with lat in HAVING that way in PG — rewrite:
    q_eff = f"""
    SELECT zona, obs_year, COUNT(*)::bigint FROM (
      SELECT obs_year,
        CASE
          WHEN lat >= 41.70 AND lng BETWEEN 2.70 AND 3.40 THEN 'Costa_Brava'
          WHEN lat >= 41.20 AND lat < 41.70 AND lng BETWEEN 1.65 AND 2.80 THEN 'Barcelona'
          WHEN lat < 41.20 AND lng BETWEEN 0.10 AND 1.75 THEN 'Tarragona_Ebro'
          ELSE NULL
        END AS zona
      FROM public_observations
      WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
        AND lng BETWEEN {LON_MIN} AND {LON_MAX}
        AND obs_year BETWEEN {YEAR0} AND {YEAR1}
    ) t
    WHERE zona IS NOT NULL
    GROUP BY 1,2 ORDER BY 1,2;
    """
    effort: dict[str, dict[int, int]] = defaultdict(dict)
    for z, y, n in sql(q_eff):
        effort[z][int(y)] = int(n)

    log("SQL: counts taxon×zone×year…")
    q_c = f"""
    SELECT taxon_id, zona, obs_year, COUNT(*)::bigint FROM (
      SELECT taxon_id, obs_year,
        CASE
          WHEN lat >= 41.70 AND lng BETWEEN 2.70 AND 3.40 THEN 'Costa_Brava'
          WHEN lat >= 41.20 AND lat < 41.70 AND lng BETWEEN 1.65 AND 2.80 THEN 'Barcelona'
          WHEN lat < 41.20 AND lng BETWEEN 0.10 AND 1.75 THEN 'Tarragona_Ebro'
          ELSE NULL
        END AS zona
      FROM public_observations
      WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
        AND lng BETWEEN {LON_MIN} AND {LON_MAX}
        AND obs_year BETWEEN {YEAR0} AND {YEAR1}
        AND taxon_id IS NOT NULL
    ) t
    WHERE zona IS NOT NULL
    GROUP BY 1,2,3;
    """
    counts: dict[int, dict[str, dict[int, int]]] = defaultdict(lambda: defaultdict(dict))
    for tid, z, y, n in sql(q_c, timeout=900):
        counts[int(tid)][z][int(y)] = int(n)

    log("SQL: canonical names…")
    q_n = f"""
    SELECT taxon_id, taxon_name, COUNT(*)::bigint n
    FROM public_observations
    WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lng BETWEEN {LON_MIN} AND {LON_MAX}
      AND obs_year BETWEEN {YEAR0} AND {YEAR1}
      AND taxon_name ~ '^[A-Z][a-z]+ [a-z]+$'
    GROUP BY 1,2;
    """
    best: dict[int, tuple[str, int]] = {}
    for tid, name, n in sql(q_n, timeout=900):
        tid, n = int(tid), int(n)
        if tid not in best or n > best[tid][1]:
            best[tid] = (name, n)
    names = {tid: nm for tid, (nm, _) in best.items()}
    return effort, counts, names


def proportion_series(
    counts_z: dict[int, int], effort_z: dict[int, int]
) -> dict[int, float]:
    """Proporción especie / esfuerzo zona·año (×1000 para legibilidad)."""
    out = {}
    for y in range(YEAR0, YEAR1 + 1):
        e = effort_z.get(y, 0)
        if e < MIN_EFFORT_YEAR:
            continue
        out[y] = counts_z.get(y, 0) / e * 1000.0
    return out


def zscore_series(rates: dict[int, float]) -> dict[int, float]:
    ys = sorted(rates)
    vals = np.array([rates[y] for y in ys], dtype=float)
    if len(vals) < 3 or np.std(vals) < 1e-12:
        return {y: 0.0 for y in ys}
    z = (vals - vals.mean()) / vals.std(ddof=1)
    return {y: float(z[i]) for i, y in enumerate(ys)}


def first_diff(rates: dict[int, float]) -> dict[int, float]:
    ys = sorted(rates)
    out = {}
    for i in range(1, len(ys)):
        out[ys[i]] = rates[ys[i]] - rates[ys[i - 1]]
    return out


def breakpoint_year(rates: dict[int, float]) -> tuple[int | None, float]:
    """Año con mayor cambio relativo vs media 3 años previos."""
    ys = sorted(rates)
    best_y, best = None, 0.0
    for i, y in enumerate(ys):
        if y < 2012 or y > 2024:
            continue
        prev = [rates[ys[j]] for j in range(max(0, i - 3), i)]
        if not prev:
            continue
        base = float(np.mean(prev))
        if base < 0.02:
            continue
        score = (rates[y] - base) / base
        if abs(score) > abs(best):
            best, best_y = score, y
    return best_y, float(best)


def ci_poisson_rate(k: int, effort: int, scale: float = 1000.0) -> tuple[float, float]:
    """IC aproximado 95 % (normal) para tasa k/E×scale."""
    if effort <= 0:
        return 0.0, 0.0
    rate = k / effort * scale
    se = math.sqrt(max(k, 0.25)) / effort * scale
    return max(0.0, rate - 1.96 * se), rate + 1.96 * se


def plot_pair_zones(
    name_a: str,
    name_b: str,
    series_a: dict[str, dict[int, float]],
    series_b: dict[str, dict[int, float]],
    counts_a: dict[str, dict[int, int]],
    counts_b: dict[str, dict[int, int]],
    effort: dict[str, dict[int, int]],
    out_path: Path,
    title_extra: str = "",
) -> None:
    zones = list(ZONES)
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.6), sharey=False)
    for ax, z in zip(axes, zones):
        za = zscore_series(series_a.get(z, {}))
        zb = zscore_series(series_b.get(z, {}))
        ys = sorted(set(za) & set(zb))
        if len(ys) < 3:
            ax.set_title(z.replace("_", " ") + " (sin datos)")
            ax.axis("off")
            continue
        ax.plot(ys, [za[y] for y in ys], "-o", color="#1f4e79", ms=3.5, label=name_a)
        ax.plot(ys, [zb[y] for y in ys], "-s", color="#c45c26", ms=3.5, label=name_b)
        # IC sombra en proporción (no z): banda estrecha en eje secundario omitida; anotamos ruptura
        ba, sa = breakpoint_year(series_a.get(z, {}))
        bb, sb = breakpoint_year(series_b.get(z, {}))
        for by, col in ((ba, "#1f4e79"), (bb, "#c45c26")):
            if by:
                ax.axvline(by, color=col, ls="--", lw=0.8, alpha=0.55)
        ax.axhline(0, color="#999", lw=0.5)
        ax.set_title(z.replace("_", " "))
        ax.set_xlabel("Año")
        ax.grid(True, alpha=0.25)
    axes[0].set_ylabel("z-score (proporción / esfuerzo zona)")
    axes[0].legend(fontsize=7, loc="best")
    fig.suptitle(
        f"{name_a}  vs  {name_b}{(' — ' + title_extra) if title_extra else ''}\n"
        "Proporción esfuerzo-corregida (z-score); líneas discontinuas = breakpoints heurísticos. "
        "Correlación ≠ causalidad.",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def xcorr_lag(
    da: dict[int, float], db: dict[int, float], lag: int
) -> tuple[float, float, int]:
    """Correlación de primeras diferencias con retardo: A(t) vs B(t+lag). lag≥0."""
    ys = sorted(set(da) & set(db))
    if lag == 0:
        xs = ys
        a = [da[y] for y in xs]
        b = [db[y] for y in xs]
    else:
        xs = [y for y in ys if (y + lag) in db and y in da]
        # A leads B by lag years: corr(A_t, B_{t+lag})
        a = [da[y] for y in xs if y in da and (y + lag) in db]
        b = [db[y + lag] for y in xs if y in da and (y + lag) in db]
        xs = [y for y in xs if y in da and (y + lag) in db]
    if len(a) < 5:
        return float("nan"), 1.0, len(a)
    r, p = pearsonr(a, b)
    return float(r), float(p), len(a)


def main() -> None:
    t0 = time.time()
    log("=== tendencias cruzadas 20261011 ===")
    marine = load_marine_catalog()
    log(f"catálogo marino filtrado: {len(marine)} spp")

    effort, counts, names = fetch_counts()

    # map tid -> marine name (prefer binomiales del catálogo)
    tid_marine: dict[int, str] = {}
    lower_marine = {k.lower(): k for k in marine}
    for tid, nm in names.items():
        if nm in marine or nm in KEEP_NAMES:
            tid_marine[tid] = nm
        elif nm.lower() in lower_marine:
            tid_marine[tid] = lower_marine[nm.lower()]

    # Forzar taxones de pares de prueba / detonantes por nombre de catálogo
    force_names = {a for pair in TEST_PAIRS for a in pair} | {
        "Rugulopteryx okamurae",
        "Pinna nobilis",
        "Pinna rudis",
        "Epinephelus costae",
        "Epinephelus marginatus",
        "Pelagia noctiluca",
        "Octopus vulgaris",
        "Paracentrotus lividus",
        "Arbacia lixula",
    }
    # Resolver tid por conteo de taxon_name exacto en caja
    force_list = ",".join("'" + n.replace("'", "''") + "'" for n in sorted(force_names))
    q_force = f"""
    SELECT taxon_name, taxon_id, COUNT(*)::bigint
    FROM public_observations
    WHERE taxon_name IN ({force_list})
      AND lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lng BETWEEN {LON_MIN} AND {LON_MAX}
      AND obs_year BETWEEN {YEAR0} AND {YEAR1}
    GROUP BY 1,2;
    """
    force_best: dict[str, tuple[int, int]] = {}
    for nm, tid, n in sql(q_force):
        tid, n = int(tid), int(n)
        if nm not in force_best or n > force_best[nm][1]:
            force_best[nm] = (tid, n)
    for nm, (tid, n) in force_best.items():
        tid_marine[tid] = nm
        names[tid] = nm
        log(f"force {nm} → tid={tid} n={n}")

    log(f"taxones con match marino en caja: {len(tid_marine)}")

    # Build pooled CAT series + per-zone
    # total obs per tid
    tot = {
        tid: sum(sum(yz.values()) for yz in counts[tid].values()) for tid in tid_marine
    }
    eligible = [tid for tid, n in tot.items() if n >= MIN_OBS_SPP]
    eligible.sort(key=lambda t: -tot[t])
    log(f"elegibles (≥{MIN_OBS_SPP} obs): {len(eligible)}")

    # proportions per zone
    prop: dict[int, dict[str, dict[int, float]]] = {}
    for tid in eligible:
        prop[tid] = {}
        for z in ZONES:
            prop[tid][z] = proportion_series(counts[tid].get(z, {}), effort.get(z, {}))

    # pooled CAT proportion (all zones)
    effort_cat: dict[int, int] = defaultdict(int)
    for z in ZONES:
        for y, n in effort[z].items():
            effort_cat[y] += n
    prop_cat: dict[int, dict[int, float]] = {}
    for tid in eligible:
        ccat: dict[int, int] = defaultdict(int)
        for z in ZONES:
            for y, n in counts[tid].get(z, {}).items():
                ccat[y] += n
        prop_cat[tid] = proportion_series(ccat, effort_cat)

    name_of = {tid: tid_marine[tid] for tid in eligible}
    tid_of = {v: k for k, v in name_of.items()}

    # ---- Bibliografía detonantes (Crossref) ----
    log("Crossref detonantes…")
    biblio = []
    # DOI preferidos (verificados) + búsquedas; VNN: solo Mediterráneo con DOI Crossref
    preferred_dois = [
        ("vazquez-luis pinna MM", "10.3389/fmars.2017.00220"),
        ("Catanese Haplosporidium pinnae", "10.1016/j.jip.2018.07.006"),
        ("Garrabou MHW Med 2022", "10.1111/gcb.16301"),
        ("Haddad-Boubaker VNN E.costae E.marginatus 2014", "10.3147/jsfp.49.53"),
        ("Penalver nodavirus Cabo de Palos 2020", "10.6018/analesbio.42.07"),
        ("Toffan nodavirus wild Mediterranean grouper", "10.48045/001c.158446"),
        ("Kersting Pinna rudis after P.nobilis extinction", "10.12681/mms.27809"),
    ]
    search_only = [
        "Rugulopteryx okamurae Mediterranean invasion first record",
        "Mycobacterium Pinna nobilis mass mortality",
    ]
    seen_doi = set()
    for q, prefer in preferred_dois:
        msg = verify_doi(prefer)
        if not msg:
            log(f"DOI no verificado: {prefer}")
            continue
        doi = msg.get("DOI") or prefer
        if doi.lower() in seen_doi:
            continue
        seen_doi.add(doi.lower())
        year = (msg.get("issued") or {}).get("date-parts", [[None]])[0][0]
        authors = msg.get("author") or []
        auth = ", ".join(
            f"{a.get('family','')} {a.get('given','')[:1]}.".strip() for a in authors[:4]
        )
        biblio.append(
            {
                "query": q,
                "doi": doi,
                "doi_ok": True,
                "year": year,
                "authors": auth,
                "title": (msg.get("title") or [""])[0],
                "journal": (msg.get("container-title") or [""])[0],
                "url": f"https://doi.org/{doi}",
            }
        )
        time.sleep(0.25)
    for q in search_only:
        items = crossref_works(q, rows=5)
        chosen = None
        for it in items:
            doi = (it.get("DOI") or "").lower()
            title = " ".join(it.get("title") or []).lower()
            if doi in seen_doi:
                continue
            if "rugulopteryx" in q.lower() and "rugulopteryx" not in title:
                continue
            chosen = it
            break
        if not chosen:
            continue
        doi = chosen.get("DOI")
        if not doi or verify_doi(doi) is None:
            continue
        seen_doi.add(doi.lower())
        year = (chosen.get("issued") or {}).get("date-parts", [[None]])[0][0]
        authors = chosen.get("author") or []
        auth = ", ".join(
            f"{a.get('family','')} {a.get('given','')[:1]}.".strip() for a in authors[:4]
        )
        biblio.append(
            {
                "query": q,
                "doi": doi,
                "doi_ok": True,
                "year": year,
                "authors": auth,
                "title": (chosen.get("title") or [""])[0],
                "journal": (chosen.get("container-title") or [""])[0],
                "url": f"https://doi.org/{doi}",
            }
        )
        time.sleep(0.35)
    with (OUT / "cruzadas_biblio_detonantes_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["query", "doi", "doi_ok", "year", "authors", "title", "journal", "url"],
        )
        w.writeheader()
        w.writerows(biblio)

    # Pinna chronology note
    pinna_note = {
        "pathogen": "Haplosporidium pinnae (protozoo parásito; no virus)",
        "spain_onset_literature": 2016,
        "gustavo_suggested": 2014,
        "source_doi": "10.3389/fmars.2017.00220",
        "catanese_doi": "10.1016/j.jip.2018.07.006",
        "decision": "Usar 2016 como inicio documentado en España (Vázquez-Luis et al. 2017).",
    }
    (OUT / "cruzadas_pinna_cronologia_20261011.json").write_text(
        json.dumps(pinna_note, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Pelagia peak year
    if "Pelagia noctiluca" in tid_of:
        pr = prop_cat[tid_of["Pelagia noctiluca"]]
        if pr:
            peak = max(pr, key=pr.get)
            for d in DETONATORS:
                if d["id"] == "pelagia_bloom":
                    d["year"] = int(peak)

    # Rugulopteryx first year in CAT if present
    for tid, nm in tid_marine.items():
        if nm == "Rugulopteryx okamurae":
            years = []
            for z in ZONES:
                years.extend(counts[tid].get(z, {}).keys())
            if years:
                fy = min(years)
                for d in DETONATORS:
                    if d["id"] == "rugulopteryx":
                        d["year"] = int(fy)
                        d["note"] += f"; primera obs datos CAT={fy}"

    # ---- Test pairs figures ----
    log("Figuras pares de prueba…")
    test_rows = []
    for a, b in TEST_PAIRS:
        if a not in tid_of or b not in tid_of:
            test_rows.append({"pair": f"{a}||{b}", "status": "sin_datos_suficientes"})
            continue
        ta, tb = tid_of[a], tid_of[b]
        slug = re.sub(r"[^a-z0-9]+", "_", f"{a}_{b}".lower())
        plot_pair_zones(
            a,
            b,
            prop[ta],
            prop[tb],
            counts[ta],
            counts[tb],
            effort,
            FIG / f"par_prueba_{slug}.png",
            title_extra="caso de prueba",
        )
        # CAT-level xcorr
        da, db = first_diff(prop_cat[ta]), first_diff(prop_cat[tb])
        best = {"r": 0, "p": 1, "lag": 0, "n": 0}
        for lag in range(0, 4):
            r, p, n = xcorr_lag(da, db, lag)
            if n >= 5 and (abs(r) > abs(best["r"]) or (math.isnan(best["r"]))):
                if not math.isnan(r):
                    best = {"r": r, "p": p, "lag": lag, "n": n}
            r2, p2, n2 = xcorr_lag(db, da, lag)  # B leads A
            if n2 >= 5 and not math.isnan(r2) and abs(r2) > abs(best["r"]):
                best = {"r": r2, "p": p2, "lag": -lag, "n": n2}
        ba, sa = breakpoint_year(prop_cat[ta])
        bb, sb = breakpoint_year(prop_cat[tb])
        test_rows.append(
            {
                "pair": f"{a} || {b}",
                "status": "ok",
                "n_obs_a": tot[ta],
                "n_obs_b": tot[tb],
                "xcorr_r": round(best["r"], 4),
                "xcorr_p": round(best["p"], 5),
                "xcorr_lag_years": best["lag"],
                "n_years_diff": best["n"],
                "break_a": ba,
                "break_a_score": round(sa, 3),
                "break_b": bb,
                "break_b_score": round(sb, 3),
                "figure": f"material/figuras/cruzadas/par_prueba_{slug}.png",
            }
        )

    with (OUT / "cruzadas_pares_prueba_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        fields = list(test_rows[0].keys()) if test_rows else ["pair", "status"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(test_rows)

    # ---- Systematic pair search (CAT pooled, first differences) ----
    log("Búsqueda sistemática de pares…")
    # restrict to spp with enough years in prop_cat
    series_ok = []
    for tid in eligible[:TOP_CLUSTER_SPP]:
        pr = prop_cat[tid]
        if len(pr) >= MIN_YEARS:
            series_ok.append(tid)
    log(f"spp con ≥{MIN_YEARS} años: {len(series_ok)}")

    pair_results = []
    diffs = {tid: first_diff(prop_cat[tid]) for tid in series_ok}
    for i, ta in enumerate(series_ok):
        for tb in series_ok[i + 1 :]:
            # same genus skip? keep — Pinna–Pinna is interesting
            best = None
            for lag in range(0, 4):
                r, p, n = xcorr_lag(diffs[ta], diffs[tb], lag)
                if n >= 5 and not math.isnan(r):
                    cand = (r, p, n, lag, "A_leads_B")
                    if best is None or abs(r) > abs(best[0]):
                        best = cand
                if lag > 0:
                    r, p, n = xcorr_lag(diffs[tb], diffs[ta], lag)
                    if n >= 5 and not math.isnan(r):
                        cand = (r, p, n, -lag, "B_leads_A")
                        if best is None or abs(r) > abs(best[0]):
                            best = cand
            if best is None:
                continue
            r, p, n, lag, direc = best
            pair_results.append(
                {
                    "species_a": name_of[ta],
                    "species_b": name_of[tb],
                    "r_diff": r,
                    "p": p,
                    "n_years": n,
                    "lag": lag,
                    "direction": direc,
                    "abs_r": abs(r),
                    "sign": "sincronizada" if r > 0 else "opuesta",
                    "tid_a": ta,
                    "tid_b": tb,
                }
            )

    # power proxy: n_years >= 8 and abs(r) with rough SE
    for row in pair_results:
        # Fisher z SE ~ 1/sqrt(n-3)
        n = row["n_years"]
        row["power_proxy"] = round(abs(row["r_diff"]) * math.sqrt(max(n - 3, 1)), 3)

    pair_results.sort(key=lambda r: (-r["power_proxy"], -r["abs_r"], r["p"]))
    pvals = [r["p"] for r in pair_results]
    qvals = bh_fdr(pvals)
    for r, q in zip(pair_results, qvals):
        r["q_fdr"] = q

    # keep robust: n_years>=6, power_proxy>=1.5 or q<=0.05
    robust = [
        r
        for r in pair_results
        if r["n_years"] >= 6 and (r["q_fdr"] <= FDR_Q or r["power_proxy"] >= 2.0)
    ]
    if len(robust) < TOP_PAIRS:
        robust = [r for r in pair_results if r["n_years"] >= 6][: max(TOP_PAIRS, 40)]

    top = robust[:TOP_PAIRS]
    # ensure mix sync/opposite
    sync = [r for r in robust if r["sign"] == "sincronizada"][:12]
    opp = [r for r in robust if r["sign"] == "opuesta"][:12]
    chosen = []
    seen = set()
    for r in sync + opp + top:
        key = tuple(sorted([r["species_a"], r["species_b"]]))
        if key in seen:
            continue
        seen.add(key)
        chosen.append(r)
        if len(chosen) >= TOP_PAIRS:
            break

    log(f"pares evaluados: {len(pair_results)}; top figuras: {len(chosen)}")

    # figures top 20
    for i, row in enumerate(chosen, 1):
        ta, tb = row["tid_a"], row["tid_b"]
        slug = f"top{i:02d}_{re.sub(r'[^a-z0-9]+', '_', (row['species_a']+'_'+row['species_b']).lower())[:80]}"
        plot_pair_zones(
            row["species_a"],
            row["species_b"],
            prop[ta],
            prop[tb],
            counts[ta],
            counts[tb],
            effort,
            FIG / f"{slug}.png",
            title_extra=f"{row['sign']} r={row['r_diff']:.2f} lag={row['lag']} q={row['q_fdr']:.3f}",
        )
        row["figure"] = f"material/figuras/cruzadas/{slug}.png"
        row["rank"] = i

    with (OUT / "cruzadas_top20_pares_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "rank",
            "species_a",
            "species_b",
            "sign",
            "r_diff",
            "p",
            "q_fdr",
            "lag",
            "direction",
            "n_years",
            "power_proxy",
            "figure",
            "biblio_status",
            "hypothesis",
        ]
        # biblio lite via globi
        for row in chosen:
            ga = globi_interactions(row["species_a"], limit=25)
            partners = {str(it.get("target", "")).lower() for it in ga}
            hit = row["species_b"].lower() in partners or any(
                row["species_b"].split()[0].lower() in p for p in partners if p
            )
            row["biblio_status"] = "GloBI_hit" if hit else "sin_GloBI"
            row["hypothesis"] = (
                ""
                if hit
                else "HIPÓTESIS: co-tendencia en ciencia ciudadana; no implica interacción"
            )
            time.sleep(0.15)
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(chosen)

    with (OUT / "cruzadas_todos_pares_xcorr_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "species_a",
            "species_b",
            "sign",
            "r_diff",
            "p",
            "q_fdr",
            "lag",
            "direction",
            "n_years",
            "power_proxy",
        ]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(pair_results)

    # ---- Clustering / PCA communities ----
    log("Clustering de tendencias…")
    # matrix spp × years (z-scored CAT proportions)
    years_all = list(range(YEAR0, YEAR1 + 1))
    mat_tids = [tid for tid in series_ok if len(prop_cat[tid]) >= MIN_YEARS]
    mat_tids = mat_tids[:TOP_CLUSTER_SPP]
    X = []
    for tid in mat_tids:
        zs = zscore_series(prop_cat[tid])
        X.append([zs.get(y, 0.0) for y in years_all if effort_cat.get(y, 0) >= MIN_EFFORT_YEAR])
    year_cols = [y for y in years_all if effort_cat.get(y, 0) >= MIN_EFFORT_YEAR]
    X = np.array(X, dtype=float)
    # drop spp with near-zero variance
    keep = np.std(X, axis=1) > 1e-6
    X = X[keep]
    mat_tids = [t for t, k in zip(mat_tids, keep) if k]

    Z = linkage(X, method="average", metric="correlation")
    # aim clusters of size; cut for ~6–12 clusters
    for k in (6, 8, 10, 12):
        lab = fcluster(Z, t=k, criterion="maxclust")
        sizes = np.bincount(lab)[1:]
        if (sizes >= 10).sum() >= 2:
            labels = lab
            nclust = k
            break
    else:
        labels = fcluster(Z, t=8, criterion="maxclust")
        nclust = 8

    # PCA
    pca = PCA(n_components=min(5, X.shape[1], X.shape[0]))
    scores = pca.fit_transform(StandardScaler().fit_transform(X))

    cluster_rows = []
    for cid in range(1, nclust + 1):
        members = [mat_tids[i] for i, L in enumerate(labels) if L == cid]
        if not members:
            continue
        # mean trajectory
        mean_z = X[[i for i, L in enumerate(labels) if L == cid]].mean(axis=0)
        # since when: year of max |slope| of mean
        slopes = np.diff(mean_z)
        turn_i = int(np.argmax(np.abs(slopes))) if len(slopes) else 0
        turn_y = year_cols[turn_i + 1] if turn_i + 1 < len(year_cols) else None
        direction = "sube" if mean_z[-1] > mean_z[0] else "baja"
        cluster_rows.append(
            {
                "cluster": cid,
                "n_species": len(members),
                "direction": direction,
                "turn_year_proxy": turn_y,
                "species": "; ".join(name_of[t] for t in members[:40]),
                "pc1_mean": round(float(scores[[i for i, L in enumerate(labels) if L == cid], 0].mean()), 3),
            }
        )
        # figure mean trajectory
        fig, ax = plt.subplots(figsize=(7.2, 3.2))
        for i, L in enumerate(labels):
            if L != cid:
                continue
            ax.plot(year_cols, X[i], color="#bbb", lw=0.6, alpha=0.5)
        ax.plot(year_cols, mean_z, color="#1f4e79", lw=2.2, label=f"media clúster {cid}")
        if turn_y:
            ax.axvline(turn_y, color="#c45c26", ls="--", label=f"giro ~{turn_y}")
        ax.set_title(
            f"Comunidad {cid}: {len(members)} spp ({direction}). "
            "Series z-score proporción/esfuerzo. Correlación ≠ causalidad."
        )
        ax.set_xlabel("Año")
        ax.set_ylabel("z-score")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.25)
        fig.tight_layout()
        fig.savefig(FIG / f"comunidad_cluster_{cid:02d}.png", dpi=140)
        plt.close(fig)

    with (OUT / "cruzadas_comunidades_clusters_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["cluster", "n_species", "direction", "turn_year_proxy", "pc1_mean", "species"],
        )
        w.writeheader()
        w.writerows(sorted(cluster_rows, key=lambda r: -r["n_species"]))

    # PCA biplot-ish: PC1 vs PC2 colored by cluster
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sc = ax.scatter(scores[:, 0], scores[:, 1], c=labels, cmap="tab10", s=18, alpha=0.85)
    for i, tid in enumerate(mat_tids):
        if abs(scores[i, 0]) > np.percentile(np.abs(scores[:, 0]), 90) or abs(
            scores[i, 1]
        ) > np.percentile(np.abs(scores[:, 1]), 90):
            ax.text(scores[i, 0], scores[i, 1], name_of[tid].split()[0], fontsize=8, alpha=0.8)
    ax.set_xlabel(f"PC1 ({100*pca.explained_variance_ratio_[0]:.1f}%)")
    ax.set_ylabel(f"PC2 ({100*pca.explained_variance_ratio_[1]:.1f}%)")
    ax.set_title("PCA de series anuales z-score (proporción/esfuerzo). Color = clúster.")
    fig.colorbar(sc, ax=ax, label="clúster")
    fig.tight_layout()
    fig.savefig(FIG / "comunidades_pca.png", dpi=140)
    plt.close(fig)

    pca_meta = {
        "n_species": len(mat_tids),
        "n_clusters": nclust,
        "variance_ratio": [float(x) for x in pca.explained_variance_ratio_],
        "years": year_cols,
        "clusters_ge10": sum(1 for r in cluster_rows if r["n_species"] >= 10),
    }
    (OUT / "cruzadas_pca_meta_20261011.json").write_text(
        json.dumps(pca_meta, indent=2), encoding="utf-8"
    )

    # ---- Cascades / BACI-lite / ITS ----
    log("Cascadas BACI / series interrumpidas…")
    cascade_rows = []
    for det in DETONATORS:
        y0 = det.get("year")
        if not y0 or y0 < YEAR0 + 2 or y0 > YEAR1 - 1:
            continue
        pre = list(range(max(YEAR0, y0 - 5), y0))
        post = list(range(y0, min(YEAR1, y0 + 5) + 1))
        if len(pre) < 2 or len(post) < 2:
            continue
        for tid in mat_tids:
            # impact zones mean rate
            pre_vals, post_vals = [], []
            for z in det["zones_impact"]:
                pr = prop[tid].get(z, {})
                pre_vals.extend([pr[y] for y in pre if y in pr])
                post_vals.extend([pr[y] for y in post if y in pr])
            if len(pre_vals) < 2 or len(post_vals) < 2:
                continue
            m_pre, m_post = float(np.mean(pre_vals)), float(np.mean(post_vals))
            if m_pre < 1e-6 and m_post < 1e-6:
                continue
            # simple Welch-ish via rates: use ratio and a crude p from paired year diffs
            # interrupted: compare mean first-diff sign before/after
            delta = m_post - m_pre
            ratio = (m_post / m_pre) if m_pre > 1e-9 else (999.0 if m_post > 0 else 0.0)
            # bootstrap-free p: permutation of labels on combined
            comb = np.array(pre_vals + post_vals)
            npre = len(pre_vals)
            obs = abs(delta)
            rng = np.random.default_rng(42 + tid % 1000)
            ge = 0
            B = 199
            for _ in range(B):
                rng.shuffle(comb)
                d = abs(comb[npre:].mean() - comb[:npre].mean())
                if d >= obs - 1e-15:
                    ge += 1
            p = (ge + 1) / (B + 1)
            cascade_rows.append(
                {
                    "detonator": det["id"],
                    "det_year": y0,
                    "species": name_of[tid],
                    "mean_pre": round(m_pre, 5),
                    "mean_post": round(m_post, 5),
                    "delta": round(delta, 5),
                    "ratio": round(ratio, 4),
                    "p_perm": round(p, 5),
                    "n_pre": len(pre_vals),
                    "n_post": len(post_vals),
                    "is_trigger": name_of[tid] == det.get("species_trigger"),
                }
            )

    p_c = [r["p_perm"] for r in cascade_rows]
    for r, q in zip(cascade_rows, bh_fdr(p_c)):
        r["q_fdr"] = round(q, 5)

    cascade_rows.sort(key=lambda r: (r["detonator"], r["q_fdr"], -abs(r["delta"])))
    with (OUT / "cruzadas_cascadas_baci_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "detonator",
            "det_year",
            "species",
            "mean_pre",
            "mean_post",
            "delta",
            "ratio",
            "p_perm",
            "q_fdr",
            "n_pre",
            "n_post",
            "is_trigger",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(cascade_rows)

    # summary per detonator: top responders q<=0.05
    for det in DETONATORS:
        y0 = det.get("year")
        if not y0:
            continue
        sub = [r for r in cascade_rows if r["detonator"] == det["id"] and r["q_fdr"] <= FDR_Q]
        sub = sorted(sub, key=lambda r: abs(r["delta"]), reverse=True)[:25]
        if not sub:
            continue
        fig, ax = plt.subplots(figsize=(8, max(3.5, 0.28 * len(sub) + 1)))
        names_s = [r["species"] for r in sub][::-1]
        deltas = [r["delta"] for r in sub][::-1]
        colors = ["#c45c26" if d < 0 else "#1f4e79" for d in deltas]
        ax.barh(names_s, deltas, color=colors)
        ax.axvline(0, color="#333", lw=0.6)
        ax.set_xlabel("Δ proporción (post − pre) ×1000 / esfuerzo")
        ax.set_title(
            f"Cascada {det['label']} (año {y0}). FDR q≤0.05. "
            "Correlación temporal ≠ causalidad."
        )
        fig.tight_layout()
        fig.savefig(FIG / f"cascada_{det['id']}.png", dpi=140)
        plt.close(fig)

    # ---- GloBI check for rising spp consumers/prey ----
    log("GloBI redes tróficas (muestra)…")
    # rising: ratio 2020-24 / 2015-19
    rising = []
    for tid in mat_tids:
        pr = prop_cat[tid]
        recent = np.mean([pr[y] for y in range(2020, 2025) if y in pr] or [0])
        prev = np.mean([pr[y] for y in range(2015, 2020) if y in pr] or [0])
        if prev > 0.05 and recent / prev >= 1.5:
            rising.append((tid, recent / prev))
    rising.sort(key=lambda x: -x[1])
    globi_rows = []
    for tid, ratio in rising[:15]:
        nm = name_of[tid]
        ints = globi_interactions(nm, limit=30)
        partners = [f"{it.get('target','')}|{it.get('type','')}" for it in ints[:20]]
        checked = []
        for p in partners[:10]:
            pname = p.split("|")[0].strip()
            if pname in tid_of:
                pt = tid_of[pname]
                pr = prop_cat[pt]
                r2 = np.mean([pr[y] for y in range(2020, 2025) if y in pr] or [0])
                p2 = np.mean([pr[y] for y in range(2015, 2020) if y in pr] or [0])
                rr = (r2 / p2) if p2 > 1e-9 else None
                checked.append(f"{pname}:{rr}")
        globi_rows.append(
            {
                "species": nm,
                "ratio_5y": round(ratio, 3),
                "globi_n": len(ints),
                "globi_sample": "; ".join(partners[:8]),
                "partners_in_data": "; ".join(checked) if checked else "",
                "interpretation": (
                    "HIPÓTESIS trófica pendiente"
                    if not checked
                    else "parejas GloBI con series en datos — correlación, no causalidad"
                ),
            }
        )
        time.sleep(0.2)

    with (OUT / "cruzadas_globi_rising_20261011.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "species",
                "ratio_5y",
                "globi_n",
                "globi_sample",
                "partners_in_data",
                "interpretation",
            ],
        )
        w.writeheader()
        w.writerows(globi_rows)

    # effort figure
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    for z, col in zip(ZONES, ["#1f4e79", "#2a9d8f", "#c45c26"]):
        ys = sorted(effort[z])
        ax.plot(ys, [effort[z][y] for y in ys], "-o", ms=3, color=col, label=z.replace("_", " "))
    ax.set_yscale("log")
    ax.set_ylabel("Observaciones (esfuerzo)")
    ax.set_xlabel("Año")
    ax.set_title("Esfuerzo por zona (public_observations)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(FIG / "esfuerzo_por_zona.png", dpi=140)
    plt.close(fig)

    meta = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M %Z"),
        "elapsed_s": round(time.time() - t0, 1),
        "n_marine_match": len(tid_marine),
        "n_eligible": len(eligible),
        "n_series_ok": len(series_ok),
        "n_pairs_tested": len(pair_results),
        "n_top_figures": len(chosen),
        "n_clusters": nclust,
        "clusters_ge10": pca_meta["clusters_ge10"],
        "n_cascade_tests": len(cascade_rows),
        "n_cascade_sig": sum(1 for r in cascade_rows if r["q_fdr"] <= FDR_Q),
        "detonators": DETONATORS,
        "pinna_note": pinna_note,
        "method": {
            "proportion": "obs_spp / effort_zone_year × 1000",
            "xcorr": "pearson on first differences, lag 0..3, BH-FDR",
            "min_years": MIN_YEARS,
            "min_obs": MIN_OBS_SPP,
            "disclaimer": "correlación ≠ causalidad",
        },
    }
    (OUT / "cruzadas_meta_20261011.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log(f"DONE in {meta['elapsed_s']}s → {OUT} / {FIG}")


if __name__ == "__main__":
    main()
