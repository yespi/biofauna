#!/usr/bin/env python3
"""Autoaprendizaje desde iNaturalist research grade (2+ curadores = fiable).

Análogo a autoaprendizaje_minka.py pero contra la API de iNaturalist.
Descarga TODAS las fotos de las observaciones research grade y registra manifest.

Uso: python3 scripts/autoaprendizaje_inat.py [MAX_TOTAL] [PER_SPECIES]
"""
import json, os, re, time, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from api_http import inat_headers

ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
IMAGES_DIR = Path(os.environ.get("IMAGES_DIR", str(ROOT / "dataset/images")))
MANIFEST = ROOT / "dataset" / "inat_manifest.jsonl"
CACHE = ROOT / "dataset" / "inat_taxon_cache.json"
INAT = "https://api.inaturalist.org/v1"

_ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY_RUN = "--dry-run" in sys.argv
RESOLVE_ONLY = "--resolve-only" in sys.argv
MAX_TOTAL = int(_ARGS[0]) if len(_ARGS) > 0 else 500
PER_SPECIES = int(_ARGS[1]) if len(_ARGS) > 1 else 30
MAX_PER_SPECIES = 1000  # máx fotos por especie (evitar acumular especies comunes sin límite)

def slug(n):
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")


def _load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text())
        except Exception:
            return {}
    return {}


def _inat_search(name: str, rank: str | None) -> list:
    import urllib.parse
    q = {"q": name, "per_page": 5}
    if rank:
        q["rank"] = rank
    url = f"{INAT}/taxa?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(url, headers=inat_headers()), timeout=30) as resp:
        return json.load(resp).get("results") or []


def resolve_inat_taxon(name: str, cache: dict) -> int | None:
    """iNat ID: campo del JSON, caché existente, o lookup por nombre científico."""
    if name in cache and cache[name]:
        return int(cache[name])
    try:
        data = _inat_search(name, "species")
        if not data:
            data = _inat_search(name, None)
        tid = None
        for t in data:
            if (t.get("name") or "").lower() == name.lower() and t.get("is_active", True):
                tid = t["id"]
                break
        if tid is None and data:
            tid = data[0].get("id")
        if tid:
            cache[name] = tid
            CACHE.write_text(json.dumps(cache, ensure_ascii=False))
        time.sleep(0.35)
        return tid
    except Exception as e:
        print(f"[inat] lookup ERR {name}: {type(e).__name__} {e}", flush=True)
        time.sleep(1.0)
        return None


def main():
    targets = json.load(open(ROOT / "dataset/target_species.json"))
    cache = _load_cache()
    pool = []
    missing = 0
    looked_up = 0
    for i, s in enumerate(targets, 1):
        iid = s.get("inat_taxon") or cache.get(s["name"])
        if not iid and not DRY_RUN:
            iid = resolve_inat_taxon(s["name"], cache)
            looked_up += 1
            if looked_up == 1 or looked_up % 25 == 0:
                print(f"[inat] lookup {looked_up} ({s['name']}) → {iid}  "
                      f"{i}/{len(targets)} cache={len(cache)}", flush=True)
        if not iid:
            missing += 1
            continue
        s = dict(s)
        s["inat_taxon"] = int(iid)
        pool.append(s)
    print(f"[inat] pool={len(pool)}/{len(targets)} cache={len(cache)} "
          f"lookups={looked_up} unresolved={missing}", flush=True)
    if DRY_RUN or RESOLVE_ONLY:
        print(f"=== autoaprendizaje iNat: {'dry-run' if DRY_RUN else 'resolve-only'}; "
              f"sin descargas (MAX_TOTAL={MAX_TOTAL}) ===", flush=True)
        return
    total = 0
    mf = open(MANIFEST, "a")
    for s in pool:
        if total >= MAX_TOTAL:
            break
        sl = slug(s["name"]); iid = s["inat_taxon"]
        dst = IMAGES_DIR / sl
        dst.mkdir(parents=True, exist_ok=True)
        if len(list(dst.glob("*.jpg"))) >= MAX_PER_SPECIES:
            continue  # especie ya llena
        url = (f"{INAT}/observations?taxon_id={iid}&quality_grade=research"
               f"&photos=true&per_page={PER_SPECIES}&order=desc&order_by=id")
        try:
            obs = json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers=inat_headers()), timeout=30))["results"]
        except Exception:
            continue
        for o in obs:
            for pi, ph in enumerate(o.get("photos") or []):
                if len(list(dst.glob("*.jpg"))) >= MAX_PER_SPECIES:
                    break
                fname = f"inat_{o['id']}_{pi}.jpg"
                out = dst / fname
                if out.exists():
                    continue
                try:
                    data = urllib.request.urlopen(urllib.request.Request(
                        ph["url"].replace("square", "medium"), headers=inat_headers()), timeout=25).read()
                    out.write_bytes(data)
                    total += 1
                    mf.write(json.dumps({
                        "filename": f"{sl}/{fname}",
                        "obs_id": o["id"],
                        "taxon_id": iid,
                        "slug": sl,
                        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    }, ensure_ascii=False) + "\n")
                except Exception:
                    continue
                time.sleep(0.15)
        if total % 50 == 0:
            print(f"  [{sl}] acumulado: {total}", flush=True)
    mf.close()
    print(f"=== autoaprendizaje iNat: {total} fotos research grade descargadas ===", flush=True)

if __name__ == "__main__":
    main()
