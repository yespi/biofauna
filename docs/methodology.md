# Methodology — BioFauna

Production identifier: **frozen BioCLIP-2.5 ViT-H/14** (1024-d) → **k-NN k=15**, tempered votes **T=0.05** with at most 3 votes per species, prototype boost, 65% centre-crop fused into the query, optional GPS prior, logistic calibration, taxonomic abstention.

Details and the kept/rejected ledger: [paper](../paper/01_biofauna.md) and [EXPERIMENTS.md](EXPERIMENTS.md).

## Validation

Only **observation-stratified** harvests. Photo-level splits inflate accuracy ~10 pp.

**Current (2026-09-23, leak-free):** 88.11% / 90.55% / 92.46% species/genus/family, n=12,373 (2,091 species).

**Leak gate (mandatory for every evaluation photo):** embed the candidate **globally** (no TTA, no ROI fusion — the same way gallery photos are embedded) and drop it if its cosine with any gallery photo of its species is **≥0.98**. Comparing a TTA/fusion embedding instead lets identical photos through (they score ~0.97–0.99), which is how 50.8% of the evaluation set became gallery copies before 2026-09-23. After any gallery growth, re-run `scripts/leak_audit_calib.py` and `scripts/purge_leaked_eval.py` (leaked rows are moved to a side file, never deleted).

**Species with no evaluation:** harvest held-out observations not used in the gallery (Minka, iNaturalist, GBIF), then multi-source searches for rare taxa (Wikimedia Commons, museum media via iDigBio/GBIF, EOL, Wikipedia, Zenodo/Biodiversity Literature Repository figures, Openverse, Observation.org, WoRMS synonyms), each photo through the leak gate and a genus-plausibility check. Leave-one-out on the gallery is reported separately and never mixed into the headline.

**August freeze (same protocol, smaller mix):** 75.97% TTA-era → 79.10% after densification on n=12,788. Do not quote those as the live system.

AutoID (FotoFauna): calibrator refit 2026-09-23 on leak-free rows; **p≥0.80 → 97.0% precision, 80.6% coverage** on a species-disjoint test split (closed-set; see the live-check caveat below).

## References

Stevens et al. 2024 (BioCLIP, CVPR). Ballesteros 2007; Cervera et al. 2004; Salvador et al. 2022 (checklists).

## Live check and open-set caveat (2026-09-21)

The panel/OOS metric is a **closed-set** evaluation: held-out observations of species that exist in the catalog, correlated by observer and site, from research-grade records. It overstates what happens on incoming photos (species outside the catalog, phone-quality images, unidentified observations). Operating KPI going forward: a **recent-observation sample** (research-grade, last ~25 days, split by time and observer, same pipeline as AutoID: crop + BioFauna), reported next to the panel. Promotions report Δ, p **and** the per-species balance (improved / worsened / unchanged, touched species first). Accuracy per species shown in dashboards is refreshed by a daily re-score against the serving index; a promotion always re-scores.

