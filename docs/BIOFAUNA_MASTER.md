# BioFauna — short master (public)

> **2026-09-28** · Live gallery **1,118,353** embeddings / **4,543** species (FAISS aligned) · operating **field evaluation 81.4%** species (n=62,408) · closed-set leak-free 88.11% · [fotofauna.yespi.es](https://fotofauna.yespi.es)

Frozen **BioCLIP-2.5 ViT-H** + k-NN k=15 + T=0.05 + max 3 votes per species + ROI fusion + calibration + hierarchical abstention.

| | |
|---|---|
| Species / genus / family | 88.11% / 90.55% / 92.46% (leak-free, 2026-09-23) |
| Real-world check | ~80% on recent research-grade observations (operating KPI) |
| AutoID | p≥0.80 → 97.0% precision / 80.6% coverage (species-disjoint split, closed-set) |

What moved the needle: ViT-H, k=15, complete gallery, ROI fusion, tempered k-NN, per-species vote cap, data quality. What did not: LoRA/QLoRA/triplet/ArcFace/SupCon on this embedding space. Measurement lesson: every evaluation photo must pass a global-embedding leak gate (O18). Ledger: [EXPERIMENTS.md](EXPERIMENTS.md) · [paper](../papers/biofauna/01_biofauna.md).
