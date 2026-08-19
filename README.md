# BioFauna

**AI-based Mediterranean marine fauna identification.**  
Formerly YOLOFauna. Production stack: **BioCLIP-2.5 ViT-H + k-NN (k=15)**.

## Architecture
- **Encoder**: BioCLIP-2.5 ViT-H (632M params, 1024-dim), frozen
- **Identification**: k-NN (k=15) over ~700K embeddings / **~3,000 species** (Aug 2026)
- **AutoID**: Publishes to Minka when p≥0.90 (**95.5%** precision, **30.2%** coverage on baseline cohort)
- **Fallback**: Hierarchical species→genus→family + iNaturalist CV cross-check

## Accuracy

**Published baseline** (out-of-sample `harvest_calib`, observation-stratified, Aug 2026):

| Level | Accuracy |
|-------|----------|
| Species | **71.7%** |
| Genus | **76.5%** |
| Family | **80.4%** |

Gains that stuck: ViT-L→ViT-H (**+6.8pp**), k=25→k=15 (**+1.1pp**).

**Remediation (Aug 2026):** gallery ~3,000 species; tier-1 OOS ~64% while consolidating SSD + HDD archive into embeddings. See [docs/STATUS.md](docs/STATUS.md) and [docs/ARCHIVE_GAP.md](docs/ARCHIVE_GAP.md).

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