# BioFauna — Documento Maestro

> **Fecha**: 2026-08-13 | **Sesion cerrada definitivamente**
> **Acierto produccion**: 74.07% (k=15, ViT-H, FAMILY_MARGIN, 2160 muestras, 828 spp)
> **GPU**: RTX 3060 12GB | **Servidor**: HanSolo (192.168.1.135)

## RESUMEN EJECUTIVO — 48h de investigacion

### Lo que funciona (en produccion)
| Componente | Aporte | Detectado |
|-----------|--------|-----------|
| ViT-L → ViT-H (BioCLIP 2.5) | +7.8pp | Unica palanca real |
| k=25 → k=15 | +1.1pp | Grid search |
| FAMILY_MARGIN (0.06) | +4.2pp | Fallback jerarquico |
| Geo-priors | Neutro en calib, ayuda en prod | Ya activo |
| 5 fusiones taxonomicas | Limpieza de datos | WoRMS |

### Lo que NO funciona (no reabrir sin evidencia nueva)
| Tecnica | Resultado | Seccion | Causa probable |
|---------|-----------|---------|----------------|
| Triplet Loss (8 var) | Degrada (-0.7 a -7pp) | §3.2 | ViT-H ya optimo |
| ArcFace (200/400/800/1158) | +1.5pp → -6.1pp | §30-32 | No escala |
| LoRA (50/100/200/400/800/1358) | +3.4pp → -0.2pp | §3.6 | No escala |
| QLoRA (int8) | 45% E0 (peor que base) | §33 | Cuantizacion degrada |
| DINOv3 | -19.9pp | §3.7 | Prototipos insuficientes |
| VLM re-ranker (texto e imagen) | Degrada / 10% | §16-17, §35 | VLM sin conocimiento dominio |
| SAM segmentacion | 0/3 calliactis | §34 | SAM no identifica sujeto |
| TTA (flip, multi-crop) | ≈ k-NN (no mejora) | §40 | BioCLIP no beneficia |
| Confident learning (476 casos) | 1 sinonimo (0.2%) | §39 | Datos ya limpios |

### Dataset
- 584K imagenes, 99.99% sin duplicados
- 5 fusiones taxonomicas aplicadas
- 3 limpiezas de archivos duplicados
- 44 secciones documentadas en CHECK_OTHER_IAs

### No reabrir sin evidencia nueva
Tecnicas de fine-tuning parcial (LoRA, ArcFace, QLoRA, Triplet) probadas 
a multiples escalas. TODAS muestran el mismo patron: mejora en pocas clases, 
colapso al crecer. No reabrir sin: (a) nuevo backbone significativamente 
distinto, (b) aumento sustancial de datos (>100K fotos nuevas), o 
(c) publicacion con evidencia replicable en dominio similar.

### Enlace a documentacion completa
- CHECK_OTHER_IAs.md (44 secciones): detalle de todos los experimentos
- SESION_STATUS.md: estado actual del sistema
- AUDITORIA_DATOS.md: resultados de limpieza de datos
- Repositorio publico: github.com/yespi/biofauna
