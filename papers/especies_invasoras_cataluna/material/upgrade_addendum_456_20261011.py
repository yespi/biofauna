#!/usr/bin/env python3
"""Addendum Gustavo 19:07 + punto 6 — mapas EPSG:3035, prosperan v2, primeras fechas.

Sin GPU. Python: /mnt/docker/biofauna/.venv/bin/python
"""
from __future__ import annotations

import csv
import math
import re
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import shapefile
from pyproj import Transformer

ROOT = Path("/mnt/docker/biofauna-public/papers/especies_invasoras_cataluna")
FIG = ROOT / "material" / "figuras"
FIG_EXP = FIG / "expansion"
FIG_P = FIG / "prosperan"
ART = Path("/mnt/docker/biofauna/artifacts/invasoras/origen_expansion")
GEO = ART / "geo"
FIG_EXP.mkdir(parents=True, exist_ok=True)
FIG_P.mkdir(parents=True, exist_ok=True)

T3035 = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
BOX_CAT = dict(swlat=40.45, nelat=42.95, swlng=0.1, nelng=3.4)

# iNat iconic / high-rank IDs for group effort (fallback → total CAT)
GROUP_ANCESTOR = {
    "Plantae": 47126,
    "Peces": 47178,
    "Aves": 3,
    "Mammalia": 40151,
    "Reptilia": 26036,
    "Insecta": 47158,
    "Crustacea": 47120,  # Arthropoda (Malacostraca ancestry incompleto)
    "Platyhelminthes": 1,  # Animalia fallback
    "Algas": 48222,  # Chromista
    "Mollusca": 47115,
}

PAPER_MARINE = {
    605992: ("Magallana gigas", "Mollusca", "marino"),
    57779: ("Asparagopsis armata", "Algas", "marino"),
    67555: ("Codium fragile", "Algas", "marino"),
    734863: ("Caulerpa cylindracea", "Algas", "marino"),
    107341: ("Oculina patagonica", "Algas", "marino"),  # cnidario; esfuerzo marino≈Chromista/total
    49504: ("Callinectes sapidus", "Crustacea", "marino"),
}

# Literatura / inventarios — año mínimo conocido (Med o CAT/ES según contexto)
LIT_FIRST = {
    "Pterois miles": {"med": 1991, "fuente": "Golani & Sonin 1992"},
    "Caulerpa cylindracea": {"med": 1990, "fuente": "Zenetos inventarios ~1990s"},
    "Caulerpa taxifolia": {"med": 1984, "fuente": "Meinesz / Jousson"},
    "Oculina patagonica": {"med": 1974, "fuente": "Zibrowius 1974"},
    "Lagocephalus sceleratus": {"med": 2003, "fuente": "lit. E Med 2000s"},
    "Asparagopsis armata": {"med": 1923, "fuente": "Med histórico fouling (Andreakis et al.)"},
    "Callinectes sapidus": {"med": 1948, "fuente": "Med histórico; Segura 2016 ES"},
    "Rugulopteryx okamurae": {"es": 2015, "fuente": "Estrecho ~2015–2019"},
    "Magallana gigas": {"es": 1969, "med": 1970, "fuente": "Grizel & Héral 1991 Francia; cultivo Med"},
    "Codium fragile": {"med": 1950, "fuente": "Med histórico fouling (hipótesis década)"},
    "Procambarus clarkii": {"es": 1973, "cat": 1983, "fuente": "lit. acuicultura ES"},
    "Trachemys scripta elegans": {"es": 1980, "cat": 1994, "fuente": "mascotismo; BQ T.scripta 1994"},
    "Vespa velutina nigrithorax": {"es": 2010, "cat": 2012, "fuente": "expansión desde Francia"},
    "Ailanthus altissima": {"es": 1800, "fuente": "ornamental histórico (aprox.)"},
    "Neogale vison": {"es": 1958, "fuente": "granjas peleteras"},
    "Myocastor coypus": {"es": 1970, "fuente": "peletería (aprox.)"},
    "Gambusia holbrooki": {"es": 1921, "fuente": "control biológico histórico"},
}


def sql(q: str):
    r = subprocess.run(
        [
            "docker",
            "exec",
            "postgres-global",
            "psql",
            "-U",
            "admin_yespi",
            "-d",
            "fauna",
            "-At",
            "-F",
            "|",
            "-c",
            q,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return [ln.split("|") for ln in r.stdout.splitlines() if ln.strip()]


def to_xy(lng, lat):
    return T3035.transform(float(lng), float(lat))


def year_from_text(s: str | None):
    if not s:
        return None
    s = str(s).strip()
    if not s or s in ("—", "-", "n/a", "sin obs BQ", "sin obs BQ/ES", "sin filas BQ"):
        return None
    # prefer YYYY-MM / YYYY-MM-DD / bare year
    m = re.search(r"(19|20)\d{2}", s)
    return int(m.group(0)) if m else None


def build_primeras_fechas():
    """Min year across lit / presencia / BQ / tabla origen → primeras_fechas_20261011.csv"""
    pres = {}
    with (ROOT / "presencia_cat_es.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            pres[r["especie"]] = r

    tabla = {}
    with (ROOT / "tabla_origen_vias_resumen.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            tabla[r["especie"]] = r

    bq = {}
    with (ROOT / "primera_obs_regiones_bq.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            bq[r["especie"]] = r

    spp = sorted(set(pres) | set(tabla) | set(bq) | set(LIT_FIRST))
    rows = []
    for sp in spp:
        p = pres.get(sp, {})
        t = tabla.get(sp, {})
        b = bq.get(sp, {})
        lit = LIT_FIRST.get(sp, {})

        cands_cat = []
        cands_es = []
        cands_med = []
        fuentes = []

        for y, src in [
            (year_from_text(p.get("primera_obs_catalunya")), f"presencia_CAT:{p.get('primera_obs_catalunya_fuente','')}"),
            (year_from_text(t.get("primera_catalunya")), "tabla_origen_CAT"),
            (year_from_text(b.get("primera_cat_caja")), "BQ_CAT"),
            (lit.get("cat"), f"lit_CAT:{lit.get('fuente','')}"),
        ]:
            if y:
                cands_cat.append(y)
                fuentes.append(f"CAT {y}←{src}")

        for y, src in [
            (year_from_text(p.get("primera_obs_espana")), f"presencia_ES:{p.get('primera_obs_espana_fuente','')}"),
            (year_from_text(t.get("primera_espana")), "tabla_origen_ES"),
            (year_from_text(b.get("primera_es_caja")), "BQ_ES"),
            (lit.get("es"), f"lit_ES:{lit.get('fuente','')}"),
        ]:
            if y:
                cands_es.append(y)
                fuentes.append(f"ES {y}←{src}")

        for y, src in [
            (year_from_text(t.get("primera_mediterraneo")), "tabla_origen_Med"),
            (year_from_text(b.get("primera_med")), "BQ_Med"),
            (lit.get("med"), f"lit_Med:{lit.get('fuente','')}"),
        ]:
            if y:
                cands_med.append(y)
                fuentes.append(f"Med {y}←{src}")

        y_cat = min(cands_cat) if cands_cat else ""
        y_es = min(cands_es) if cands_es else ""
        y_med = min(cands_med) if cands_med else ""
        all_y = [y for y in (y_cat, y_es, y_med) if y != ""]
        # also bare lit without region
        if lit.get("es") or lit.get("med") or lit.get("cat"):
            pass
        y_any = min(all_y) if all_y else ""

        # BF later than literature is NOT a discovery — flag it
        bf_cat = year_from_text(p.get("primera_obs_catalunya"))
        flag = ""
        if y_any and bf_cat and bf_cat > y_any:
            flag = f"BF/iNat CAT ({bf_cat}) posterior a 1ª fuente ({y_any}); no usar BF como 1ª"

        rows.append(
            dict(
                especie=sp,
                primera_any=y_any,
                primera_catalunya=y_cat,
                primera_espana=y_es,
                primera_mediterraneo=y_med,
                presencia_cat=p.get("presencia_catalunya", ""),
                grupo=p.get("grupo_taxonomico") or PAPER_MARINE.get(
                    next((k for k, v in PAPER_MARINE.items() if v[0] == sp), None), ("", "", "")
                )[1],
                medio=p.get("medio")
                or next((v[2] for v in PAPER_MARINE.values() if v[0] == sp), ""),
                nota_fuentes="; ".join(fuentes[:8]),
                aviso_bf_no_es_primera=flag,
            )
        )

    out = ROOT / "material" / "primeras_fechas_20261011.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "especie",
                "primera_any",
                "primera_catalunya",
                "primera_espana",
                "primera_mediterraneo",
                "presencia_cat",
                "grupo",
                "medio",
                "nota_fuentes",
                "aviso_bf_no_es_primera",
            ],
        )
        w.writeheader()
        w.writerows(rows)
    print("wrote", out.name, "n=", len(rows), "con_aviso_bf=", sum(1 for r in rows if r["aviso_bf_no_es_primera"]))
    return {r["especie"]: r for r in rows}


def load_coast_land_projected(extent_ll, pad=0.4):
    """Return land/coast polylines in EPSG:3035 clipped to lon/lat extent."""
    lng0, lng1, lat0, lat1 = extent_ll
    coast_r = shapefile.Reader(str(GEO / "ne_10m_coastline"))
    land_r = shapefile.Reader(str(GEO / "ne_10m_land"))
    pad_lng0, pad_lng1 = lng0 - pad, lng1 + pad
    pad_lat0, pad_lat1 = lat0 - pad, lat1 + pad

    def parts(reader, as_poly=False):
        out = []
        for sh in reader.shapes():
            pts = sh.points
            idxs = list(sh.parts) + [len(pts)]
            for i in range(len(idxs) - 1):
                seg = pts[idxs[i] : idxs[i + 1]]
                if not seg:
                    continue
                xs = [p[0] for p in seg]
                ys = [p[1] for p in seg]
                if max(xs) < pad_lng0 or min(xs) > pad_lng1 or max(ys) < pad_lat0 or min(ys) > pad_lat1:
                    continue
                px, py = [], []
                for x, y in seg:
                    if pad_lng0 <= x <= pad_lng1 and pad_lat0 <= y <= pad_lat1:
                        e, n = to_xy(x, y)
                        px.append(e)
                        py.append(n)
                if len(px) >= (3 if as_poly else 2):
                    out.append((px, py))
        return out

    return parts(coast_r), parts(land_r, as_poly=True)


def plot_expansion_maps_3035():
    """Regen figuras/expansion/* con EPSG:3035 + NE 10m + aspect equal."""
    SPECIES = {
        123459: "Pterois miles",
        734863: "Caulerpa cylindracea",
        107341: "Oculina patagonica",
        132368: "Lagocephalus sceleratus",
        57779: "Asparagopsis armata",
        49504: "Callinectes sapidus",
        67555: "Codium fragile",
        605992: "Magallana gigas",
    }
    rows = []
    with (ART / "pobs_key_taxa.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                tid = int(r["taxon_id"])
                lat = float(r["lat"])
                lng = float(r["lng"])
                y = int(r["obs_year"])
            except (TypeError, ValueError):
                continue
            if tid in SPECIES:
                rows.append((tid, y, lat, lng))

    PERIODS = [(2000, 2004), (2005, 2009), (2010, 2014), (2015, 2019), (2020, 2024), (2025, 2026)]
    # Med box
    extent = (-6.5, 37.5, 30.0, 46.5)
    coast, land = load_coast_land_projected(extent)
    corners = [to_xy(x, y) for x in (extent[0], extent[1]) for y in (extent[2], extent[3])]
    e0, e1 = min(c[0] for c in corners), max(c[0] for c in corners)
    n0, n1 = min(c[1] for c in corners), max(c[1] for c in corners)

    for tid, name in SPECIES.items():
        pts = [(y, lat, lng) for t, y, lat, lng in rows if t == tid]
        fig, axes = plt.subplots(2, 3, figsize=(12, 7.2))
        axes = axes.ravel()
        for ax, (y0, y1) in zip(axes, PERIODS):
            ax.set_facecolor("#cfe8f3")
            ax.set_xlim(e0, e1)
            ax.set_ylim(n0, n1)
            ax.set_aspect("equal", adjustable="box")
            for xs, ys in land:
                ax.fill(xs, ys, facecolor="#f0e4c8", edgecolor="none", zorder=1)
            for xs, ys in coast:
                ax.plot(xs, ys, color="#4e342e", lw=0.45, zorder=2)
            sub = [(lat, lng) for y, lat, lng in pts if y0 <= y <= y1]
            if sub:
                xs = [to_xy(lng, lat)[0] for lat, lng in sub]
                ys = [to_xy(lng, lat)[1] for lat, lng in sub]
                ax.scatter(xs, ys, s=8, c="#1a5276", alpha=0.65, edgecolors="none", zorder=3)
            ax.set_title(f"{y0}–{y1}  n={len(sub)}", fontsize=9)
            ax.tick_params(labelsize=6)
            ax.set_xticks([])
            ax.set_yticks([])
        fig.suptitle(
            f"{name}: expansión BioQuest — EPSG:3035 (ETRS89-LAEA) · costa NE 10m",
            fontsize=11,
        )
        fig.tight_layout()
        out = FIG_EXP / f"expansion_5y_{name.replace(' ', '_')}.png"
        fig.savefig(out, dpi=140)
        plt.close(fig)
        # copy to artifacts for ORIGEN links
        art_out = ART / out.name
        art_out.write_bytes(out.read_bytes())
        print("wrote", out.name)

    # multiespecie panels
    for y0, y1 in [(2010, 2014), (2015, 2019), (2020, 2024)]:
        fig, ax = plt.subplots(figsize=(9, 6.5))
        ax.set_facecolor("#cfe8f3")
        ax.set_xlim(e0, e1)
        ax.set_ylim(n0, n1)
        ax.set_aspect("equal", adjustable="box")
        for xs, ys in land:
            ax.fill(xs, ys, facecolor="#f0e4c8", edgecolor="none", zorder=1)
        for xs, ys in coast:
            ax.plot(xs, ys, color="#4e342e", lw=0.5, zorder=2)
        cmap = plt.cm.tab10
        for i, (tid, name) in enumerate(SPECIES.items()):
            sub = [(lat, lng) for t, y, lat, lng in rows if t == tid and y0 <= y <= y1]
            if not sub:
                continue
            xs = [to_xy(lng, lat)[0] for lat, lng in sub]
            ys = [to_xy(lng, lat)[1] for lat, lng in sub]
            ax.scatter(xs, ys, s=10, alpha=0.55, c=[cmap(i / 10)], label=f"{name} (n={len(sub)})", zorder=3)
        ax.legend(fontsize=7, loc="lower left", framealpha=0.9)
        ax.set_title(f"Invasoras clave {y0}–{y1} — EPSG:3035 · NE 10m · aspecto 1:1")
        ax.set_xticks([])
        ax.set_yticks([])
        fig.tight_layout()
        out = FIG_EXP / f"expansion_multiespecie_{y0}-{y1}.png"
        fig.savefig(out, dpi=140)
        plt.close(fig)
        (ART / out.name).write_bytes(out.read_bytes())
        print("wrote", out.name)


def fetch_effort_by_group():
    """Yearly CAT effort total + by taxonomic group (ancestry; fallback total)."""
    total = {}
    with (ROOT / "esfuerzo_bioquest_anual.csv").open(encoding="utf-8") as f:
        # support both schemas
        rows = list(csv.DictReader(f))
        for r in rows:
            y = int(r.get("year") or r.get("año"))
            n = float(r.get("n_obs_caja_cat") or r.get("obs_totales_catalogo") or 0)
            total[y] = n

    by_group = defaultdict(dict)
    for grupo, anc in GROUP_ANCESTOR.items():
        q = f"""
        SELECT o.obs_year::text, count(*)::text
        FROM public_observations o
        JOIN taxon_ancestry a ON a.taxon_id = o.taxon_id
        WHERE o.lat BETWEEN {BOX_CAT['swlat']} AND {BOX_CAT['nelat']}
          AND o.lng BETWEEN {BOX_CAT['swlng']} AND {BOX_CAT['nelng']}
          AND o.obs_year IS NOT NULL
          AND ({anc} = ANY(a.ancestor_ids) OR a.taxon_id = {anc})
        GROUP BY 1 ORDER BY 1;
        """
        try:
            for y, n in sql(q):
                by_group[grupo][int(y)] = float(n)
        except subprocess.CalledProcessError as e:
            print("WARN effort group", grupo, e)
    return total, by_group


def mann_kendall(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 4:
        return None, None
    s = 0
    for i in range(n - 1):
        s += np.sign(x[i + 1 :] - x[i]).sum()
    var = n * (n - 1) * (2 * n + 5) / 18.0
    if var <= 0:
        return None, None
    z = (s - 1) / math.sqrt(var) if s > 0 else (s + 1) / math.sqrt(var) if s < 0 else 0.0
    tau = s / (n * (n - 1) / 2)
    return float(tau), float(z)


def poisson_ci(obs, effort, z=1.96):
    """Rate per 1000 effort with approx Poisson CI."""
    if effort <= 0:
        return 0.0, 0.0, 0.0
    rate = 1000.0 * obs / effort
    se = 1000.0 * math.sqrt(max(obs, 0)) / effort
    return rate, max(0.0, rate - z * se), rate + z * se


def absence_power(hist_rates, recent_efforts, alpha=0.05):
    """P(all zero | historical mean rate) under Poisson; power = 1 - that.

    hist_rates: per-1000-effort rates in years with presence
    recent_efforts: list of effort values in recent absent years
    """
    hist = [r for r in hist_rates if r > 0]
    if not hist or not recent_efforts:
        return None, None
    r_mean = float(np.mean(hist))  # per 1000
    mu = sum((r_mean / 1000.0) * e for e in recent_efforts if e > 0)
    if mu <= 0:
        return None, None
    p_miss = math.exp(-mu)
    return p_miss, 1.0 - p_miss


def prosperan_v2(fechas: dict):
    total_eff, group_eff = fetch_effort_by_group()

    # species present in CAT from presencia + paper marine with BQ CAT
    present = []
    meta = {}
    with (ROOT / "presencia_cat_es.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("presencia_catalunya") == "sí":
                present.append(r["especie"])
                meta[r["especie"]] = r

    # add marine paper spp with CAT obs from serie or BQ
    by = defaultdict(dict)
    with (ROOT / "serie_anual_normalizada.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("region") != "Catalunya":
                continue
            sp = r["especie"]
            y = int(r["year"])
            by[sp][y] = float(r["obs"] or 0)

    # fetch CAT yearly for paper marine not in serie
    for tid, (name, grupo, medio) in PAPER_MARINE.items():
        if name not in by or sum(by[name].values()) == 0:
            q = f"""
            SELECT obs_year::text, count(*)::text FROM public_observations
            WHERE taxon_id={tid}
              AND lat BETWEEN {BOX_CAT['swlat']} AND {BOX_CAT['nelat']}
              AND lng BETWEEN {BOX_CAT['swlng']} AND {BOX_CAT['nelng']}
              AND obs_year IS NOT NULL
            GROUP BY 1 ORDER BY 1;
            """
            for y, n in sql(q):
                by[name][int(y)] = float(n)
        if name not in present and sum(by[name].values()) > 0:
            present.append(name)
            meta[name] = dict(grupo_taxonomico=grupo, medio=medio)

    present = sorted(set(present))
    rows_out = []
    panel = []

    for sp in present:
        grupo = (meta.get(sp) or {}).get("grupo_taxonomico") or fechas.get(sp, {}).get("grupo") or "Plantae"
        years_obs = sorted(by.get(sp, {}))
        if not years_obs:
            rows_out.append(
                dict(
                    especie=sp,
                    categoria="sin_serie",
                    tau="",
                    z="",
                    primera_any=fechas.get(sp, {}).get("primera_any", ""),
                    primera_serie="",
                    ultima="",
                    n_obs=0,
                    potencia_ausencia="",
                    p_miss="",
                    nota="sin serie CAT",
                )
            )
            continue

        # series from min(primera_any, first BQ year) to 2026
        y_first_src = year_from_text(str(fechas.get(sp, {}).get("primera_any") or ""))
        y0 = min(years_obs)
        if y_first_src and y_first_src < y0:
            # literature earlier: still plot BQ from first BQ year (can't invent zeros before BQ era)
            pass
        y_start = y0
        ys = list(range(y_start, 2027))
        rates, lo, hi, obs_l, eff_l = [], [], [], [], []
        for y in ys:
            o = by[sp].get(y, 0.0)
            # effort: group if available ≥20% of total, else total
            e_g = group_eff.get(grupo, {}).get(y, 0.0)
            e_t = total_eff.get(y, 0.0)
            e = e_g if e_g >= 0.05 * e_t and e_g > 0 else e_t
            r, a, b = poisson_ci(o, e)
            rates.append(r)
            lo.append(a)
            hi.append(b)
            obs_l.append(o)
            eff_l.append(e)

        rates_a = np.asarray(rates)
        ys_a = np.asarray(ys)
        # recent absence
        absent_gap = 5
        recent_mask = ys_a >= (2026 - absent_gap)
        earlier_mask = ~recent_mask
        cat = None
        p_miss = pot = None
        nota = ""
        if earlier_mask.any() and rates_a[earlier_mask].sum() > 0 and rates_a[recent_mask].sum() == 0:
            hist_r = rates_a[earlier_mask & (rates_a > 0)]
            recent_e = [eff_l[i] for i, m in enumerate(recent_mask) if m]
            p_miss, pot = absence_power(hist_r, recent_e)
            n_hist = int(sum(obs_l[i] for i, m in enumerate(earlier_mask) if m))
            n_hist_yrs = int(((earlier_mask) & (rates_a > 0)).sum())
            # potencia solo creíble con ≥5 obs históricas en ≥2 años (evita n=1 → falsa certeza)
            if (
                pot is not None
                and pot >= 0.95
                and n_hist >= 5
                and n_hist_yrs >= 2
            ):
                cat = "desaparecida"
                nota = (
                    f"0 obs últimos {absent_gap} a con potencia≥0.95 "
                    f"(p_miss={p_miss:.3g}; n_hist={n_hist})"
                )
            else:
                cat = "desaparecida_proxy"
                nota = (
                    f"0 obs últimos {absent_gap} a; "
                    f"potencia/n insuficiente (p_miss={p_miss}; n_hist={n_hist})"
                )

        if cat is None:
            # trim leading zeros
            first = int(np.argmax(rates_a > 0)) if rates_a.sum() > 0 else 0
            r_use = rates_a[first:]
            if len(r_use) < 4:
                cat = "dato_escaso"
                nota = "n años < 4 tras 1ª obs BQ"
                tau = z = None
            else:
                tau, z = mann_kendall(r_use)
                mid = len(r_use) // 2
                m0 = float(r_use[:mid].mean()) if mid else 0.0
                m1 = float(r_use[mid:].mean())
                ratio = (m1 / m0) if m0 > 1e-12 else (99.0 if m1 > 0 else 1.0)
                nota = f"ratio_2a/1a={ratio:.2f}; esfuerzo={grupo}|total"
                if z is not None and z >= 1.64 and ratio >= 1.3:
                    cat = "en_expansion"
                elif z is not None and z <= -1.64 and ratio <= 0.7:
                    cat = "en_declive"
                else:
                    cat = "estable"
        else:
            tau = z = None

        ultima = max((y for y in years_obs if by[sp].get(y, 0) > 0), default="")
        rows_out.append(
            dict(
                especie=sp,
                categoria=cat,
                tau=f"{tau:.3f}" if tau is not None else "",
                z=f"{z:.2f}" if z is not None else "",
                primera_any=fechas.get(sp, {}).get("primera_any", ""),
                primera_serie=y_start,
                ultima=ultima,
                n_obs=int(sum(by[sp].values())),
                potencia_ausencia=f"{pot:.3f}" if pot is not None else "",
                p_miss=f"{p_miss:.3g}" if p_miss is not None else "",
                nota=nota,
                grupo=grupo,
            )
        )
        panel.append((sp, ys, rates, lo, hi, cat))

        # per-species chart
        fig, ax = plt.subplots(figsize=(7.2, 3.4))
        ax.plot(ys, rates, "-o", ms=3, color="#1f618d", lw=1.3, label="tasa/esfuerzo×1000")
        ax.fill_between(ys, lo, hi, color="#1f618d", alpha=0.18, label="IC Poisson ≈95%")
        ax.set_title(f"{sp} — {cat} · grupo={grupo}")
        ax.set_xlabel("Año")
        ax.set_ylabel("obs / esfuerzo (grupo|caja) ×1000")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc="upper left")
        if y_first_src:
            ax.axvline(y_first_src, color="#c0392b", ls="--", lw=0.9, alpha=0.7)
            ax.text(y_first_src, ax.get_ylim()[1] * 0.92, f"1ª fuente {y_first_src}", fontsize=7, color="#c0392b")
        fig.tight_layout()
        safe = sp.replace(" ", "_").replace("/", "_")
        fig.savefig(FIG_P / f"trend_{safe}.png", dpi=120)
        plt.close(fig)

    # CSV
    out_csv = ROOT / "material" / "prosperan_desaparecen_20261011.csv"
    fields = [
        "especie",
        "categoria",
        "tau",
        "z",
        "primera_any",
        "primera_serie",
        "ultima",
        "n_obs",
        "potencia_ausencia",
        "p_miss",
        "grupo",
        "nota",
    ]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows_out)

    # small multiples — all
    panel = sorted(panel, key=lambda t: t[0])
    n = len(panel)
    ncols = 5
    nrows = max(1, math.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 2.35 * nrows), sharex=True)
    axes = np.array(axes).reshape(-1)
    colors = {
        "en_expansion": "#c0392b",
        "estable": "#2980b9",
        "en_declive": "#8e44ad",
        "desaparecida": "#1c2833",
        "desaparecida_proxy": "#7f8c8d",
        "dato_escaso": "#95a5a6",
    }
    for i, (sp, ys, rates, lo, hi, cat) in enumerate(panel):
        ax = axes[i]
        ax.plot(ys, rates, color=colors.get(cat, "#333"), lw=1.15)
        ax.fill_between(ys, lo, hi, color=colors.get(cat, "#333"), alpha=0.12)
        ax.set_title(f"{sp}\n({cat})", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.2)
    for j in range(len(panel), len(axes)):
        axes[j].axis("off")
    fig.suptitle(
        "¿Prosperan o desaparecen? — tasa corregida por esfuerzo (grupo|caja) · IC Poisson · EPSG zona CAT",
        fontsize=11,
    )
    fig.tight_layout()
    panel_path = FIG / "prosperan_panel_small_multiples.png"
    fig.savefig(panel_path, dpi=140)
    plt.close(fig)

    # markdown
    counts = defaultdict(int)
    for r in rows_out:
        counts[r["categoria"]] += 1
    lines = [
        "# ¿Prosperan o desaparecen? — invasoras en Cataluña",
        "",
        "**Generado:** 2026-10-11 ~19:50 CEST (addendum puntos 5–6). **Sin GPU.**",
        "",
        "Tasa anual = `obs_especie / esfuerzo_grupo_o_caja × 1000`.",
        "Esfuerzo: preferente por grupo taxonómico (ancestry iNat en caja CAT); si cobertura <5 % del total, se usa esfuerzo total de la caja.",
        "IC: Poisson ±1,96√obs / esfuerzo. Tendencia: Mann–Kendall sobre la tasa desde la 1ª obs BioQuest.",
        "1ª fecha de referencia: `primeras_fechas_20261011.csv` (mínimo lit./BQ/presencia; BF posterior no cuenta como hallazgo).",
        "",
        "Clasificación:",
        "",
        "- **en_expansion:** Z≥1,64 y ratio 2ª/1ª mitad ≥1,3",
        "- **en_declive:** Z≤−1,64 y ratio ≤0,7",
        "- **estable:** resto con serie suficiente",
        "- **desaparecida:** 0 obs en últimos 5 años y potencia ≥0,95 de haber detectado la tasa histórica",
        "- **desaparecida_proxy:** 0 obs recientes sin potencia suficiente",
        "- **dato_escaso / sin_serie:** n insuficiente",
        "",
        "## Resumen",
        "",
        "| Categoría | N |",
        "|---|---:|",
    ]
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {k} | {v} |")
    lines += [
        "",
        f"CSV: [`prosperan_desaparecen_20261011.csv`](material/prosperan_desaparecen_20261011.csv). "
        f"Panel: [`figuras/prosperan_panel_small_multiples.png`](material/figuras/prosperan_panel_small_multiples.png). "
        f"Series: [`figuras/prosperan/`](material/figuras/prosperan/).",
        "",
        "## Destacadas: declive o desaparición",
        "",
        "| Especie | Cat. | tau | Z | 1ª fuente | 1ª–últ. BQ | n | potencia | Nota |",
        "|---|---|---:|---:|---:|---|---:|---:|---|",
    ]
    focus = [r for r in rows_out if r["categoria"] in ("en_declive", "desaparecida", "desaparecida_proxy")]
    if not focus:
        lines.append("| — | — | — | — | — | — | — | — | Ninguna con señal clara |")
    for r in sorted(focus, key=lambda x: x["categoria"]):
        lines.append(
            f"| *{r['especie']}* | {r['categoria']} | {r['tau'] or '—'} | {r['z'] or '—'} | "
            f"{r.get('primera_any') or '—'} | {r.get('primera_serie','—')}–{r.get('ultima','—')} | "
            f"{r.get('n_obs','—')} | {r.get('potencia_ausencia') or '—'} | {r['nota']} |"
        )
    lines += [
        "",
        "## Lectura",
        "",
        "1. El esfuerzo caja crece ~84× (2013→2024): sin normalizar, casi todo «expande».",
        "2. **desaparecida** exige potencia estadística; **desaparecida_proxy** es solo «no vista».",
        "3. La 1ª fecha de literatura puede ser décadas anterior a BioQuest; la serie gráfica empieza en la 1ª obs BQ.",
        "4. GLM Poisson formal con offset queda como mejora; aquí Mann–Kendall + IC Poisson + potencia de ausencia.",
        "",
    ]
    (ROOT / "PROSPERAN_O_DESAPARECEN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        "prosperan v2",
        len(rows_out),
        "panel",
        n,
        "focus",
        len(focus),
        "counts",
        dict(counts),
    )
    return rows_out


def main():
    fechas = build_primeras_fechas()
    plot_expansion_maps_3035()
    prosperan_v2(fechas)


if __name__ == "__main__":
    main()
