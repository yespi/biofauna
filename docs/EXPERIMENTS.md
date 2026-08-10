# BioFauna — Experiments (condensed)

> Public summary of ablations through **2026-08-10**.  
> Trusted metric: observation-stratified `harvest_calib` species top-1.

## Kept in production

| Change | Effect |
|--------|--------|
| BioCLIP ViT-L → **ViT-H** re-embedding | **+6.8pp** (63.9% → 70.6%) |
| k-NN **k=25 → k=15** | **+1.1pp** (70.6% → **71.7%**) |
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

## Evaluation hygiene

- Photo-level 80/20 splits inflate accuracy (~10pp) via immersion bursts.
- An off-by-one `REF_LAB` filter produced a false LoRA “+3.4pp”; corrected eval shows null gain.
- Long GPU jobs must use `systemd-run --user` (shell/`nohup` jobs die).

## Still open

- DINOv3 embeddings extracted (~1,301 spp) — **not** yet calibrated as a production encoder
- QLoRA via **torchao/hqq** (bitsandbytes incompatible with our open_clip ViT-H path)
- Confident learning / Macro-F1 dashboards / curator-correction log
- Confirmatory LoRA@1358 spp → must still pass `harvest_calib` to matter

See also: [STATUS.md](STATUS.md), [paper/01_biofauna.md](../paper/01_biofauna.md).
