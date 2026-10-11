#!/usr/bin/env python3
"""Mapas CAT en UTM31N + costa NE 10m; sección ¿Prosperan o desaparecen?

Orden Robotin addendum 19:07 (puntos 4–5). Sin GPU.
"""
from __future__ import annotations

import csv
import math
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 10, "axes.labelsize": 11, "xtick.labelsize": 9, "ytick.labelsize": 9, "axes.titlesize": 12})
import numpy as np
import shapefile
from pyproj import Transformer

ROOT = Path("/mnt/docker/biofauna-public/papers/especies_invasoras_cataluna")
FIG = ROOT / "material" / "figuras"
FIG_P = FIG / "prosperan"
FIG_P.mkdir(parents=True, exist_ok=True)
GEO = Path("/mnt/docker/biofauna/artifacts/invasoras/origen_expansion/geo")
PRES = ROOT / "presencia_cat_es.csv"
SERIE = ROOT / "serie_anual_normalizada.csv"
ESF = ROOT / "esfuerzo_bioquest_anual.csv"

# ETRS89 / UTM zone 31N — Cataluña
TRANSFORMER = Transformer.from_crs("EPSG:4326", "EPSG:25831", always_xy=True)

BOX_CAT = dict(swlat=40.45, nelat=42.95, swlng=0.1, nelng=3.4)
PAPER_TAXA = {
    39782: ("Trachemys scripta", "agua_dulce"),
    51271: ("Trachemys scripta elegans", "agua_dulce"),
    1264432: ("Neogale vison", "terrestre"),
    49504: ("Callinectes sapidus", "marino"),
    57779: ("Asparagopsis armata", "marino"),
    605992: ("Magallana gigas", "marino"),
    67555: ("Codium fragile", "marino"),
    734863: ("Caulerpa cylindracea", "marino"),
    107341: ("Oculina patagonica", "marino"),
}
MEDIO_COLOR = {
    "marino": "#1a5276",
    "agua_dulce": "#148f77",
    "terrestre": "#a04000",
}


def to_utm(lng, lat):
    return TRANSFORMER.transform(lng, lat)


def sql(q: str):
    r = subprocess.run(
        ["docker", "exec", "postgres-global", "psql", "-U", "admin_yespi", "-d", "fauna", "-At", "-F", "|", "-c", q],
        capture_output=True,
        text=True,
        check=True,
    )
    return [ln.split("|") for ln in r.stdout.splitlines() if ln.strip()]


def load_coast_utm(xlim_ll, ylim_ll):
    coast = shapefile.Reader(str(GEO / "ne_10m_coastline"))
    land = shapefile.Reader(str(GEO / "ne_10m_land"))
    pad = 0.3
    lng0, lng1 = xlim_ll[0] - pad, xlim_ll[1] + pad
    lat0, lat1 = ylim_ll[0] - pad, ylim_ll[1] + pad

    def parts(reader):
        out = []
        for sh in reader.shapes():
            pts = sh.points
            parts_i = list(sh.parts) + [len(pts)]
            for i in range(len(parts_i) - 1):
                seg = pts[parts_i[i] : parts_i[i + 1]]
                xs = [p[0] for p in seg]
                ys = [p[1] for p in seg]
                if not xs:
                    continue
                if max(xs) < lng0 or min(xs) > lng1 or max(ys) < lat0 or min(ys) > lat1:
                    continue
                ux, uy = [], []
                for x, y in seg:
                    if lng0 <= x <= lng1 and lat0 <= y <= lat1:
                        e, n = to_utm(x, y)
                        ux.append(e)
                        uy.append(n)
                if len(ux) >= 2:
                    out.append((ux, uy))
        return out

    return parts(coast), parts(land)


def fetch_points():
    ids = ",".join(str(i) for i in PAPER_TAXA)
    q = f"""
    SELECT taxon_id::text, lat::text, lng::text, obs_year::text
    FROM public_observations
    WHERE taxon_id = ANY(ARRAY[{ids}]::int[])
      AND lat BETWEEN {BOX_CAT['swlat']} AND {BOX_CAT['nelat']}
      AND lng BETWEEN {BOX_CAT['swlng']} AND {BOX_CAT['nelng']}
      AND lat IS NOT NULL AND lng IS NOT NULL AND obs_year IS NOT NULL;
    """
    pts = []
    for tid, lat, lng, y in sql(q):
        name, medio = PAPER_TAXA[int(tid)]
        e, n = to_utm(float(lng), float(lat))
        pts.append(dict(name=name, medio=medio, e=e, n=n, year=int(float(y))))
    return pts


def plot_decade_maps_utm(pts):
    xlim_ll = (0.0, 3.5)
    ylim_ll = (40.4, 43.0)
    # corners in UTM for equal-aspect box
    corners = [to_utm(x, y) for x in xlim_ll for y in ylim_ll]
    e0, e1 = min(c[0] for c in corners), max(c[0] for c in corners)
    n0, n1 = min(c[1] for c in corners), max(c[1] for c in corners)
    coast, land = load_coast_utm(xlim_ll, ylim_ll)
    decades = [(1990, 1999), (2000, 2009), (2010, 2019), (2020, 2026)]
    kept = []
    for y0, y1 in decades:
        sub = [p for p in pts if y0 <= p["year"] <= y1]
        out = FIG / f"mapa_cat_{y0}_{y1}.png"
        if not sub:
            if out.exists():
                out.unlink()
            print("REMOVED", out.name)
            continue
        fig, ax = plt.subplots(figsize=(8.5, 9.5))
        ax.set_xlim(e0, e1)
        ax.set_ylim(n0, n1)
        ax.set_aspect("equal", adjustable="box")
        ax.set_facecolor("#cfe8f3")
        for xs, ys in land:
            ax.fill(xs, ys, facecolor="#f0e4c8", edgecolor="none", zorder=1)
        for xs, ys in coast:
            ax.plot(xs, ys, color="#4e342e", lw=0.9, zorder=2)
        by_m = defaultdict(list)
        for p in sub:
            by_m[p["medio"]].append(p)
        rng = np.random.default_rng(7)
        for medio, rows in by_m.items():
            xs = np.array([r["e"] for r in rows]) + rng.normal(0, 400, len(rows))
            ys = np.array([r["n"] for r in rows]) + rng.normal(0, 400, len(rows))
            ax.scatter(
                xs,
                ys,
                s=22,
                alpha=0.75,
                c=MEDIO_COLOR[medio],
                edgecolors="#222",
                linewidths=0.25,
                zorder=3,
                label=f"{medio} (n={len(rows)})",
            )
        ax.set_xlabel("Easting UTM31N (m)")
        ax.set_ylabel("Northing UTM31N (m)")
        ax.set_title(
            f"Invasoras del paper — Cataluña {y0}–{y1}\n"
            f"EPSG:25831 (ETRS89/UTM31N) · costa Natural Earth 10m · BioQuest"
        )
        ax.grid(True, alpha=0.25, zorder=0)
        ax.legend(loc="upper left", fontsize=9, framealpha=0.92)
        spp = sorted({p["name"] for p in sub})
        ax.text(
            0.02,
            0.02,
            f"n={len(sub)} pts · {len(spp)} taxones · aspecto 1:1 (sin deformar)",
            transform=ax.transAxes,
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.88),
        )
        fig.tight_layout()
        fig.savefig(out, dpi=150)
        plt.close(fig)
        kept.append(out.name)
        print("wrote", out.name, "n=", len(sub))
    return kept


def mann_kendall(x):
    """Tau and simple Z (sin ties correction fuerte)."""
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


def classify_trend(years, rates, last_year=2025, absent_gap=5):
    years = np.asarray(years)
    rates = np.asarray(rates, dtype=float)
    if len(years) == 0 or rates.sum() == 0:
        return "sin_datos", None, None, None
    # recent absence despite effort window
    recent = rates[years >= last_year - absent_gap + 1]
    earlier = rates[(years < last_year - absent_gap + 1) & (years >= years.min())]
    if earlier.sum() > 0 and (len(recent) == 0 or recent.sum() == 0):
        return "desaparecida_proxy", None, None, "sin registros últimos 5 años (proxy; esfuerzo≠0 global)"
    # use years with effort-normalized rate; drop leading zeros before first obs
    first = np.argmax(rates > 0)
    y = years[first:]
    r = rates[first:]
    if len(y) < 4:
        return "dato_escaso", None, None, "n años < 4 tras 1ª obs"
    tau, z = mann_kendall(r)
    # half-split slope
    mid = len(r) // 2
    m0 = r[:mid].mean() if mid else 0
    m1 = r[mid:].mean()
    ratio = (m1 / m0) if m0 > 1e-12 else (99.0 if m1 > 0 else 1.0)
    if z is not None and z >= 1.64 and ratio >= 1.3:
        cat = "en_expansion"
    elif z is not None and z <= -1.64 and ratio <= 0.7:
        cat = "en_declive"
    else:
        cat = "estable"
    return cat, tau, z, f"ratio_2a/1a={ratio:.2f}"


def load_effort_cat():
    eff = {}
    with ESF.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("region") == "Catalunya":
                eff[int(r["year"])] = float(r["obs_totales_catalogo"])
    return eff


def prosperan_analysis():
    # species present in CAT
    present = []
    with PRES.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("presencia_catalunya") == "sí":
                present.append(r["especie"])
    # yearly series CAT
    by = defaultdict(dict)
    with SERIE.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("region") != "Catalunya":
                continue
            sp = r["especie"]
            if sp not in present:
                continue
            y = int(r["year"])
            obs = float(r["obs"] or 0)
            rate = r.get("obs_por_1000_esfuerzo")
            by[sp][y] = dict(obs=obs, rate=float(rate) if rate not in (None, "", "None") else None)

    eff = load_effort_cat()
    rows = []
    # panel of species with enough years
    panel_spp = []
    for sp in sorted(present):
        years = sorted(by[sp])
        if not years:
            rows.append(dict(especie=sp, categoria="sin_serie", tau="", z="", nota="sin serie_anual CAT"))
            continue
        ys = []
        rates = []
        for y in range(min(years), 2027):
            ys.append(y)
            if by[sp].get(y, {}).get("rate") is not None:
                rates.append(by[sp][y]["rate"])
            else:
                o = by[sp].get(y, {}).get("obs", 0) or 0
                e = eff.get(y, 0)
                rates.append(1000 * o / e if e else 0.0)
        cat, tau, z, nota = classify_trend(ys, rates)
        rows.append(
            dict(
                especie=sp,
                categoria=cat,
                tau=f"{tau:.3f}" if tau is not None else "",
                z=f"{z:.2f}" if z is not None else "",
                primera=min(years),
                ultima=max(y for y in years if by[sp][y]["obs"] > 0),
                n_obs=int(sum(by[sp][y]["obs"] for y in years)),
                nota=nota or "",
            )
        )
        if cat != "sin_serie" and sum(rates) > 0:
            panel_spp.append((sp, ys, rates, cat))

    # CSV
    out_csv = ROOT / "material" / "prosperan_desaparecen_20261011.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["especie", "categoria", "tau", "z", "primera", "ultima", "n_obs", "nota"],
        )
        w.writeheader()
        w.writerows(rows)

    # individual line plots for declive / desaparecida / top expansion
    highlight = [r for r in rows if r["categoria"] in ("en_declive", "desaparecida_proxy", "en_expansion")]
    for r in highlight:
        sp = r["especie"]
        data = next((x for x in panel_spp if x[0] == sp), None)
        if not data:
            continue
        _, ys, rates, cat = data
        fig, ax = plt.subplots(figsize=(7, 3.2))
        ax.plot(ys, rates, "-o", ms=3, color="#1f618d", lw=1.4)
        ax.fill_between(ys, rates, alpha=0.15, color="#1f618d")
        ax.set_title(f"{sp} — tasa/esfuerzo ×1000 · {cat}")
        ax.set_xlabel("Año")
        ax.set_ylabel("obs / esfuerzo caja ×1000")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        safe = sp.replace(" ", "_").replace("/", "_")
        fig.savefig(FIG_P / f"trend_{safe}.png", dpi=130)
        plt.close(fig)

    # small multiples panel (max 25)
    panel_spp = sorted(panel_spp, key=lambda t: t[0])[:25]
    n = len(panel_spp)
    ncols = 5
    nrows = math.ceil(n / ncols) if n else 1
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 2.4 * nrows), sharex=True)
    axes = np.array(axes).reshape(-1)
    colors = {
        "en_expansion": "#c0392b",
        "estable": "#2980b9",
        "en_declive": "#8e44ad",
        "desaparecida_proxy": "#7f8c8d",
        "dato_escaso": "#95a5a6",
    }
    for i, (sp, ys, rates, cat) in enumerate(panel_spp):
        ax = axes[i]
        ax.plot(ys, rates, color=colors.get(cat, "#333"), lw=1.2)
        ax.set_title(sp, fontsize=9)
        ax.tick_params(labelsize=8)
        ax.grid(True, alpha=0.2)
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")
    fig.suptitle(
        "¿Prosperan o desaparecen? — tasa CAT corregida por esfuerzo BioQuest (panel)",
        fontsize=11,
    )
    fig.tight_layout()
    panel_path = FIG / "prosperan_panel_small_multiples.png"
    fig.savefig(panel_path, dpi=140)
    plt.close(fig)

    # markdown section
    counts = defaultdict(int)
    for r in rows:
        counts[r["categoria"]] += 1
    lines = [
        "# ¿Prosperan o desaparecen? — invasoras en Cataluña",
        "",
        "**Generado:** 2026-10-11 ~19:30 CEST (orden Robotin addendum). **Sin GPU.**",
        "",
        "Tasa anual = `obs_especie_año / esfuerzo_BioQuest_caja_año × 1000` (`serie_anual_normalizada.csv`).",
        "Tendencia: Mann–Kendall (tau, Z) sobre la serie desde la 1ª observación; clasificación operativa:",
        "",
        "- **en_expansion:** Z≥1,64 y ratio 2ª mitad/1ª ≥1,3",
        "- **en_declive:** Z≤−1,64 y ratio ≤0,7",
        "- **estable:** resto con serie suficiente",
        "- **desaparecida_proxy:** tuvo obs y 0 en últimos 5 años (no prueba ausencia biológica)",
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
        "CSV: [`prosperan_desaparecen_20261011.csv`](material/prosperan_desaparecen_20261011.csv). "
        "Panel: [`figuras/prosperan_panel_small_multiples.png`](material/figuras/prosperan_panel_small_multiples.png).",
        "",
        "## Especies en declive o desaparecidas (proxy)",
        "",
        "| Especie | Categoría | tau | Z | 1ª–última | n obs | Nota |",
        "|---|---|---:|---:|---|---:|---|",
    ]
    focus = [r for r in rows if r["categoria"] in ("en_declive", "desaparecida_proxy")]
    if not focus:
        lines.append("| — | — | — | — | — | — | Ninguna con señal clara de declive en este proxy |")
    for r in focus:
        lines.append(
            f"| *{r['especie']}* | {r['categoria']} | {r['tau'] or '—'} | {r['z'] or '—'} | "
            f"{r.get('primera','—')}–{r.get('ultima','—')} | {r.get('n_obs','—')} | {r['nota']} |"
        )
    lines += [
        "",
        "## Lectura",
        "",
        "1. El esfuerzo crece ~84× (2013→2024): sin normalizar, casi todo «expande».",
        "2. **desaparecida_proxy** ≠ extinción local: puede ser sesgo taxonómico (pocas fotos).",
        "3. GLM Poisson formal con offset queda como mejora; aquí Mann–Kendall + ratio de mitades.",
        "",
    ]
    (ROOT / "PROSPERAN_O_DESAPARECEN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("prosperan rows", len(rows), "panel", panel_path.name, "focus", len(focus))
    return rows


def main():
    pts = fetch_points()
    print("pts", len(pts))
    plot_decade_maps_utm(pts)
    prosperan_analysis()


if __name__ == "__main__":
    main()
