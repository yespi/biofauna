#!/usr/bin/env python3
"""Autoaprendizaje desde Minka research grade (2+ curadores = identificación fiable).

Descarga TODAS las fotos de las observaciones `quality_grade=research` de cada
especie objetivo y registra un manifest (obs_id → taxón) para poder RE-VERIFICAR
los cambios de taxón (una obs en investigación puede cambiar de especie/familia
si un curador la corrige).

Uso: python3 scripts/autoaprendizaje_minka.py [MAX_TOTAL] [PER_SPECIES]
"""
import json, os, re, time, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from api_http import minka_headers

ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
IMAGES_DIR = Path(os.environ.get("IMAGES_DIR", str(ROOT / "dataset/images")))
MANIFEST = ROOT / "dataset" / "minka_manifest.jsonl"
MINKA = "https://api.minka-sdg.org/v1"

MAX_TOTAL = int(sys.argv[1]) if len(sys.argv) > 1 else 500
PER_SPECIES = int(sys.argv[2]) if len(sys.argv) > 2 else 30
MAX_PER_SPECIES = 1000  # máx fotos por especie (evitar acumular especies comunes sin límite)

def slug(n):
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")

def main():
    targets = json.load(open(ROOT / "dataset/target_species.json"))
    pool = [s for s in targets if s.get("minka_taxon")]
    total = 0
    mf = open(MANIFEST, "a")
    for s in pool:
        if total >= MAX_TOTAL:
            break
        sl = slug(s["name"]); mid = s["minka_taxon"]
        dst = IMAGES_DIR / sl
        dst.mkdir(parents=True, exist_ok=True)
        if len(list(dst.glob("*.jpg"))) >= MAX_PER_SPECIES:
            continue  # especie ya llena
        url = (f"{MINKA}/observations?taxon_id={mid}&quality_grade=research"
               f"&photos=true&per_page={PER_SPECIES}&order=desc&order_by=id")
        try:
            obs = json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers=minka_headers()), timeout=30))["results"]
        except Exception:
            continue
        for o in obs:
            for pi, ph in enumerate(o.get("photos") or []):
                if len(list(dst.glob("*.jpg"))) >= MAX_PER_SPECIES:
                    break
                fname = f"minka_{o['id']}_{pi}.jpg"
                out = dst / fname
                if out.exists():
                    continue
                try:
                    data = urllib.request.urlopen(urllib.request.Request(
                        ph["url"].replace("square", "medium"), headers=minka_headers()), timeout=25).read()
                    out.write_bytes(data)
                    total += 1
                    # manifest: obs_id → taxón (para re-verificación de cambios)
                    mf.write(json.dumps({
                        "filename": f"{sl}/{fname}",
                        "obs_id": o["id"],
                        "taxon_id": mid,
                        "slug": sl,
                        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    }, ensure_ascii=False) + "\n")
                except Exception:
                    continue
                time.sleep(0.15)
        if total % 50 == 0:
            print(f"  [{sl}] acumulado: {total}", flush=True)
    mf.close()
    print(f"=== autoaprendizaje Minka: {total} fotos research grade descargadas ===", flush=True)

if __name__ == "__main__":
    main()
