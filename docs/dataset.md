## Dataset — what to download vs what we ship

### Live scale (2026-09-14)

| Resource | Production | This repository |
|----------|------------|-----------------|
| Photographs | ~838k on disk | **Not released** (iNaturalist / Minka licences) |
| Per-photo ViT-H embeddings | **848,883** / **4,702** species | **Not released** (~3+ GB, derived from photos) |
| Prototype centroids | 4,702 × 1024 float32 | **`data/patterns/<slug>/prototype.npy`** |
| Checklist + taxon IDs | 2,985 taxa | **`dataset/catalog.json`** (no photographer `obs` maps) |
| Calibrator | `calibration.json` n=19,087 | `data/calibration.json` |
| Geo priors / cryptic pairs / exceptions | live JSON | `dataset/` |

### Rebuild photos

Use taxon IDs in `dataset/catalog.json`:

1. **Minka** — `minka_taxon`
2. **iNaturalist** — `inat_taxon` when present (`dataset/inat_taxon_cache.json`)
3. **GBIF** — scientific `name` / `accepted_name` + multimedia

Then embed with BioCLIP-2.5 ViT-H (`scripts/reembed_vith.py`) and write `embeddings.npy` next to each prototype. The public identifier switches from nearest-centroid to tempered k-NN when those files exist.

### Layout

```
data/patterns/<slug>/prototype.npy   # shipped
data/patterns/<slug>/embeddings.npy  # you rebuild
dataset/catalog.json                 # taxon index
dataset/taxonomic_exceptions.json
dataset/cryptic_pairs.jsonl
dataset/geo_priors.json
dataset/calibration.json
```

Expert field-guide crops were tested as an ablation and **hurt** k-NN; they are not required.
