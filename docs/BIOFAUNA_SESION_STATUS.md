# BioFauna — Estado de Sesion

> **Hora**: 2026-08-13 14:00 | **SESION COMPLETA. TODAS LAS VIAS AGOTADAS.**
> **Acierto produccion**: 74.07% FAMILY_MARGIN (2160 muestras, 828 spp)
> **GPU**: Libre (49°C)

## CIERRE DEFINITIVO — 48h de sesion

### Vias de modelo (15+ tecnicas, 0 mejoran)
Triplet, ArcFace (4 escalas), LoRA (6 escalas), QLoRA, DINOv3, VLM re-ranker (texto e imagen), SAM, TTA

### Vias de datos (4 vias, 0 accionables)
CL (476/476, 1 sinonimo), Re-ranking (geo-prior empeora), Repesca (gap max 18 fotos), Fuentes alternativas (0 fotos)

### Fusiones taxonomicas (3)
- ambigolimax_valentianus → lehmannia_valentiana
- jania_adhaerens → jania_pedunculata
- branchiomma_luctuosum → myxicola_infundibulum

### Sistema en produccion
| Metrica | Valor |
|---------|-------|
| Baseline | **74.07%** (FAMILY_MARGIN) |
| Muestras/Especies | 2160/828 |
| AutoID p≥0.90 | 32.9% cobertura, 96.7% precision |
| Dataset | 584K imagenes, 98.1% limpias |
| Docs | 39 secciones en CHECK_OTHER_IAs |

### Proximos pasos (solo mantenimiento)
- Repesca diaria (cron 6:00 AM, automatico)
- Renombrar YOLOFauna → BioFauna (cuando haya ventana)
- SDXL en /mnt/gpu/ (pendiente)
