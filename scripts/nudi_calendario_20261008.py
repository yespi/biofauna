#!/usr/bin/env python3
"""8-oct-2026 (orden Gustavo 7-oct): calendario de observacion de los nudibranquios (Nudibranchia, 133 spp del catalogo) en el Mediterraneo.
Fuente: dataset/enrich_obs_metadata_progress_20260919.json (observaciones de iNat/Minka/GBIF con fecha y coordenadas). Solo CPU/lectura.
Regla (documentada, ajustable): caja mediterranea lon -5.6..36.3, lat 30..46.6; sin duplicados (observador+fecha+coord redondeada); histograma de dia del ano suavizado (ventana circular de 15 dias);
dia 'observable' si suavizado >= 15 % del maximo (8-oct: con datos en >= 11 de los 12 meses (y n>=30) o cobertura >= 300 dias = «Todo el año»; ranking de ubicaciones por celdas de 0,1°, nombre = localidad mas frecuente de las observaciones de la celda); huecos <= 21 dias se unen y se descartan segmentos < 10 dias; circular (cruza fin de ano). Con n < 20 -> 'sin dato suficiente'. Cobertura >= 350 dias -> 'Todo el año'.
Salida: artifacts/nudi_calendario_20261008.csv y /mnt/docs/biofauna/proyecto_nudibranquios/CALENDARIO_BORRADOR_20261008.md. Es un BORRADOR (sin sustrato ni revision a ojo)."""
import json, collections, csv, datetime, os
import numpy as np
R = "/mnt/docker/biofauna/"
MES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIM = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]; CUM = np.cumsum([0] + DIM)  # año no bisiesto, 365 dias
t = json.load(open(R + "dataset/target_species.json")); nu = {x["name"]: x for x in t if x.get("order") == "Nudibranchia"}
d = json.load(open(R + "dataset/enrich_obs_metadata_progress_20260919.json"))
seen = set(); by = collections.defaultdict(list); loc = collections.defaultdict(list)
for src, v in d.items():
    for o, m in v.items():
        n = m.get("obs_taxon_name_api")
        if n not in nu: continue
        try: lat = float(m["obs_lat"]); lon = float(m["obs_lon"]); dt = datetime.date.fromisoformat(m["obs_date"][:10])
        except Exception: continue
        if not (-5.6 <= lon <= 36.3 and 30 <= lat <= 46.6): continue
        key = (m.get("observer_login"), m["obs_date"][:10], round(lat, 3), round(lon, 3), n)
        if key in seen: continue
        seen.add(key); doy = min(dt.timetuple().tm_yday, 365) - 1; by[n].append(doy); loc[n].append((lat, lon, m.get('obs_place_guess') or ''))
def fmt(day):  # dia 0..364 -> "15 Marzo"
    m = int(np.searchsorted(CUM, day, side="right") - 1); return f"{day - CUM[m] + 1} {MES[m]}"
def rangos(doys):
    h = np.bincount(doys, minlength=365).astype(float); k = 15; hh = np.concatenate([h[-k:], h, h[:k]]); s = np.convolve(hh, np.ones(k) / k, mode="same")[k:-k]
    on = s >= 0.15 * s.max()
    # unir huecos <= 10 dias (circular)
    idx = np.where(on)[0]
    if len(idx) == 0: return [], 0
    on2 = on.copy(); n = 365
    for i in range(n):
        if not on[i]:
            # longitud del hueco que empieza en i
            j = 0
            while j <= 21 and not on[(i + j) % n]: j += 1
            if j <= 21 and on[(i - 1) % n] and on[(i + j) % n]:
                for q in range(j): on2[(i + q) % n] = True
    cov = int(on2.sum())
    if cov >= 300: return [("Todo el año",)], cov   # 8-oct (Gustavo): con datos casi todo el año se asume que se puede ver siempre
    # segmentos circulares
    start = [i for i in range(n) if on2[i] and not on2[(i - 1) % n]]; out = []
    for st in start:
        e = st
        while on2[(e + 1) % n]: e += 1
        if ((e - st) % n) + 1 >= 10: out.append((st, e % n))
    return out, cov
GEN = {"spain", "españa", "spanje", "espanya", "es", "france", "italy", "italia", "greece", "croatia", "turkey", "portugal", "malta", "cyprus", "tunisia", "morocco", "israel", "egypt", "libya", "algeria", "montenegro", "albania", "slovenia", "lebanon",
       "girona", "tarragona", "barcelona", "castellón", "castellon", "valencia", "alicante", "murcia", "almería", "almeria", "granada", "málaga", "malaga", "cádiz", "cadiz", "cataluña", "catalonia", "catalunya", "illes balears", "baleares", "islas baleares", "andalucía", "andalucia",
       "mar mediterráneo", "mar mediterrània", "mar mediterranean", "mediterranean sea", "mediterranean", "mar balear", "mar menorca", "mediterráneo", "atlantic ocean", "aegean", "south aegean", "mar", "sea", "región de murcia", "comunidad valenciana", "país valencià", "mallorca", "menorca", "ibiza", "eivissa"}
def nombre_celda(items):
    c = collections.Counter()
    for _, _, pg in items:
        for tkn in {x.strip() for x in pg.replace(";", ",").split(",")}:
            if len(tkn) < 3 or tkn.lower() in GEN or tkn.upper().startswith("ES-") or tkn.isdigit() or any(ch.isdigit() for ch in tkn[:2]): continue
            c[tkn] += 1
    if c and c.most_common(1)[0][1] >= 2: return c.most_common(1)[0][0]
    return None
ZONAS = {"Tossa de Mar": (41.717, 2.934), "Illes Medes / L'Estartit": (42.050, 3.226), "Blanes": (41.674, 2.797), "Cap de Creus / Cadaqués": (42.319, 3.294), "Roses": (42.262, 3.176), "L'Escala": (42.124, 3.133),
         "Begur / Aiguablava": (41.953, 3.213), "Palamós": (41.846, 3.129), "Llafranc / Calella de Palafrugell": (41.893, 3.195), "Sant Feliu de Guíxols": (41.781, 3.030), "Lloret de Mar": (41.700, 2.845), "El Port de la Selva": (42.334, 3.203),
         "Portbou / Colera": (42.420, 3.150), "Barcelona": (41.380, 2.190), "Sitges": (41.235, 1.810), "Tarragona": (41.115, 1.255), "Cambrils": (41.060, 1.060), "L'Ametlla de Mar": (40.880, 0.800), "Cala Montjoi": (42.300, 3.240), "Maresme": (41.55, 2.55)}
def zona(la, lo):
    best = min(ZONAS.items(), key=lambda kv: (kv[1][0] - la) ** 2 + (kv[1][1] - lo) ** 2); d = ((best[1][0] - la) ** 2 + (best[1][1] - lo) ** 2) ** .5
    return best[0] if d <= 0.06 else None   # ~6 km
CELL = collections.defaultdict(list)
for n_, L_ in loc.items():
    for la, lo, pg in L_: CELL[(round(la, 1), round(lo, 1))].append((la, lo, pg))
CNAME = {k: (nombre_celda(v) or f"zona {abs(k[0]):.1f}°{'N' if k[0] >= 0 else 'S'} {abs(k[1]):.1f}°{'E' if k[1] >= 0 else 'W'}") for k, v in CELL.items()}
def top_ubic(n_, k=3):
    c = collections.Counter(zona(la, lo) or CNAME[(round(la, 1), round(lo, 1))] for la, lo, _ in loc[n_]); return ", ".join(x for x, _ in c.most_common(k))
def texto(rs):
    if rs and rs[0] == ("Todo el año",): return "Todo el año"
    ps = []
    for st, e in rs:
        ms, me = int(np.searchsorted(CUM, st, side="right") - 1), int(np.searchsorted(CUM, e, side="right") - 1)
        if ms == me and (st - CUM[ms]) <= 3 and (e - CUM[me]) >= DIM[me] - 4: ps.append(MES[ms])
        else: ps.append(f"{fmt(st)}-{fmt(e)}")
    return "; ".join(ps)
rows = []
for n, x in sorted(nu.items()):
    dd = by.get(n, [])
    if len(dd) < 20: rows.append({"especie": n, "n_obs": len(dd), "periodo": "sin dato suficiente", "cobertura_dias": "", "meses_top": "", "ubicaciones_top": top_ubic(n) if len(dd) else ""}); continue
    rs, cov = rangos(np.array(dd)); mc = collections.Counter(int(np.searchsorted(CUM, q, side="right") - 1) for q in dd)
    rows.append({"especie": n, "n_obs": len(dd), "periodo": ("Todo el año" if len(mc) >= 11 else texto(rs)), "meses_con_datos": len(mc), "cobertura_dias": cov, "meses_top": ", ".join(MES[m][:3] for m, _ in mc.most_common(3)), "ubicaciones_top": top_ubic(n)})
os.makedirs("/mnt/docs/biofauna/proyecto_nudibranquios", exist_ok=True)
with open(R + "artifacts/nudi_calendario_20261008.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["especie","n_obs","periodo","meses_con_datos","cobertura_dias","meses_top","ubicaciones_top"], restval=""); w.writeheader(); w.writerows(rows)
ok = [r for r in rows if r["periodo"] != "sin dato suficiente"]
with open("/mnt/docs/biofauna/proyecto_nudibranquios/CALENDARIO_BORRADOR_20261008.md", "w") as f:
    f.write("# Calendario de observación de nudibranquios (Mediterráneo) — BORRADOR 8-oct-2026\n\n")
    f.write(f"{len(ok)} de {len(rows)} especies del catálogo tienen datos suficientes (≥20 observaciones únicas en la caja mediterránea; total {sum(r['n_obs'] for r in rows)}). **Borrador automático: sin sustrato, sin revisión a ojo y con los sesgos de la ciencia ciudadana (esfuerzo de buceo estival).** Regla y código: `scripts/nudi_calendario_20261008.py`.\n\n")
    f.write("| Especie | Obs. | Periodo observable | Dónde más se ve (top 3) |\n|---|---:|---|---|\n")
    for r in sorted(rows, key=lambda r: -r["n_obs"]): f.write(f"| *{r['especie']}* | {r['n_obs']} | {r['periodo']} | {r['ubicaciones_top']} |\n")
print(len(rows), len(ok)); print(collections.Counter(r["periodo"] == "Todo el año" for r in ok))
for r in sorted(ok, key=lambda r: -r["n_obs"])[:12]: print(r["especie"], r["n_obs"], r["periodo"])
