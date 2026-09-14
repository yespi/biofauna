# BioFauna — short master (public)

> **2026-09-14** · Live **85.78%** species OOS (n=19,087) · FAISS **848,883** / 4,702 spp · [fotofauna.yespi.es](https://fotofauna.yespi.es)

Frozen **BioCLIP-2.5 ViT-H** + k-NN k=15 + T=0.05 + ROI fusion + calibration + hierarchical abstention.

| | |
|---|---|
| Species / genus / family | 85.78% / 89.15% / 91.41% |
| AutoID | p≥0.80 (August study ~95.3% precision / ~57.4% coverage) |

What moved the needle: ViT-H, k=15, complete gallery, ROI fusion, tempered k-NN, data quality. What did not: LoRA/QLoRA/triplet/ArcFace/SupCon on this embedding space. Ledger: [EXPERIMENTS.md](EXPERIMENTS.md) · [paper](../paper/01_biofauna.md).
