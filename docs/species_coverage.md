# Species coverage

> **2026-10-06.** Live FAISS gallery **4,543** species / **1,132,767** embeddings (2,982 in the Mediterranean checklist, 1,561 outside it). Field panel 78,145 rows over **2,970** species: **82.85 %** species accuracy; 521 species at 100 %, 1,151 below 80 %. Photos on disk exceed vectors by 96,392 (867 species), being re-embedded. The table below is the 2026-09-23 snapshot.

> **2026-09-23**

| Metric | Value |
|--------|-------|
| Live FAISS gallery | **4,543** species / **1,118,353** embeddings (1,567 gallery classes outside the catalog, 1.8% of vectors) |
| Mediterranean checklist | **2,985** (`dataset/catalog.json`) |
| Species with leak-free evaluation | **2,091** (894 being re-harvested after the 2026-09-23 leak purge) |
| OOS species accuracy (leak-free) | **88.11%** (n=12,373); 1,429 species at 100%, 431 below 80% |
| Hardest taxa to evaluate | ~70 rare heterobranchs (e.g. *Runcina*, *Trapania*, *Tenellia*, *Doto*) with almost no photos outside the gallery; searched in Wikimedia, GBIF, iDigBio, EOL, Wikipedia, Zenodo/BLR, Openverse, Observation.org |
| AutoID | p≥0.80 (see STATUS) |

Tables: [`../papers/biofauna/appendix_species.md`](../papers/biofauna/appendix_species.md).

Sources: Minka + iNaturalist (primary), GBIF/Wikimedia/museum media for rare taxa. Field-guide OCR was tested and **did not** beat retrieval. Fine-tuning did not beat frozen ViT-H on this gallery ([EXPERIMENTS.md](EXPERIMENTS.md)).
