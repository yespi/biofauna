# BioFauna — Documento Maestro (público)

> **Fecha**: 2026-09-01 · Baseline vigente: **79.25%** species / **75.10%** Tier-1 (`harvest_calib`, n=12.788) · FAISS **785.897** / 4.702 spp, aligned  
> **GPU**: RTX 3060 12GB · **Live**: [fotofauna.yespi.es](https://fotofauna.yespi.es)
> Incidente FAISS/etiquetas (1-sep, solo identify vivo) documentado en el paper §4.16. Ablaciones negativas de abajo siguen vigentes.

## Resumen

BioFauna identifica fauna marina mediterránea con **BioCLIP-2.5 ViT-H** (congelado) + **k-NN k=15** + calibración logística + abstención jerárquica.

| Resultado | Valor |
|-----------|-------|
| Especies (baseline calib, n=12.788, 1-sep-2026) | **79.25%** (Tier-1 75.10%) |
| Género / familia | 81.1% / 84.5% |
| AutoID p≥0.80 | ~95.3% precisión, ~57.4% cobertura (oleada en marcha) |

## Qué funciona

| Componente | Aporte |
|-----------|--------|
| ViT-L → ViT-H | +6.8pp |
| k=25 → k=15 | +1.1pp |
| Fallback jerárquico | ~+2pp ponderado |
| Geo-priors | Neutro en calib, útil en prod |
| Re-embed completo del catálogo (SSD+archivo unificado, ago 2026) | 71.7% → 75.4% especie sobre catálogo ampliado |

## Qué NO funciona (no reabrir)

Triplet, ArcFace, LoRA, QLoRA, DINOv3, VLM re-ranker, dedup agresivo, crops de guías, y (agosto 2026) LoRA a escala completa del catálogo (−31,2pp) y una cabeza de proyección lineal sobre el backbone congelado (−0,6 a −1,1pp) — ver [EXPERIMENTS.md](EXPERIMENTS.md).

## Estado agosto 2026

- **~2.900** especies con ≥2 fotos embebidas en producción (**~4.700** especies objetivo con al menos una foto)
- Remediación tier-1 **cerrada** (21-23 ago): re-embed completo SSD+archivo, baseline 75,4/81,8/85,7% (especie/género/familia)
- Freeze de especies levantado tras cerrar la remediación
- Detalle operativo: repositorio privado `hansolo-docs` / `biofauna/BIOFAUNA_HANDOFF_GENERAL.md`

## Enlaces

- [Paper](../paper/01_biofauna.md)
- [STATUS](STATUS.md)
- [species_coverage](species_coverage.md)
- [HISTORY](HISTORY.md)

## ⚠️ Fuga de datos en el set de calibración — encontrada y arreglada (2026-08-26)

El 25/26-ago-2026 se descubrió que el 42,7% (9.544/22.332) de las fotos del set de calibración
`calib_raw_k15.jsonl` estaban también embebidas en el catálogo de referencia contra el que se
comparaban — la misma foto servía de pregunta y de respuesta. Causa: el harvester de calibración
comprobaba "¿ya visto?" contra una ruta de manifiesto legacy abandonada tras una migración de
directorio de imágenes; la deduplicación nunca funcionó desde entonces. Arreglado (comprobación
directa por similitud de embedding contra el catálogo, validada en producción real). El baseline
limpio (n=12.788, sin fuga), verificado con el script oficial de métricas: **75,8% especie /
81,1% género / 84,5% familia** — muy parecido al 75,4% contaminado que se citaba antes en este
documento, y no cambia ninguna conclusión de los experimentos cerrados (las regresiones de LoRA y
head sidecar son de una magnitud muchísimo mayor que el margen de error introducido por la fuga).
