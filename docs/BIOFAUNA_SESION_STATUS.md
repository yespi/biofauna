# BioFauna — Estado de Sesion

> **Hora**: 2026-08-13 15:00 | **SESION COMPLETA. 48h de trabajo continuo.**
> **Acierto produccion**: 74.07% FAMILY_MARGIN (2160 muestras, 828 spp)
> **GPU**: Libre (49°C)

## CIERRE DEFINITIVO

### Vias de modelo (15+ tecnicas, 0 mejoran)
Triplet, ArcFace (200/400/800/1158), LoRA (50/100/200/400/800/1358), 
QLoRA (int8), DINOv3, VLM re-ranker (texto e imagen v1/v2), SAM, TTA

### Vias de datos (4 vias, 0 accionables)
CL (476/476, 1 sinonimo), Re-ranking (geo-prior empeora), 
Repesca (gap max 18 fotos, no hay mas fotos), Fuentes alternativas (0 fotos)

### Depuraciones finales (Claude)
- TTA: funcionaba correctamente. El 1.5% era por duplicados exactos en el indice
- ArcFace hibrido: 22.1% (especies cambiaron por fusiones). Inviable
- Calliactis: 104/134 segmentadas. 0/3 sigue igual. Sin solucion automatica

### Fusiones taxonomicas (3)
1. ambigolimax_valentianus → lehmannia_valentiana
2. jania_adhaerens → jania_pedunculata  
3. branchiomma_luctuosum → myxicola_infundibulum

### Duplicados en indice
15 pares con similitud >0.98. 2 ya fusionados. Resto son pares cripticos.

### Sistema en produccion
| Metrica | Valor |
|---------|-------|
| Baseline FAMILY_MARGIN | **74.07%** |
| Muestras/Especies | 2160/828 |
| AutoID p>=0.90 | 32.9% cobertura, 96.7% precision |
| Dataset | 584K imagenes, 98.1% limpias |
| Docs | 40 secciones en CHECK_OTHER_IAs |

### Pendiente (mantenimiento, no urgencia)
- Renombrar YOLOFauna → BioFauna
- SDXL en /mnt/gpu/
- QLoRA int4 (mslk pending)
