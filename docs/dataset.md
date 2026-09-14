## Dataset Information

### Scale (2026-09-14, live)

| Resource | Approx. size |
|----------|--------------|
| Image folders | ~4,700 Mediterranean (+adjacent) species (2,983 with ≥1 photo) |
| Photographs on disk | ~838K |
| ViT-H embeddings (production FAISS gallery) | **848,883** / **4,702** species |
| Prototype centroids published in this repo | `data/patterns/` — 4,702 species (`prototype.npy` per species; full per-photo `embeddings.npy` galleries are not redistributed here, see below) |

> Earlier snapshot (2026-08-10): ~3,000 species, ~585K photos, ~553K embeddings / 1,358 species. Catalog and gallery have since grown substantially (nomenclature audit, gallery-quality campaigns, eval_n expansion — see [`STATUS.md`](STATUS.md) and [`HISTORY.md`](HISTORY.md) for the changelog).

### Sources

Primary sources: **Minka** (Mediterranean citizen science) and **iNaturalist** (research-grade / community). Expert field-guide crops (Pontes, Salvador, Ballesteros) were OCR-labeled and tested as ablations; they are not required to reproduce the 71.7% baseline.

### Obtaining the Dataset

Images cannot be redistributed directly due to licensing, but can be reproduced:

1. **iNaturalist API** — taxon IDs in `docs/species_table.md`
2. **Minka API** — Minka taxon IDs
3. **GBIF** — scientific name + multimedia filter

### Directory Structure

```
dataset/
├── patterns/                 # Active gallery (embeddings.npy per species)
├── calibration.json          # Logistic calibrator + field_acc
├── calib_raw_k15.jsonl       # harvest_calib rows (when published)
└── papers/                   # Optional guide crops / OCR labels
```

### Species Catalog

Historical checklist size in early drafts: **1,369** named taxa.  
Current image corpus spans ~**3,000** folders; the live identifier serves the active patterns subset (~**1,158** species).

Full historical table: `docs/species_table.md`
