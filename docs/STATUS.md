# BioFauna — Project Status (public)

> **2026-08-26** · Full-corpus OOS baseline: **75.8% species / 81.1% genus / 84.5% family** (n=12,788, deduplicated)  
> **Archive-gap remediation closed** (Aug 21-23); **calibration-set data leakage found & fixed** (Aug 25-26) — see notes below

## Production stack

| Piece | Setting |
|-------|---------|
| Encoder | BioCLIP-2.5 ViT-H (1024-dim), **frozen** |
| Retrieval | k-NN **k=15** + logistic calibration |
| Storage | Active SSD gallery + **HDD archive** (full-resolution backup per species), now unified in re-embedding |
| AutoID | p≥0.90 → 95.5% precision at 30.2% coverage |
| Fallback | Hierarchical species→genus→family + iNaturalist CV cross-check |

## Published baseline vs current

| Cohort | Species accuracy | Notes |
|--------|------------------|-------|
| **Paper baseline** (Aug 2026, ~810 spp cohort) | **71.7%** | Original observation-stratified `harvest_calib` |
| **Current full corpus** (Aug 21-26 2026, n=12,788 deduplicated) | **75.8%** | Post archive-gap fix + calibration-set dedup; genus 81.1%, family 84.5% |

Do not compare these numbers without noting corpus size and embedding coverage.

## Archive gap (August 2026) — closed

During disk management, excess photos were moved to an HDD archive while a **~300-photo sample** stayed on SSD for fast access. Re-embedding pipelines accidentally read **SSD only**, so:

- Many species had **1000+ total photos** but the model only saw **~300 embeddings**.
- Download jobs thought species were “incomplete” and re-fetched photos already in archive.
- Accuracy dropped on rich archived species (especially heterobranchs), down to ~51-64% tier-1 OOS during remediation.

**Fix, closed 2026-08-23:** unified photo counting (`species_photos.py`), paused redundant iNat downloads, and a GPU consolidation job that merged SSD+archive → full ViT-H re-embed → re-archive excess. Result: full-corpus baseline recovered and improved past the original paper figure, to **75.8% species / 81.1% genus / 84.5% family** (n=12,788 deduplicated; see the separate data-leakage note below for why n changed from 22,332), without changing the encoder.

## Verified techniques (`harvest_calib`)

| Technique | Result | Verdict |
|-----------|--------|---------|
| ViT-L → ViT-H | 63.9% → 70.6% | ✅ +6.8pp |
| k=25 → k=15 | 70.6% → 71.7% | ✅ +1.1pp |
| Full SSD+archive re-embed (catalog expanded to ~4,700 target spp) | 71.7% → 75.4% (n=22,332) | ✅ +3.7pp vs. original cohort, closes archive gap |
| Hierarchical fallback | +2pp weighted | ✅ |
| QLoRA (ViT-L base, Aug 2026) | Base-model mismatch vs. production ViT-H | ❌ discarded before eval |
| LoRA fine-tune, full catalog scale (1,358/2,934 spp) | **−31.2pp** species on n=22,332 | ❌ severe overfit to fine-tuned subset |
| Linear head sidecar on frozen ViT-H (no backbone change) | **−0.6 to −1.1pp** across species/genus/family | ❌ net regression, no cutover |

Full log: [EXPERIMENTS.md](EXPERIMENTS.md).

## Development roadmap (public summary)

1. ~~Consolidate SSD + archive per species~~ ✅ done (Aug 21-23)
2. ~~Rebuild FAISS index + recalibrate~~ ✅ done
3. Explore encoder-level improvements beyond parameter-efficient fine-tuning (closed as ineffective at this scale — see EXPERIMENTS.md)
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

## Calibration-set data leakage (August 2026) — found & fixed

On 2026-08-25/26, while grid-searching the k-NN neighbor count, an anomalous accuracy curve
(monotonically *improving* toward k=1, which a healthy k-NN classifier should not do) led to
discovering that **42.7% (9,544/22,332) of the calibration photos were also embedded in the
reference gallery** — the same photo served as both query and answer. Root cause: the
calibration harvester's "already trained on this observation?" check pointed at a manifest path
abandoned during an earlier image-directory migration, so deduplication silently stopped
working. Fixed with a direct embedding-similarity check against the live reference catalog
instead of manifest files; validated on a real (non-synthetic) harvest run before merging.

The clean subset (n=12,788, no leakage) is now the reference calibration set. Verified with the
project's official metrics script: **75.8% species / 81.1% genus / 84.5% family** — close to the
previously-reported 75.4%/81.8%/85.7%, and the leakage does not change any closed-experiment
verdict (LoRA and head-sidecar regressions are an order of magnitude larger than the ~1pp shift
introduced by the leak at k=15; the effect was much larger only at low k, which is what first
made it visible).
