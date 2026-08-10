# Species Coverage — BioFauna

> Updated **2026-08-10**. Encoder: BioCLIP-2.5 ViT-H. Classifier: k-NN **k=15**.

| Metric | Value |
|--------|-------|
| Species folders on disk | ~3,000 (2,994 with ≥1 photo) |
| Photographs | ~584K–587K |
| ViT-H embeddings (full re-embed) | ~553K / **1,358** species |
| Active production patterns | ~454K / **1,158** species |
| Species accuracy (`harvest_calib`) | **71.7%** |
| Genus / family | **76.5%** / **80.4%** |
| Calibration set | 1,946 photos · 810 species |
| AutoID threshold | **p≥0.90** → 95.5% precision · 30.2% coverage |
| Hierarchical fallback | On (`MIN_RISK` / family margin) · ~+2pp weighted |

## Catalog vs live gallery

Early public drafts listed a **1,369**-species checklist with prototypes. The image corpus has since grown to ~**3,000** folders; the live identifier serves the **active patterns** subset (~1,158 species with usable embeddings).

Full tables (historical / checklist style):

- [`species_table.md`](species_table.md)
- [`paper/appendix_species.md`](../paper/appendix_species.md)

## Notes from 2026-08 experiments

- Expert-guide OCR (MiniCPM-V): 525/525 pages; crops tested as ablations → **did not** beat 71.7%.
- Burst dedup (cos>0.99) → **−1.6pp** on `harvest_calib` (near-duplicates help k-NN).
- Fine-tuning (triplet / ArcFace / LoRA) → no out-of-sample gain beyond 71.7% under the trusted protocol.
