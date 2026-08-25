# BioFauna — Documento Maestro (público)

> **Fecha**: 2026-08-25 · Baseline vigente: **75.4%** species (`harvest_calib`, n=22.332)  
> **GPU**: RTX 3060 12GB · **Live**: [fotofauna.yespi.es](https://fotofauna.yespi.es)

## Resumen

BioFauna identifica fauna marina mediterránea con **BioCLIP-2.5 ViT-H** (congelado) + **k-NN k=15** + calibración logística + abstención jerárquica.

| Resultado | Valor |
|-----------|-------|
| Especies (baseline calib, n=22.332) | 75.4% |
| Género / familia | 81.8% / 85.7% |
| AutoID p≥0.90 | 95.5% precisión, 30.2% cobertura |

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
