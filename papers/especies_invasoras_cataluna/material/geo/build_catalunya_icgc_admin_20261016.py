#!/usr/bin/env python3
"""GeoJSON aproximación ICGC: unión de las 4 provincias + franja marina (bbox extendido)."""
from __future__ import annotations

import json
from pathlib import Path

SRC = Path("/mnt/docker/bioquest/webapp/public/data/spain-provinces.geojson")
OUT = Path(__file__).parent / "catalunya_icgc_admin.geojson"
CAT_PROV = {"Barcelona", "Girona", "Lleida", "Tarragona"}
# ~12 millas náuticas al este de la costa catalana (aprox. 0,22° longitud a 41°N)
MARINE_LNG_EXT = 0.22


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    feats = [
        f
        for f in data.get("features", [])
        if f.get("properties", {}).get("name") in CAT_PROV
    ]
    if len(feats) != 4:
        raise SystemExit(f"esperadas 4 provincias, halladas {len(feats)}")
    lats, lngs = [], []

    def walk_coords(obj):
        if isinstance(obj, (int, float)):
            return
        if len(obj) >= 2 and isinstance(obj[0], (int, float)) and isinstance(obj[1], (int, float)):
            lngs.append(float(obj[0]))
            lats.append(float(obj[1]))
            return
        for item in obj:
            walk_coords(item)

    for f in feats:
        walk_coords(f["geometry"].get("coordinates", []))
    swlat, nelat = min(lats), max(lats)
    swlng, nelng = min(lngs), max(lngs)
    marine = {
        "type": "Feature",
        "properties": {
            "name": "Franja marina 12 mn (aprox.)",
            "kind": "marine_buffer_bbox",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [swlng, swlat],
                    [nelng + MARINE_LNG_EXT, swlat],
                    [nelng + MARINE_LNG_EXT, nelat],
                    [swlng, nelat],
                    [swlng, swlat],
                ]
            ],
        },
    }
    out = {
        "type": "FeatureCollection",
        "metadata": {
            "source": "spain-provinces.geojson (BioQuest)",
            "note": "Sustituto del polígono administrativo ICGC hasta disponer de capa oficial; "
            "la franja marina es un rectángulo de extensión ~12 mn al este de la envolvente provincial.",
            "bbox_study": [swlng, swlat, nelng + MARINE_LNG_EXT, nelat],
        },
        "features": feats + [marine],
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT, "features", len(out["features"]))


if __name__ == "__main__":
    main()
