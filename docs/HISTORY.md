# BioFauna — History (from YOLOFauna)

> How the project started, why it was renamed, and what to keep from the early years.

## Timeline

| Period | Name | Stack (simplified) | Species accuracy\* |
|--------|------|--------------------|--------------------|
| 2024 → mid-2026 | **YOLOFauna** | Experiments around local ID for FotoFauna; name suggested “YOLO” but the lasting stack became **BioCLIP**, not YOLO detectors | ~**63.9%** (ViT-L + k-NN) |
| 2026-08-07 | Transition | Full gallery re-embedding with **BioCLIP-2.5 ViT-H** | **70.6%** |
| 2026-08-08 | **Rename → BioFauna** | Public name matches architecture (BioCLIP / biology, not YOLO) | 70.6% |
| 2026-08-09–10 | BioFauna production tune | k-NN **k=15**, hierarchical fallback, calibration hygiene | **71.7%** |
| 2026-08-21–23 | Archive-gap fix | Full SSD+HDD-archive re-embed, catalog expanded to ~4,700 target spp | **75.4%** (n=22,332; genus 81.8%, family 85.7%) |
| 2026-08-24–25 | Fine-tuning round 2 | QLoRA (ViT-L mismatch), LoRA (full-scale, backbone), linear head sidecar (frozen backbone) — all closed negative | **75.4%** unchanged (no cutover) |

\*Trusted metric: observation-stratified `harvest_calib` (not photo-level splits).

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
