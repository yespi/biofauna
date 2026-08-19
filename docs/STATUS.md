# BioFauna — Project Status (public)

> **2026-08-19** · Tier-1 OOS on expanded corpus: **~64%** (remediation)  
> **Critical fix in progress:** SSD + HDD archive photo consolidation (see [Archive gap](#archive-gap-august-2026))

## Production stack

| Piece | Setting |
|-------|---------|
| Encoder | BioCLIP-2.5 ViT-H (1024-dim), **frozen** |
| Retrieval | k-NN **k=15** + logistic calibration |
| Storage | Active SSD gallery + **HDD archive** (full-resolution backup per species) |
| AutoID | p≥0.90 → high precision on validated cohort |
| Fallback | Hierarchical species→genus→family + iNaturalist CV cross-check |

## Published baseline vs remediation

| Cohort | Species accuracy | Notes |
|--------|------------------|-------|
| **Paper baseline** (Aug 2026, ~1.1k spp) | **71.7%** | Observation-stratified `harvest_calib` |
| **Expanded corpus** (Aug 2026, ~3k spp) | **~64% tier-1 OOS** | Sparse / partial embeddings during data push |

Do not compare these numbers without noting corpus size and embedding coverage.

## Archive gap (August 2026)

During disk management, excess photos were moved to an HDD archive while a **~300-photo sample** stayed on SSD for fast access. Re-embedding pipelines accidentally read **SSD only**, so:

- Many species had **1000+ total photos** but the model only saw **~300 embeddings**.
- Download jobs thought species were “incomplete” and re-fetched photos already in archive.
- Accuracy dropped on rich archived species (especially heterobranchs).

**Fix (private ops):** unified photo counting (`species_photos.py`), paused redundant iNat downloads, and a GPU consolidation job that merges SSD+archive → full ViT-H re-embed → re-archive excess. Expected to recover a large share of tier-1 accuracy without changing the encoder.

## Verified techniques (`harvest_calib`)

| Technique | Result | Verdict |
|-----------|--------|---------|
| ViT-L → ViT-H | 63.9% → 70.6% | ✅ +6.8pp |
| k=25 → k=15 | 70.6% → 71.7% | ✅ +1.1pp |
| QLoRA (800 spp, cryptic pairs) | No OOS gain on partial gallery | ❌ until gallery unified |
| Triplet / ArcFace / LoRA at scale | Degrades or plateaus | ❌ |
| Hierarchical fallback | +2pp weighted | ✅ |

## Development roadmap (public summary)

1. **Consolidate** SSD + archive per species (in progress, Aug 2026)
2. Rebuild FAISS index + recalibrate
3. Measure tier-1 OOS toward **≥80%** goal
4. Resume targeted downloads only where **total** photos &lt; 1000/spp

## Evaluation rule

Only observation-stratified `harvest_calib` numbers are trusted. Photo-level splits inflate accuracy. During remediation, prefer tier-scoped OOS metrics on the full calibration corpus.

## Docs map

| Doc | Role |
|-----|------|
| [Paper](../paper/01_biofauna.md) | Scientific write-up (baseline results) |
| [BIOFAUNA_MASTER.md](BIOFAUNA_MASTER.md) | Short public master |
| [species_coverage.md](species_coverage.md) | Coverage metrics |
| [methodology.md](methodology.md) | Pipeline |
| [HISTORY.md](HISTORY.md) | YOLOFauna → BioFauna rename |

Private operational detail (HanSolo): see internal `hansolo-docs` repo — `biofauna/BIOFAUNA_ARCHIVE_SSD_GAP.md`.
