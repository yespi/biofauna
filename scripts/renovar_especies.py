#!/usr/bin/env python3
"""Renovación (rotación): en especies saturadas (>=1000 fotos), descarta las fotos
más antiguas para que el autoaprendizaje las reemplace con research grade nuevas.

Esto "sanea" el modelo: el patrón se mantiene fresco (variabilidad reciente) y
acotado, sin acumular fotos indefinidamente. El autoaprendizaje (lunes/martes)
rellena automáticamente el hueco con observaciones recientes validadas.

Uso: python3 scripts/renovar_especies.py [ROTATE_N]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
IMAGES_DIR = Path(os.environ.get("IMAGES_DIR", str(ROOT / "dataset/images")))
MAX_PER_SPECIES = 1000
ROTATE_N = int(sys.argv[1]) if len(sys.argv) > 1 else 200

def slug(n):
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")

def main():
    targets = json.load(open(ROOT / "dataset/target_species.json"))
    renovadas = descartadas = 0
    for s in targets:
        sl = slug(s["name"])
        dst = IMAGES_DIR / sl
        if not dst.exists():
            continue
        # más antiguas primero (por mtime)
        jpgs = sorted(dst.glob("*.jpg"), key=lambda p: p.stat().st_mtime)
        if len(jpgs) < MAX_PER_SPECIES:
            continue
        for p in jpgs[:ROTATE_N]:
            try:
                p.unlink()
                descartadas += 1
            except OSError:
                pass
        renovadas += 1
        print(f"  {sl}: {len(jpgs)} → {len(jpgs)-ROTATE_N} (descartadas {ROTATE_N} antiguas)", flush=True)
    print(f"=== renovación: {renovadas} especies rotadas, {descartadas} fotos descartadas ===", flush=True)

if __name__ == "__main__":
    main()
