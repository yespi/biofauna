# Historical note — Sonnet 5 handoff reply (2026-08-08)

> **Superseded.** This document answered an early ViT-H handoff review (baseline then **70.6%**, k still often discussed as 25, many items still “TODO”).  
> Current public status: **[STATUS.md](STATUS.md)** · experiments: **[EXPERIMENTS.md](EXPERIMENTS.md)** · paper: **[../paper/01_biofauna.md](../paper/01_biofauna.md)**.

## What aged well from that reply

- Dedup / confident learning / Macro-F1 were correctly flagged as data work.
- Hierarchical fallback was the right product direction (now on; ~+2pp weighted).
- Encoder scale matters: ViT-H delivered the real **+6.8pp**.

## What the 2026-08-10 evidence changed

| 2026-08-08 expectation | Outcome |
|------------------------|---------|
| Triplet on ViT-H next | ❌ Degrades |
| Dedup will help | ❌ −1.6pp on `harvest_calib` |
| k=25 fixed forever | ❌ **k=15** wins out-of-sample (+1.1pp) |
| Keep name YOLOFauna | Renamed publicly to **BioFauna** |
| Plan centered on more fine-tuning | Ceiling under protocol ≈ **71.7%**; adapters did not help |

The original long-form reply text is retained below for provenance only.

---

# Respuesta a Sonnet 5 — Análisis del Handoff YOLOFauna (archivo)

> 2026-08-08. Respuesta de Yespi/Gustavo al análisis de Sonnet 5 sobre HANDOFF_YOLOFAUNA_COMPLETO.md

## 1. Versión del documento analizado

Sonnet 5 leyó el handoff del **6 de agosto**, que refleja el estado PRE-ViT-H (baseline 63.8% con BioCLIP-2 ViT-L). Desde entonces hemos avanzado significativamente.

## 2. Puntos con los que CONCUERDO y aplico (estado 08-ago)

### 2.1 Deduplicación de fotos casi-idénticas
Planificado entonces. **Medido después**: empeora el métrico confiable (−1.6pp).

### 2.2 Fallback jerárquico (especie → género → familia)
Implementado en producción.

### 2.3 Macro-F1 y accuracy por especie
Sigue siendo deseable; no es el headline actual.

### 2.4 k adaptativo / k fijo
Resuelto en la práctica con **k=15** validado por `harvest_calib`.

### 2.5 Confident learning
Sigue abierto.

## 3. Discrepancias históricas

- El encoder **sí** importó (ViT-H +6.8pp).
- El nombre público pasó a **BioFauna**.

## 4. Plan de entonces vs ahora

El plan 08-ago priorizaba triplet ViT-H y más fine-tuning. El plan 10-ago prioriza **no repetir ablations cerradas**, mantener 71.7%, y elegir DINOv3 / QLoRA compatible / producto.
