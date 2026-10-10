# Evolución de las especies invasoras en Cataluña (lista UE)

**Estado: borrador v1.1 (2026-10-10).** Resultados + intro/métodos/discusión; bloque exóticas marinas Weitzmann.

## Documentos
- [`INTRODUCCION.md`](INTRODUCCION.md) · [`METODOS.md`](METODOS.md) · [`DISCUSION.md`](DISCUSION.md)
- [`RESULTADOS_v1.md`](RESULTADOS_v1.md) — presencia CAT/ES, categorías, series normalizadas, mapas, **§11 exóticas marinas**, esfuerzo BioQuest.
- [`marinas_weitzmann_comparativa_20261010.csv`](marinas_weitzmann_comparativa_20261010.csv)
- CSV en este directorio: `presencia_cat_es.csv`, `serie_anual_normalizada.csv`, `estacionalidad_mensual_cat.csv`, resúmenes y `esfuerzo_bioquest_anual.csv`.
- Figuras: [`figuras/`](figuras/).
- Lista de trabajo: `target_species.json` (114 spp internas BioFauna; ver nota en RESULTADOS sobre el recuento oficial UE ~103).

## Fuentes
- **BioQuest** (principal para esfuerzo y spp del catálogo Academy): BD `fauna` / `public_observations`. Cómo consultarla: `/mnt/docs/biofauna/proyecto_invasoras/BIOQUEST_COMO_CONSULTAR.md`.
- iNaturalist (places Catalunya=61614, Spain=6774) y Minka (caja Cataluña 8-oct) para completar la lista UE (el catálogo Academy no la descarga entera).

## Script
`/mnt/docker/biofauna/scripts/invasoras_paper_resultados_v1_20261009.py` → también escribe `/mnt/docker/biofauna/artifacts/invasoras/`.
