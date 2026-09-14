# Species coverage

> **2026-09-14**

| Metric | Value |
|--------|-------|
| Live FAISS gallery | **4,702** species / **848,883** embeddings |
| Mediterranean checklist | **2,985** (`dataset/catalog.json`; 2,983 overlap the live prototype set) |
| OOS species accuracy | **85.78%** (n=19,087) |
| AutoID | p≥0.80 (see STATUS) |

Tables: [`../paper/appendix_species.md`](../paper/appendix_species.md).

Sources: Minka + iNaturalist (primary). Field-guide OCR was tested and **did not** beat retrieval. Fine-tuning did not beat frozen ViT-H on this gallery ([EXPERIMENTS.md](EXPERIMENTS.md)).
