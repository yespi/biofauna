# Species Coverage — BioFauna

> Updated **2026-08-25**. Encoder: BioCLIP-2.5 ViT-H. Classifier: k-NN **k=15**.

| Metric | Value (Aug 2026) |
|--------|------------------|
| Target species list | **~4,709** |
| Species with ≥2 embedded photos (production) | **~2,934** |
| FAISS embeddings (post full re-embed) | **~763K** |
| Species accuracy (`harvest_calib`, full corpus, n=22,332) | **75.4%** |
| Genus / family (same corpus) | **81.8%** / **85.7%** |
| AutoID threshold | **p≥0.90** → 95.5% precision · 30.2% coverage |

## Catalog vs live gallery

The public paper (Aug 2026) reports its original headline results on an **observation-stratified calibration set** with ~810 species and **71.7%** top-1 accuracy. The live gallery has since expanded to a ~4,700-species target catalog for Mediterranean (and adjacent) coverage. A photo-archival bug (SSD-only re-embedding, missing HDD-archived photos) temporarily lowered tier-1 accuracy during that expansion; a full catalog re-embed (SSD+archive unified, Aug 21–23 2026) closed that gap and raised the full-corpus baseline to **75.4%** species / **81.8%** genus / **85.7%** family on n=22,332 — see the paper's [Post-publication development](../paper/01_biofauna.md#post-publication-development-august-2026) section.

Full tables (historical / checklist style):

- [`species_table.md`](species_table.md)
- [`paper/appendix_species.md`](../paper/appendix_species.md)

## Data sources (2026)

| Source | Role |
|--------|------|
| iNaturalist + Minka | Primary reference photos |
| GROC / Sea Slug Forum | Opisthobranch guides |
| OpenAlex OA PDFs | Automated genus-level field guides (`guide_oa_*.jpg`) |
| Salvador / Pontes scans | Expert nudibranch guides (OCR tested; VLM re-rank closed) |

## Notes from experiments

- Expert-guide OCR (MiniCPM-V): 525/525 pages; crops tested as ablations → **did not** beat 71.7%.
- Burst dedup (cos>0.99) → **−1.6pp** on `harvest_calib`.
- Fine-tuning (triplet / ArcFace / LoRA) → no out-of-sample gain beyond 71.7%.
- **Species freeze** (Aug 2026): halt new pattern creation while tier-1 remediation runs.
