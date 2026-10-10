# Evolución de las especies invasoras en Cataluña (lista UE)

**Estado: borrador v1.3 (2026-10-10, origen/vías + láminas históricas).** Resultados + intro/métodos/discusión; bloque Weitzmann; **análisis origen y vías especie por especie** (DOI Crossref); mapas expansión 5 años; contraste *Pterois miles*; **láminas de expansión estilo mapa histórico** (A3/A4).

## Documentos
- [`INTRODUCCION.md`](INTRODUCCION.md) · [`METODOS.md`](METODOS.md) · [`DISCUSION.md`](DISCUSION.md)
- [`RESULTADOS_v1.md`](RESULTADOS_v1.md) — presencia CAT/ES, categorías, series, mapas, **§7 origen/vías**, §11 marinas, §12 expansión 5 años.
- [`ORIGEN_Y_VIAS_EXPANSION.md`](ORIGEN_Y_VIAS_EXPANSION.md) — origen, vía, primeras citas Med/ES/CAT, frentes, causas; caso pez león.
- [`laminas_expansion/`](laminas_expansion/) — láminas A3/A4 por especie principal (punto de entrada, flechas por periodo, frentes, recuadro origen/vía/1ª cita; hipótesis en discontinuo).
- [`tabla_origen_vias_resumen.csv`](tabla_origen_vias_resumen.csv) · [`primera_obs_regiones_bq.csv`](primera_obs_regiones_bq.csv)
- [`REVISION_CRITICA_20261010.md`](REVISION_CRITICA_20261010.md)
- [`marinas_weitzmann_comparativa_20261010.csv`](marinas_weitzmann_comparativa_20261010.csv)
- CSV: `presencia_cat_es.csv`, `serie_anual_normalizada.csv`, `estacionalidad_mensual_cat.csv`, `esfuerzo_bioquest_anual.csv`.
- Figuras: [`figuras/`](figuras/) · [`figuras/expansion/`](figuras/expansion/).

## Cifras ancla (fuentes)
- Presencia: **35**/114 CAT · **52**/114 ES (`presencia_cat_es.csv`).
- BioQuest: **1.071.684** obs; esfuerzo caja CAT **1.220** (2013) → **102.301** (2024) (`public_observations`).
- Serrano et al. 2013: https://doi.org/10.1371/journal.pone.0052739
- *Pterois miles*: lit. Israel 1991 (https://doi.org/10.1007/bf02906001); BQ Med desde 2015-08; 0 obs ES/CAT.

## Qué falta para publicar
1. Verificar lista UE 114 vs EUR-Lex/EASIN.
2. Cerrar hipótesis de origen/vía restantes con EASIN/AquaNIS primarios.
3. Láminas con fotos de Cataluña (autor, licencia, lugar, coordenadas).
4. Redacción final + PDF unificado.

## Fuentes / script
BioQuest = BD `fauna` / `public_observations` (solo SELECT). Script: `/mnt/docker/biofauna/scripts/invasoras_paper_resultados_v1_20261009.py`.
