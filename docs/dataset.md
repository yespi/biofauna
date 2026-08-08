## Dataset Information

### Sources

The training dataset consists of **525,000+ photographs** of Mediterranean marine fauna from:

| Source | Images | % |
|--------|--------|---|
| [Minka](https://minka-sdg.org) | 289,660 | 56% |
| [iNaturalist](https://inaturalist.org) | 226,455 | 43% |
| Other (field guides, personal) | 4,479 | 1% |

### Obtaining the Dataset

The dataset cannot be redistributed directly due to image licensing, but can be reproduced:

1. **From iNaturalist**: Use the [iNaturalist API](https://api.inaturalist.org/v1/docs/) with taxon IDs from `docs/species_table.md`
2. **From Minka**: Use the [Minka API](https://api.minka-sdg.org/) with Minka taxon IDs
3. **From GBIF**: Query [GBIF](https://gbif.org) by scientific name with multimedia filter

### Directory Structure

```
data/
├── images/
│   ├── actinia_striata/
│   │   ├── inat_12345_0.jpg
│   │   └── minka_67890_1.jpg
│   ├── elysia_timida/
│   │   └── ...
│   └── ... (1,369 species)
├── patterns/
│   ├── actinia_striata/
│   │   ├── prototype.npy     # Species centroid embedding
│   │   └── embeddings.npy    # All individual embeddings
│   └── ...
├── calibration.json          # Model calibration data
├── target_species.json       # Complete species catalog
└── geo_priors.json           # Geographic occurrence data
```

### Species Catalog

The model covers **1,369 Mediterranean marine species** across:
- Mollusca (1,014)
- Plantae/algae (466)
- Actinopterygii/fish (312)
- Cnidaria (170)
- Crustacea (167)
- Porifera/sponges (102)
- Echinodermata (54)
- And more...

Full list: `docs/species_table.md`
