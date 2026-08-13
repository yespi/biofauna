# BioFauna — Estado de Sesion

> **Hora**: 2026-08-12 06:00 | **Sesion completa. Todas las vias de modelo agotadas.**
> **Acierto produccion**: 74.07% FAMILY_MARGIN (2148 muestras, 824 spp)
> **GPU**: Libre (55°C)

## Resultados finales

| Via | Resultado | Evidencia |
|-----|-----------|-----------|
| ViT-L -> ViT-H | +7.8pp | ✅ En produccion |
| FAMILY_MARGIN | +4.2pp | ✅ En produccion |
| Geo-priors | -0.78pp | ✅ En produccion (neutro en calib) |
| Triplet (8 var) | -0.7 a -7pp | ❌ Cerrado |
| ArcFace (200/400/800/1158) | +1.5pp -> -6.1pp | ❌ No escala |
| LoRA (todas escalas) | +3.4pp -> -0.2pp | ❌ No escala |
| DINOv3 | -19.9pp | ❌ Cerrado |
| Ruta A/B (VLM) | Degrada / Solo Haminoea | ❌ Cerrado |
| QLoRA (torchao) | Pendiente | ⏳ Ultima via |

## Pendiente (datos, no modelo)

1. Revisar 540 sospechosos CL (solo 34/574 hechos)
2. Extraer rasgos diagnosticos de guias (6/34 spp)
3. QLoRA torchao
4. Renombrar YOLOFauna -> BioFauna
