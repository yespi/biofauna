# BioFauna — public status

> **2026-09-21.** Live production numbers from HanSolo `/health` + `calibration.json`. Not a session diary. (Table below: 2026-09-21; older 14 Sep figures kept in `EXPERIMENTS.md`.)

| | |
|---|---|
| Encoder | Frozen **BioCLIP-2.5 ViT-H/14** (`imageomics/bioclip-2.5-vith14`) |
| Classifier | k-NN **k=15**, vote aggregator **T=0.05**, prototype boost, 65% ROI fusion |
| Live gallery | **1,072,233** embeddings / **4,705** species (1,720 of them outside the 2,985-species target catalog: 1.8% of vectors), `faiss_aligned=true` |
| Catalog | **2,985** Mediterranean checklist taxa ([`../dataset/catalog.json`](../dataset/catalog.json)) |
| Out-of-sample (panel) | **92.36%** species overlay (n=24,475; 314 species <80%, 500 at 80–99%, 2,008 at 100%, 163 without eval). **Real-world check: ~80%** on 300 recent Minka research-grade observations (in-catalog birds 84% vs 96% on the panel) — see `EXPERIMENTS.md` O16 |
| AutoID | Trial since 2026-09-21: publishes on BioFauna alone (no iNaturalist requirement) with domain guards (Mediterranean bbox; birds only when an independent BioCLIP zero-shot agrees, 98.5% precision at 69% coverage), 15/h cap. Community-ID audit pending |
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

Admins can export live gallery ZIPs from FotoFauna (**BioFauna Fotos**). See [`ff_download.md`](ff_download.md).

## Read next

| Doc | Role |
|-----|------|
| [Paper EN](../paper/01_biofauna.md) · [ES](../paper/01_biofauna_es.md) | Methods + experiment catalog |
| [EXPERIMENTS](EXPERIMENTS.md) | Same ledger, more McNemar detail |
| [dataset](dataset.md) · [self_host](self_host.md) · [api](api.md) | Reconstruct / run |
| [HISTORY](HISTORY.md) | YOLOFauna → BioFauna |
| [archive/](archive/README.md) | August 2026 notes, including the **closed** archive-gap |

Private ops diary stays in `hansolo-docs` (`BIOFAUNA_SESION_STATUS.md`). This file is the public snapshot.
