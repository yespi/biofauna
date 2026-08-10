# BioFauna

**AI-based Mediterranean marine fauna identification.**  
Formerly YOLOFauna. Production stack: **BioCLIP-2.5 ViT-H + k-NN (k=15)**.

## Architecture
- **Encoder**: BioCLIP-2.5 ViT-H (632M params, 1024-dim), frozen
- **Identification**: k-NN (k=15) over ~450K–550K embeddings + logistic calibration
- **AutoID**: Publishes to Minka when p≥0.90 (**95.5%** precision, **30.2%** coverage)
- **Fallback**: Hierarchical species→genus→family + iNaturalist CV cross-check

## Accuracy (out-of-sample, `harvest_calib`, 2026-08-10)

| Level | Accuracy |
|-------|----------|
| Species | **71.7%** |
| Genus | **76.5%** |
| Family | **80.4%** |

Gains that stuck: ViT-L→ViT-H (**+6.8pp**), k=25→k=15 (**+1.1pp**).  
Triplet / ArcFace / LoRA / dedup / expert crops did **not** beat 71.7% on the trusted protocol.

## Quick Start
```bash
# Service
python3 -m uvicorn scripts.identify_service:app --host 0.0.0.0 --port 8090

# Re-embedding (ViT-H)
python3 scripts/reembed_vith.py

# Calibration (observation-stratified)
python3 scripts/harvest_calib.py 3 --out dataset/calib_raw.jsonl
python3 scripts/fit_calib.py
```

## Docs
- [Paper](paper/01_biofauna.md)
- [Master Document](docs/BIOFAUNA_MASTER.md)
- [Methodology](docs/methodology.md)

## Previous Project
This project supersedes [YOLOFauna](https://github.com/yespi/yolofauna).
