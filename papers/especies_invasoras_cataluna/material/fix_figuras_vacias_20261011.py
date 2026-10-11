#!/usr/bin/env python3
"""Rellena mapas de década vacíos + top25 sin barras a cero (BioQuest SELECT).

Sin GPU. Usa taxones del paper (lista UE + Weitzmann/Academy presentes en BQ),
no solo IDs UE que no coinciden con public_observations (p. ej. Trachemys
scripta elegans 51271 vs T. scripta 39782).
"""
from __future__ import annotations

import csv
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import shapefile

ROOT = Path("/mnt/docker/biofauna-public/papers/especies_invasoras_cataluna")
FIG = ROOT / "material" / "figuras"
ART = Path("/mnt/docker/biofauna/artifacts/invasoras/origen_expansion")
GEO = ART / "geo"
PRES = ROOT / "material" / "presencia_cat_es.csv"

BOX_CAT = dict(swlat=40.45, nelat=42.95, swlng=0.1, nelng=3.4)

# Taxones paper con presencia real en BioQuest (marina Weitzmann + UE/Academy)
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
    123459: ("Pterois miles", "marino"),
    132368: ("Lagocephalus sceleratus", "marino"),
}

MEDIO_COLOR = {
    "marino": "#1a5276",
    "agua_dulce": "#148f77",
    "terrestre": "#a04000",
    "otro": "#7f8c8d",
}


def sql(q: str) -> list[dict]:
    r = subprocess.run(
        ["docker", "exec", "postgres-global", "psql", "-U", "admin_yespi", "-d", "fauna", "-At", "-F", "|", "-c", q],
        capture_output=True,
        text=True,
        check=True,
    )
    rows = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("|")
        rows.append(parts)
    return rows


def load_coast():
    if not (GEO / "ne_110m_coastline.shp").exists():
        return []
    coast = shapefile.Reader(str(GEO / "ne_110m_coastline"))
    return coast.shapes()


def clip_coast(shapes, xlim, ylim):
    lng0, lng1 = xlim
    lat0, lat1 = ylim
    out = []
    for sh in shapes:
        pts = sh.points
        parts = list(sh.parts) + [len(pts)]
        for i in range(len(parts) - 1):
            seg = pts[parts[i] : parts[i + 1]]
            xs = [p[0] for p in seg]
            ys = [p[1] for p in seg]
            if not xs:
                continue
            if max(xs) < lng0 or min(xs) > lng1 or max(ys) < lat0 or min(ys) > lat1:
                continue
            out.append((xs, ys))
    return out


def fetch_points():
    ids = ",".join(str(i) for i in PAPER_TAXA)
    q = f"""
    SELECT taxon_id::text, COALESCE(taxon_name,''), lat::text, lng::text, obs_year::text
    FROM public_observations
    WHERE taxon_id = ANY(ARRAY[{ids}]::int[])
      AND lat BETWEEN {BOX_CAT['swlat']} AND {BOX_CAT['nelat']}
      AND lng BETWEEN {BOX_CAT['swlng']} AND {BOX_CAT['nelng']}
      AND lat IS NOT NULL AND lng IS NOT NULL AND obs_year IS NOT NULL;
    """
    pts = []
    for parts in sql(q):
        if len(parts) < 5:
            continue
        tid = int(parts[0])
        name, medio = PAPER_TAXA.get(tid, (parts[1] or f"taxon_{tid}", "otro"))
        pts.append(
            {
                "taxon_id": tid,
                "name": name,
                "medio": medio,
                "lat": float(parts[2]),
                "lng": float(parts[3]),
                "year": int(float(parts[4])),
            }
        )
    return pts


def plot_decade_maps(pts, coast_shapes):
    decades = [(1990, 1999), (2000, 2009), (2010, 2019), (2020, 2026)]
    xlim = (0.0, 3.5)
    ylim = (40.4, 43.0)
    coast = clip_coast(coast_shapes, xlim, ylim)
    kept = []
    for y0, y1 in decades:
        sub = [p for p in pts if y0 <= p["year"] <= y1]
        out = FIG / f"mapa_cat_{y0}_{y1}.png"
        if not sub:
            # sin datos reales → no dejar gráfica vacía
            if out.exists():
                out.unlink()
            print(f"REMOVED empty {out.name}")
            continue
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_facecolor("#d6eaf8")
        ax.fill_between(xlim, ylim[0], ylim[1], color="#f5e6c8", zorder=0)
        for xs, ys in coast:
            ax.plot(xs, ys, color="#5c4a32", lw=0.8, zorder=2)
        by_m = defaultdict(list)
        for p in sub:
            by_m[p["medio"]].append(p)
        rng = np.random.default_rng(42)
        for medio, rows in by_m.items():
            xs = np.array([r["lng"] for r in rows], dtype=float)
            ys = np.array([r["lat"] for r in rows], dtype=float)
            # jitter leve para que puntos coincidentes no se oculten
            xs = xs + rng.normal(0, 0.015, size=len(xs))
            ys = ys + rng.normal(0, 0.012, size=len(ys))
            ax.scatter(
                xs,
                ys,
                s=28,
                alpha=0.75,
                c=MEDIO_COLOR.get(medio, "#7f8c8d"),
                edgecolors="#222",
                linewidths=0.2,
                zorder=3,
                label=f"{medio} (n={len(rows)})",
            )
        ax.set_xlabel("Longitud (°E)")
        ax.set_ylabel("Latitud (°N)")
        ax.set_title(
            f"Invasoras del paper — Cataluña {y0}–{y1}\n"
            f"(BioQuest public_observations; UE+Weitzmann/Academy en BQ)"
        )
        ax.grid(True, alpha=0.3, zorder=1)
        ax.legend(loc="upper left", fontsize=8, framealpha=0.92)
        spp = sorted({p["name"] for p in sub})
        ax.text(
            0.02,
            0.02,
            f"n={len(sub)} pts · {len(spp)} taxones: " + ", ".join(spp[:6]) + ("…" if len(spp) > 6 else ""),
            transform=ax.transAxes,
            fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.85),
        )
        fig.tight_layout()
        fig.savefig(out, dpi=140)
        plt.close(fig)
        kept.append(out.name)
        print("wrote", out.name, "n=", len(sub))
    return kept


def fix_top25():
    rows = []
    with PRES.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                n = int(float(r.get("obs_catalunya") or 0))
            except ValueError:
                continue
            if n <= 0:
                continue
            rows.append((r["especie"], n))
    rows.sort(key=lambda x: -x[1])
    top = rows[:25]
    if not top:
        print("top25: sin filas")
        return
    fig, ax = plt.subplots(figsize=(9, 7))
    names = [t[0] for t in reversed(top)]
    vals = [t[1] for t in reversed(top)]
    ax.barh(names, vals, color="#16a085")
    ax.set_xlabel("Observaciones (máx. entre iNat / BioQuest / Minka caja)")
    ax.set_title("Top invasoras UE con presencia en Cataluña (≥1 obs)")
    for y, v in enumerate(vals):
        ax.text(v + max(vals) * 0.01, y, str(v), va="center", fontsize=9)
    fig.tight_layout()
    out = FIG / "top25_obs_catalunya.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print("wrote", out.name, "n_spp=", len(top), "min_obs=", top[-1][1])


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    pts = fetch_points()
    print("pts CAT paper taxa:", len(pts))
    by_dec = defaultdict(int)
    for p in pts:
        by_dec[p["year"] // 10 * 10] += 1
    print("by decade approx:", dict(sorted(by_dec.items())))
    coast = load_coast()
    kept = plot_decade_maps(pts, coast)
    fix_top25()
    print("kept maps:", kept)


if __name__ == "__main__":
    main()
