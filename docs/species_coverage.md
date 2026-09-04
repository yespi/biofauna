# Species Coverage — BioFauna

> Updated **2026-09-04**. Encoder: BioCLIP-2.5 ViT-H. Classifier: k-NN **k=15**.

| Metric | Value (Sep 2026) |
|--------|------------------|
| Target species list | **4,702** in the live FAISS gallery |
| FAISS embeddings (production, aligned) | **785,897** |
| Species accuracy (`calib_raw.jsonl`, n=12,788) | **79.10%** (10,115; Tier-1 **74.88%**) |
| 1-Sep densification harvest (Δ19 photos) | 79.25% / Tier-1 75.10% |
| AutoID threshold | **p≥0.80** → ~95.3% precision · ~57.4% coverage |
| Staging 807k (not serving) | 807,267 embeddings — do not cut over |
| night85 overlay (not serving) | McNemar **282/80 +1.58 pp** vs replica scorer — do not cut over |

## Catalog vs live gallery

The public paper (Aug 2026) reports its original headline results on an **observation-stratified calibration set** with ~810 species and **71.7%** top-1 accuracy. The live gallery has since expanded to a ~4,700-species target catalog for Mediterranean (and adjacent) coverage. A photo-archival bug (SSD-only re-embedding, missing HDD-archived photos) temporarily lowered tier-1 accuracy during that expansion; a full catalog re-embed (SSD+archive unified, Aug 21-23 2026) closed that gap and raised the full-corpus baseline to 75.4% species / 81.8% genus / 85.7% family on n=22,332. That figure was later found (Aug 25-26 2026) to include ~43% leaked calibration samples (duplicates of the reference gallery, caused by a broken deduplication check); fixed, and re-measured on the clean n=12,788 subset at **75.8%** species / **81.1%** genus / **84.5%** family — see the paper's [Post-publication development](../paper/01_biofauna.md#post-publication-development-august-2026) section.

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
