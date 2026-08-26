# BioFauna — Experiments (condensed)

> Public summary of ablations through **2026-08-25**.  
> Trusted metric: observation-stratified `harvest_calib` species top-1.

## Kept in production

| Change | Effect |
|--------|--------|
| BioCLIP ViT-L → **ViT-H** re-embedding | **+6.8pp** (63.9% → 70.6%) |
| k-NN **k=25 → k=15** | **+1.1pp** (70.6% → 71.7%) |
| Full SSD+HDD-archive re-embed, catalog expanded to ~4,700 target spp | **+3.7pp** vs. original cohort (71.7% → **75.8%** clean / n=12,788 dedup, was reported as 75.4%/n=22,332 before a calibration-set leakage fix — see below) — closed the archive-gap regression |
| Hierarchical fallback (`MIN_RISK`, family margin) | ~**+2pp weighted** (not species top-1) |
| Logistic calibration + AutoID p≥0.90 | **95.5%** precision @ **30.2%** coverage |

## Closed / negative (do not repeat as-is)

| Experiment | Out-of-sample result |
|------------|----------------------|
| QLoRA ViT-L with trainable proj head | 1.7% (catastrophic) |
| Triplet loss on ViT-H (8 variants) | Degrades (−0.7 to −7pp) |
| ArcFace on frozen ViT-H | Tie with k-NN (~71.4% vs 71.6%) |
| LoRA+ArcFace after eval-bug fix (100 spp) | **+0.0pp** |
| Near-duplicate burst dedup | **70.1%** (−1.6pp) — bursts help k-NN |
| Expert-guide crops (weighted) | **70.8%** (−0.9pp) |
| **QLoRA on BioCLIP-2 ViT-L, 2026-08-24** | Base-model mismatch: ViT-L (768-dim) vs. production ViT-H (1024-dim) — incompatible architecture, discarded before evaluation |
| **LoRA on ViT-H backbone, full catalog scale, 2026-08-24/25** | Trained ArcFace head + last 4 backbone blocks on 1,358 of 2,934 species. **−31.2pp** species on the full n=22,332 eval (75.4% → 44.2%; the 75.4% figure was later found to include ~43% leaked calibration samples, see below — a ~1pp shift on the clean subset does not change this verdict). Overfit to the fine-tuned species subset, distorted the shared embedding space for the rest. No cutover. |
| **Linear projection head ("head sidecar") on frozen ViT-H, 2026-08-25** | 512-dim head trained on top of standard embeddings (backbone untouched), full 3,878-species catalog, 40 epochs. Training-time mini-set (n=800) suggested +2.6pp, but the full n=22,332 eval showed a **net regression**: species 74.8% (−0.6pp), genus 80.7% (−1.1pp), family 84.6% (−1.1pp). No cutover — even a lower-risk, backbone-frozen fine-tune did not beat plain k-NN retrieval. |

## Evaluation hygiene

- Photo-level 80/20 splits inflate accuracy (~10pp) via immersion bursts.
- An off-by-one `REF_LAB` filter produced a false LoRA “+3.4pp”; corrected eval shows null gain.
- Long GPU jobs must use `systemd-run --user` or `nohup setsid ... & disown` (shell-attached jobs die when the driving session recycles).
- A self-consistent training-time mini-set (n=800) is **not predictive** of the full out-of-sample eval (n=22,332): it overstated the head-sidecar result by ~3pp in the optimistic direction, and previously understated how bad the LoRA regression would be.

## Still open

- DINOv3 embeddings extracted (~1,301 spp) — **not** yet calibrated as a production encoder
- QLoRA via **torchao/hqq** (bitsandbytes incompatible with our open_clip ViT-H path)
- Confident learning / Macro-F1 dashboards / curator-correction log
- No parameter-efficient fine-tuning variant (LoRA, QLoRA, head sidecar) has yet beaten the frozen-backbone k-NN baseline at any catalog scale tried so far

See also: [STATUS.md](STATUS.md), [paper/01_biofauna.md](../paper/01_biofauna.md).

## Calibration-set data leakage — found & fixed (2026-08-25/26)

A grid search over the k-NN neighbor count produced a suspicious curve (monotonically improving
toward k=1), which led to finding that 42.7% of the calibration photos were duplicates already
present in the reference gallery (a broken deduplication check, pointing at an abandoned
manifest path from an earlier migration). Fixed with a direct embedding-similarity check;
validated live. **Current baseline on the clean subset (n=12,788): 75.8% species / 81.1% genus /
84.5% family** — close to the previously-reported 75.4%/81.8%/85.7% on n=22,332. Does not change
any verdict above: both closed fine-tuning experiments regress far more (−31.2pp, −0.6 to
−1.1pp) than the leakage's effect at the production k=15 setting (~1pp).
