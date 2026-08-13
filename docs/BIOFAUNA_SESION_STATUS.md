# BioFauna — Estado de Sesion

> **Fecha**: 2026-08-13 18:00 | **Sesion de investigacion CERRADA (48h)**
> **Acierto produccion**: 74.07% FAMILY_MARGIN (2160 muestras, 828 spp)
> **GPU**: Libre

## RESUMEN EJECUTIVO

### Logros
- 44 secciones documentadas en CHECK_OTHER_IAs
- 15+ tecnicas de modelo probadas (0 mejoran baseline)
- 476 CL sospechosos revisados (1 sinonimo encontrado)
- 5 fusiones taxonomicas + 3 limpiezas de duplicados
- Dataset 99.99% limpio (454K embeddings, 584K imagenes)
- 153 pares de especies analizados por similitud (Nivel 1+2 Faiss)

### Sistema en produccion
| Componente | Puerto | Estado |
|-----------|--------|--------|
| BioFauna ID | :8090 | ⚠️ Inestable (tarda ~40s en arrancar, bg loop falla) |
| fauna_api | :3005 | 🟢 Up (15h) |
| Ollama | — | 🔴 Parado |
| Swap | — | 🟢 0B usado |

### Bug BioFauna ID
- `UnboundLocalError: variable S` en FAISS path (parcialmente corregido)
- Background `_bg_loop` atascado en `aplidium_coeruleum` (creado embeddings dummy)
- Servicio arranca con `python3 -m uvicorn` pero tarda ~40s en cargar modelo+FAISS
- Pendiente: verificar identificacion con imagen real (no donax)

### Lo que funciona
| Tecnica | Aporte |
|---------|--------|
| ViT-H (BioCLIP 2.5) | +7.8pp |
| k=15 + FAMILY_MARGIN | 74.07% |
| 5 fusiones taxonomicas | Datos limpios |
| Geo-priors | Neutro en calib, ayuda en prod |

### Lo que NO funciona (no reabrir)
Triplet, ArcFace (200-1158), LoRA (50-1358), QLoRA, DINOv3, VLM re-ranker, SAM, TTA

### Pendiente
1. Arreglar BioFauna ID definitivamente (bug FAISS + bg loop)
2. Feature "Duplicado (x)" en Recortar webapp
3. Renombrar YOLOFauna → BioFauna (cuando haya ventana)
