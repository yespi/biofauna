#!/usr/bin/env python3
"""Construye priors geograficos desde Minka. Resumible, lock file, sin iNat."""
import json, sys, time, urllib.request, urllib.parse, os
from pathlib import Path
from datetime import datetime

ROOT = Path("/work")
PAT = ROOT / "dataset/patterns"
OUT = ROOT / "dataset/geo_priors.json"
LOCK = ROOT / "dataset/.geo_priors.lock"
TARGETS = ROOT / "dataset/target_species.json"
CACHE = ROOT / "dataset/inat_taxon_cache.json"
UA = "yespi-fotofauna-yolo/1.0"

PER_PAGE = 30
MAX_OBS = 100
SLEEP = 3.0

def log(*a):
    print(datetime.now().strftime("%H:%M:%S"), *a, flush=True)

# Lock file
if LOCK.exists():
    log("LOCK existe, borro y sigo")
    LOCK.unlink()
LOCK.write_text(str(os.getpid()))

try:
    existing = json.loads(OUT.read_text()) if OUT.exists() else {}
    pat_slugs = sorted([d.name for d in PAT.iterdir() if d.is_dir() and (d/"prototype.npy").exists()])
    missing = [s for s in pat_slugs if s not in existing or not existing[s]]
    
    if not missing:
        log(f"COMPLETO: {len(pat_slugs)} especies")
        LOCK.unlink()
        sys.exit(0)
    
    log(f"Pendientes: {len(missing)} de {len(pat_slugs)} ({sum(1 for v in existing.values() if v)} ya con coords)")
    
    targets = json.loads(TARGETS.read_text())
    name_to_info = {}
    import re
    for t in targets:
        slug = re.sub(r"[^a-z0-9]+", "_", t["name"].lower()).strip("_")
        name_to_info[slug] = t
    
    inat_cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    
    t0 = time.time()
    processed = errors = 0
    total_minka = total_inat = 0
    
    for sp_slug in pat_slugs:
        if sp_slug in existing and existing[sp_slug]:
            continue
        
        info = name_to_info.get(sp_slug, {})
        sp_name = info.get("name", sp_slug.replace("_", " "))
        inat_id = inat_cache.get(sp_name)
        
        if not inat_id or inat_id == "None":
            existing[sp_slug] = []
            errors += 1
            continue
        
        coords = []
        
        # Minka
        try:
            url = (f"https://api.minka-sdg.org/v1/observations?"
                   f"q={urllib.parse.quote(sp_name)}&quality_grade=research"
                   f"&has[]=geo&per_page={PER_PAGE}&order=desc&order_by=id")
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                for obs in data.get("results", []):
                    if len(coords) >= MAX_OBS:
                        break
                    lat = lon = None
                    raw_lat = obs.get("latitude")
                    if isinstance(raw_lat, str) and "," in raw_lat:
                        try:
                            parts = raw_lat.split(",")
                            lat, lon = float(parts[0]), float(parts[1])
                        except:
                            pass
                    elif raw_lat is not None:
                        lat, lon = float(raw_lat), obs.get("longitude")
                        if lon is not None:
                            lon = float(lon)
                    if lat is None:
                        geo = obs.get("geojson") or {}
                        gc = geo.get("coordinates") or []
                        if len(gc) >= 2:
                            lon, lat = float(gc[0]), float(gc[1])
                    if lat is not None and lon is not None:
                        coords.append([round(float(lat), 4), round(float(lon), 4)])
        except:
            pass
        
        if coords:
            total_minka += 1
        
        # iNat fallback (1 pagina, sin retry)
        if len(coords) == 0:
            try:
                url = (f"https://api.inaturalist.org/v1/observations?"
                       f"taxon_id={inat_id}&quality_grade=research&has[]=geo"
                       f"&per_page={PER_PAGE}&page=1&order=desc&order_by=id")
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    if resp.status != 429:
                        data = json.loads(resp.read())
                        for obs in data.get("results", []):
                            if len(coords) >= MAX_OBS:
                                break
                            lat = obs.get("latitude")
                            lon = obs.get("longitude")
                            if lat is not None and lon is not None:
                                pt = [round(float(lat), 4), round(float(lon), 4)]
                                if pt not in coords:
                                    coords.append(pt)
            except:
                pass
        
        if len(coords) > 0 and not coords:
            coords = []  # mantiene consistencia
        
        existing[sp_slug] = coords
        processed += 1
        
        # Guardar cada 5
        if processed % 5 == 0:
            try:
                tmp = OUT.with_suffix(".tmp")
                tmp.write_text(json.dumps(existing))
                tmp.rename(OUT)
            except Exception as e:
                log(f"  ERROR guardando: {e}")
        
        elapsed = time.time() - t0
        rate = processed / max(elapsed, 1) * 60
        log(f"[{processed}/{len(missing)}] {sp_name}: {len(coords)} pts M:{total_minka} | {rate:.0f}/min")
        
        time.sleep(SLEEP)
    
    # Guardado final
    try:
        tmp = OUT.with_suffix(".tmp")
        tmp.write_text(json.dumps(existing))
        tmp.rename(OUT)
    except Exception as e:
        log(f"ERROR final: {e}")
    
    total_coords = sum(len(v) for v in existing.values())
    with_coords = sum(1 for v in existing.values() if v)
    log(f"=== FIN ({time.time()-t0:.0f}s): {with_coords}/{len(existing)} spp, {total_coords} pts ===")

finally:
    if LOCK.exists():
        LOCK.unlink()
