# BioFauna — Estado de Sesion

> **Hora**: 2026-08-13 11:00 | **TODAS las vias de modelo agotadas. Fase datos.**
> **Acierto produccion**: 74.07% FAMILY_MARGIN (2148 muestras, 824 spp)
> **GPU**: Libre

## CIERRE DEFINITIVO DE VIAS DE MODELO

| Via | Resultado | Evidencia |
|-----|-----------|-----------|
| ViT-L -> ViT-H | +7.8pp | EN PRODUCCION |
| FAMILY_MARGIN (k=15) | +4.2pp | EN PRODUCCION |
| Triplet (8 var) | -0.7 a -7pp | harvest_calib |
| ArcFace (200/400/800/1158) | +1.5pp -> -6.1pp | harvest_calib |
| LoRA (todas escalas) | +3.4pp -> -0.2pp | harvest_calib |
| QLoRA (int8) | 45% E0 (no mejora) | harvest_calib |
| DINOv3 | -19.9pp | harvest_calib |
| VLM re-ranker texto | Degrada BioCLIP | Cerrado |
| VLM re-ranker imagenes | 10% vs 60% k-NN | Piloto 10 spp |
| SAM segmentacion | No separa organismo correcto | Cerrado |

## PROXIMAS VIAS (solo datos)

1. **Confident learning**: revisar 476 sospechosos pendientes
2. **Re-ranking barato**: distancia ponderada dentro del top-k
3. **Buscar mas "calliactis"**: embeddings contaminados por simbiosis
4. **Repesca + atributos diagnosticos**: mantenimiento
