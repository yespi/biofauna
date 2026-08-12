# BioFauna — Documento Maestro

> **Nombre**: BioFauna. Usa BioCLIP, no YOLO.  
> **Servidor**: HanSolo (Ubuntu, RTX 3060 12GB, IP 192.168.1.135, SSH :3322)  
> **Ultima actualizacion**: 2026-08-11 08:35  
> **Acierto out-of-sample**: 71.69% especie (k=15) | 76.52% genero | 80.37% familia
> 
> CONCLUSION (2026-08-11): 71.69% es el techo del k-NN con ViT-H. Triplet, ArcFace, LoRA, dedup, crops, DINOv3 → ninguno supera el baseline. FAMILY_MARGIN existente ya aporta +4.11pp sobre especie pura (70.83%→74.94%). El override de generos cripticos es redundante. Las 160 spp con 0% se desglosan en 3 cubos (cripticos ya cubiertos, simbiosis, variables). La mejora pasa por calidad de datos, no por logica de fallback adicional. Ver CHECK_OTHER_IAs.md §4 y §9.
>
> NOTA SOBRE LORA: LoRA 1358 spp dio D=+0.2pp en eval interno (split train/test de lora_full.py, 7h18min GPU, tendencia a sobreajuste). Este resultado NO esta verificado con harvest_calib — la limitacion estructural es que harvest_calib.py carga BioCLIP original sin pesos LoRA. Se trata como senal preliminar no verificada, no como cierre con evidencia real (a diferencia de dedup/crops/DINOv3 que si tienen numero harvest).
> **Auditoria de datos**: 98.1% limpio. Ver [`AUDITORIA_DATOS.md`](AUDITORIA_DATOS.md). Caso lima/limax corregido (720 img). Sinonimos fusionados.
>
> NOTA SOBRE IDs: Minka e iNaturalist usan sistemas de ID distintos. Mismo numero de observacion -> especies completamente distintas en cada plataforma. El calib_raw se genero contra la API de Minka (api.minka-sdg.org). Cualquier evaluacion futura debe usar exclusivamente Minka para ser comparable.

## 1. ARQUITECTURA

```
Usuario -> fotofauna.yespi.es -> fauna_api (:3005) -> BioFauna ID (:8090)
                                      ↓                      ↓
                                  PostgreSQL          GPU RTX 3060 12GB
                                                     Encoder + k-NN + calibracion
```

**Encoder**: BioCLIP-2.5 ViT-H (632M params, 1024-dim)  
**Identificacion**: k-NN (k=15) sobre ~550K embeddings + calibracion logistica (ECE=0.04, AUC=0.845)  
**Dataset**: 584K fotos de 3000 especies mediterraneas (iNat + Minka)  
**AutoID**: publica en Minka cuando p>=0.90 (95.5% precision, 30.2% cobertura)

### Archivos clave
| Que | Ruta |
|-----|------|
| Servicio ID | scripts/identify_service.py |
| Re-embedding | scripts/reembed_vith.py |
| Calibracion | scripts/harvest_calib.py + scripts/fit_calib.py |
| LoRA training | scripts/lora_full.py |
| Confident learning | scripts/confident_learning.py |
| Log curadores | scripts/check_curator_feedback.py (cron 30 4 * * *) |
| Checkpoint LoRA | dataset/checkpoints/lora_full_best.pt (3.7 GB) |
| DINOv3 (descartado) | dataset/patterns_dinov3/ + scripts/eval_dinov3_minka.py |
| Patrones ViT-H | dataset/patterns/ |
| Imagenes | /mnt/gpu/fotofauna-images/ (584K, 3000 spp) |

## 2. RESULTADOS

### Accuracy (harvest_calib out-of-sample, 1946 muestras, 810 especies)

| Nivel | ViT-L (baseline) | ViT-H (actual) | Mejora |
|-------|-----------------|----------------|--------|
| Especie | 63.8% | **71.69%** | **+7.89pp** |
| Genero | 69.1% | 76.52% | +7.42pp |
| Familia | 74.5% | 80.37% | +5.87pp |

### AutoID: p>=0.90 -> 95.5% precision, 30.2% cobertura

### Per-species accuracy (820 spp, 2043 muestras)
Distribucion bimodal: 160 spp con 0% accuracy, 433 spp con >90% accuracy. El 71.69% es un promedio entre las que funcionan perfectamente y las que fallan por completo.

## 3. CRONOLOGIA DE EXPERIMENTOS

| Fecha | Experimento | Resultado | Veredicto |
|-------|------------|-----------|-----------|
| 08-06 | QLoRA ViT-L | 1.7% | cerrado |
| 08-07 | ViT-H re-embedding | 70.6% | nuevo baseline |
| 08-08 | ViT-H v2 | 70.6%, 1358 spp | baseline |
| 08-08 | Triplet ViT-H (8 var) | Degrada | cerrado |
| 08-08 | ArcFace | Empata k-NN | cerrado |
| 08-09 | LoRA+ArcFace 50 spp | +3.4pp interno | no escalado |
| 08-09 | Fallback jerarquico | +2pp weighted | activo |
| 08-09 | Grid search k-NN | k=15 en prod | aplicado |
| 08-09 | Recalibracion | ECE=0.04, AUC=0.845 | aplicado |
| 08-09 | OCR MiniCPM-V | 525/525 pags | completado |
| 08-10 | Crops expertos | -0.9pp | cerrado |
| 08-10 | LoRA 100 spp | D=+0.0pp harvest | cerrado |
| 08-10 | Repesca diaria | Cron 4:00 AM | activo |
| 08-10/11 | LoRA 1358 spp | D=+0.2pp interno, 7h18min | senal preliminar |
| 08-11 | Per-species accuracy | Bimodal: 53% >90%, 20% =0% | informado |
| 08-11 | Confident learning | 574 sospechosos | informado |
| 08-11 | Log curadores | Cron diario activo | completado |
| 08-11 | **DINOv3** | **51.78% (-19.9pp) Minka held-out** | **cerrado** |

## 4. ESTADO ACTUAL

71.69% es el techo verificado. El cuello de botella no es el encoder: es la cola larga (160 spp con 0% accuracy). Proximas vias:

1. Resolver harvest_calib con pesos LoRA (limitacion estructural)
2. Mejorar datos de las 160 especies peores (revisar confident learning suspects, mas fotos, sinonimos)
3. QLoRA con torchao (bitsandbytes incompatible con open_clip)
4. Completar repesca diaria (~334 spp)

## 5. CONFIGURACION

- open_clip 3.3.0, torch 2.13.0+cu130, CUDA 13.0
- GPU: RTX 3060 12GB

```bash
# Servicio BioFauna
systemctl --user status biofauna
curl http://localhost:8090/health

# Calibracion
python3 scripts/harvest_calib.py
python3 scripts/fit_calib.py

# Confident learning
python3 scripts/confident_learning.py

# Curadores
python3 scripts/check_curator_feedback.py
```
