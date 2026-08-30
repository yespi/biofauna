# BioFauna — Experiments (condensed)

> Public summary of ablations through **2026-08-28**.  
> Trusted metric: observation-stratified `harvest_calib` species top-1.

## Kept in production

| Change | Effect |
|--------|--------|
| BioCLIP ViT-L → **ViT-H** re-embedding | **+6.8pp** (63.9% → 70.6%) |
| k-NN **k=25 → k=15** | **+1.1pp** (70.6% → 71.7%) |
| Full SSD+HDD-archive re-embed, catalog expanded to ~4,700 target spp | **+3.7pp** vs. original cohort (71.7% → **75.8%** clean / n=12,788 dedup, was reported as 75.4%/n=22,332 before a calibration-set leakage fix — see below) — closed the archive-gap regression |
| Hierarchical fallback (`MIN_RISK`, family margin) | ~**+2pp weighted** (not species top-1) |
| Logistic calibration + AutoID p≥0.80 | ~**95.3%** precision @ ~**57.4%** coverage (lowered from p≥0.90/95.5%/30.2% on 2026-08-27 to raise automation throughput; both operating points are valid, the platform runs at the lower threshold) |
| **Test-time augmentation** (query embedding averaged with its own 90% center crop, 2026-08-26/27) | **+0.21 to +0.75pp** species depending on eval protocol (see below) — **the only single-photo technique in this project's history to beat the frozen-backbone k-NN baseline without a data-quality fix** |
| **Multi-photo observation late fusion** (mean k-NN+prototype score across an observation's own 2+ photos, geo prior applied once post-fusion, 2026-08-27) | **+0.79pp** species full corpus (75.97%→76.76%, n=12,788), **+3.15pp** on the 25.1% of observations with 2+ photos (81.55%→84.70%, n=3,209) — see below |
| **Bucket B Fisher-diagonal re-ranking** (documented cryptic pairs only, confidence-gated margin τ=0.20, 2026-08-28) | **+0.14pp net** on top of ROI fusion, official geo-inclusive calibration harvest (76.78%→**76.92%**, n=12,788), 58 fixed / 41 broken (1.4:1) — see below |
| **Adaptive prototype boost by local k-NN margin** (query-level, not species-level; ARC_MIN=1.0/ARC_MAX=5.0, empirical p25/p75 thresholds, 2026-08-29) | **+0.16pp net** on top of ROI fusion + Bucket B (76.92%→**77.08%**, n=12,788), 37 fixed / 17 broken (2.18:1) — see below |
| **Bucket B local-subspace PCA/LDA projection** (per-pair PCA+LDA, generalizes the diagonal Fisher rerank to full covariance in a low-dim subspace, τ=0.485 via 5-fold OOF, 2026-08-29) | **+0.34-0.36pp net** on top of Bucket B + k-NN-margin (77.08%→**77.44%** official harvest, n=12,788), 109 fixed / 65 broken (1.68:1), exact McNemar p=0.0011 — see below |

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
| **Prototype/embedding outlier filtering, median-cosine, 2026-08-26** | Two thresholds tested on `embeddings.npy` before prototype averaging. Thr=0.5: **73.93%** (−0.21pp). Thr=0.7: **72.69%** (−1.45pp). Monotonic degradation — filtered legitimate intra-species variation, not noise. No sidecar, no cutover. |
| **Widened same-genus abstention margin, 2026-08-26** | Simulated raising the shared-genus abstention threshold (production 0.06) for the genera involved in same-genus confusion pairs. Even the smallest step (→0.10) cost **152** currently-correct species predictions to recover only **17** genuine errors (≈9:1 against). No change. |
| **Non-oracle "prefer epibiont" re-ranking rule, 2026-08-26/27** | Deployable rule (does not use the ground-truth label): when the current top-1 is a known host species and its parasite/epibiont partner appears anywhere in the same query's own top-k, override to the partner. Simulated over all errors: 216 activations, 64 fixed / 116 broken (genuine host photos with the partner as top-k noise) — **net −0.23pp species, −0.26pp genus**. Below the pre-registered +0.3pp bar. No change. |
| **SupCon contrastive re-ranker scoped to 20 heaviest cryptic pairs, frozen ViT-H, 2026-08-27** | Small projection head (1024→512→256) trained with Supervised Contrastive Loss, hard-negative (cryptic partner) + mandatory easy-negative (different genus) batch sampling, trained exclusively on the reference gallery (anti-leak by construction — never touched the n=12,788 eval set). **Two independent hyperparameter regimes** (LR 1e-3 unregularized; LR 5e-5 + dropout 0.3 + weight decay 1e-2) both showed per-pair validation loss diverging monotonically from **epoch 1** while training loss kept falling — textbook memorization, reproducible across very different optimizer settings. **Pre-registered kill-switch invoked before the n=12,788 evaluation was ever run**, saving that compute. Checkpoint destroyed. Third independent architecture (after full-backbone LoRA and the frozen-backbone linear head) to fail to extract a generalizable signal from this embedding space at this data regime. |
| **Asymmetric TTA (horizontal flip), 2026-08-29** | Third view added to the production ROI-fusion embedding (orig + crop65 + horizontal mirror, equal 1/3 weights), evaluated on top of the fully consolidated pipeline (ROI fusion + Bucket B rerank, 76.92% official baseline). **76.92%→76.79% (−0.13pp)**, 162 fixed / 179 broken (0.91:1 — breaks almost as much as it fixes). Unlike the 65% center crop (which removes a real noise source, background/substrate), a mirror flip adds morphological variance without removing anything: many species have asymmetric markings, structure orientation, or pose-dependent features that a horizontal flip genuinely alters, and the reference catalog already contains enough natural orientation variety that averaging with the mirror adds noise rather than reducing it. No cutover, no further weight sweep (the noise source itself is the problem, not the mixing ratio). |
| **Adaptive per-species prototype weighting (intra-species dispersion), 2026-08-29** | Per-species `arc_weight` (prototype-boost strength) scaled by intra-species reference-cluster dispersion (`1 - mean cosine to centroid`), clipped to [0.5x, 2.0x] of the base 3.0 (2,994/4,709 species with ≥5 reference embeddings modulated). Evaluated on top of the fully consolidated pipeline (76.92% baseline). **76.92%→76.83% (−0.09pp)**, 48 fixed / 60 broken (0.80:1). Smaller in magnitude than the flip TTA but still net-negative: species-level dispersion is a global property that says nothing about whether the prototype is trustworthy for *this specific query photo* — exactly the local/global mismatch the next entry addresses. No cutover. |
| **Hierarchical family-consensus constraint on k-NN (v2, with OOF protocol), 2026-08-30** | ❌ Descartado — negativo y significativo. Multiplicative penalty on k-NN neighbors outside the dominant family (γ threshold on consensus share, penalty multiplier), same conceptual family as the March 27 Bucket C closure but at family granularity with a multiplicative in-aggregation penalty rather than a post-hoc override. Retomado con protocolo OOF/K-Fold tras el incidente de la falsa alarma McNemar del 29-ago: 5-fold CV sobre el catálogo completo (n=12,788), γ/penalty elegidos por fold usando solo los otros 4. **77.44%→77.03% (−0.41pp)**, 82 fixed / 134 broken (0.61:1 — breaks nearly twice what it fixes). Exact McNemar: χ²=12.042, **p=0.0005 — significant**, unlike the attention-crop pilot's noise-level result: this is a confirmed, real regression, not an ambiguous null. 4/5 folds converged on the most conservative point in the grid (γ=0.95); the 5th chose the most aggressive (γ=0.80) — instability across folds is itself evidence the mechanism has no real optimum, just a "least-bad" point per training sample. Confirms the Bucket C precedent at finer granularity: family-level taxonomic consensus filtering still net-harms more than it helps. No cutover. |
| **Attention-guided crop for Bucket B, 2026-08-29** | ❌ Descartado — ruido aleatorio sin significancia (p=0.7663). Monkeypatch de `open_clip.ResidualAttentionBlock` a `need_weights=True` (verificado numéricamente idéntico al embedding de producción, diff=0.0) para extraer el mapa de atención CLS→parche de la última capa de ViT-H, calcular su centroide ponderado, recortar la imagen original en esa zona (50% del lado corto) y fusionar ese embedding 50/50 con el de producción. Evaluado sobre las 1.731 obs de la zona de disparo de Cubo B (mismo género + margen kNN<0,05 + par documentado): **77,08%→77,12% (+0,04pp)**, 93 arreglados / 88 rotos (ratio 1,06:1). McNemar exacto sobre el catálogo completo: χ²=0,088, **p=0,7663 — no significativo**. El centroide de atención de la última capa no apunta de forma consistente a una región morfológicamente discriminante para estos pares (o el recorte resultante no aísla señal adicional sobre lo que orig+crop65 ya captura) — el ratio ~1:1 indica movimiento casi aleatorio de predicciones, no discriminación real. Sin cutover. |
| **Taxonomic consensus re-ranking (Phylum/Class filter), 2026-08-27** | Penalize k-NN candidates whose broad taxonomic group ("iconic taxon") disagrees with the k=20-neighborhood's dominant group, targeting the 32.02% of baseline errors (984/3,073) that cross taxonomic groups. Swept 4 trigger thresholds (plurality/0%, 35%, 40%, 70%) with a proportional (non-binary) penalty. **Every configuration net-regressed** (best: −0.02pp at 70%/2 broken/0 fixed; worst: −0.12pp at plurality/47 broken/31 fixed) — the break rate outpaced the fix rate at every point on the sweep. Root cause (confirmed by manual audit of 5 raw k=20 neighbor lists): in 80% of cross-group errors the k-NN retrieval itself already votes for the wrong group (not a re-ranking artifact — no post-hoc group filter can fix it), and the mechanism cannot distinguish legitimate cross-phylum visual convergence (e.g. the sea hare *Aplysia depilans* vs. the flatworm *Thysanozoon brocchii*, 79.9% neighborhood consensus for the *wrong* phylum) from genuine noise. No cutover. See paper §4.8. |
| **Ancestral subspace inheritance for low-reference species, pre-registration diagnosis, 2026-08-30** | ❌ No viable — 0 GPU compute spent. Hypothesis: species with <5 own reference embeddings involved in a Bucket B/inter-genus confusable pair could borrow their genus/family's pooled reference embeddings to build a usable PCA/LDA discriminant subspace instead of being skipped. Measured against the 77.77% official baseline (n=12,788) **before** writing any pilot code: only 3 unique species with <5 references appear as the ground-truth label anywhere in the 12,788-observation eval set (7 observations total, 0/7 correct already), and of those 7 errors only 1 is a same-family/different-genus confusion (in principle addressable) — 6/7 are far-family confusions the mechanism was never designed to touch. An addressable population of 1 observation cannot support McNemar or OOF calibration with any real power (the same underpowered-sample failure mode as the 29-ago audit false alarm, more extreme). Same discipline as the SupCon kill-switch (27-ago): diagnosed as infeasible and closed **before** spending compute, not after a negative result. Reopen only if the eval corpus grows enough low-reference-species coverage to matter (e.g. a future archive expansion), not by re-running the same mechanism on the same data. |
| **Substrate/background neutralization ("Frente B"), 2026-08-30** | ❌ Descartado — regresión real y significativa. Hipótesis: si el 64.47% del error restante (1,833/2,843) es confusión con familia taxonómica distinta ("Cubo C"), y ese bucket ya se demostró que viene mal votado desde la propia recuperación kNN (no arreglable por rerank posterior, ver fila de arriba), limpiar la entrada visual eliminando la textura de fondo/sustrato (en vez de un recorte geométrico fijo como la Fusión ROI) podría reducir falsos positivos causados por el entorno. Mecanismo: modelo de color de fondo estimado de un anillo del 6% del borde de cada foto, máscara de primer plano por distancia z-score al percentil 35 (fijado a priori, sin búsqueda sobre accuracy), limpieza morfológica, relleno del fondo con su propio color medio; fusión 50/50 con el embedding global (peso también fijo a priori, mismo criterio que ALPHA_ROI=0.5). Evaluado sobre las 12,788 obs con el mismo arnés que la Fusión ROI original (`inference_decide.knn_scores`+`add_prototype_boost`, sin geo, `arc_weight` estático=3.0, para ablación limpia): **75.21%→74.29% (fusión, −0.92pp) vs. su propio control global**, 245 arreglados / 363 rotos (0.67:1) — McNemar exacto χ²=22.515, **p<0.0001**. Contra el baseline oficial 77.77% real: **77.77%→74.29% (−3.48pp)**, 325 arreglados / 770 rotos (0.42:1), χ²=180.033, **p<0.0001**. La variante solo-máscara es aún peor (69.57%, −5.65pp vs. control). Confirma el aviso que ya llevaba la Fusión ROI en su propio docstring: el sustrato/hábitat es señal real para especies epibiontes/incrustantes, no solo ruido, y un modelo de fondo basado únicamente en el borde es demasiado tosco para fondos no uniformes (varios sustratos, gradientes de luz, otros organismos en el margen). Sin cutover. |
| **Prior geográfico/ecológico externo (GBIF/WoRMS), 2026-08-30** | ❌ Descartado — sin señal real, no significativo. Hipótesis: penalizar candidatos kNN geográficamente implausibles (lejos de su rango documentado) podría recuperar parte del 64.47% de error de familia distinta. Metadatos revisados antes de construir nada: lat/lon cacheado localmente para el 99.8% de las obs (sin llamadas nuevas), pero **ninguna** ecorregión MEOW/profundidad/distribución WoRMS existe en este entorno — los tres scripts `download_gbif*`/`download_worms*`/`download_obis*` existentes descargan FOTOS de referencia, no metadatos de rango; construir eso requeriría ~1.600-4.700 llamadas nuevas a la API de WoRMS (una fase de recolección propia). Se usó en su lugar `geo_priors.json`, la nube de puntos por especie ya en producción (fuente Minka, 1,386/4,709 especies). Diagnóstico previo a pilotar: solo 29/1,833 errores (1.6%) cumplen un criterio estricto de implausibilidad; de los 718 recuperables en el top-5, en los 577 con datos geográficos en ambos lados la distancia NO discrimina (verdadera más cerca en 35.5% de los casos, predicha más cerca en 31.9%, mediana de diferencia ≈0.3km — ruido). Piloto real (penalización logarítmica multiplicativa, τ=300km fijo a priori, fuerza calibrada por 5-fold OOF, reutilizando `exp_hierarchical_query_cache.npz`, cero GPU): **4 de 5 folds eligieron STRENGTH=0** (ninguna penalización) como óptimo sobre sus propios datos de entrenamiento. McNemar exacto contra su propio control (ablación limpia, mismo pipeline sin rerank Cubo B/subespacio): 7 arreglados / 15 rotos (0.47:1), χ²=2.227, **p=0.1338 — no significativo**. Confirma el diagnóstico: la distancia al rango documentado no separa especies que ya compiten visualmente en el top-5, porque suelen convivir en la misma zona (por eso son confundibles). No cierra la puerta a datos WoRMS/GBIF genuinos (no probados, coste de recolección explícitamente fuera de este piloto), solo a la nube de puntos de Minka como proxy. Sin cutover. |

### Positive: ROI multi-crop fusion (2026-08-27, shipped)

Motivated directly by the taxonomic-filter post-mortem above: if the encoder's *input* is contaminated by background/substrate rather than the ranking step being fixable after the fact, clean the crop before BioCLIP-2.5 sees it. Compared three per-photo embedding strategies on n=12,788 (single-view, no TTA, isolated baseline): global (100% frame) 75.21%; strict center crop (65%, ~35% border removed) alone 75.81% (+0.60pp, but 624 correct predictions broken); **50/50 weighted fusion of global + 65% crop, re-normalized, single k-NN pass on the fused vector: 76.84% (+1.63pp)**, with a much healthier break/fix ratio (266 broken) and 130 of 1,038 cross-taxonomic-group errors cleanly recovered. **Shipped to production**, replacing the prior 90%-crop TTA — mathematically the same weighted-average-then-renormalize operation, just a stricter crop fraction (65% vs. 90%) validated against a real ablation. Runs per-photo inside the multi-photo late-fusion pipeline (§4.7); N=1 reduces exactly to the single-photo case. See paper §4.9.

### Positive: Bucket B Fisher-diagonal re-ranking (2026-08-28, shipped)

Targets the 685 baseline errors where top-1/top-2 share a genus (same-genus cryptic confusion, "Bucket B"), a different failure mode from the cross-taxonomic-group "Bucket C" errors above. Rather than a global taxonomic filter, this projects the query onto a *pair-local* diagonal Fisher/Mahalanobis discriminant direction — `w = (mean_A − mean_B) / (var_A + var_B + ε)`, computed independently for each documented cryptic pair from that pair's own reference embeddings — and flips top-1↔top-2 only when the projection favors top-2. Four iterations:

- **v1 (free trigger** — any same-genus top-1/top-2 pair with margin <0.05): 28.5% of Bucket B fixed (195/685), but **net −1.02pp** (326 broken elsewhere) — the trigger was firing on undocumented, unvalidated pairs.
- **v2 (trigger restricted to `cryptic_pairs.jsonl`-documented pairs only)**: barely moved the needle (net −0.77pp, 190 fixed/288 broken) — 91% of v1's free triggers turned out to already be documented pairs, disproving the hypothesis that undocumented pairs were the main noise source.
- **v3 (confidence-gated margin τ** — only flip when the Fisher-score gap between candidates exceeds τ, added on top of v2's trigger): swept τ ∈ [0, 0.05, 0.10, 0.15]; **first positive result at τ=0.15 (+0.05pp**, 85 fixed/78 broken) — soft, unconditional inversion was the real problem, not the trigger.
- **v4 (fine sweep τ ∈ [0.15, 0.18, 0.20, 0.25, 0.30]**, reusing v3's cached continuous Fisher scores — zero additional GPU cost, no geo prior applied in this ablation harness): unimodal curve peaking at **τ=0.20: +0.13pp net** (76.84%→**76.97%**, n=12,788), 58 fixed / 41 broken (1.4:1 ratio), 115 total inversions, 8.5% of Bucket B fixed.

**Official, geo-inclusive calibration harvest confirms it:** re-scoring all 12,788 photos with the exact production `decide()` path (k-NN + prototype boost + geo prior — the same code `harvest_calib.py` uses to fit `calibration.json`) gives **76.78% → 76.92% (+0.14pp)**, corroborating the ablation's +0.13pp within rounding. **76.92% is the citable official figure** (same geo-inclusive convention as the 76.78% ROI-fusion baseline above it); the 76.84%/76.97% pair above is the no-geo ablation harness used during the τ sweep itself.

**Shipped to production** (`identify_service.py`): fires only when top-1/top-2 share a genus, form a documented cryptic pair, and have kNN margin <0.05; swaps top-1↔top-2 only if the Fisher-score gap exceeds τ=0.20. Discriminant directions for all 2,042 (of 2,046) documented pairs with ≥5 reference embeddings/species are precomputed at service startup by reading `embeddings.npy` directly from disk per pair — the shared `KE` catalog matrix is freed after FAISS loads (2026-08-26 memory optimization) and cannot be reused for this. Runs immediately after k-NN/prototype/geo scoring and before hierarchical abstention, so abstention logic sees the corrected top-1/top-2. Official calibration re-harvested and re-fit against the fully consolidated pipeline (ROI fusion + this re-ranker): species 76.92% / genus 81.88% / family 85.53% (n=12,788); `biofauna-id.service` has not been restarted to serve either the new code or the new calibration, pending explicit authorization.

### Positive: Adaptive prototype boost by local k-NN margin (2026-08-29, shipped)

The production prototype-boost weight (`arc_weight`, static 3.0 for every query and every species) treats a k-NN vote that's already decisive the same as one that's a coin flip. Two axes were tried for making it adaptive:

- **Species-level (rejected):** scale `arc_weight` by each species' intra-species reference-cluster dispersion (tight clusters trusted more) — closed negative above (−0.09pp). A global species property says nothing about whether the prototype is trustworthy for *this specific query photo*.
- **Query-level (this entry):** scale `arc_weight` by the **k-NN margin measured before any boost is applied** — `Δ = maxsim(top1) − maxsim(top2)` on the raw k-NN scores. Narrow margin (k-NN genuinely undecided) → raise `arc_weight` toward a ceiling to let the prototype break the tie; wide margin (k-NN already confident) → drop it toward a floor to avoid interference. Linear interpolation between the two.

**Calibration pitfall caught before shipping.** A first pass used guessed thresholds (0.05/0.15, borrowed from the Bucket B margin scale) and measured a statistically negligible **+0.02pp** (34 fixed / 31 broken, 1.10:1 — indistinguishable from noise). Checking the *actual* margin distribution explained why: 38% of queries are a degenerate case (all k=15 neighbors belong to a single species — margin defined as exactly 1.0, not a comparable continuous value), and among the remaining 62% the median real margin (0.039) was already below the guessed 0.05 "low" threshold — more than half the catalog was getting near-maximum boost regardless of true ambiguity, diluting any signal. Re-calibrating against the empirical p25/p75 of the *non-degenerate* margin distribution (0.00296 / 0.033315) — computed for free from the already-harvested first pass, no extra GPU cost — and widening the ceiling from 3.0/1.5 to **ARC_MIN=1.0 / ARC_MAX=5.0** (per user direction) gave a much sharper result:

| Calibration | Species ACC (n=12,788) | Δ vs. consolidated | Fixed / broken | Ratio |
|---|---|---|---|---|
| Consolidated (ROI fusion + Bucket B) | 76.92% | — | — | — |
| Margin-adaptive, guessed thresholds (0.05/0.15, ARC 1.5–5.0) | 76.95% | +0.02pp | 34 / 31 | 1.10:1 |
| **Margin-adaptive, empirical p25/p75 (0.00296/0.033315, ARC 1.0–5.0)** | **77.08%** | **+0.16pp** | **37 / 17** | **2.18:1** |

The calibrated version beats even Bucket B's own fix/break ratio (1.4:1). Closed as the definitive configuration without a further ARC_MAX fine-sweep (4.0–7.0 in 0.5 steps was designed but not run — diminishing-returns judgment call, not a negative result).

**Shipped to production** (`identify_service.py`): the pure k-NN scores/max-similarities (`scores`/`maxsim`, already fused across multi-photo late fusion) are read *before* the existing prototype-boost block to compute the local margin, replacing the static `BIOFAUNA_ARC_WEIGHT` env default with a per-query dynamic value (env-overridable ceiling/floor/thresholds, `BIOFAUNA_KNNMARGIN_ADAPTIVE=1` by default). Falls back to the old static behavior if disabled. Official calibration re-harvested and re-fit against the fully consolidated pipeline (ROI fusion + Bucket B + this mechanism): species 77.08% / genus 82.08% / family 85.65% (n=12,788). **`biofauna-id.service` restarted with explicit user authorization (2026-08-29)** — this is now the live-served baseline.

### Positive: Bucket B local-subspace PCA/LDA projection (2026-08-29, shipped)

The diagonal Fisher rerank already in production (see above) assumes a *diagonal* covariance — it ignores correlation between embedding dimensions. The natural generalization is a full-covariance LDA per pair, but with 1024 dimensions and as few as 5-200 reference embeddings per species, a 1024×1024 covariance matrix is hopelessly singular. Fix: reduce first with PCA fit *only on that pair's own reference embeddings* (K = min(30, n_a+n_b−2), a sample-size rule, not tuned on accuracy) into a well-conditioned low-dimensional subspace, then fit LDA inside it.

**Honesty about "no re-inference."** The design assumed a cache of query embeddings already existed on disk. Checked before writing any code: the only cached query embeddings found (`grid_k_margin_query_embeddings_20260825.npz`, `calib_val_embeddings_sidecar_20260825.npz`) were from Aug 25, over the *leaked* n=22,332 set, and predate ROI fusion/Bucket B/k-NN-margin entirely — unusable. Reference embeddings (used to fit PCA/LDA) needed zero re-inference, already on disk; query embeddings for the 1,731-obs Bucket B trigger zone required one new (but minimal, scoped, and now cached) GPU pass.

**Protocol applied:** 5-fold cross-validation on the trigger zone. PCA/LDA components are fit *only* from reference embeddings (never test data — no leakage there by construction). The one parameter chosen by looking at outcomes — a confidence threshold τ analogous to the Fisher rerank's τ=0.20 — was calibrated per fold using only the other 4 folds, then applied blind to the held-out fold. All 5 folds independently converged on the same value (τ=0.485, the 10th percentile of the observed |decision_function| distribution), a strong stability signal rather than fold-specific noise.

| Pipeline | Species ACC (n=12,788) | Δ | Fixed / broken | Ratio |
|---|---|---|---|---|
| Consolidated (ROI fusion + Bucket B + k-NN-margin) | 77.08% | — | — | — |
| **+ Local-subspace PCA/LDA, 5-fold OOF (pilot, τ=0.485)** | **77.42%** | **+0.34pp** | **109 / 65** | **1.68:1** |

Exact McNemar on the full corpus: χ²=10.626, **p=0.0011** — clearly significant, and a better ratio than the Fisher rerank's own 1.4:1.

**Independent audit caught a real (if minor) issue.** A second-party review (Cursor, `BIOFAUNA_AUDIT_SUBSPACE_20260829.md`) found that the candidate grid the τ search swept over was derived from percentiles of the *full* 1,731-obs confidence distribution — including each fold's own held-out data — a minor distributional leak (the chosen τ *value* per fold was still selected using only that fold's training data; only the *menu of candidates* leaked slightly). Re-run with a train-only grid: 109 fixed / 63 broken — the verdict is unchanged. Audit approved for production.

**Shipped to production** (`identify_service.py`), as a second stage immediately after the Fisher rerank, on the same trigger condition (same genus, documented pair, k-NN margin < 0.05), with τ=0.485 frozen (not re-calibrated live). **Precompute cost measured before deciding the loading strategy**: building all 2,042 documented pairs' subspaces eagerly took 916.8s (~15.3 min) — unacceptable for service startup, on top of the existing ~98s Fisher-diagonal precompute. Switched to **lazy, per-pair construction on first trigger** (~0.4-0.5s, thread-safe, cached in RAM thereafter) — of the 2,046 documented pairs, only 401 ever appeared active across the full 12,788-observation evaluation, so most never pay this cost at all in real traffic. Official calibration re-harvested and re-fit against the fully consolidated pipeline: species 77.44% / genus 82.08% / family 85.65% (n=12,788). **`biofauna-id.service` restarted with explicit user authorization (2026-08-29)** and verified live via `/health` and real HTTP requests (cold-cache request 1.73s, warm-cache request 0.54s for the same pair) — this is now the live-served baseline.

**Latency benchmark against the live service** (90 real HTTP requests, 30 per group): outside the trigger zone (mechanism is a no-op) averaged 683ms; inside the trigger zone on a never-before-seen pair (cold cache) averaged 1350ms (+667ms net); inside the trigger zone on an already-cached pair (warm cache) averaged 658ms (−26ms, within noise). With only 401-457 unique pairs active across 12,788 observations, the ~0.5-1s cold-start cost is paid at most once per pair over the service's entire runtime, not per request.

## Evaluation hygiene

- Photo-level 80/20 splits inflate accuracy (~10pp) via immersion bursts.
- An off-by-one `REF_LAB` filter produced a false LoRA “+3.4pp”; corrected eval shows null gain.
- Long GPU jobs must use `systemd-run --user` or `nohup setsid ... & disown` (shell-attached jobs die when the driving session recycles).
- A self-consistent training-time mini-set (n=800) is **not predictive** of the full out-of-sample eval (n=22,332): it overstated the head-sidecar result by ~3pp in the optimistic direction, and previously understated how bad the LoRA regression would be.
- **Significance testing on small held-out samples can produce false non-significance.** A Bootstrap audit on a reduced holdout (n=2,558, only 14 vs. 11 disagreements) reported p=0.312 for the Bucket B + k-NN-margin mechanisms and nearly triggered reverting both from production. An exact McNemar test computed directly against the full n=12,788 corpus gave p≈0.0022 for the combined effect (p≈0.0097 for the k-NN-margin mechanism alone, p≈0.08 for Bucket B alone — corroborated independently twice, see §"Bucket B" above). The audit's number wasn't a computation error; the holdout was simply too small (too few disagreements) to have power. **Standing rule for any dynamic-threshold mechanism from here on**: report the exact McNemar test + CI on the full evaluation set, and calibrate any threshold/percentile via K-fold CV or a held-out dev split — never fit and evaluate a threshold on the same full set.

| **Seasonal (monthly) prior, 2026-08-28** | Circular (von Mises κ=2.0) per-species monthly density, multiplying k=15+prototype-boost scores by month-of-observation density. **Proof of concept on 376 species with dense local coverage (median 414 obs/species, multi-year, from a local warehouse) was positive: 79.87%→80.80% (+0.93pp, n=1,401).** Scaling to the full 2,989-species catalog via the public API failed across three iterations: 100-most-recent-observations sampling regressed even with a minimum-density guardrail (best case −0.52pp) due to recency bias; fixing an unimplemented test-set leak (7,855/87,700 downloaded observations, 8.96%, were test-set members) made the ungated regression worse (−1.65pp), confirming the leak had been propping up the earlier number; month-balanced sampling (12 requests/species instead of 1, ~31k calls, same rate limit) closed most of the gap (−0.73pp→−0.19pp at N≥50) but never reached positive. The mechanism works; the available data density does not scale to it. No cutover. See paper §4.10. |

### Positive: Local-subspace PCA/LDA extends to inter-genus/same-family pairs (2026-08-30, shipped)

The Bucket B local-subspace mechanism (§4.13) generalizes cleanly to a different error
bucket: same-family, different-genus confusions (16.15% of remaining error, 466/2,885
cases). Same technique, same discipline (documented pairs only, 5-fold OOF, τ calibrated
from scratch rather than reusing Bucket B's 0.485 since the confidence scale is a property
of a different pair population): 577 of 12,788 observations qualify (same family +
different genus + k-NN margin < 0.05 + pair documented in `cryptic_pairs.jsonl`, 48.5% of
the 1,190 raw candidates), 145 unique pairs, PCA(K≤30)+LDA fit per pair from reference
embeddings only.

| Pipeline | Species ACC (n=12,788) | Δ | Fixed / broken | Ratio |
|---|---|---|---|---|
| Consolidated (77.44% official) | 77.44% | — | — | — |
| **+ Local-subspace PCA/LDA, inter-genus/same-family, 5-fold OOF (pilot)** | **77.69%** | **+0.25pp** | **60 / 28** | **2.14:1** |

Exact McNemar: χ²=10.920, **p=0.0008** — significant, and an even better fix/break ratio
than Bucket B's own 1.68:1. Unlike Bucket B's clean single-value convergence, the 5 OOF
folds did not agree on one τ (1.1812, 0.6151, 0.6059, 1.1825, 0.5078 — two loose clusters
rather than one stable value); the **median** (0.6151) was frozen for production rather than
the mean, so the two high outliers don't pull the threshold above where 3 of 5 folds
actually landed.

**Shipped to production** (`identify_service.py`) as a second trigger on the same
local-subspace mechanism, immediately after the existing same-genus (Bucket B) check: same
genus → τ=0.485; same family, different genus → τ=0.6151; anything else → mechanism does
not fire. `_get_local_subspace()` is reused unchanged (a per-pair PCA/LDA cache keyed by
the pair's two slugs, regardless of their taxonomic relationship). Official calibration
re-harvested against the fully consolidated pipeline (both local-subspace triggers active):
**species 77.77% / genus 82.38% / family 85.65%** (n=12,788) — the full-catalog re-harvest
outperforms the isolated pilot's 77.69%, likely because the pilot's τ was validated on a
577-observation subset while production sees the full trigger population. `biofauna-id.service`
restarted with explicit authorization (the fourth restart of this consolidation effort) and
verified live via `/health` and real HTTP requests (cold-cache 2.58s, warm-cache 0.51s for
the same pair).

## Updated error taxonomy at 77.44% (2026-08-30)

With the current baseline at 77.44% (n=12,788), 2,885 species-level errors remain (22.56%).
Breaking them down by taxonomic distance between the true species and the top-1 prediction:

| Bucket | Count | Share of remaining errors |
|---|---|---|
| Same genus (Bucket B — the local-subspace/Fisher rerank's own territory) | 639 | 22.15% |
| Same family, different genus (inter-genus, not yet attacked) | 466 | 16.15% |
| Different family (Bucket C — cross-group, closed negative twice) | 1,780 | 61.70% |

The inter-genus/same-family bucket (16.15%) is the natural next target for the local-subspace
mechanism, since it shares Bucket B's core assumption (a documented, curated pair with its own
reference embeddings makes a well-defined local discriminant possible) without extending into
the cross-family territory that has failed twice (§4.8, and the family-consensus k-NN
constraint above). A background/substrate-noise breakdown of the remaining errors was
attempted by direct visual sampling but could not be completed this pass due to a tool outage;
the qualitative finding from the original Bucket C audit (§4.8: 80% of cross-group errors
already have the wrong group winning the raw k-NN vote, not fixable by re-ranking) remains the
best available evidence for the largest (different-family) bucket.

## Still open

- DINOv3 embeddings extracted (~1,301 spp) — **not** yet calibrated as a production encoder
- QLoRA via **torchao/hqq** (bitsandbytes incompatible with our open_clip ViT-H path)
- Confident learning / Macro-F1 dashboards / curator-correction log
- No parameter-efficient or contrastive fine-tuning variant (LoRA, QLoRA, linear head sidecar, SupCon re-ranker) has yet beaten the frozen-backbone k-NN baseline at any catalog scale or scope tried so far — this line of attack is considered closed for the current data regime (see the SupCon entry above); the plausible remaining levers are more photos for genuinely photo-starved species (not just "Tier 1" — verify against confusion-rival photo counts first) or a different encoder/signal modality, not more training on top of this one
- Geographic priors for cryptic pairs: 2 of ~40 scoped species pairs show real, usable geographic separation (`Mesophyllum lichenoides`/`M. expansum`; `Lutraria magna`/`L. lutraria`) after backfilling missing coordinates for species with zero cached observations — small, not yet exploited in the abstention rule
- Independently re-measuring the *combined* full-corpus accuracy of ROI multi-crop fusion + multi-photo late fusion (both now run together in production but were each validated in isolation against their own baseline — see the ROI fusion entry below)

See also: [STATUS.md](STATUS.md), [paper/01_biofauna.md](../paper/01_biofauna.md).

## Calibration-set data leakage — found & fixed (2026-08-25/26)

A grid search over the k-NN neighbor count produced a suspicious curve (monotonically improving
toward k=1), which led to finding that 42.7% of the calibration photos were duplicates already
present in the reference gallery (a broken deduplication check, pointing at an abandoned
manifest path from an earlier migration). Fixed with a direct embedding-similarity check;
validated live. **Baseline on the clean subset (n=12,788) at the time: 75.8% species / 81.1% genus /
84.5% family** — close to the previously-reported 75.4%/81.8%/85.7% on n=22,332. Does not change
any verdict above: both closed fine-tuning experiments regress far more (−31.2pp, −0.6 to
−1.1pp) than the leakage's effect at the production k=15 setting (~1pp).

## TTA integration and calibration re-fit (2026-08-26/27)

With no further model-side gains found (see the four negative entries above, closed the same
session), test-time augmentation was integrated into production and the official calibration
artifact re-generated end-to-end against it (same clean, leak-free n=12,788 harvest). **Current
citable baseline: 75.97% species / 81.29% genus / 84.90% family** — superseding the 75.8/81.1/84.5
figure above. Separately, a genuine (not cripsis-driven) photo-count deficit was found and closed
for exactly 3 species (`Aglaophenia acacia`, `Polycitor adriaticus`, `Dagetichthys lusitanicus`;
+145 photos, +49 reference embeddings after quality filtering), and the FAISS production index was
rebuilt to include them (762,033 → 762,082 embeddings).

## Multi-photo observation fusion (2026-08-27)

25.1% of the n=12,788 calibration set's observations (3,209 of 12,788) carry 2+ photos of the same
individual (mean 1.45 photos/observation overall, up to 20 on one observation); every result above
uses only the first photo per observation. Two zero-training, inference-time fusion strategies were
compared against that single-photo baseline: **late fusion** (run the per-photo k-NN+prototype
pipeline independently on each photo, average the resulting per-species score vectors, apply the
geographic prior once on the averaged vector) and **early fusion** (average the N L2-normalized,
TTA-augmented query embeddings before a single k-NN search). Both beat the baseline; late fusion
won on both the full corpus (75.97%→**76.76%**, +0.79pp) and the multi-photo subset alone
(81.55%→**84.70%**, +3.15pp), against early fusion's 76.62%/84.14%. Harvest of the 3,209
observations' extra photos hit two short-lived transient network outages (traced to a 10-minute DNS
watchdog timer bouncing the host's network interface, unrelated to Minka) — retried with a 2s
backoff and a memory-capped (`systemd-run --scope -p MemoryMax=12G`, to protect the concurrently
running production service) re-run, reaching 3,209/3,209 with zero errors. Deployed to the
production `/identify` endpoint (optional `files` list, capped at 5 photos/request; N=1 reduces
algebraically to the pre-existing single-photo computation). See paper §4.7.
