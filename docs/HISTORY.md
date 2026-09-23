# BioFauna — History (from YOLOFauna)

> How the project started, why it was renamed, and what to keep from the early years.

## Timeline

| Period | Name | Stack (simplified) | Species accuracy\* |
|--------|------|--------------------|--------------------|
| 2024 → mid-2026 | **YOLOFauna** | Experiments around local ID for FotoFauna; name suggested “YOLO” but the lasting stack became **BioCLIP**, not YOLO detectors | ~**63.9%** (ViT-L + k-NN) |
| 2026-08-07 | Transition | Full gallery re-embedding with **BioCLIP-2.5 ViT-H** | **70.6%** |
| 2026-08-08 | **Rename → BioFauna** | Public name matches architecture (BioCLIP / biology, not YOLO) | 70.6% |
| 2026-08-09–10 | BioFauna production tune | k-NN **k=15**, hierarchical fallback, calibration hygiene | **71.7%** |
| 2026-08-21-23 | Archive-gap fix | Full SSD+HDD-archive re-embed, catalog expanded to ~4,700 target spp | **75.4%** (n=22,332; genus 81.8%, family 85.7%) — later found to include leaked samples, see below |
| 2026-08-24-25 | Fine-tuning round 2 | QLoRA (ViT-L mismatch), LoRA (full-scale, backbone), linear head sidecar (frozen backbone) — all closed negative | **75.4%** unchanged (no cutover) |
| 2026-08-25-26 | Calibration-set leakage found & fixed | 42.7% of calibration photos were duplicates already in the reference gallery (broken dedup check); fixed, re-measured on clean n=12,788 | **75.8%** species / 81.1% genus / 84.5% family |
| 2026-08-27–30 | TTA, ROI fusion, Bucket B, local subspace | Inference stack frozen at 77.77% after five negative post-freeze hypotheses | **77.77%** |
| 2026-08-31 | Tier-1 gallery densification | Same frozen ViT-H; FAISS **785,897** / 4,702 spp. Staging 807,267 not cut over | **79.25%** / Tier-1 75.10% |
| 2026-09-01 | FAISS / label-array desync (live only) | `/reload` rebuilt `KY` without reloading FAISS; terrestrial→marine at 85–100%. Disk evals valid. AutoID wave resumed | **79.25%** harvest; jsonl later **79.10%** |
| 2026-09-04 | night85 staging densification | Overlay McNemar **282/80 +1.58 pp**. Later absorbed into gallery work | **79.10%** jsonl |
| 2026-09-10 | Quality gallery refresh + **k-NN T=0.05** | +2.16 pp (quality) and **+7.81 pp** (T=0.05) on their McNemar tests; FAISS 838,115 | New scorer; not the same cohort as 79.10% |
| 2026-09-11–14 | Eval harvest expansion, Q≥8 swaps, nomenclature, seagrass n=60 | Live calibrator n=19,087 | **85.78%** species / 89.15% genus / 91.41% family; FAISS **848,883** / 4,702 |

| 2026-09-20–21 | Growth waves K19–K20, contamination clean-up, label-alignment guard | FAISS **1,072,233** / 4,705 | Panel then read 92.36% (contained leak, see 2026-09-23) |
| 2026-09-22 | Per-species vote cap 3 (K23) | McNemar +1.13 pp, 177/70 species | In production 07:17 CEST |
| 2026-09-23 | Evaluation leak audit (O18): 50.8% of eval rows were gallery copies; gate fixed, rows purged, calibrator refit | — | **88.11%** species / 90.55% genus / 92.46% family, n=12,373 (leak-free) |

\*Trusted metric: observation-stratified harvest (not photo-level splits). **Do not subtract 79.10 from 85.78** and call it a model gain — different evaluation mix.

## Why “YOLOFauna”?

FotoFauna needed a **self-hosted** Mediterranean identifier besides iNaturalist CV. Early exploration mixed detection/cropping ideas with embedding retrieval. The working name **YOLOFauna** stuck in code paths (`fotofauna-yolo/`, `/vision/yolofauna/…`, env vars `YOLOFAUNA_*`) even after the production brain was clearly **BioCLIP + k-NN**.

That naming was misleading in reviews (“where is YOLO?”). On **2026-08-08** the project was renamed **BioFauna** for documentation and the public GitHub surface.

## What YOLOFauna-era work contributed

Kept (still in BioFauna):

- Citizen-science gallery (Minka + iNaturalist) and WoRMS hygiene
- Prototype / `patterns/` gallery layout and FastAPI identify service
- Logistic calibration + AutoID thresholding for Minka publication
- Taxonomic abstention / hierarchical fallback ideas
- Integration into FotoFauna (local ID first, then iNat cross-check)

Superseded or closed:

- ViT-L as production encoder → replaced by **ViT-H**
- QLoRA-as-headline method → documented as failed / non-shipping path
- Many ViT-L-era fine-tunes that never beat ~63.9%
- Separate public repo narrative under the YOLOFauna name

## Repositories

| Repo | Role |
|------|------|
| **[yespi/biofauna](https://github.com/yespi/biofauna)** | Canonical code + docs + paper |
| [yespi/yolofauna](https://github.com/yespi/yolofauna) | **Retired redirect** (archived). Do not develop there |

Legacy env/path names (`YOLOFAUNA_*`, `fotofauna-yolo`) may still appear in deployment for compatibility; new docs should say **BioFauna**.

## Further reading

- Current status: [`STATUS.md`](STATUS.md)
- Experiments / negative results: [`EXPERIMENTS.md`](EXPERIMENTS.md)
- Paper: [`../paper/01_biofauna.md`](../paper/01_biofauna.md)
- Short master: [`BIOFAUNA_MASTER.md`](BIOFAUNA_MASTER.md)
