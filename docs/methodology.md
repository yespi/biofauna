# Methodology — BioFauna

Production identifier: **frozen BioCLIP-2.5 ViT-H/14** (1024-d) → **k-NN k=15**, tempered votes **T=0.05**, prototype boost, 65% centre-crop fused into the query, optional GPS prior, logistic calibration, taxonomic abstention.

Details and the kept/rejected ledger: [paper](../paper/01_biofauna.md) and [EXPERIMENTS.md](EXPERIMENTS.md).

## Validation

Only **observation-stratified** harvests. Photo-level splits inflate accuracy ~10 pp.

**Current (2026-09-14):** 85.78% / 89.15% / 91.41% species/genus/family, n=19,087.

**August freeze (same protocol, smaller mix):** 75.97% TTA-era → 79.10% after densification on n=12,788. Do not quote those as the live system.

AutoID (FotoFauna): last published operating point **p≥0.80 → ~95.3% precision, ~57.4% coverage** (August split). The on-disk calibrator was refit 14 Sep.

## References

Stevens et al. 2024 (BioCLIP, CVPR). Ballesteros 2007; Cervera et al. 2004; Salvador et al. 2022 (checklists).

## Live check and open-set caveat (2026-09-21)

The panel/OOS metric is a **closed-set** evaluation: held-out observations of species that exist in the catalog, correlated by observer and site, from research-grade records. It overstates what happens on incoming photos (species outside the catalog, phone-quality images, unidentified observations). Operating KPI going forward: a **recent-observation sample** (research-grade, last ~25 days, split by time and observer, same pipeline as AutoID: crop + BioFauna), reported next to the panel. Promotions report Δ, p **and** the per-species balance (improved / worsened / unchanged, touched species first). Accuracy per species shown in dashboards is refreshed by a daily re-score against the serving index; a promotion always re-scores.

