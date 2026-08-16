# BioFauna — Project Status (public)

> **2026-08-16** · Canonical **published** accuracy: **71.7%** species (k=15, `harvest_calib`, Aug 2026)  
> **In progress:** tier-1 remediation on an expanded corpus (~3,000 species). See [Development note](#development-august-2026) below.

## Production stack

| Piece | Setting |
|-------|---------|
| Encoder | BioCLIP-2.5 ViT-H (1024-dim), **frozen** |
| Retrieval | k-NN **k=15** + logistic calibration |
| AutoID | p≥0.90 → **95.5%** precision, **30.2%** coverage |
| Fallback | Hierarchical species→genus→family + iNaturalist CV cross-check |

## Verified results (`harvest_calib`, observation-stratified)

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

## Development (August 2026)

The production gallery grew from ~1,100 to **~3,000 species** during an intensive data-collection phase (iNaturalist global downloads, field guides, Sea Slug Forum, GROC, OpenAlex OA guides). On the **expanded** corpus, tier-1 (non-heterobranch marine) fresh accuracy is **~51%** while reference embeddings are still sparse for many species — expected until more photos are embedded and recalibrated.

Current work (private ops docs on HanSolo):

- Global iNaturalist downloads (no Mediterranean bbox limit)
- Taxonomic synonym resolution (WoRMS / WikiSpecies)
- Open-access field-guide PDF extraction (`fetch_oa_guides_hard.py`)
- **Species freeze** — no new species/patterns until remediation closes (disk + calibration stability)
- Batch re-embed → FAISS → `harvest_calib` → `fit_calib` when download impact is sufficient

**Do not** compare the ~51% remediation number to the **71.7%** paper baseline without noting different corpus size and calibration cohort.

## Evaluation rule

Only observation-stratified `harvest_calib` numbers are trusted. Photo-level splits inflate accuracy by ~10pp. Use `biofauna_kpi.py` on the private deployment for fresh tier metrics during remediation.

## Docs map

| Doc | Role |
|-----|------|
| [Paper](../paper/01_biofauna.md) | Scientific write-up (baseline results) |
| [BIOFAUNA_MASTER.md](BIOFAUNA_MASTER.md) | Short public master |
| [species_coverage.md](species_coverage.md) | Coverage metrics |
| [methodology.md](methodology.md) | Pipeline |
| [dataset.md](dataset.md) / [api.md](api.md) / [self_host.md](self_host.md) | Reproduce / run |
| [EXPERIMENTS.md](EXPERIMENTS.md) | Ablation log (condensed) |
| [HISTORY.md](HISTORY.md) | Origins as YOLOFauna → BioFauna |
