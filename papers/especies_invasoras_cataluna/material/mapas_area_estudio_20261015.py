#!/usr/bin/env python3
"""Fig. 1 área de estudio + mapas década UTM31N con costa Natural Earth 10m."""
from __future__ import annotations

import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import shapefile
from pyproj import Transformer

M = Path(__file__).parent
F = M / "figuras"
GEO = Path("/mnt/docker/biofauna/artifacts/invasoras/origen_expansion/geo")
ICGC = M / "geo" / "catalunya_icgc_admin.geojson"
BOX = dict(swlat=40.45, nelat=42.95, swlng=0.1, nelng=3.4)
T = Transformer.from_crs("EPSG:4326", "EPSG:25831", always_xy=True)


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
            "-A",
            "-F",
            "|",
            "-c",
            q,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    rows = []
    for ln in r.stdout.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("(") or "|" not in ln:
            continue
        parts = ln.split("|")
        if parts[0] in ("gx", "taxon_id", "year"):
            continue
        rows.append(parts)
    return rows


def load_coast():
    land = shapefile.Reader(str(GEO / "ne_10m_land"))
    pad = 0.35
    lng0, lng1 = BOX["swlng"] - pad, BOX["nelng"] + pad
    lat0, lat1 = BOX["swlat"] - pad, BOX["nelat"] + pad
    polys = []
    for sh in land.shapes():
        pts = sh.points
        parts_i = list(sh.parts) + [len(pts)]
        for i in range(len(parts_i) - 1):
            seg = pts[parts_i[i] : parts_i[i + 1]]
            xs = [p[0] for p in seg]
            ys = [p[1] for p in seg]
            if max(xs) < lng0 or min(xs) > lng1 or max(ys) < lat0 or min(ys) > lat1:
                continue
            ux, uy = [], []
            for x, y in seg:
                if lng0 <= x <= lng1 and lat0 <= y <= lat1:
                    e, n = T.transform(x, y)
                    ux.append(e)
                    uy.append(n)
            if len(ux) >= 3:
                polys.append((ux, uy))
    return polys


def load_icgc_outline():
    if not ICGC.exists():
        return []
    import json

    data = json.loads(ICGC.read_text(encoding="utf-8"))
    lines = []
    for feat in data.get("features", []):
        if feat.get("properties", {}).get("kind") == "marine_buffer_bbox":
            continue
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            rings = [geom["coordinates"][0]]
        else:
            rings = [p[0] for p in geom["coordinates"]]
        for ring in rings:
            lngs, lats = zip(*ring)
            lines.append((list(lngs), list(lats)))
    return lines


def fig_area_heatmap():
    q = f"""
    SELECT FLOOR((lng - {BOX['swlng']}) / 0.09)::int AS gx,
           FLOOR((lat - {BOX['swlat']}) / 0.09)::int AS gy,
           COUNT(*)::int AS n
    FROM public_observations
    WHERE quality_grade='research' AND obs_year BETWEEN 2018 AND 2024
      AND lat BETWEEN {BOX['swlat']} AND {BOX['nelat']}
      AND lng BETWEEN {BOX['swlng']} AND {BOX['nelng']}
    GROUP BY 1,2;
    """
    rows = sql(q)
    if not rows:
        return
    gx = np.array([int(r[0]) for r in rows])
    gy = np.array([int(r[1]) for r in rows])
    n = np.array([int(r[2]) for r in rows])
    w, h = gx.max() + 1, gy.max() + 1
    grid = np.zeros((h, w))
    for a, b, c in zip(gy, gx, n):
        grid[a, b] = np.log10(c + 1)
    polys = load_coast()
    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.imshow(
        grid,
        origin="lower",
        extent=[BOX["swlng"], BOX["nelng"], BOX["swlat"], BOX["nelat"]],
        cmap="YlOrRd",
        alpha=0.85,
        aspect="equal",
    )
    for ux, uy in polys:
        lngs, lats = zip(*[T.transform(e, n, direction="INVERSE") for e, n in zip(ux, uy)])
        ax.plot(lngs, lats, color="#4e342e", lw=0.8, zorder=3)
    for lngs, lats in load_icgc_outline():
        ax.plot(lngs, lats, color="#1a5276", lw=1.0, zorder=4, alpha=0.9)
    ax.set_xlabel("Longitud (°)")
    ax.set_ylabel("Latitud (°)")
    ax.set_title(
        "Área de estudio (contorno provincial ICGC aprox.) y densidad de esfuerzo (log10 obs), 2018–2024"
    )
    fig.tight_layout()
    fig.savefig(F / "area_estudio_esfuerzo_heatmap_20261015.png", dpi=200)
    plt.close(fig)


def fig_decades_ue():
    """Puntos de especies UE presentes en CAT (taxones con obs>0)."""
    import json

    ts = json.loads((M / "target_species.json").read_text())
    ids = ",".join(str(t["inat_taxon"]) for t in ts if t.get("inat_taxon"))
    q = f"""
    SELECT taxon_id::text, lat::float, lng::float, obs_year::int
    FROM public_observations
    WHERE quality_grade='research' AND taxon_id = ANY(ARRAY[{ids}]::int[])
      AND lat BETWEEN {BOX['swlat']} AND {BOX['nelat']}
      AND lng BETWEEN {BOX['swlng']} AND {BOX['nelng']};
    """
    pts = []
    for tid, lat, lng, y in sql(q):
        pts.append((float(lng), float(lat), int(y)))
    polys = load_coast()
    corners = [
        T.transform(BOX["swlng"], BOX["swlat"]),
        T.transform(BOX["nelng"], BOX["nelat"]),
    ]
    e0, e1 = min(corners[0][0], corners[1][0]), max(corners[0][0], corners[1][0])
    n0, n1 = min(corners[0][1], corners[1][1]), max(corners[0][1], corners[1][1])
    for y0, y1 in [(1990, 1999), (2000, 2009), (2010, 2019), (2020, 2026)]:
        sub = [(lng, lat) for lng, lat, y in pts if y0 <= y <= y1]
        out = F / f"mapa_cat_{y0}_{y1}.png"
        if not sub:
            continue
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_xlim(e0, e1)
        ax.set_ylim(n0, n1)
        ax.set_aspect("equal")
        ax.set_facecolor("#cfe8f3")
        for ux, uy in polys:
            ax.fill(ux, uy, facecolor="#f0e4c8", edgecolor="none", zorder=1)
        xs, ys = zip(*[T.transform(lng, lat) for lng, lat in sub])
        ax.scatter(xs, ys, s=12, c="#c0392b", alpha=0.6, edgecolors="none", zorder=2)
        ax.set_title(f"Registros lista UE en caja de estudio, {y0}–{y1}")
        ax.set_xlabel("Easting UTM31N (m)")
        ax.set_ylabel("Northing UTM31N (m)")
        fig.tight_layout()
        fig.savefig(out, dpi=160)
        plt.close(fig)
        print("wrote", out.name, "n=", len(sub))


def main():
    fig_area_heatmap()
    fig_decades_ue()


if __name__ == "__main__":
    main()
