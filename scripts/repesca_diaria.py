#!/usr/bin/env python3
"""
Repesca diaria de imágenes para BioFauna.
- Descarga fotos de iNaturalist para especies sin imágenes de entrenamiento.
- Recoge feedback de curadores en Minka (confirmaciones/correcciones).
- Guarda todo en IMAGES_DIR/<especie>/ (default: $BIOFAUNA_ROOT/dataset/images).

Cron: see docs/cron.md (BF-01). Do not run as root unless that user has the same Python packages.
"""

import json, os, sys, time, re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

import requests
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from api_http import inat_headers, minka_headers

# ── Config ──────────────────────────────────────────────────────────────────
ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
IMAGES_DIR = Path(os.environ.get("IMAGES_DIR", str(ROOT / "dataset/images")))
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DATASET = ROOT / "dataset"
LOG = ROOT / "logs" / "repesca.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

MAX_PER_SPECIES = 1000       # máx fotos nuevas por especie
MAX_TOTAL_DOWNLOADS = 1000  # límite diario total
PHOTOS_PER_INAT_PAGE = 30  # número de fotos por página en iNat API
MIN_IMG_SIZE_KB = 5        # ignorar fotos más pequeñas
REQUEST_DELAY = 0.5        # segundos entre requests a iNat API

MINKA_API = "https://api.minka-sdg.org/v1"
INAT_API = "https://api.inaturalist.org/v1"

# Curadores de confianza en Minka
CURATORS = {"xasalva", "bertinhaco", "mpontes", "guillermoalvarez"}

# ── Logging ─────────────────────────────────────────────────────────────────
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

# ── Utilidades ──────────────────────────────────────────────────────────────
def _slug(n):
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")

def _safe_filename(url, obs_id, idx=0):
    """Genera nombre de archivo único: inat_<obs_id>_<idx>.jpg"""
    return f"inat_{obs_id}_{idx}.jpg"

def _valid_image(path):
    """Verifica que la imagen sea válida y de tamaño mínimo."""
    try:
        if path.stat().st_size < MIN_IMG_SIZE_KB * 1024:
            return False
        Image.open(path).verify()
        return True
    except Exception:
        return False

# ── Cargar taxonomía ────────────────────────────────────────────────────────
def load_taxonomy():
    """Carga la taxonomía completa (target_species + iNat cache)."""
    with open(DATASET / "target_species.json") as f:
        target = json.load(f)
    
    # iNat cache: scientific_name → inat_taxon_id
    inat_cache = {}
    try:
        with open(DATASET / "inat_taxon_cache.json") as f:
            inat_cache = json.load(f)
    except Exception:
        pass
    
    # Construir NAMEMAP
    namemap = {}
    for s in target:
        slug = _slug(s["name"])
        namemap[slug] = {
            "scientific": s["name"],
            "minka_taxon": s.get("minka_taxon"),
            "inat_taxon": inat_cache.get(s["name"]),
            "prio": s.get("prio", 99),
        }
    
    log(f"Taxonomía: {len(namemap)} especies, {len(inat_cache)} con iNat ID")
    return namemap

# ── Inventario de imágenes existentes ───────────────────────────────────────
def inventory_images():
    """Devuelve {slug: n_fotos} para cada especie con imágenes en el SSD."""
    inv = {}
    if IMAGES_DIR.exists():
        for d in IMAGES_DIR.iterdir():
            if d.is_dir():
                n = len([f for f in d.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")])
                if n > 0:
                    inv[d.name] = n
    log(f"Inventario: {len(inv)} especies con {sum(inv.values()):,} fotos totales")
    return inv

# ── Especies del modelo sin imágenes ────────────────────────────────────────
def find_missing_species(namemap, inventory):
    """Encuentra especies del modelo sin fotos de entrenamiento."""
    patterns_dir = DATASET / "patterns"
    if not patterns_dir.exists():
        return []
    
    model_species = set(d.name for d in patterns_dir.iterdir() if d.is_dir())
    missing = model_species - set(inventory.keys())
    
    result = []
    for slug in sorted(missing):
        info = namemap.get(slug, {})
        inat_id = info.get("inat_taxon")
        name = info.get("scientific", slug)
        if inat_id:
            result.append({
                "slug": slug,
                "name": name,
                "inat_taxon": inat_id,
                "existing": inventory.get(slug, 0),
            })
    
    log(f"Especies sin fotos: {len(missing)} total, {len(result)} con iNat ID")
    return result

# ── Descargar de iNaturalist ────────────────────────────────────────────────
def download_inat_photos(species_list, max_total=MAX_TOTAL_DOWNLOADS):
    """Descarga fotos de iNaturalist para las especies dadas."""
    downloaded = 0
    results = defaultdict(int)
    
    for sp in species_list:
        if downloaded >= max_total:
            log(f"Límite diario alcanzado ({max_total} fotos)")
            break
        
        slug = sp["slug"]
        inat_id = sp["inat_taxon"]
        name = sp["name"]
        needed = min(MAX_PER_SPECIES - sp["existing"], MAX_PER_SPECIES)  # cap de 1000 totales por especie
        if needed <= 0:
            continue
        
        sp_dir = IMAGES_DIR / slug
        sp_dir.mkdir(exist_ok=True)
        
        log(f"  {name}: necesito {needed} fotos (inat_taxon={inat_id})")
        
        page = 1
        species_downloaded = 0
        while species_downloaded < needed and page <= 5:
            try:
                url = (f"{INAT_API}/observations"
                       f"?taxon_id={inat_id}"
                       f"&photos=true"
                       f"&quality_grade=research"
                       f"&per_page={PHOTOS_PER_INAT_PAGE}"
                       f"&page={page}"
                       f"&order=desc&order_by=created_at")
                
                r = requests.get(url, headers=inat_headers(), timeout=30)
                if r.status_code != 200:
                    log(f"    iNat API error {r.status_code}: {r.text[:100]}")
                    break
                
                data = r.json()
                obs_list = data.get("results", [])
                if not obs_list:
                    break
                
                for obs in obs_list:
                    if species_downloaded >= needed or downloaded >= max_total:
                        break
                    
                    photos = obs.get("photos", [])
                    if not photos:
                        continue
                    
                    obs_id = obs.get("id")
                    for pi, photo in enumerate(photos[:3]):  # máx 3 fotos por observación
                        photo_url = photo.get("url", "").replace("square", "medium")
                        if not photo_url:
                            continue
                        
                        dest = sp_dir / _safe_filename(photo_url, obs_id, pi)
                        if dest.exists():
                            continue
                        
                        try:
                            img_r = requests.get(photo_url, timeout=15)
                            if img_r.status_code == 200:
                                dest.write_bytes(img_r.content)
                                if _valid_image(dest):
                                    species_downloaded += 1
                                    downloaded += 1
                                else:
                                    dest.unlink()  # borrar inválida
                        except Exception:
                            pass
                        time.sleep(0.2)
                
                page += 1
                time.sleep(REQUEST_DELAY)
                
            except Exception as e:
                log(f"    Error descargando {name}: {e}")
                break
        
        results[slug] = species_downloaded
        if species_downloaded > 0:
            log(f"    → {species_downloaded} fotos descargadas para {name}")
    
    return results

# ── Feedback de curadores en Minka ──────────────────────────────────────────
def collect_curator_feedback():
    """Consulta nuestras observaciones en Minka y recoge feedback de curadores.
    
    Para cada observación publicada vía autoID:
    - Si un curador la confirma → descargar la foto original con etiqueta verificada.
    - Si un curador la corrige → guardar el par (predicción original, corrección).
    
    Retorna: (confirmadas, corregidas)
    """
    # Consultar Minka directamente (sin DB, usando la API)
    # Buscar observaciones recientes de nuestro usuario en Minka
    autoids = []
    try:
        # Buscar por usuario yespi en Minka
        r = requests.get(f"{MINKA_API}/observations", params={
            "user_login": "yespi",
            "per_page": 50,
            "order_by": "created_at",
            "order": "desc",
            "verifiable": "any",
        }, headers=minka_headers(), timeout=15)
        if r.status_code == 200:
            for obs in r.json().get("results", []):
                obs_id = obs.get("id")
                uri = obs.get("uri", "")
                sci_name = obs.get("species_guess", "")
                obs_date = obs.get("observed_on", "")
                autoids.append((obs_id, uri, sci_name, "minka_api", obs_date))
    except Exception:
        pass
    
    confirmadas = []
    corregidas = []
    
    for obs_id, uri, sci_name, source, sent_at in autoids:
        minka_id = uri.rstrip("/").split("/")[-1]
        if not minka_id.isdigit():
            continue
        
        try:
            r = requests.get(f"{MINKA_API}/observations/{minka_id}", headers=minka_headers(), timeout=15)
            if r.status_code != 200:
                continue
            
            obs = r.json().get("results", [{}])[0]
            identifications = obs.get("identifications", [])
            photos = obs.get("photos", [])
            
            for id_ in identifications:
                user = id_.get("user", {})
                login = user.get("login", "")
                
                if login in CURATORS:
                    taxon = id_.get("taxon", {})
                    curator_name = taxon.get("name", "")
                    is_current = id_.get("current", False)
                    
                    if curator_name.lower() == sci_name.lower():
                        # Confirmación: el curador está de acuerdo
                        confirmadas.append({
                            "minka_id": minka_id,
                            "species": curator_name,
                            "curator": login,
                            "photos": [p.get("url", "").replace("square", "medium") for p in photos],
                            "confidence": "curator_confirmed",
                        })
                    elif is_current and curator_name:
                        # Corrección: el curador ha cambiado la identificación
                        corregidas.append({
                            "minka_id": minka_id,
                            "original": sci_name,
                            "corrected": curator_name,
                            "curator": login,
                            "photos": [p.get("url", "").replace("square", "medium") for p in photos],
                        })
            time.sleep(0.3)
        except Exception as e:
            pass
    
    log(f"Feedback curadores: {len(confirmadas)} confirmadas, {len(corregidas)} corregidas")
    return confirmadas, corregidas

def download_curator_photos(confirmadas, namemap):
    """Descarga las fotos de observaciones confirmadas por curadores."""
    downloaded = 0
    for item in confirmadas:
        slug = _slug(item["species"])
        info = namemap.get(slug, {})
        if not info:
            continue
        
        sp_dir = IMAGES_DIR / slug
        sp_dir.mkdir(exist_ok=True)
        
        for pi, url in enumerate(item["photos"][:2]):  # máx 2 por obs
            if not url:
                continue
            dest = sp_dir / f"minka_curator_{item['minka_id']}_{pi}.jpg"
            if dest.exists():
                continue
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    dest.write_bytes(r.content)
                    if _valid_image(dest):
                        downloaded += 1
                    else:
                        dest.unlink()
            except Exception:
                pass
            time.sleep(0.2)
    
    log(f"Descargadas {downloaded} fotos de curadores")

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    log("=== INICIO REPESCA DIARIA ===")
    t0 = time.time()
    
    namemap = load_taxonomy()
    inventory = inventory_images()
    
    # 1. Repesca de iNaturalist para especies sin fotos
    log("\n--- FASE 1: Repesca iNaturalist ---")
    missing = find_missing_species(namemap, inventory)
    if missing:
        results = download_inat_photos(missing)
        total_new = sum(results.values())
        log(f"Repesca iNat completada: {total_new} fotos nuevas en {len([v for v in results.values() if v>0])} especies")
    else:
        log("Todas las especies ya tienen imágenes. Nada que descargar.")
    
    # 2. Feedback de curadores en Minka
    log("\n--- FASE 2: Feedback curadores Minka ---")
    try:
        confirmadas, corregidas = collect_curator_feedback()
        if confirmadas:
            download_curator_photos(confirmadas, namemap)
        if corregidas:
            log(f"Correcciones de curadores (para entrenamiento futuro):")
            for c in corregidas[:10]:
                log(f"  #{c['minka_id']}: {c['original']} → {c['corrected']} ({c['curator']})")
            # Guardar correcciones para uso futuro
            corrections_file = DATASET / "curator_corrections.jsonl"
            with open(corrections_file, "a") as f:
                for c in corregidas:
                    f.write(json.dumps(c) + "\n")
    except Exception as e:
        log(f"Error en feedback curadores: {e}")
    
    elapsed = time.time() - t0
    log(f"\n=== FIN REPESCA ({elapsed:.0f}s) ===")

if __name__ == "__main__":
    main()
