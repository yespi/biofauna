# BioFauna — Project Status (public)

> **2026-08-27** · Full-corpus OOS baseline: **75.97% species / 81.29% genus / 84.90% family** (n=12,788, deduplicated, old crop90 TTA); **76.84% single-photo with ROI multi-crop fusion** (replaces crop90 TTA, +1.63pp vs. its own no-TTA baseline) and **76.76% species with multi-photo late fusion** — both now live in production simultaneously (per-photo ROI fusion feeds the cross-photo late fusion); the *combined* full-corpus accuracy of both stacked has not yet been independently re-measured on n=12,788, see note below  
> **Archive-gap remediation closed** (Aug 21-23); **calibration-set data leakage found & fixed** (Aug 25-26); **TTA integrated + calibration re-fit, SupCon re-ranker attempt killed by design** (Aug 26-27); **multi-photo observation fusion shipped to production, taxonomic consensus re-ranking closed as negative, ROI multi-crop fusion shipped to production replacing crop90 TTA** (Aug 27) — see notes below

## Production stack

| Piece | Setting |
|-------|---------|
| Encoder | BioCLIP-2.5 ViT-H (1024-dim), **frozen** |
| Retrieval | k-NN **k=15** + logistic calibration, **ROI multi-crop fusion** (query + strict 65% center crop, 50/50 weighted average, re-normalized — replaces the prior 90%-crop TTA, see §4.9) |
| Storage | Active SSD gallery + **HDD archive** (full-resolution backup per species), now unified in re-embedding |
| AutoID | p≥0.80 → ~95.3% precision at ~57.4% coverage (lowered from p≥0.90/95.5%/30.2% on 2026-08-27 to raise automation volume; see AutoID note below) |
| Fallback | Hierarchical species→genus→family + iNaturalist CV cross-check |

## Published baseline vs current

| Cohort | Species accuracy | Notes |
|--------|------------------|-------|
| **Paper baseline** (Aug 2026, ~810 spp cohort) | **71.7%** | Original observation-stratified `harvest_calib` |
| **Full corpus, deduplicated** (Aug 25-26 2026, n=12,788) | **75.8%** | Post archive-gap fix + calibration-set dedup; genus 81.1%, family 84.5% |
| **+ TTA, current** (Aug 27 2026, n=12,788) | **75.97%** | Test-time augmentation added, calibration re-fit end-to-end; genus 81.29%, family 84.90% |
| **+ Multi-photo late fusion** (Aug 27 2026, n=12,788) | **76.76%** | Zero-training inference-time fusion for observations with 2+ photos (25.1% of corpus); 84.70% on that subset alone. See paper §4.7. Measured on top of the crop90 TTA baseline (75.97%), not the ROI fusion below |
| **ROI multi-crop fusion, current** (Aug 27 2026, n=12,788, single photo) | **76.84%** | Global (100%) + strict center crop (65%) embeddings, 50/50 weighted, replaces crop90 TTA in production; +1.63pp vs. its own no-TTA baseline (75.21%), cleanly recovers 130 of 1,038 cross-taxonomic-group errors. See paper §4.9 |

Do not compare these numbers without noting corpus size and embedding coverage. The multi-photo and ROI-fusion rows were each measured against their **own** baseline in isolation — both run together in production now, but the combined full-corpus number has not yet been separately re-measured.

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
| **Test-time augmentation** (query + 90% center crop, averaged) | **+0.21 to +0.75pp** species depending on eval protocol (both positive, see paper §"Post-publication development") | ✅ **only single-photo technique to beat frozen k-NN baseline** — live in production |
| **Multi-photo late fusion** (mean k-NN score across an observation's 2+ photos, geo prior applied once post-fusion) | **+0.79pp** species full corpus (75.97%→76.76%), **+3.15pp** on the 25.1% multi-photo subset (81.55%→84.70%); early (embedding-mean) fusion also positive but weaker (+0.65pp / +2.59pp) | ✅ zero-training, zero extra GPU compute beyond the extra photos themselves — live in production, capped at 5 photos/request, N=1 reduces exactly to prior behavior (paper §4.7) |
| Prototype/embedding outlier filtering (median-cosine, thr 0.5/0.7) | **−0.21pp / −1.45pp** species | ❌ filtered legitimate intra-species variation, not noise |
| Widened same-genus abstention margin (0.06→0.10+) for cryptic pairs | 9:1 cost/benefit (152 correct predictions lost per 17 errors fixed) | ❌ |
| Non-oracle "prefer epibiont" re-ranking rule for parasite/host pairs | **−0.23pp** species, **−0.26pp** genus | ❌ |
| SupCon contrastive re-ranker, scoped to 20 heaviest cryptic pairs, frozen backbone | Per-pair validation loss diverged from epoch 1 in **two independent hyperparameter regimes** — memorization, no generalization; **kill-switch invoked before touching the eval set** | ❌ third independent architecture to fail on this data regime |

Full log: [EXPERIMENTS.md](EXPERIMENTS.md).

## AutoID confidence/volume tuning (2026-08-27)

Production auto-publication volume was running at ~5 identifications/hour against a configured
cap of 20/hour. Two independent causes, both fixed: (1) a hardcoded 900-second per-wave scan
timeout was cutting off the hourly Minka page-scan well before the hourly quota could be reached
— raised to 1800s; (2) the confidence threshold (p≥0.90, 95.5% precision at 30.2% coverage) was
conservative relative to what the freshly re-fit calibration curve supports — lowered to p≥0.80
(≈95.3% precision at ≈57.4% coverage per the re-fit calibration curve, a ~33% relative increase
in the fraction of candidates that clear the bar for an estimated ~1.5pp precision cost). A
further lever (broadening the Minka observation pool from "zero identifications" to "pending
confirmation, may have partial IDs") is documented but not yet exercised, held in reserve for if
the narrower pool runs dry.

## Development roadmap (public summary)

1. ~~Consolidate SSD + archive per species~~ ✅ done (Aug 21-23)
2. ~~Rebuild FAISS index + recalibrate~~ ✅ done
3. ~~Test-time augmentation~~ ✅ done (Aug 26-27), only single-photo technique so far to beat the frozen-backbone k-NN baseline
4. ~~Multi-photo observation fusion~~ ✅ done (Aug 27), zero-training inference-time ensemble over an observation's existing extra photos — see paper §4.7
5. Explore encoder-level improvements beyond parameter-efficient fine-tuning and beyond frozen-backbone contrastive heads (closed as ineffective at this scale across three independent architectures — see EXPERIMENTS.md)
6. Resume targeted downloads only where **total** photos &lt; 1000/spp, or where a specific species is confirmed photo-starved relative to its confusion rivals (not just Tier assignment — see EXPERIMENTS.md, three species closed this way on 2026-08-27)

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
