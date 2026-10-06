# BioFauna — public status

> **2026-10-06.** Live gallery **1,132,767** embeddings / **4,543** species (two promotions since 2026-10-03: *clean combo* on 5 Oct, +0.163 pp on the panel; *harvest batches 01+02* on 6 Oct, +0.223 pp, and +0.42 to +0.50 pp on the leak-free rows). Field panel (78,145 rows): **82.85 %** species (82.463 % on 5 Oct); clean v2 evaluation 62,796 rows 82.84 %; **leak-free rows 54,878: 80.63 %** before the promotions. Every promotion needs ≥ +0.2 pp, McNemar p<0.05, a per-species guard (no species with n≥10 loses ≥3 photos or >30 points), a backup and a rollback script. Found: **96,392 photos on disk never embedded** (867 species; harvested after each species' last embedding); a full per-species re-embedding of the 715 species still below 100 % is under way. Measured and **not adopted**: prototype cleaning, DINOv3 tie-break, vision-language comparator, Grounding DINO / YOLO26n crops, under-exposure enhancement, colour and zone tie-breaks (see [`EXPERIMENTS.md`](EXPERIMENTS.md)). AutoID: sibling-avoidance rule removed (correct in 3 of 11 judged substitutions vs 102 of 105 for the rest), rescue in two steps on, crop-mix publication paused, genus at p≥0.95 on, species threshold 0.83 unchanged. Paper: [`../papers/biofauna/`](../papers/biofauna/) §5.3.

> **2026-10-03.** Live gallery **1,118,321** embeddings / **4,543** species. Tier-1 data experiments (more photos, gallery purges, hard-species batch) moved the field panel by ≤ +0.03 pp: the remaining error is diffuse and comes from congeneric look-alikes (96% of the gallery folders of the 17 most confusable marine pairs were already correctly filed). Baselines on the same 78,180 rows: nearest centroid 74.73%, plain k-NN 79.86%, full system 82.46%. Hierarchical abstention: in-sample cascade +12 pp of publishable photos, but out-of-sample (n=1,267) only +2.4 pp at ~90% precision with genus probability ≥ 0.95, which is what AutoID now publishes (family stays off). Details: [`EXPERIMENTS.md`](EXPERIMENTS.md).

> **2026-09-23.** Live production numbers from HanSolo `/health` + `calibration.json`. Not a session diary. Older figures kept in `EXPERIMENTS.md`; **every panel figure before 2026-09-23 contained an evaluation leak (O18).**

> **2026-09-28 — operating metric moved to a field evaluation; three new production guards.**
> Live gallery **1,118,353** embeddings / **4,543** species. After the leak fix, the *closed-set* leak-free figure stands at 88.11%; the *operating* number is now a **field evaluation** (only field photos —iNaturalist/Minka research grade—, 20–30 per species, leak-audited before merging): **62,408 rows → 81.4% species / 84.9% genus**. New: **k-NN margin guard** in AutoID (no species publication when top-1/top-2 margin < 0.02; those rows score 53%), **automatic curator-correction guard** (retracts our IDs when a curator corrects at class level or above), and a **catalogue-wide zero-shot second opinion used as a rescue** (BioCLIP-2.5 text labels, 2,985 species; when top-1 similarity < 0.85 and the zero-shot agrees with another species at p ≥ 0.90 it wins) → **+0.91 pp** measured on the field evaluation. Gallery hygiene: 135 duplicate synonym slugs merged (Minka name authority), ~1,000 mislabelled photos relocated with manifests/rollback, 57 quarantined. Continuous QA: prototype-contamination (daily) and mined-eval leak audit (weekly, auto-purge).

| | |
|---|---|
| Encoder | Frozen **BioCLIP-2.5 ViT-H/14** (`imageomics/bioclip-2.5-vith14`) |
| Classifier | k-NN **k=15**, vote aggregator **T=0.05** with **max 3 votes per species** (K23, since 2026-09-22), prototype boost, 65% ROI fusion |
| Live gallery | **1,118,353** embeddings / **4543** species (1567 of them outside the 2,985-species target catalog), `faiss_aligned=true` |
| Catalog | **2,985** Mediterranean checklist taxa ([`../dataset/catalog.json`](../dataset/catalog.json)) |
| Out-of-sample (panel) | **88.11%** species / 90.55% genus / 92.46% family on the leak-free set (n=12,373; 2,091 species with eval: 1,429 at 100%, 431 <80%; 894 catalog species being re-harvested after the leak purge). **Real-world check: ~80%** on 300 recent Minka research-grade observations (in-catalog birds 84% vs 96% on the panel) — see `EXPERIMENTS.md` O16 |
| Calibrator | Refit 2026-09-23 on leak-free rows: p≥0.80 → 97.0% precision / 80.6% coverage (species-disjoint test split, closed-set) |
| AutoID | Since 2026-09-21: publishes on BioFauna alone (no iNaturalist requirement) with domain guards (Mediterranean bbox; birds only when an independent BioCLIP zero-shot agrees, 98.5% precision at 69% coverage). Throughput 30/h and 1,000/day, managed from the FotoFauna admin; reaching the hourly cap pauses until the next hour (volume alerts are warnings; quality alerts still trip the breaker). Community-ID audit pending |
| Service | https://fotofauna.yespi.es · GPU RTX 3060 12 GB |

**Two labelled metrics** (do not mix them): August leak-checked harvest n=12,788 peaked around **75.97–79.10%** while the inference stack and gallery grew. The 14 Sep figure is a **larger, harder** evaluation mix after T=0.05 and quality campaigns. Paper: [`../papers/biofauna/01_biofauna.md`](../papers/biofauna/01_biofauna.md).

## This repository contains

- Prototype centroids (4543 × 1024) — nearest-centroid demo without photos
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
| [Paper EN](../papers/biofauna/01_biofauna.md) · [ES](../papers/biofauna/01_biofauna_es.md) | Methods + experiment catalog |
| [EXPERIMENTS](EXPERIMENTS.md) | Same ledger, more McNemar detail |
| [dataset](dataset.md) · [self_host](self_host.md) · [api](api.md) | Reconstruct / run |
| [HISTORY](HISTORY.md) | YOLOFauna → BioFauna |
| [archive/](archive/README.md) | August 2026 notes, including the **closed** archive-gap |

Private ops diary stays in `hansolo-docs` (`BIOFAUNA_SESION_STATUS.md`). This file is the public snapshot.

## 2026-10-01
k-NN on GPU (≈3.5× faster per call), crop fallback for AutoID in production (35 → 48 publishable in 500 queue photos; 85.7% of the added ones correct, n=49), calibrated refit weekly with a guard, confidence model in shadow (no gain). See the paper update of 2026-10-01.
