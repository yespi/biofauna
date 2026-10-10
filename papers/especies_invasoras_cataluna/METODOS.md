# Métodos — Invasoras Cataluña / España

**Generado:** 2026-10-10 (HanSolo). **Sin GPU; sin escribir en producción.** Solo `SELECT` en PostgreSQL y GET a APIs públicas.

## 1. Lista de especies

- Fuente: `artifacts/invasoras_ue_cruce_20261004.json` → **114** especies (lista interna BioFauna).
- Copia en el paper: `target_species.json`.

## 2. Regiones

| Región | Definición |
|---|---|
| Cataluña (iNat) | Place iNaturalist **61614** |
| España (iNat) | Place **6774** |
| Caja Minka / BioQuest | lat 40,45–42,95; lon 0,10–3,40 (8-oct-2026; incluye franjas fuera de Cataluña administrativa) |

Las cifras «combinadas» usan el **máximo** entre fuentes por región, no la suma (evita doble conteo iNat/Minka).

## 3. BioQuest / Atlas

- BD: contenedor `postgres-global`, base `fauna`, tabla `public_observations` (`source` ∈ {inat, minka}).
- Catálogo Academy: `academy_catalog_core` (**8** spp con `group='invasora'` a 9-oct; no cubre la lista UE completa).
- Metadatos origen/vector: `academy_invasive` (solo cuando existe; no se inventan).
- Documentación: `/mnt/docs/biofauna/proyecto_invasoras/BIOQUEST_COMO_CONSULTAR.md`.

**Gráfica de esfuerzo:** conteo anual de filas en `public_observations` dentro de la caja CAT (SQL en `RESULTADOS_v1.md` §1). Figura: `figuras/esfuerzo_bioquest_catalunya.png`.

## 4. iNaturalist (complemento lista UE)

Enriquecimiento por taxon_id (place Catalunya/España): conteos, primera observación (`order_by=observed_on`), estacionalidad mensual (`interval=month`). Caché local: `artifacts/invasoras/inat_enrich_cache.json`.

## 5. Categorías operativas (Cataluña)

Reglas documentadas en `RESULTADOS_v1.md` §4 (no son estatus legales EASIN):

- **ausente:** 0 obs en todas las fuentes.
- **ocasional_o_puntual:** &lt;10 obs, o &lt;3 localidades, o &lt;3 años con obs.
- **en_expansion:** ≥10 obs y ratio tasa normalizada (últimos 5 años / 5 previos) ≥ 1,5.
- **establecida:** resto con ≥10 obs, ≥3 localidades y ≥3 años.

## 6. Normalización por esfuerzo

Por especie y año: `obs_especie_año / obs_totales_BioQuest_caja_año × 1000`. Proxy imperfecto (catálogo Academy dirigido, no censo aleatorio de biota). CSV: `serie_anual_normalizada.csv`, `esfuerzo_bioquest_anual.csv`.

## 7. Mapas por década

Scatter lat/lng (matplotlib) sobre caja CAT; puntos de especies UE presentes en BioQuest (cobertura incompleta). PNG en `figuras/mapa_cat_*.png`.

## 8. Exóticas marinas (Weitzmann)

Lista provisional ampliada: `artifacts/invasoras/marinas_weitzmann_20261010.json`.

Comparación de primeras fechas en Cataluña:

- **BioFauna:** mínimo `obs_date` en caja CAT en `dataset/enrich_obs_metadata_progress_20260919.json` (proxy de primera observación enlazada a foto de galería).
- **iNaturalist:** primera obs en place 61614 (API v1).
- **BioQuest:** mínimo año-mes en `public_observations` (resolución mensual).

Referencias (DOI verificados en Crossref/OpenAlex, 10-oct-2026):

- García, M., Weitzmann, B., et al. (2015). *The Mediterranean Sea*. Capítulo sobre especies exóticas. https://doi.org/10.1007/698_2015_411
- Serrano, O., et al. (2013). *PLoS ONE* (registros marinos / invasions — ver cita completa en §11 de resultados).
- ClimateFish (2022). *Frontiers in Marine Science* **9**:910887. https://doi.org/10.3389/fmars.2022.910887

## 9. Reproducibilidad

Script de generación de tablas/figuras (cuando esté versionado): `scripts/invasoras_paper_resultados_v1_20261009.py` → escribe también `/mnt/docker/biofauna/artifacts/invasoras/`.
