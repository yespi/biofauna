#!/usr/bin/env python3
"""P1: esfuerzo independiente POR GRUPO y registros por observador (GBIF, dataset iNaturalist Research-grade).
Región: GADM ESP.6_1 (Cataluña). Filtros: dataset iNat RG, HUMAN_OBSERVATION, occurrenceStatus PRESENT, con coordenadas.
Salidas: esfuerzo_grupo_gbif_20261016.csv (year,grupo,n), registros_ue_gbif_20261016.csv (una fila/obs UE: especie,grupo,year,observador,lat,lng),
gbif_meta_20261016.json (fecha, conteos, claves). Pausa 0,3 s entre peticiones."""
import json, time, requests, pandas as pd
from pathlib import Path
M = Path(__file__).parent
API = "https://api.gbif.org/v1/occurrence/search"
BASE = dict(gadmGid="ESP.6_1", datasetKey="50c9509d-22c7-4a22-a47d-8c48425ef4a7",
            basisOfRecord="HUMAN_OBSERVATION", occurrenceStatus="PRESENT", hasCoordinate="true")
Y = "2008,2025"
GROUPS = {  # grupo -> parámetros GBIF (taxonKey)
 "Plantas": [6], "Aves": [212], "Mamíferos": [359], "Herpetofauna": [11592253, 11418114, 131],
 "Insectos": [216]}  # Peces = Chordata(44) - aves - mamíferos - herpetofauna - Ascidiacea(356) (la clase Actinopterygii no tiene clave estable en el backbone)
CLS2G = {"Magnoliopsida":"Plantas","Liliopsida":"Plantas","Polypodiopsida":"Plantas","Aves":"Aves","Mammalia":"Mamíferos",
 "Reptilia":"Herpetofauna","Amphibia":"Herpetofauna","Actinopterygii":"Peces","Insecta":"Insectos"}
s = requests.Session()
def get(url, **p):
    for i in range(5):
        try:
            r = s.get(url, params=p, timeout=60); r.raise_for_status(); time.sleep(0.3); return r.json()
        except Exception as e:
            time.sleep(2 * (i + 1))
    raise RuntimeError(url)
def years(**extra):
    d = get(API, **BASE, **extra, year=Y, limit=0, facet="year", facetLimit=40)
    return {int(c["name"]): c["count"] for c in d["facets"][0]["counts"]}, d["count"]
rows, meta = [], {"fecha": time.strftime("%Y-%m-%d"), "filtros": BASE, "ventana": Y}
tot, ntot = years(); meta["total"] = ntot
acc = {}
for g, keys in GROUPS.items():
    acc[g] = {}
    for k in keys:
        yy, _ = years(taxonKey=k)
        for y, n in yy.items(): acc[g][y] = acc[g].get(y, 0) + n
ch, _ = years(taxonKey=44); asc, _ = years(taxonKey=356)
acc["Peces"] = {y: max(ch.get(y, 0) - asc.get(y, 0) - sum(acc[g].get(y, 0) for g in ("Aves", "Mamíferos", "Herpetofauna")), 0) for y in ch}
GROUPS["Peces"] = []
animalia, _ = years(taxonKey=1)
asig = {}
for g in GROUPS:
    for y, n in acc[g].items(): asig[y] = asig.get(y, 0) + n
for g in GROUPS:
    for y in sorted(tot): rows.append((y, g, acc[g].get(y, 0)))
# Invertebrados no insectos y resto
animal_prop = {y: animalia.get(y, 0) - sum(acc[g].get(y, 0) for g in GROUPS if g != "Plantas") for y in tot}
# Chordata no incluido arriba (tunicados etc.) se deja en "Otros animales"
for y in sorted(tot):
    rows.append((y, "Otros animales (invert. no insectos)", max(animal_prop[y], 0)))
    rows.append((y, "Otros (hongos, cromistas, etc.)", max(tot[y] - acc["Plantas"].get(y, 0) - animalia.get(y, 0), 0)))
eff = pd.DataFrame(rows, columns=["year", "grupo", "n"]).sort_values(["grupo", "year"])
eff.to_csv(M / "esfuerzo_grupo_gbif_20261016.csv", index=False)
print(eff.groupby("grupo").n.sum())
# registros UE
ts = json.loads((M / "target_species.json").read_text())
recs, keys = [], {}
for t in ts:
    nm = t["name"]
    m = get("https://api.gbif.org/v1/species/match", name=nm, strict="false", kingdom=t.get("kingdom") or None)
    k = m.get("usageKey"); keys[nm] = {"key": k, "match": m.get("matchType"), "accepted": m.get("scientificName")}
    if not k: continue
    g = CLS2G.get(t.get("class"), "Otros animales (invert. no insectos)" if t.get("kingdom") == "Animalia" else "Otros (hongos, cromistas, etc.)")
    off = 0
    while True:
        d = get(API, **BASE, taxonKey=k, year=Y, limit=300, offset=off)
        for o in d["results"]:
            recs.append((nm, g, o.get("year"), o.get("month"), o.get("recordedBy") or o.get("identifiedBy") or "", o.get("decimalLatitude"), o.get("decimalLongitude"), o.get("coordinateUncertaintyInMeters"), o.get("gbifID")))
        off += 300
        if d["endOfRecords"] or off >= 100000: break
    print(nm, k, sum(1 for r in recs if r[0] == nm), flush=True)
df = pd.DataFrame(recs, columns=["especie","grupo","year","month","observador","lat","lng","incert_m","gbifID"])
df.to_csv(M / "registros_ue_gbif_20261016.csv", index=False)
meta["claves_gbif"] = keys; meta["n_registros_ue"] = len(df)
(M / "gbif_meta_20261016.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
