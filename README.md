# BioFauna

**AI-based Mediterranean marine fauna identification.**  
Formerly YOLOFauna. Production stack: **BioCLIP-2.5 ViT-H + k-NN (k=15)**.

## Architecture
- **Encoder**: BioCLIP-2.5 ViT-H (632M params, 1024-dim), frozen
- **Identification**: k-NN (k=15) over **785,897** embeddings / **4,702** species (Sep 2026)
- **AutoID**: Publishes to Minka when p≥0.80 (**~95.3%** precision, **~57.4%** coverage)
- **Fallback**: Hierarchical species→genus→family + iNaturalist CV cross-check

## Accuracy

**Live official baseline** (out-of-sample `harvest_calib`, n=12,788, 2026-09-01):

| Level | Accuracy |
|-------|----------|
| Species | **79.25%** (Tier-1 **75.10%**) |
| Gallery | **785,897** embeddings / **4,702** species, FAISS aligned |

Paper TTA-era figure (Aug 2026) was 75.97% species; inference mechanisms then 77.77%; densification to 79.25% did not change the frozen encoder. A 1-Sep production-only FAISS/label desync is documented in paper §4.16 — disk evals were never invalid. See [docs/STATUS.md](docs/STATUS.md) and [paper/01_biofauna.md](paper/01_biofauna.md) / [español](paper/01_biofauna_es.md).

## Quick Start
```bash
# Service
python3 -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090

# Calibration (observation-stratified)
python3 src/harvest_calib.py 3 --out dataset/calib_raw.jsonl
python3 src/fit_calib.py
```

## Docs
| Doc | What |
|-----|------|
| [STATUS](docs/STATUS.md) | Current public status (start here) |
| [ARCHIVE_GAP](docs/ARCHIVE_GAP.md) | SSD vs HDD archive consolidation (Aug 2026) |
| [HISTORY](docs/HISTORY.md) | Origins as YOLOFauna → rename to BioFauna |
| [Paper](paper/01_biofauna.md) | Full write-up |
| [Master](docs/BIOFAUNA_MASTER.md) | Short architecture + results |
| [Experiments](docs/EXPERIMENTS.md) | Ablation log |
| [Methodology](docs/methodology.md) | Pipeline |
| [Species coverage](docs/species_coverage.md) | Dataset / gallery sizes |
| [Dataset](docs/dataset.md) · [API](docs/api.md) · [Self-host](docs/self_host.md) | Reproduce / run |
| [Species table](docs/species_table.md) · [Appendix](paper/appendix_species.md) | Historical checklists |

## Naming note
This project was originally called **YOLOFauna**. It was renamed to **BioFauna** in August 2026 because the production system is BioCLIP-based (not YOLO). See [HISTORY](docs/HISTORY.md). The old [yolofauna](https://github.com/yespi/yolofauna) repository is a retired redirect.