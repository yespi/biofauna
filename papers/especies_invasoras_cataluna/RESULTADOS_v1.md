# Resultados v1 — Especies invasoras de la lista UE en Cataluña y España

**Generado:** 2026-10-10T00:29:52 CEST (HanSolo). **Sin GPU; solo SELECT en BD + GET a APIs.**

## 1. Fuentes y cómo consultar BioQuest

BioQuest (`bioquest.yespi.es`) **comparte backend y base de datos** con FotoFauna:

| Pieza | Dónde |
|---|---|
| Contenedor web | `bioquest-webapp` |
| API / scripts Academy | `fauna_api` (`/mnt/docker/ecosistema-fauna/backend/`) |
| Base de datos | `postgres-global`, BD `fauna` |
| Observaciones Atlas | tabla `public_observations` (iNat + Minka; clave `taxon_id` = iNat) |
| Catálogo Academy | `academy_catalog_core` (185 spp; **8** con `group='invasora'`) |
| Metadatos invasoras | `academy_invasive` (origen/vector; 9 filas) |
| Sync | `bq_sync_nightly.py`, `bq_download_inat.py`, `bq_download_minka.py` |

Consulta de ejemplo (solo lectura):

```bash
docker exec postgres-global psql -U admin_yespi -d fauna -c "\\d public_observations"
docker exec postgres-global psql -U admin_yespi -d fauna -c \
  "SELECT taxon_name, source, COUNT(*) FROM public_observations GROUP BY 1,2 ORDER BY 3 DESC LIMIT 20;"
docker exec fauna_api python3 -c "from academy_catalog import download_species; print(len(download_species()))"
```

Volumen BioQuest al generar: **1071684** observaciones, **694** taxones (iNat 687317, Minka 384367).

**Limitación clave:** el catálogo Academy no descarga la lista UE completa. De las **114** spp de nuestra lista interna, solo **3** tienen filas en `public_observations`. Por eso las cifras de presencia de la lista UE se completan con iNaturalist (place Catalunya=61614, Spain=6774) y Minka (caja 8-oct).

Documentación operativa: `/mnt/docs/biofauna/proyecto_invasoras/BIOQUEST_COMO_CONSULTAR.md`.

## 2. Lista analizada

- Fichero: `artifacts/invasoras_ue_cruce_20261004.json` → **114** especies.
- Lista interna BioFauna 114 spp (artifacts/invasoras_ue_cruce_20261004.json); el Reglamento UE de preocupación unionense ronda ~88–103 según actualización — no re-verificado aquí contra EUR-Lex.
- `target_species.json` del paper: copia en `artifacts/invasoras/` y `proyecto_invasoras/`.

## 3. Presencia en Cataluña y España

| Región | Especies con ≥1 obs | Fuente principal |
|---|---:|---|
| Cataluña | **35** / 114 | máx(iNat place, BioQuest caja, Minka caja) |
| España | **52** / 114 | máx(iNat place Spain, BioQuest caja ES) |

Tabla completa: [`presencia_cat_es.csv`](presencia_cat_es.csv).

### Top 15 en Cataluña (obs combinadas)

| Especie | Obs CAT | Observadores iNat | Localidades* | Categoría | Medio |
|---|---:|---:|---:|---|---|
| *Ailanthus altissima* | 1540 | 450 | 431 | en_expansion | terrestre |
| *Procambarus clarkii* | 646 | 386 | 441 | establecida | agua_dulce |
| *Myocastor coypus* | 498 | 301 | 242 | establecida | terrestre |
| *Trachemys scripta elegans* | 263 | 138 | 177 | establecida | agua_dulce |
| *Broussonetia papyrifera* | 175 | 93 | 145 | establecida | terrestre |
| *Alopochen aegyptiaca* | 167 | 100 | 92 | establecida | terrestre |
| *Vespa velutina nigrithorax* | 156 | 88 | 143 | en_expansion | terrestre |
| *Gambusia holbrooki* | 128 | 89 | 93 | en_expansion | agua_dulce |
| *Neogale vison* | 109 | 64 | 76 | establecida | terrestre |
| *Pennisetum setaceum* | 109 | 50 | 75 | en_expansion | terrestre |
| *Delairea odorata* | 107 | 49 | 69 | en_expansion | terrestre |
| *Rugulopteryx okamurae* | 101 | 4 | 25 | en_expansion | marino |
| *Acacia saligna* | 65 | 49 | 55 | en_expansion | terrestre |
| *Ludwigia peploides* | 58 | 36 | 49 | en_expansion | agua_dulce |
| *Lepomis gibbosus* | 36 | 28 | 34 | establecida | agua_dulce |

\* Localidades ≈ celdas lat/lng redondeadas a 0,001° sobre muestra iNat (máx. 2.000 obs) o BioQuest.

## 4. Categorías, medio y grupo taxonómico

Reglas (documentadas; no son estatus legales EASIN):

- **ausente:** 0 observaciones en Cataluña (todas las fuentes).
- **ocasional_o_puntual:** <10 obs, o <3 localidades, o <3 años con obs.
- **en_expansion:** ≥10 obs y ratio de tasa (obs/esfuerzo) últimos 5 años / 5 previos ≥ 1,5.
- **establecida:** resto con ≥10 obs, ≥3 localidades y ≥3 años.

### Por categoría (Cataluña)

| Categoría | N |
|---|---:|
| ausente | 79 |
| ocasional_o_puntual | 15 |
| establecida | 11 |
| en_expansion | 9 |

### Por medio

| Medio | N |
|---|---:|
| terrestre | 81 |
| agua_dulce | 32 |
| marino | 1 |

### Por grupo taxonómico

| Grupo | N |
|---|---:|
| Plantae | 47 |
| Mammalia | 16 |
| Peces | 12 |
| Crustacea | 9 |
| Aves | 8 |
| Insecta | 7 |
| Platyhelminthes | 4 |
| Reptilia | 2 |
| Amphibia | 2 |
| Gastropoda | 2 |
| Bivalvia | 2 |
| Asteroidea | 1 |
| otro | 1 |
| Algas | 1 |

## 5. Volumen anual normalizado por esfuerzo

El esfuerzo de observación en ciencia ciudadana crece mucho. Normalizamos las series de cada especie como `obs_especie_año / obs_totales_BioQuest_caja_año × 1000`, usando el esfuerzo del catálogo Academy en la caja de Cataluña/España (proxy imperfecto: el catálogo no es una muestra aleatoria de toda la biota).

CSV: `serie_anual_normalizada.csv`, `esfuerzo_bioquest_anual.csv`. Figura: `figuras/esfuerzo_bioquest_catalunya.png`.

## 6. Primera observación, picos y estacionalidad

Primera observación iNat (place) y picos = años con z-score ≥ 1,5 en la tasa normalizada (mín. 3 obs ese año).
Estacionalidad mensual: histograma iNat `interval=month` en Cataluña → `estacionalidad_mensual_cat.csv`.

### Primeras observaciones (selección con presencia CAT)

| Especie | Primera CAT | Fuente | Primera ES | Picos CAT |
|---|---|---|---|---|
| *Ailanthus altissima* | 2008-06-08 | inat | 2002-05-29 | 2021 |
| *Procambarus clarkii* | 2001-09-23 | inat | 1990-09-01 | — |
| *Myocastor coypus* | 2012-06-25 | inat | 2012-06-25 | 2021;2026 |
| *Trachemys scripta elegans* | 2006-05-06 | inat | 2004-03-20 | — |
| *Broussonetia papyrifera* | 2017-06-09 | inat | 2016-04-15 | 2021 |
| *Alopochen aegyptiaca* | 2010-04-16 | inat | 2002-11-30 | — |
| *Vespa velutina nigrithorax* | 2017-11-22 | inat | 2015-11-20 | — |
| *Gambusia holbrooki* | 2007-07-13 | inat | 2007-07-13 | — |
| *Neogale vison* | 2010-08-08 | inat | 2010-08-08 | — |
| *Pennisetum setaceum* | 2016-01-20 | inat | 2000-09-06 | 2024 |
| *Delairea odorata* | 2009-12-29 | inat | 2009-05-15 | — |
| *Rugulopteryx okamurae* | 2024-05-31 | inat | 2019-08-16 | — |
| *Acacia saligna* | 2019-07-08 | inat | 2006-02-13 | 2026 |
| *Ludwigia peploides* | 2009-08-02 | inat | 2009-08-02 | — |
| *Lepomis gibbosus* | 2003-07-21 | inat | 2003-07-21 | — |
| *Pacifastacus leniusculus* | 2018-08-27 | inat | 2006-02-26 | 2026 |
| *Obama nungara* | 2016-02-29 | inat | 2016-02-29 | — |
| *Threskiornis aethiopicus* | 2005-03-25 | inat | 2004-04-15 | — |
| *Reynoutria japonica* | 2018-07-20 | inat | 2008-09-24 | — |
| *Impatiens glandulifera* | 2022-08-21 | inat | 2019-08-15 | — |

## 7. Origen nativo y vía de entrada

**Actualizado 10-oct-2026 (~16:45):** análisis especie por especie, mapas de expansión por periodos de 5 años, contraste *Pterois miles* y tabla resumen en [`ORIGEN_Y_VIAS_EXPANSION.md`](ORIGEN_Y_VIAS_EXPANSION.md) · CSV [`tabla_origen_vias_resumen.csv`](tabla_origen_vias_resumen.csv) · primeras fechas BQ [`primera_obs_regiones_bq.csv`](primera_obs_regiones_bq.csv) · figuras [`figuras/expansion/`](figuras/expansion/).

Metadatos previos en BD (`academy_invasive`, Wikidata + `bq_invasive_update.py`) — **no se inventan** filas ahí; el paper ahora completa con literatura (DOI Crossref) e **hipótesis** marcadas:

| Especie (Academy) | Origen | Vía |
|---|---|---|
| *Oxyura jamaicensis* | Desconocido | Vector desconocido |
| *Neogale vison* | Norteamérica | Escapes de granjas peleteras |
| *Procyon lotor* | Norteamérica | Liberación / escape de mascotas exóticas |
| *Trachemys scripta* | Norteamérica | Liberación de mascotas |
| *Pterois miles* | Mar Rojo / Indo-Pacífico | Migración lessepsiana (Suez) |
| *Lagocephalus sceleratus* | Mar Rojo / Indo-Pacífico | Migración lessepsiana (Suez) |
| *Caulerpa cylindracea* | Indo-Pacífico | Agua de lastre / cascos |
| *Magallana gigas* | Desconocido (Academy) | Vector desconocido (lit.: acuicultura) |

### 7.1 *Pterois miles* — contraste mapas vs bibliografía

- **Literatura:** 1ª cita Med **Israel 1991** ([Golani & Sonin 1992](https://doi.org/10.1007/bf02906001)); expansión fuerte desde ~2012 Chipre/Líbano ([Bariche et al. 2013](https://doi.org/10.12681/mms.470); [Kletou et al. 2016](https://doi.org/10.1186/s41200-016-0065-y)); genética Mar Rojo ([Bariche et al. 2017](https://doi.org/10.1038/s41598-017-07326-1)). Vía mayoritaria = **Suez**; acuariofilia = hipótesis secundaria; **lastre no** es la vía principal.
- **BioQuest (`public_observations`, taxon_id 123459):** n=1.663; primera fila **2000** en Mar Rojo; primera en caja Med **2015-08** (Israel); **0** obs España/Cataluña; frente E→centro Med 2016–2025.
- **Por qué los mapas pueden sugerir «~2008 + lastre»:** ausencia de ciencia ciudadana antes de ~2000–2008; la nube 2005–2010 es Mar Rojo nativo, no la invasión de 1991. Detalle en `ORIGEN_Y_VIAS_EXPANSION.md` §2.

## 8. Mapas por década

Scatter lat/lng (matplotlib) sobre caja Cataluña, solo puntos de especies UE presentes en BioQuest (cobertura incompleta de la lista). Archivos: `figuras/mapa_cat_YYYY_YYYY.png`.

## 9. Limitación — sesgo de esfuerzo

1. **Más observadores ≠ más invasoras:** el aumento de apps y proyectos (iNat, Minka SDG, FECDAS) infla las series crudas. Por eso se reportan tasas normalizadas.
2. **Cobertura taxonómica desigual:** plantas y aves están mejor muestreadas que peces dulceacuícolas o planarias; ausencia de obs no implica ausencia biológica.
3. **BioQuest es un catálogo dirigido** (185 spp Academy), no un censo: el esfuerzo-proxy solo refleja esas especies/regiones descargadas por `bq_download_*`.
4. **Solapamiento iNat/Minka:** las cifras «combinadas» usan el máximo entre fuentes, no la suma.
5. **Caja Minka ≠ Cataluña administrativa** (incluye franjas de Aragón/Andorra/Rosellón).
6. **Localidades** son una aproximación por rejilla 0,001° sobre muestra.

## 10. Gráfica BioQuest (esfuerzo anual en caja Cataluña)

Consulta (solo lectura):

```sql
SELECT obs_year, COUNT(*) AS n_obs
FROM public_observations
WHERE lat BETWEEN 40.45 AND 42.95 AND lng BETWEEN 0.1 AND 3.4
GROUP BY obs_year ORDER BY obs_year;
```

| Año | n obs (caja CAT) |
|---:|---:|
| 2013 | 1.220 |
| 2018 | 5.303 |
| 2022 | 25.543 |
| 2024 | 102.301 |
| 2025 | 105.404 |
| 2026 | 37.731 (parcial) |

Serie completa en `esfuerzo_bioquest_anual.csv`. Figura: `figuras/esfuerzo_bioquest_catalunya.png`.

## 11. Otras exóticas marinas (Weitzmann y colaboradores)

Además de la lista UE, revisamos un subconjunto de **exóticas marinas** del inventario ampliado de Boris Weitzmann (`marinas_weitzmann_20261010.json`), contrastando **primera observación en Cataluña** según iNaturalist (place 61614) y según fotos enlazadas a la galería BioFauna (mínimo `obs_date` en caja CAT en `enrich_obs_metadata_progress_20260919.json`).

| Especie | 1ª BF galería (CAT) | n enrich CAT | 1ª iNat (CAT) | n iNat CAT | Lectura breve |
|---|---|---:|---|---:|---|
| *Bursatella leachii* | 2013-10-06 | 68 | 2007-10-26 | 7 | BF entra años después del primer iNat |
| *Oculina patagonica* | 2017-08-15 | 793 | 2011-08-15 | 126 | Amplia galería BF; primer iNat ~6 años antes |
| *Caulerpa taxifolia* | — | 0 | — | 0 | Sin obs iNat place Catalunya a 10-oct-2026 |
| *Caulerpa cylindracea* | 2014-08-05 | 397 | 2014-11-11 | 57 | Alineado ~2014; BQ Minka desde 2014-08 (384 obs caja) |
| *Zebrasoma flavescens* | — | 0 | 2008-10-01 | 10 | Acuariofilia; sin fotos BF en CAT |
| *Balistoides conspicillum* | — | 0 | 2018-04-04 | 6 | Idem |

CSV: [`marinas_weitzmann_comparativa_20261010.csv`](marinas_weitzmann_comparativa_20261010.csv). JSON fuente: `/mnt/docker/biofauna/artifacts/invasoras/marinas_weitzmann_comparativa_20261010.json`.

**Referencias (DOI verificados 10-oct-2026):**

- García, M., Weitzmann, B., et al. (2015). Exotic species in the Mediterranean. En *The Mediterranean Sea* (Springer). https://doi.org/10.1007/698_2015_411
- Serrano, E., Coma, R., Ribes, M., Weitzmann, B., García, M. & Ballesteros, E. (2013). Rapid northward spread of a zooxanthellate coral enhanced by artificial structures and sea warming in the western Mediterranean. *PLoS ONE* **8**(1): e52739. https://doi.org/10.1371/journal.pone.0052739 (DOI verificado Crossref 10-oct-2026; *Oculina patagonica*).
- ClimateFish / Coronado-Franco et al. (2022). *Front. Mar. Sci.* **9**:910887. https://doi.org/10.3389/fmars.2022.910887

No extrapolamos primer registro **oficial** de cada especie: comparamos solo fuentes ciudadanas y galería BF.

## 12. Expansión espacial por periodos (5 años)

Misma lógica que los mapas animados de BioQuest: puntos `lat`/`lng` × `obs_year` en `public_observations` (solo SELECT), agrupados en ventanas 2000–2004 … 2025–2026 para especies principales con cobertura Academy.

| Figura | Especie / contenido |
|---|---|
| `figuras/expansion/expansion_5y_Pterois_miles.png` | Pez león (incluye Mar Rojo N) |
| `figuras/expansion/expansion_5y_Caulerpa_cylindracea.png` | *C. cylindracea* |
| `figuras/expansion/expansion_5y_Oculina_patagonica.png` | *O. patagonica* |
| `figuras/expansion/expansion_5y_Lagocephalus_sceleratus.png` | *L. sceleratus* |
| `figuras/expansion/expansion_5y_Callinectes_sapidus.png` | *C. sapidus* |
| `figuras/expansion/expansion_5y_Asparagopsis_armata.png` | *A. armata* |
| `figuras/expansion/expansion_multiespecie_*.png` | Multiespecie 2010–2014 / 2015–2019 / 2020–2024 |
| `figuras/expansion/pterois_miles_longitud_vs_ano.png` | Longitud vs año + hitos lit. 1991 / ~2012 |

Script: `/mnt/docker/biofauna/artifacts/invasoras/origen_expansion/gen_maps_origen.py`.

## 13. Archivos generados

En `/mnt/docker/biofauna/artifacts/invasoras/`:
- `bq_scan_20261010.jsonl`
- `esfuerzo_bioquest_anual.csv`
- `esfuerzo_bioquest_catalunya.png`
- `estacionalidad_mensual_cat.csv`
- `inat_enrich_cache.json`
- `mapa_cat_1990_1999.png`
- `mapa_cat_2000_2009.png`
- `mapa_cat_2010_2019.png`
- `mapa_cat_2020_2026.png`
- `marinas_weitzmann_20261010.json`
- `meta_fuentes.json`
- `presencia_cat_es.csv`
- `presencia_cat_es.json`
- `resumen_categorias.csv`
- `resumen_grupo.csv`
- `resumen_medio.csv`
- `serie_anual_normalizada.csv`
- `target_species.json`
- `top25_obs_catalunya.png`
- `origen_expansion/` (CSV coords, frentes anuales, PNG expansión)

Figuras en `figuras/` y `figuras/expansion/` de este directorio del paper.
