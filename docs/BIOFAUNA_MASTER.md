# BioFauna — Master Document (public)

> **Name**: BioFauna (formerly YOLOFauna). Uses BioCLIP, not YOLO.  
> **Last update**: 2026-08-10  
> **Out-of-sample accuracy**: **71.7%** species (k=15) | **76.5%** genus | **80.4%** family

## Architecture

```
User → fotofauna.yespi.es → fauna_api → BioFauna ID (:8090)
                                      ↓
                         GPU: BioCLIP-2.5 ViT-H + k-NN + calibration
```

| Component | Setting |
|-----------|---------|
| Encoder | BioCLIP-2.5 ViT-H (1024-dim), frozen |
| Classifier | k-NN **k=15** + logistic calibration |
| Dataset (images) | ~584K photos, ~3,000 species folders |
| Active gallery | ~1,158 species / ~454K embeddings |
| AutoID | p≥0.90 → **95.5%** precision, **30.2%** coverage |

## Results that matter

| Change | Species accuracy | Keep? |
|--------|------------------|-------|
| ViT-L → ViT-H | 63.9% → 70.6% | ✅ |
| k=25 → k=15 | 70.6% → 71.7% | ✅ |
| Triplet / ArcFace / LoRA / dedup / crops | ≤71.7% or worse | ❌ |

## Production identification flow

```
Upload → BioFauna (ViT-H k-NN)
  ├─ p≥0.90 → AutoID species
  └─ p<0.90 → iNaturalist CV cross-check
```

## Evaluation rule

Only **`harvest_calib`** (observation-stratified) + **`fit_calib`** numbers are trusted.  
Photo-level train/test splits inflate results by ~10pp — do not use them as headlines.

## Paper

See [`paper/01_biofauna.md`](../paper/01_biofauna.md).

## Objective

Aspirational: 80% species top-1. Current verified ceiling under this protocol: **71.7%**. Next levers under consideration: DINOv3 calibration, open_clip-compatible QLoRA (torchao/hqq), VLM re-rank, curator-correction telemetry.
