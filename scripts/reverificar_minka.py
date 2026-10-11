#!/usr/bin/env python3
"""Re-verifica las fotos del autoaprendizaje de Minka.

Una observación en investigación puede CAMBIAR de especie/familia si un curador
la corrige. Este script re-consulta cada observación del manifest y, si el taxón
actual difiere del que se usó al descargar, mueve la foto a la carpeta correcta
(o la elimina si ya no hay taxón de especie).

Uso: python3 scripts/reverificar_minka.py
"""
import json, os, re, time, urllib.request, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from api_http import minka_headers

ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
IMAGES_DIR = Path(os.environ.get("IMAGES_DIR", str(ROOT / "dataset/images")))
MANIFEST = ROOT / "dataset" / "minka_manifest.jsonl"
MINKA = "https://api.minka-sdg.org/v1"

def slug(n):
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")

def main():
    if not MANIFEST.exists():
        print("sin manifest"); return
    rows = [json.loads(l) for l in open(MANIFEST) if l.strip()]
    moved = removed = ok = 0
    # dedup por obs_id (mantener la última)
    seen = {}
    for r in rows:
        seen[r["obs_id"]] = r
    for obs_id, r in seen.items():
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(
                f"{MINKA}/observations/{obs_id}", headers=minka_headers()), timeout=25))
            o = (d.get("results") or [{}])[0]
        except Exception:
            continue
        taxon = o.get("taxon") or {}
        current_name = taxon.get("name", "")
        current_slug = slug(current_name)
        fname = Path(r["filename"]).name
        src = IMAGES_DIR / r["slug"] / fname
        if current_name and current_slug and current_slug != r.get("slug"):
            # cambió de especie → mover a la carpeta correcta
            dst = IMAGES_DIR / current_slug
            dst.mkdir(parents=True, exist_ok=True)
            if src.exists():
                src.rename(dst / fname)
                moved += 1
                print(f"MOVED: {r['slug']}/{fname} → {current_slug}", flush=True)
        elif not current_name or not current_slug:
            # ya no hay taxón de especie (retirada) → eliminar
            if src.exists():
                src.unlink()
                removed += 1
                print(f"REMOVED: {r['slug']}/{fname} (obs sin taxón)", flush=True)
        else:
            ok += 1
        time.sleep(0.1)
    print(f"=== reverificación: {ok} OK, {moved} movidas (cambio de taxón), {removed} eliminadas ===", flush=True)

if __name__ == "__main__":
    main()
