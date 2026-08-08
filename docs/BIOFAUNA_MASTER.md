# BioFauna — Documento Maestro

> **Nombre**: BioFauna (antes YOLOFauna). Usa BioCLIP, no YOLO.  
> **Servidor**: HanSolo (Ubuntu, RTX 3060 12GB, IP 192.168.1.135, SSH :3322)  
> **Última actualización**: 2026-08-08

## 1. ARQUITECTURA

```
Usuario → fotofauna.yespi.es → fauna_api (:3005) → BioFauna ID (:8090)
                                      ↓                      ↓
                                 PostgreSQL          GPU RTX 3060 12GB
                                                    Encoder + k-NN + calibración
```

**Encoder**: BioCLIP-2.5 ViT-H (632M params, **1024-dim**)  
**Identificación**: k-NN (k=25) sobre ~550K embeddings + calibración logística (ECE=0.04, AUC=0.845)  
**Dataset**: 550K fotos de 1,378 especies mediterráneas (iNat + Minka)  
**AutoID**: publica en Minka cuando p≥0.90 (95.5% precisión, 30.2% cobertura)

### Archivos clave
| Qué | Ruta |
|-----|------|
| Servicio ID | `/mnt/docker/fotofauna-yolo/scripts/identify_service.py` |
| Re-embedding | `/mnt/docker/fotofauna-yolo/scripts/reembed_vith.py` |
| Triplet loss | `/mnt/docker/fotofauna-yolo/scripts/train_triplet.py` |
| Calibración | `scripts/harvest_calib.py` + `scripts/fit_calib.py` |
| Patrones | `/mnt/docker/fotofauna-yolo/dataset/patterns/` |
| Imágenes | `/mnt/gpu/fotofauna-images/` (550K, 1,378 spp) |
| Crops guías | `dataset/papers/salvador_crops_guia/` + `pontes_crops/` |
| API keys | `/mnt/utils/.api-keys` |

## 2. RESULTADOS

### Accuracy (calibración out-of-sample, 3,291 muestras, 997 especies)

| Nivel | ViT-L (baseline) | ViT-H (actual) | Mejora |
|-------|-----------------|----------------|--------|
| Especie | 63.8% | **70.6%** | **+6.8pp** |
| Género | 69.1% | 75.8% | +6.7pp |
| Familia | 74.5% | 80.2% | +5.7pp |

### AutoID: p≥0.90 → 95.5% precisión, 30.2% cobertura

## 3. CRONOLOGÍA DE EXPERIMENTOS

| Fecha | Experimento | Resultado | Veredicto |
|-------|------------|-----------|-----------|
| 08-06 | QLoRA ViT-L (proj_head) | 1.7% | ❌ proj_head entrenable |
| 08-07 | **ViT-H re-embedding** | **70.6%** | ✅ **Nuevo baseline** |
| 08-07 | Guías campo (Salvador+Pontes) | 1,616 crops | ✅ Extraídos |
| 08-08 | Corrupción patrones | Pérdida | ❌ Triplet 768vs1024 |
| 08-08 | **ViT-H re-embedding v2** | 🔄 En curso | ETA ~16:30 |

### Lección de los 9 fallidos en ViT-L
QLoRA, DINOv3, MLP, weighted k-NN, etc. → todos ≤63.8%.  
**Conclusión**: fine-tuning de ViT-L no rindió. Escalar a ViT-H SÍ (+6.8pp).  
Son palancas distintas: fine-tuning ≠ capacidad del backbone.

## 4. PLAN DE ACCIÓN (resecuenciado)

### Fase 0: AHORA
- [ ] 🔄 Terminar re-embedding ViT-H (~16:30)
- [ ] Backup verificado

### Fase 1: LIMPIEZA DE DATOS (antes que modelo)
- [ ] **Deduplicación**: ráfagas misma obs, cos>0.99
- [ ] **Confident learning**: etiquetas ruidosas
- [ ] Corregir etiquetas sospechosas

### Fase 2: MEJORA DEL MODELO
- [ ] Triplet loss ViT-H 1024-dim (objetivo 73-75%)
- [ ] **Fallback jerárquico**: especie→género→familia
- [ ] k adaptativo
- [ ] QLoRA ViT-H (sin proj_head)

### Fase 3: MÉTRICAS
- [ ] Macro-F1 por especie
- [ ] Log correcciones AutoID (curadores Minka)
- [ ] Validación en producción

### Fase 4: DATOS ADICIONALES
- [ ] Identificar 1,616 crops con ViT-H
- [ ] OCR Salvador+Pontes (llama3.2-vision)
- [ ] Añadir crops al training + recalibrar

## 5. CONFIGURACIÓN

- open_clip 3.3.0, torch 2.13.0+cu130, CUDA 13.0
- GPU: RTX 3060 12GB | ViT-H: 4.0 GB | k-NN: ~2.1 GB | Qwen: 5.2 GB

```bash
# Servicio
cd /mnt/docker/fotofauna-yolo
python3 -m uvicorn scripts.identify_service:app --host 0.0.0.0 --port 8090
# Re-embedding
python3 scripts/reembed_vith.py
# Calibración
python3 scripts/harvest_calib.py 5 --out dataset/calib_raw_vith.jsonl
python3 scripts/fit_calib.py
# Triplet
python3 scripts/train_triplet.py
# Backup verificado
/tmp/backup_verify.sh
```

## 6. CHECKLIST ANTI-REGRESIÓN

- [ ] ❌ Proj_head entrenable → 1.7%
- [ ] ❌ Backup sin verificar → 9h perdidas
- [ ] ❌ Dimensiones 768 vs 1024 → corrupción
- [ ] ❌ Servicio corriendo en backup → race condition
- [ ] ❌ Escalar sin test pequeño → horas perdidas
- [ ] ❌ Datos sucios antes que modelo → NUEVO: limpiar primero

## 7. OBJETIVO: 80% especie
