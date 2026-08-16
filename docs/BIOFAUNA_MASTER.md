# BioFauna — Documento Maestro (público)

> **Fecha**: 2026-08-16 · Baseline publicado: **71.7%** species (`harvest_calib`)  
> **GPU**: RTX 3060 12GB · **Live**: [fotofauna.yespi.es](https://fotofauna.yespi.es)

## Resumen

BioFauna identifica fauna marina mediterránea con **BioCLIP-2.5 ViT-H** (congelado) + **k-NN k=15** + calibración logística + abstención jerárquica.

| Resultado | Valor |
|-----------|-------|
| Especies (baseline calib) | 71.7% |
| Género / familia | 76.5% / 80.4% |
| AutoID p≥0.90 | 95.5% precisión, 30.2% cobertura |

## Qué funciona

| Componente | Aporte |
|-----------|--------|
| ViT-L → ViT-H | +6.8pp |
| k=25 → k=15 | +1.1pp |
| Fallback jerárquico | ~+2pp ponderado |
| Geo-priors | Neutro en calib, útil en prod |

## Qué NO funciona (no reabrir)

Triplet, ArcFace, LoRA, QLoRA, DINOv3, VLM re-ranker, dedup agresivo, crops de guías — ver [EXPERIMENTS.md](EXPERIMENTS.md).

## Estado agosto 2026

- **~3,000** especies con patrón en producción
- Remediación tier-1 en curso (más fotos globales + re-embed por lotes)
- **Freeze** activo: no se añaden especies nuevas hasta cerrar remediación
- Detalle operativo: repositorio privado `hansolo-docs` / `biofauna/BIOFAUNA_SESION_STATUS.md`

## Enlaces

- [Paper](../paper/01_biofauna.md)
- [STATUS](STATUS.md)
- [species_coverage](species_coverage.md)
- [HISTORY](HISTORY.md)
