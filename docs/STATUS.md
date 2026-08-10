# BioFauna — Project Status (public)

> **2026-08-10** · Canonical accuracy: **71.7%** species (k=15, `harvest_calib`)

## Production stack

| Piece | Setting |
|-------|---------|
| Encoder | BioCLIP-2.5 ViT-H (1024-dim), **frozen** |
| Retrieval | k-NN **k=15** + logistic calibration |
| AutoID | p≥0.90 → **95.5%** precision, **30.2%** coverage |
| Fallback | Hierarchical species→genus→family + iNaturalist CV cross-check |

## Verified results (`harvest_calib`)

| Technique | Result | Verdict |
|-----------|--------|---------|
| ViT-L → ViT-H | 63.9% → 70.6% | ✅ +6.8pp |
| k=25 → k=15 | 70.6% → 71.7% | ✅ +1.1pp |
| Triplet (8 variants) | Degrades | ❌ |
| ArcFace (frozen) | ~71.4% (tie) | ❌ no gain |
| LoRA+ArcFace (100 spp, fixed eval) | +0.0pp | ❌ |
| Dedup bursts | 70.1% (−1.6pp) | ❌ |
| Expert crops | 70.8% (−0.9pp) | ❌ |
| Hierarchical fallback | +2pp weighted | ✅ |

## In progress / next

1. Confirmatory LoRA run at 1,358 spp (if still training) → then `harvest_calib` + `fit_calib`
2. Keep BioFauna service on the **71.7%** calibration
3. Decide next lever: **DINOv3** calibration, open_clip-compatible **QLoRA** (torchao/hqq), or **product/curator** telemetry

## Evaluation rule

Only observation-stratified `harvest_calib` numbers are trusted. Photo-level splits inflate accuracy by ~10pp.

## Docs map

| Doc | Role |
|-----|------|
| [Paper](../paper/01_biofauna.md) | Scientific write-up |
| [BIOFAUNA_MASTER.md](BIOFAUNA_MASTER.md) | Short public master |
| [methodology.md](methodology.md) | Pipeline |
| [species_coverage.md](species_coverage.md) | Coverage metrics |
| [dataset.md](dataset.md) / [api.md](api.md) / [self_host.md](self_host.md) | Reproduce / run |
| [EXPERIMENTS.md](EXPERIMENTS.md) | Ablation log (condensed) |
| [HANDOFF_YOLOFAUNA_RESPUESTAS_A_SONNET5.md](HANDOFF_YOLOFAUNA_RESPUESTAS_A_SONNET5.md) | Historical (2026-08-08) |
