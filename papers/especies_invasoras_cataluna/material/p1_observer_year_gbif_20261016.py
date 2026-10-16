#!/usr/bin/env python3
"""P1/P2 datos: esfuerzo por observador-año y grupo (facet recordedBy, GBIF, dataset iNat RG, GADM ESP.6_1, 2013-2025).
Salida: observador_anio_grupo_gbif_20261016.csv.gz (year,grupo,obs_id seudónimo,n). Mismos filtros que p1_gbif_esfuerzo_y_registros."""
import time, hashlib, requests, pandas as pd
from pathlib import Path
M = Path(__file__).parent
API = "https://api.gbif.org/v1/occurrence/search"
BASE = dict(gadmGid="ESP.6_1", datasetKey="50c9509d-22c7-4a22-a47d-8c48425ef4a7", basisOfRecord="HUMAN_OBSERVATION",
            occurrenceStatus="PRESENT", hasCoordinate="true")
s = requests.Session()
def fac(year, key=None):
    p = dict(BASE, year=year, limit=0, facet="recordedBy", facetLimit=100000)
    if key: p["taxonKey"] = key
    for i in range(5):
        try:
            r = s.get(API, params=p, timeout=120); r.raise_for_status(); time.sleep(0.3)
            return {c["name"]: c["count"] for c in r.json()["facets"][0]["counts"]}
        except Exception: time.sleep(3 * (i + 1))
    raise RuntimeError((year, key))
def add(a, b, sign=1):
    for k, v in b.items(): a[k] = a.get(k, 0) + sign * v
    return a
rows = []
for y in range(2013, 2026):
    keys = lambda ks: add({}, {}) if not ks else None
    def multi(ks):
        d = {}
        for k in ks: add(d, fac(y, k))
        return d
    tot = fac(y); pl = multi([6]); an = multi([1]); ch = multi([44]); asc = multi([356])
    av = multi([212]); ma = multi([359]); he = multi([11592253, 11418114, 131]); ins = multi([216])
    pe = add(add(add(add(dict(ch), asc, -1), av, -1), ma, -1), he, -1)
    ot_an = add(add(add(add(add(dict(an), av, -1), ma, -1), he, -1), ins, -1), pe, -1)
    ot = add(add(dict(tot), pl, -1), an, -1)
    for g, d in {"Plantas": pl, "Aves": av, "Mamíferos": ma, "Herpetofauna": he, "Peces": pe, "Insectos": ins,
                 "Otros animales (invert. no insectos)": ot_an, "Otros (hongos, cromistas, etc.)": ot}.items():
        for o, n in d.items():
            if n > 0: rows.append((y, g, o, n))
    print(y, len(tot), flush=True)
df = pd.DataFrame(rows, columns=["year", "grupo", "observador", "n"])
df["obs_id"] = df.observador.map(lambda x: hashlib.sha1(("inv2026" + x).encode()).hexdigest()[:10])
df.to_pickle("/tmp/obs_year_raw.pkl")  # con nombres, solo local
df.drop(columns="observador").to_csv(M / "observador_anio_grupo_gbif_20261016.csv.gz", index=False)
print(df.groupby("grupo").n.sum())
