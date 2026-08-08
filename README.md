# BioFauna

**AI-based Mediterranean marine fauna identification.**  
Formerly known as YOLOFauna. Uses BioCLIP-2.5 ViT-H + k-NN.

## Architecture
- **Encoder**: BioCLIP-2.5 ViT-H (632M params, 1024-dim)
- **Identification**: k-NN (k=25) over 550K embeddings + logistic calibration
- **AutoID**: Publishes to Minka when p≥0.90 (95.5% precision)

## Accuracy
| Level | Accuracy |
|-------|----------|
| Species | 70.6% |
| Genus | 75.8% |
| Family | 80.2% |

## Quick Start
```bash
# Service
python3 -m uvicorn scripts.identify_service:app --host 0.0.0.0 --port 8090

# Re-embedding (ViT-H)
python3 scripts/reembed_vith.py

# Calibration
python3 scripts/harvest_calib.py 5 --out dataset/calib_raw_vith.jsonl
python3 scripts/fit_calib.py
```

## Docs
- [Master Document](docs/BIOFAUNA_MASTER.md)
- [Sonnet 5 Feedback](docs/HANDOFF_YOLOFAUNA_RESPUESTAS_A_SONNET5.md)

## Previous Project
This project supersedes [YOLOFauna](https://github.com/yespi/yolofauna).
