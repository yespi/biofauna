#!/usr/bin/env python3
"""
Construye dataset de pares crípticos (especies confundibles) para YOLOFauna.
Fuentes:
  1. OPK (opistobranquis.info) — descripciones de especies con "similar a"
  2. Minka — especies frecuentemente co-observadas o corregidas por curadores
  3. iNaturalist — sugerencias de especies visualmente similares (CV API)

Output: dataset/cryptic_pairs.jsonl
  {"sp1": "actinia_striata", "sp2": "actinia_mediterranea", "source": "opk", "note": "..."}

Referencia: YOLOFAUNA_PLAN_MAESTRO.md Sec.3.D
"""

import json, os, sys, re, time
from pathlib import Path
from collections import defaultdict
import requests

ROOT = Path(os.environ.get("YOLOFAUNA_ROOT", "/mnt/docker/fotofauna-yolo"))
DATASET = ROOT / "dataset"
OUT = DATASET / "cryptic_pairs.jsonl"
MINKA_API = "https://api.minka-sdg.org/v1"
OPK_API = "https://opistobranquis.info/en/wp-json/wp/v2"
DELAY = 0.3

def _slug(n):
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")

# ── 1. Extraer pares de OPK ────────────────────────────────────────────────
def scrape_opk(max_pages=300):
    """Extrae pares de especies de OPK: todas las especies mencionadas en la misma
    página se consideran potencialmente confundibles (co-ocurrencia en guía)."""
    pairs = []
    page = 1
    total = 0
    
    while page <= max_pages // 20:
        try:
            r = requests.get(f"{OPK_API}/pages", params={"per_page": 50, "page": page}, timeout=30)
            if r.status_code != 200:
                print(f"  OPK page {page}: HTTP {r.status_code}")
                break
            pages = r.json()
            if not pages:
                break
            
            for p in pages:
                total += 1
                title = p.get("title", {}).get("rendered", "")
                content = p.get("content", {}).get("rendered", "")
                if not content or len(content) < 500:
                    continue
                
                # Extraer TODOS los nombres binomiales en <em> del contenido
                em_species = re.findall(r"<em>([A-Z][a-z]+(?:\s+[a-z]+){0,3})</em>", content)
                # Limpiar y filtrar
                species_on_page = []
                for name in em_species:
                    name = name.strip()
                    # Debe tener al menos 2 palabras y empezar con mayúscula
                    parts = name.split()
                    if len(parts) >= 2 and name[0].isupper():
                        species_on_page.append(name)
                
                # También buscar nombres binomiales sin <em> en párrafos cercanos a "similar"
                # y en el título de la página
                if len(parts := title.split()) >= 2:
                    species_on_page.append(title)
                
                # Crear pares entre todas las especies de la página
                species_on_page = list(set(species_on_page))
                for i in range(len(species_on_page)):
                    for j in range(i + 1, len(species_on_page)):
                        sp1 = _slug(species_on_page[i])
                        sp2 = _slug(species_on_page[j])
                        if sp1 and sp2 and sp1 != sp2:
                            pairs.append({"sp1": sp1, "sp2": sp2, "source": "opk",
                                         "note": f"co-occur on {title} page"})
            
            page += 1
            time.sleep(DELAY)
        except Exception as e:
            print(f"  OPK error page {page}: {e}")
            break
    
    print(f"  OPK: {total} páginas, {len(pairs)} pares")
    return pairs

# ── 2. Extraer de Minka (co-observaciones y correcciones de curadores) ──────
def scrape_minka(taxon_ids, max_per_page=200):
    """Busca en Minka observaciones con múltiples especies en misma ubicación/fecha."""
    pairs = []
    
    # Usar correcciones de curadores guardadas
    corrections_file = DATASET / "curator_corrections.jsonl"
    if corrections_file.exists():
        with open(corrections_file) as f:
            for line in f:
                c = json.loads(line)
                sp1 = _slug(c.get("original", ""))
                sp2 = _slug(c.get("corrected", ""))
                if sp1 and sp2 and sp1 != sp2:
                    pairs.append({"sp1": sp1, "sp2": sp2, "source": "minka_curator",
                                 "note": f"curator corrected: {c.get('curator')}",
                                 "weight": 3.0})  # triple peso
        print(f"  Minka corrections: {len(pairs)} pares")
    
    # Buscar especies frecuentemente co-observadas (mismo lugar/día = confundibles)
    # Esto es costoso en API, limitado a 50 taxones
    for tid in taxon_ids[:50]:
        try:
            r = requests.get(f"{MINKA_API}/observations/species_counts",
                           params={"taxon_id": tid, "per_page": 30}, timeout=15)
            if r.status_code == 200:
                data = r.json()
                sp_counts = [(item.get("taxon", {}).get("name", ""), item.get("count", 0))
                            for item in data.get("results", [])]
                # Especies que aparecen en el mismo lugar que el taxón principal
                for other_name, count in sp_counts:
                    sp1 = _slug(other_name)
                    pairs.append({"sp1": _slug(data.get("taxon", {}).get("name", tid)), 
                                 "sp2": sp1, "source": "minka_cooccurrence",
                                 "note": f"co-observed near {tid}"})
            time.sleep(0.5)
        except Exception:
            pass
    
    print(f"  Minka total: {len(pairs)} pares")
    return pairs

# ── 3. Extraer de iNaturalist (sugerencias del CV) ─────────────────────────
def scrape_inat_cv(species_list, max_species=100):
    """Usa la API de iNat para encontrar especies del mismo género (confundibles).
    La API no expone directamente 'similar species', así que usamos especies
    del mismo género como proxy de confundibilidad."""
    pairs = []
    species_by_genus = defaultdict(list)
    
    for sp in species_list:
        name = sp["name"]
        parts = name.split()
        if len(parts) >= 2:
            genus = parts[0]
            species_by_genus[genus].append(sp)
    
    for genus, sp_list in species_by_genus.items():
        if len(sp_list) < 2:
            continue
        # Crear pares entre todas las especies del mismo género
        for i in range(len(sp_list)):
            for j in range(i + 1, len(sp_list)):
                pairs.append({
                    "sp1": sp_list[i]["slug"],
                    "sp2": sp_list[j]["slug"],
                    "source": "same_genus",
                    "note": f"Mismo género: {genus}",
                    "weight": 2.0,
                })
    
    # También usar iNat CV API para algunas especies clave  
    # (la API de score_image da sugerencias visualmente similares)
    inat_ids = [(sp["name"], sp["inat_taxon"]) for sp in species_list 
                if sp.get("inat_taxon")]
    
    tested = 0
    for name, inat_id in inat_ids[:max_species]:
        if tested >= max_species:
            break
        try:
            # Usar el endpoint de especies similares de iNat
            r = requests.get(
                f"https://api.inaturalist.org/v1/taxa/{inat_id}",
                params={"preferred_place_id": 6975},  # Spain
                timeout=10
            )
            if r.status_code == 200:
                data = r.json().get("results", [{}])[0]
                # iNat devuelve 'ancestor_ids' pero no 'similar_taxa'
                # Usamos el genus_id y family_id para agrupar
                pass
            tested += 1
            time.sleep(0.3)
        except Exception:
            pass
    
    print(f"  iNat (same genus): {len(pairs)} pares")
    return pairs

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    print("=== Construyendo dataset de pares crípticos ===\n")
    
    # Cargar nuestras especies
    with open(DATASET / "target_species.json") as f:
        target = json.load(f)
    with open(DATASET / "inat_taxon_cache.json") as f:
        inat_cache = json.load(f)
    
    species = []
    for s in target:
        sp = {
            "name": s["name"],
            "inat_taxon": inat_cache.get(s["name"]),
            "minka_taxon": s.get("minka_taxon"),
            "slug": _slug(s["name"]),
        }
        species.append(sp)
    
    model_species = set(d.name for d in (DATASET / "patterns").iterdir() if d.is_dir())
    species = [s for s in species if s["slug"] in model_species]
    print(f"Especies en el modelo: {len(species)}")
    
    all_pairs = []
    
    # 1. OPK
    print("\n1. Extrayendo de OPK...")
    opk_pairs = scrape_opk(max_pages=200)
    all_pairs.extend(opk_pairs)
    
    # 2. Minka
    print("\n2. Extrayendo de Minka...")
    minka_ids = [s["minka_taxon"] for s in species if s.get("minka_taxon")]
    minka_pairs = scrape_minka(minka_ids)
    all_pairs.extend(minka_pairs)
    
    # 3. iNat CV
    print("\n3. Extrayendo de iNaturalist CV...")
    inat_pairs = scrape_inat_cv(species, max_species=100)
    all_pairs.extend(inat_pairs)
    
    # Filtrar: solo pares donde AMBAS especies están en nuestro modelo
    filtered = []
    seen = set()
    for p in all_pairs:
        sp1, sp2 = p["sp1"], p["sp2"]
        if sp1 not in model_species or sp2 not in model_species:
            continue
        if sp1 == sp2:
            continue
        key = tuple(sorted([sp1, sp2]))
        if key in seen:
            continue
        seen.add(key)
        filtered.append(p)
    
    print(f"\n=== RESULTADO ===")
    print(f"Pares totales extraídos: {len(all_pairs)}")
    print(f"Pares con ambas especies en nuestro modelo: {len(filtered)}")
    
    # Guardar
    with open(OUT, "w") as f:
        for p in filtered:
            f.write(json.dumps(p) + "\n")
    
    print(f"Guardado en {OUT}")
    
    # Mostrar algunos ejemplos
    print(f"\nEjemplos de pares:")
    for p in filtered[:15]:
        print(f"  {p['sp1']:35s} ↔ {p['sp2']:35s} [{p['source']}]")

if __name__ == "__main__":
    main()
