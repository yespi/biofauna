## Dataset Information

### Scale (2026-08-10)

| Resource | Approx. size |
|----------|--------------|
| Image folders | ~3,000 Mediterranean species (2,994 with ≥1 photo) |
| Photographs on disk | ~584K–587K |
| ViT-H embeddings (full re-embed) | ~553K / 1,358 species |
| Active production patterns | ~454K / ~1,158 species |

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
