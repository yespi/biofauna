# Species Coverage — BioFauna

> Updated **2026-08-16**. Encoder: BioCLIP-2.5 ViT-H. Classifier: k-NN **k=15**.

| Metric | Value (Aug 2026) |
|--------|------------------|
| Target species list | **~2,989** |
| Species with prototype (production) | **~2,998** |
| Photographs on reference SSD | **~584K+** (growing) |
| FAISS embeddings | **~711K** |
| Species accuracy (`harvest_calib`, **baseline cohort**) | **71.7%** |
| Tier-1 fresh accuracy (expanded corpus, remediation) | **~51%** — not comparable to 71.7% |
| Genus / family (baseline) | **76.5%** / **80.4%** |
| AutoID threshold | **p≥0.90** → 95.5% precision · 30.2% coverage |

## Catalog vs live gallery

The public paper (Aug 2026) reports results on an **observation-stratified calibration set** with ~810 species and **71.7%** top-1 accuracy. The live gallery has since expanded to ~3,000 species for Mediterranean coverage; tier-1 marine species with few reference embeddings score lower until remediation completes.

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
