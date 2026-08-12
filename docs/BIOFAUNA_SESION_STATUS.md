# BioFauna — Estado de Sesión

> **Hora**: 2026-08-12 09:15 | **LoRA + ArcFace completados. Sin mejora.**
> **Acierto producción**: 74.07% FAMILY_MARGIN (2148 muestras, 824 spp)
> **GPU**: ArcFace 200 spp corriendo (E13/15, ~30 min restantes)

## 🔄 RESULTADOS DE LA NOCHE

### Re-embedding LoRA
- **Completado**: 2994 spp, 586,435 imágenes, 8.3h GPU
- Sin incidencias. Backup cada 2h funcionando.

### Evaluación LoRA + geo-priors
| Métrica | ViT-H baseline | LoRA 1358 + geo-priors | Delta |
|---------|---------------|----------------------|-------|
| Especie | 69.88% (1501/2148) | 69.68% (1496/2147) | **-0.20pp** |

**Conclusión: LoRA NO mejora.** El +0.2pp interno no se traslada a datos reales. Patrón confirmado: LoRA no escala.

### ArcFace 200 spp (en curso)
- E0-E12 completados sin morir (¡no como antes!)
- E12: acc=94.5%, best=94.5% (baseline=94.1%)
- Mejora interna: +0.4pp. Pendiente de evaluar out-of-sample.

### Geo-priors
- Añadidos a harvest_calib y eval_lora_full
- 1,374/1,437 especies con datos (77,494 puntos)
- Impacto en LoRA: mínimo (-0.20pp con vs sin)

## 📊 SISTEMA ACTUAL
| Métrica | Valor |
|---------|-------|
| Baseline FAMILY_MARGIN | **74.07%** (2148/824) |
| AutoID p≥0.90 | 35.9% cobertura, 97.8% precisión |
| Dataset | 584K img, 98.1% limpias |
| Fusiones | 2 aplicadas |
| HF cache | Local, sin warnings |

## ⏭️ PENDIENTE
- ArcFace 200 spp: terminar y evaluar out-of-sample
- QLoRA torchao
- SDXL en /mnt/gpu/
- Renombrar YOLOFauna → BioFauna
