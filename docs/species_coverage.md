# Species coverage

> **2026-09-23**

| Metric | Value |
|--------|-------|
| Live FAISS gallery | **4,705** species / **1,072,233** embeddings (1,720 gallery classes outside the catalog, 1.8% of vectors) |
| Mediterranean checklist | **2,985** (`dataset/catalog.json`) |
| Species with leak-free evaluation | **2,091** (894 being re-harvested after the 2026-09-23 leak purge) |
| OOS species accuracy (leak-free) | **88.11%** (n=12,373); 1,429 species at 100%, 431 below 80% |
| Hardest taxa to evaluate | ~70 rare heterobranchs (e.g. *Runcina*, *Trapania*, *Tenellia*, *Doto*) with almost no photos outside the gallery; searched in Wikimedia, GBIF, iDigBio, EOL, Wikipedia, Zenodo/BLR, Openverse, Observation.org |
| AutoID | p≥0.80 (see STATUS) |

Tables: [`../paper/appendix_species.md`](../paper/appendix_species.md).

Sources: Minka + iNaturalist (primary), GBIF/Wikimedia/museum media for rare taxa. Field-guide OCR was tested and **did not** beat retrieval. Fine-tuning did not beat frozen ViT-H on this gallery ([EXPERIMENTS.md](EXPERIMENTS.md)).
