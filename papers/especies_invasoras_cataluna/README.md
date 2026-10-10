# Evolución de las especies invasoras en Cataluña (lista UE)

**Estado: borrador v1.2 (2026-10-10, 2ª vuelta revisor).** Resultados + intro/métodos/discusión; bloque exóticas marinas Weitzmann; DOI Serrano 2013 verificado.

## Documentos
- [`INTRODUCCION.md`](INTRODUCCION.md) · [`METODOS.md`](METODOS.md) · [`DISCUSION.md`](DISCUSION.md)
- [`RESULTADOS_v1.md`](RESULTADOS_v1.md) — presencia CAT/ES, categorías, series normalizadas, mapas, **§11 exóticas marinas**, esfuerzo BioQuest.
- [`REVISION_CRITICA_20261010.md`](REVISION_CRITICA_20261010.md) — hallazgos del revisor (esfuerzo 1.220, Serrano DOI, etc.).
- [`marinas_weitzmann_comparativa_20261010.csv`](marinas_weitzmann_comparativa_20261010.csv)
- CSV: `presencia_cat_es.csv`, `serie_anual_normalizada.csv`, `estacionalidad_mensual_cat.csv`, `esfuerzo_bioquest_anual.csv`.
- Figuras: [`figuras/`](figuras/).

## Cifras ancla (fuentes)
- Presencia: **35**/114 CAT · **52**/114 ES (`presencia_cat_es.csv`).
- BioQuest: **1.071.684** obs; esfuerzo caja CAT **1.220** (2013) → **102.301** (2024) (`public_observations`).
- Serrano et al. 2013: https://doi.org/10.1371/journal.pone.0052739

## Qué falta para publicar
1. Verificar lista UE 114 vs EUR-Lex/EASIN.
2. Orígenes/vectores EASIN (hoy 4 spp en `academy_invasive`).
3. Láminas con fotos de Cataluña (autor, licencia, lugar, coordenadas).
4. Redacción final + PDF unificado.

## Fuentes / script
BioQuest = BD `fauna` / `public_observations` (solo SELECT). Script: `/mnt/docker/biofauna/scripts/invasoras_paper_resultados_v1_20261009.py`.
