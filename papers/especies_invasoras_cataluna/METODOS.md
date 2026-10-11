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

**Gráfica de esfuerzo:** conteo anual de filas en `public_observations` dentro de la caja CAT (SQL en `RESULTADOS_v1.md` §1). Figura: `material/figuras/esfuerzo_bioquest_catalunya.png`.

## 4. iNaturalist (complemento lista UE)

Enriquecimiento por taxon_id (place Catalunya/España): conteos, primera observación (`order_by=observed_on`), estacionalidad mensual (`interval=month`). Caché local: `artifacts/invasoras/inat_enrich_cache.json`.

## 5. Categorías operativas (Cataluña)

Reglas documentadas en `RESULTADOS_v1.md` §4 (no son estatus legales EASIN):

- **ausente:** 0 obs en todas las fuentes.
- **ocasional_o_puntual:** &lt;10 obs, o &lt;3 localidades, o &lt;3 años con obs.
- **en_expansion:** ≥10 obs y ratio tasa normalizada (últimos 5 años / 5 previos) ≥ 1,5.
- **establecida:** resto con ≥10 obs, ≥3 localidades y ≥3 años.

## 6. Normalización por esfuerzo

Por especie y año: `obs_especie_año / obs_totales_BioQuest_caja_año × 1000`. Proxy imperfecto (catálogo Academy dirigido, no censo aleatorio de biota). CSV: `material/serie_anual_normalizada.csv`, `material/esfuerzo_bioquest_anual.csv`.

## 7. Mapas por década

Scatter en **EPSG:25831 (ETRS89 / UTM 31N)** con costa/tierra **Natural Earth 10m**, `aspect=equal` (sin deformar). Taxones del paper en BioQuest (UE + Weitzmann/Academy). Décadas sin puntos se **omiten**. Script: `material/gen_mapas_proyeccion_y_prosperan_20261011.py`. PNG en `material/figuras/mapa_cat_*.png`.

## 7bis. ¿Prosperan o desaparecen?

Tasa anual = `obs_especie / esfuerzo_grupo_o_caja × 1000` (esfuerzo por grupo taxonómico vía `taxon_ancestry` si cobertura ≥5 % del total; si no, esfuerzo caja CAT). IC Poisson ±1,96√obs/esfuerzo. Mann–Kendall + ratio de mitades → en_expansion / estable / en_declive. Ausencia: **desaparecida** solo si 0 obs en 5 años **y** potencia ≥0,95 **y** ≥5 obs históricas en ≥2 años; si no, `desaparecida_proxy`. Script: `material/upgrade_addendum_456_20261011.py`. Detalle: `PROSPERAN_O_DESAPARECEN.md` · CSV · panel + series en `material/figuras/prosperan/`.

## 8. Origen, vías y mapas de expansión (10-oct-2026; corrección Magallana + proyección 11-oct)

- `SELECT` de `lat`,`lng`,`obs_year` en `public_observations` para taxones Academy/Weitzmann con cobertura (p. ej. *Pterois miles* 123459, *Caulerpa cylindracea* 734863, *Oculina patagonica* 107341, *Magallana gigas* 605992, …).
- Agrupación en periodos de **5 años** (2000–2004 … 2025–2026); cajas Med / ES / CAT como en §2. **Med verdadero** excluye Cantábrico/Vizcaya (lng/lat Atl N no cuentan como 1ª Med).
- Bibliografía: DOI comprobados uno a uno en Crossref; sin DOI válido → texto marcado **hipótesis**.
- **Regla de flechas marinas:** solo por mar (Estrecho de Gibraltar, Suez) o **salto humano discontinuo** (acuicultura/fouling/semillas). Prohibido dibujar expansión terrestre de especies marinas.
- **Proyección:** mapas España/Med y láminas en **EPSG:3035 (ETRS89-LAEA)**; costa **Natural Earth 10m**; `aspect=equal` (sin estirar). Mapas década CAT en **EPSG:25831**.
- Salidas: `ORIGEN_Y_VIAS_EXPANSION.md`, `material/tabla_origen_vias_resumen.csv`, `material/figuras/expansion/`, `material/upgrade_addendum_456_20261011.py`.
- Láminas históricas (A3/A4): `material/laminas_expansion/` · `gen_laminas_historicas.py`.

## 8bis. Primeras fechas (mínimo de cualquier fuente)

CSV canónico: [`material/primeras_fechas_20261011.csv`](material/primeras_fechas_20261011.csv). Para cada especie se toma el **mínimo** entre literatura, `material/tabla_origen_vias_resumen.csv`, BioQuest y `material/presencia_cat_es.csv`. Que BioFauna/iNat tengan la 1ª obs más tarde **no** es un resultado de llegada; se marca en `aviso_bf_no_es_primera`.

## 9. Exóticas marinas (Weitzmann)

Lista provisional ampliada: `artifacts/invasoras/marinas_weitzmann_20261010.json`.

Comparación de primeras fechas en Cataluña (siempre vía `material/primeras_fechas_20261011.csv`):

- **Literatura / inventarios:** año mínimo documentado (DOI).
- **iNaturalist / presencia:** primera obs en place 61614 / `material/presencia_cat_es.csv`.
- **BioQuest:** mínimo año-mes en `public_observations` (resolución mensual).
- **BioFauna:** solo como contraste; si es posterior a lit./BQ, no cuenta como 1ª.

Referencias (DOI verificados en Crossref/OpenAlex, 10-oct-2026):

- García, M., Weitzmann, B., et al. (2015). *The Mediterranean Sea*. Capítulo sobre especies exóticas. https://doi.org/10.1007/698_2015_411
- Serrano, E., Coma, R., Ribes, M., Weitzmann, B., García, M. & Ballesteros, E. (2013). *PLoS ONE* **8**(1): e52739. https://doi.org/10.1371/journal.pone.0052739 (*Oculina patagonica*; DOI Crossref 10-oct-2026).
- ClimateFish (2022). *Frontiers in Marine Science* **9**:910887. https://doi.org/10.3389/fmars.2022.910887

## 10. Reproducibilidad

Script de generación de tablas/figuras (cuando esté versionado): `scripts/invasoras_paper_resultados_v1_20261009.py` → escribe también `/mnt/docker/biofauna/artifacts/invasoras/`.  
Mapas origen/expansión: `artifacts/invasoras/origen_expansion/gen_maps_origen.py` (ejecutado en contenedor `fauna_api`).

## 11. Nativas en expansión — método corregido por esfuerzo (11-oct-2026)

Script compartido con el paper de declives: `/mnt/docker/biofauna-public/scripts/tendencias_esfuerzo_nativas_declives_20261011.py`.

1. Tasa = `obs_especie_año / esfuerzo_caja_año × 1000`.
2. `ratio_5y` = media 2020–2024 / media 2015–2019.
3. Panel de controles (10 spp comunes): media `ratio_5y` = **2,398**.
4. `ratio_vs_controls` = `ratio_5y` / 2,398 (umbrales en `NATIVAS_EN_EXPANSION.md`).

Sin el paso 3–4, el crecimiento del esfuerzo (~84×) clasifica casi todo como «en expansión».
