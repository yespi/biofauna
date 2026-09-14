# BioFauna — public status

> **2026-09-14.** Live production numbers from HanSolo `/health` + `calibration.json`. Not a session diary.

| | |
|---|---|
| Encoder | Frozen **BioCLIP-2.5 ViT-H/14** (`imageomics/bioclip-2.5-vith14`) |
| Classifier | k-NN **k=15**, vote aggregator **T=0.05**, prototype boost, 65% ROI fusion |
| Live gallery | **848,883** embeddings / **4,702** species, `faiss_aligned=true` |
| Catalog | **2,985** Mediterranean checklist taxa ([`../dataset/catalog.json`](../dataset/catalog.json)) |
| Out-of-sample | **85.78%** species / **89.15%** genus / **91.41%** family (n=**19,087**) |
| AutoID | FotoFauna publishes at calibrated **p≥0.80** (August operating-point study: ~95.3% precision / ~57.4% coverage; calibrator file refreshed 14 Sep) |
| Service | https://fotofauna.yespi.es · GPU RTX 3060 12 GB |

**Two labelled metrics** (do not mix them): August leak-checked harvest n=12,788 peaked around **75.97–79.10%** while the inference stack and gallery grew. The 14 Sep figure is a **larger, harder** evaluation mix after T=0.05 and quality campaigns. Paper: [`../paper/01_biofauna.md`](../paper/01_biofauna.md).

## This repository contains

- Prototype centroids (4,702 × 1024) — nearest-centroid demo without photos
- Taxon IDs to rebuild images from Minka / iNaturalist / GBIF
- Calibrators, geo priors, cryptic pairs, taxonomic exceptions
- Experiment ledger (kept vs rejected)

## This repository does not contain

- Photographs or per-photo `embeddings.npy` (licence + size)
- HanSolo AutoID / MiniCPM sidecars

## Read next

| Doc | Role |
|-----|------|
| [Paper EN](../paper/01_biofauna.md) · [ES](../paper/01_biofauna_es.md) | Methods + experiment catalog |
| [EXPERIMENTS](EXPERIMENTS.md) | Same ledger, more McNemar detail |
| [dataset](dataset.md) · [self_host](self_host.md) · [api](api.md) | Reconstruct / run |
| [HISTORY](HISTORY.md) | YOLOFauna → BioFauna |
| [archive/](archive/README.md) | August 2026 notes, including the **closed** archive-gap |

Private ops diary stays in `hansolo-docs` (`BIOFAUNA_SESION_STATUS.md`). This file is the public snapshot.
