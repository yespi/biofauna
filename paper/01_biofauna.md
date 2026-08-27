# BioFauna: Scaling BioCLIP with ViT-H for Mediterranean Marine Species Identification

**Authors**: Gustavo Zafra (Yespi)  
**Taxonomic contributors**: Xavier Salvador, Miquel Pontes, Manuel Ballesteros  
**Repository**: https://github.com/yespi/biofauna  
**Live system**: https://fotofauna.yespi.es  
**Version**: 2026-08-27

> **Naming.** This project was originally developed under the name **YOLOFauna** (2024–2026). It was renamed **BioFauna** when the production stack settled on BioCLIP retrieval rather than YOLO detection. A short provenance note is in [`docs/HISTORY.md`](../docs/HISTORY.md).

---

## Abstract

We present BioFauna, a deep learning system for automated identification of Mediterranean marine fauna from photographs. The production system uses **BioCLIP-2.5 ViT-H** (632M parameters, 1024-dimensional embeddings) as a frozen vision encoder, followed by **k-nearest neighbors** (k=15) over a database of ~450K–550K image embeddings and logistic confidence calibration. It runs on consumer hardware (NVIDIA RTX 3060 12GB) and is deployed on the FotoFauna citizen science platform.

On an out-of-sample calibration set stratified by observation ID (`harvest_calib`, 1,946 photographs, 810 species), the system achieves **71.7% top-1 species accuracy**, **76.5% genus**, and **80.4% family**. High-confidence predictions (calibrated probability ≥ 0.90) reach **95.5% precision** at **30.2% coverage**, suitable for automated publication to Minka. Scaling from BioCLIP ViT-L to ViT-H contributed **+6.8pp** species accuracy; reducing k from 25 to 15 contributed a further **+1.1pp**. Extensive fine-tuning experiments on the ViT-H backbone (triplet loss, ArcFace, LoRA+ArcFace, expert-guide crops, near-duplicate deduplication) did **not** improve the out-of-sample species metric beyond 71.7%.

We release the identification service code, calibration artifacts, and species appendix as open-source software. The BioCLIP backbone is auto-downloaded from HuggingFace. The system has been validated in production with curator-reviewed auto-publications on Minka.

**Keywords**: BioCLIP-2.5, ViT-H, k-NN, fine-grained visual classification, marine biodiversity, citizen science, taxonomic abstention, model calibration, Mediterranean Sea

---

## 1. Introduction

### 1.1 The Biodiversity Identification Bottleneck

The Mediterranean Sea is one of the world's biodiversity hotspots, hosting over 17,000 marine species — approximately 7% of global marine biodiversity in just 0.8% of ocean surface area (Coll et al., 2010; Bianchi & Morri, 2000). Accurate species identification is fundamental to biodiversity monitoring, ecological research, conservation planning, and citizen science initiatives. Yet taxonomic expertise is increasingly scarce (Hopkins & Freckleton, 2002; Kim & Byrne, 2006).

Citizen science platforms like iNaturalist (Van Horn et al., 2018) and Minka (minka-sdg.org) address this through community identification, but rare or taxonomically difficult species may wait days or never receive expert attention. In the Mediterranean, many endemics and language-specific field guides (Catalan, Spanish, Italian) intensify the bottleneck.

### 1.2 Automated Image-Based Identification

Automated image-based identification can provide instant suggestions that accelerate the pipeline. Traditional CNN approaches (iNaturalist challenges; Van Horn et al., 2018, 2021) require large per-species labeled sets and struggle with long-tailed distributions. Vision-language models open a different route: strong pretrained embeddings plus retrieval over a regional gallery.

### 1.3 Vision-Language Models for Biology

BioCLIP (Stevens et al., 2024) is trained contrastively on TreeOfLife-450M with taxonomic text structure. BioCLIP-2.5 provides a **ViT-H/14** vision encoder (632M parameters, **1024-dim** embeddings), substantially stronger than the earlier ViT-L/14 (428M, 768-dim) used in our initial experiments.

### 1.4 What Worked (and What Did Not)

Early work on this project (formerly YOLOFauna) explored QLoRA fine-tuning of ViT-L under a 12GB VRAM constraint. Those runs either failed (projection-head corruption → 1.7% accuracy) or failed to beat a frozen-backbone k-NN baseline (~63.9% species). **Re-embedding the gallery with BioCLIP-2.5 ViT-H** raised out-of-sample species accuracy to **70.6%** (+6.8pp) without fine-tuning. A subsequent k-NN grid search, validated with observation-stratified `harvest_calib`, selected **k=15** and reached **71.7%**.

Follow-up attempts to improve ViT-H further — triplet projections, ArcFace classifiers, LoRA+ArcFace, expert field-guide crops, and aggressive near-duplicate removal — did not beat 71.7% on the same protocol. We therefore present BioFauna as a **retrieval system on a strong frozen backbone**, with hierarchical abstention and calibrated AutoID thresholds, rather than as a QLoRA success story.

### 1.5 Contributions

1. **ViT-H gallery re-embedding** for Mediterranean marine fauna (~553K embeddings / 1,358 species with reliable prototypes; ~1,158 species active in production patterns).
2. **Observation-stratified evaluation** (`harvest_calib`) as the only trusted accuracy protocol, exposing inflated splits caused by photo-level train/test leakage.
3. **k-NN tuning with k=15**, improving 70.6% → **71.7%** species accuracy over k=25.
4. **Hierarchical fallback / taxonomic abstention** (species→genus→family) adding ~**+2pp weighted** utility in production.
5. **Calibrated AutoID** at p≥0.90 with **95.5% precision / 30.2% coverage**, dual-checked with iNaturalist CV when below threshold.
6. **Negative-result ablations** documenting that triplet, ArcFace, LoRA, dedup, and expert crops do not raise the ViT-H out-of-sample species ceiling under our protocol.
7. **Open deployment** on FotoFauna / Minka with curator validation.

## 2. Related Work

### 2.1 Automated Species Identification

The iNaturalist challenges (Van Horn et al., 2018, 2021) have driven significant progress in fine-grained visual classification of organisms. The iNaturalist 2021 dataset contains 2.7M images across 10,000 species, and top-performing models achieve >90% top-1 accuracy. However, these models are trained on global data and may underperform on region-specific fauna, particularly in the Mediterranean where many species have restricted ranges and distinctive morphologies.

PlantCLEF (Goëau et al., 2013) and FishBase-based systems have addressed plant and fish identification respectively, but comprehensive invertebrate identification — particularly for mollusks, which constitute 1,014 of our 1,369 species — remains challenging due to high intra-class variation and inter-class similarity.

### 2.2 Fine-Grained Visual Classification

Fine-grained visual classification (FGVC) focuses on distinguishing visually similar categories, such as bird species (Wah et al., 2011), car models (Krause et al., 2013), or aircraft types (Maji et al., 2013). Key approaches include:

- **Attention-based methods**: Directing model focus to discriminative regions (Fu et al., 2017; Zheng et al., 2017)
- **Part-based models**: Detecting and comparing object parts (Zhang et al., 2014; Huang et al., 2016)
- **Metric learning**: Learning embeddings where similar categories are close and dissimilar ones are far (Schroff et al., 2015; Hermans et al., 2017)

Our work extends FGVC to the taxonomic domain, where similarity has a natural hierarchical structure (species within a genus are inherently similar) and domain knowledge from taxonomic literature can guide the learning process.

### 2.3 Vision-Language Models

CLIP (Radford et al., 2021) demonstrated that contrastive pre-training on 400M image-text pairs produces versatile visual representations. BioCLIP (Stevens et al., 2024) applied this paradigm to biological data, training on TreeOfLife-450M with taxonomic structure. Key differences from general CLIP:

- **Taxonomic prompts**: Text encoder trained on scientific names at multiple ranks
- **Hierarchical awareness**: Model understands that "Actinia striata" is a type of "Actinia" which is a type of "Actiniidae"
- **Rare species**: BioCLIP's text encoder can represent species never seen during training via taxonomic composition

### 2.4 Parameter-Efficient Fine-Tuning

Full fine-tuning of large models is computationally prohibitive. Parameter-efficient methods have emerged as alternatives:

- **Adapter layers** (Houlsby et al., 2019): Small bottleneck layers inserted between transformer blocks
- **Prefix tuning** (Li & Liang, 2021): Learnable prefix vectors prepended to input sequences
- **LoRA** (Hu et al., 2021): Low-rank decomposition of weight updates: W = W₀ + BA, where B∈ℝ^(d_out×r), A∈ℝ^(r×d_in), r << min(d_in, d_out)
- **QLoRA** (Dettmers et al., 2023): Extends LoRA with 4-bit NormalFloat quantization of the frozen backbone, plus double quantization and paged optimizers

We initially planned to rely on QLoRA for domain adaptation under a 12 GB VRAM budget. In practice, open_clip + bitsandbytes proved fragile on our BioCLIP stack, and **frozen ViT-H retrieval outperformed** the fine-tuning attempts we could run reliably. We retain LoRA/QLoRA discussion here as related work and as documented negative results (§3.3, §4.4).

### 2.5 Taxonomic Abstention

Most classification systems report a single best-guess prediction. However, in taxonomic contexts, a coarser but correct prediction (e.g., genus when species is uncertain) is often more useful than a precise but incorrect one. This concept — known as hierarchical classification with rejection — has been explored in medical diagnosis (He et al., 2018) and document classification (Sun & Lim, 2001).

In biodiversity, the iNaturalist platform shows a "similar species" list but does not explicitly abstain to higher taxonomic levels. Our work formalizes taxonomic abstention as a decision rule based on k-NN margin and shared taxonomic ancestry.



## 3. Methods

### 3.1 Dataset

#### 3.1.1 Sources and Composition

Our image corpus contains approximately **584,000–587,000 photographs** across **~3,000 Mediterranean marine species folders** (2,994 with ≥1 photo). The identification gallery used in production embeds **~450K–554K** images for **1,158–1,358** species with reliable prototypes (species with too few images remain in the catalog but are not active gallery members).

| Source | Role |
|--------|------|
| Minka (minka-sdg.org) | Regional citizen science, Mediterranean focus |
| iNaturalist (inaturalist.org) | Research-grade and community observations |
| Expert guides (Pontes, Salvador, Ballesteros) | Cropped plates + OCR labels (MiniCPM-V); measured separately — see §4.4 |

Names are cross-referenced with **WoRMS**. Images are filtered for minimum resolution and format validity.

#### 3.1.2 Expert Literature

Species lists and morphological notes were validated against Ballesteros (2007), Cervera et al. (2004), Salvador et al. (2022), and Pontes et al. field work (GROC/OPK). OCR of scanned guides (525/525 pages with MiniCPM-V 4.5) produced labeled crops used in ablation experiments (§4.4).

### 3.2 Model Architecture (Production)

#### 3.2.1 Encoder: BioCLIP-2.5 ViT-H

Production encoder: **`hf-hub:imageomics/bioclip-2.5-vith14`**

| Property | Value |
|----------|-------|
| Architecture | ViT-H/14 |
| Parameters | ~632M |
| Embedding dim | **1024** (L2-normalized) |
| Input | 224×224 |
| Training status in BioFauna | **Frozen** (no LoRA in production) |

Inference footprint on RTX 3060: BioFauna service ≈ **4.4 GB** VRAM (encoder + FAISS/k-NN index).

#### 3.2.2 Identification: k-NN over Image Embeddings

1. Embed the query crop with ViT-H.
2. Retrieve **k=15** nearest gallery embeddings (cosine / inner product on L2-normalized vectors).
3. Aggregate votes/scores per species; optional geographic prior when GPS is present.
4. Apply hierarchical fallback when species margin is low (`MIN_RISK`, `FAMILY_MARGIN≈0.08`).
5. Map features → calibrated P(correct) via logistic regression (`fit_calib.py`).

**Why k=15.** Internal grid searches suggested small k values (≈10) maximize accuracy, but photo-level splits inflate absolute numbers. Observation-stratified `harvest_calib` selected **k=15** as the production balance between accuracy and abstention coverage (k=8 measured worse at 71.0%).

#### 3.2.3 Prototype / Gallery Layout

Per species directory under `dataset/patterns/`: `embeddings.npy` (+ metadata). Active production patterns: **~1,158 species / ~454K embeddings**. Full ViT-H re-embedding backup: **1,358 species / ~553K embeddings**.

### 3.3 Fine-Tuning Attempts (Ablations, Not Production)

We document these because earlier drafts of this paper presented QLoRA as the primary method.

| Experiment | Outcome (out-of-sample unless noted) |
|------------|--------------------------------------|
| QLoRA ViT-L + trainable proj head | **1.7%** species (catastrophic) |
| Triplet on ViT-L embeddings | Historically helped ViT-L era; **not** the ViT-H story |
| Triplet on ViT-H (8 variants) | **Degrades** −0.7 to −7pp |
| ArcFace on frozen ViT-H | **71.4%** vs k-NN **71.6%** (tie); photo splits inflate internal val |
| LoRA+ArcFace (FIXED, eval bug corrected) | **+0.0pp** on 100 spp; full 1,358 spp run confirmatory |
| Expert crops weighted in gallery | **70.8%** (−0.9pp vs 71.7%) |
| Near-duplicate dedup (cos>0.99) | **70.1%** (−1.6pp) — bursts *help* k-NN |

**Lesson:** with ViT-H, capacity is already high; frozen-backbone metric learning / light adapters did not move the trusted metric. Bitsandbytes QLoRA remains incompatible with the open_clip ViT-H path we use; torchao/hqq remains future work.

### 3.5 Taxonomic Abstention Rule

#### 3.5.1 Motivation

Standard classification systems report a single "best guess" at the species level. However, in taxonomic contexts, many species within a genus are visually indistinguishable:

- *Actinia striata* vs *Actinia mediterranea*: distinguished only by subtle tentacle banding
- *Berthella aurantiaca* vs *Berthellina edwardsii*: "cannot be differentiated by sight alone" (GROC field guide)
- Multiple *Cuthona* / *Trinchesia* species: require microscopic examination

In these cases, reporting "genus *Actinia*" is more useful than incorrectly reporting "species *Actinia striata*".

#### 3.5.2 Decision Rule

The taxonomic abstention rule is:

1. Compute margin $m = s_1 - s_2$ between top-1 and top-2 cosine similarities
2. If $m < \tau$ AND top-1 and top-2 share the same **genus** → abstain to **genus**
3. If $m < \tau$ AND top-1 and top-2 share the same **family** → abstain to **family**
4. Otherwise → report **species**

where the threshold $\tau = 0.06$ was selected to optimize weighted taxonomic accuracy on the calibration set. The threshold was validated by sweeping values from 0.02 to 0.10:

| τ | Species | Genus | Family | Weighted Accuracy |
|---|---------|-------|--------|------------------|
| 0.02 | 1,936 | 282 | 209 | 71.0% |
| 0.04 | 1,764 | 370 | 293 | 71.7% |
| **0.06** | **1,737** | **383** | **307** | **71.8%** |
| 0.08 | 1,726 | 387 | 314 | 71.9% |
| 0.10 | 1,721 | 387 | 319 | 71.9% |

The stability across this range indicates the rule is robust to threshold choice. We selected 0.06 as the most conservative option achieving near-maximum accuracy.

#### 3.5.3 Per-Level Accuracy

On the calibration set, the abstention rule achieves:

| Level | Predictions | Correct | Accuracy |
|-------|------------|---------|----------|
| Species | 1,737 (71.6%) | 1,127 | 64.9% |
| Genus | 383 (15.8%) | 341 | **89.0%** |
| Family | 307 (12.6%) | 275 | **89.6%** |

Among the 383 genus-level abstentions, 238 (62.1%) would have been correct at species level — these are cases where the model knew the right species but was appropriately conservative. The remaining 145 (37.9%) were genuine species-level errors where abstention prevented an incorrect species identification.

#### 3.5.4 Comparison with Other Rules

We evaluated four alternative abstention rules, none of which improved upon the margin-based approach:

- **Minimum risk**: Computes expected taxonomic cost for each level using full k-NN distribution → saturated risk values when votes are scattered (all ~2.7, coin-toss)
- **Vote concentration**: Abstains when ≥70% of k-NN vote mass is in the same genus/family → threshold too strict (triggers on only 2% of images)
- **Multi-level calibration**: Uses separate logistic models for species/genus/family → features don't discriminate between levels (all calibrated probabilities track together)
- **Top-3 family check**: Extends the margin rule to consider top-3 instead of top-2 → adds zero cases (no images where top-2 differs in family but top-3 matches)

### 3.5.5 Expert-Knowledge Abstention Rules

In addition to the margin-based abstention rule, we incorporate expert taxonomic knowledge from published literature and field guides. The GROC/OPK database (Ballesteros, Pontes, Salvador) contains explicit statements about species that "cannot be differentiated by sight alone" or "require laboratory analysis to distinguish."

We encode this knowledge as hard abstention rules:

**Indistinguishable pairs** (7 pairs): When the top-2 k-NN results are a known indistinguishable pair, the system abstains to the shared genus regardless of the similarity margin:

| Species A | Species B | Shared Genus | Source |
|-----------|-----------|-------------|--------|
| *Berthella aurantiaca* | *Berthellina edwardsii* | — | GROC: "no es poden diferenciar a simple vista" |
| *Discodoris stellifera* | *Geitodoris planata* | — | GROC: "no es poden diferenciar a simple vista" |
| *Actinia striata* | *Actinia mediterranea* | *Actinia* | Classic cryptic species complex |
| *Thordisa filix* | *Thordisa amanzii* | *Thordisa* | GROC: "no es pot diferenciar de manera visual" |

**Always-abstain genera** (10 genera): Species in these genera are forced to genus-level identification because they require microscopic examination, genetic analysis, or dissection for reliable species identification:

- *Doto*, *Trinchesia*, *Cuthona*, *Tenellia*, *Runcina*, *Eubranchus*, *Fjordia*, *Coryphella*, *Cuthonella*, *Rubramoena*

These rules are applied as a post-processing step after the k-NN identification, with highest priority (overriding both the margin-based abstention and the zero-shot fallback).

### 3.6 Confidence Calibration

#### 3.6.1 Why Calibration Matters

Cosine similarity scores from k-NN are **not calibrated probabilities**. A similarity of 0.938 can correspond to a correct identification 95% of the time for one species but only 30% for another. Calibration maps these raw scores to well-calibrated probability estimates that are directly interpretable as "probability the identification is correct."

#### 3.6.2 Calibration Features

We train a logistic regression calibrator on 10 features derived from the k-NN search:

| Feature | Description | Rationale |
|---------|-------------|-----------|
| `s1` | Top-1 cosine similarity | Primary signal |
| `s2` | Top-2 cosine similarity | Ambiguity indicator |
| `margin` | s1 - s2 | Confidence gap |
| `votes1` | Fraction of k-NN votes for top-1 | Consensus measure |
| `share1` | Score share of top-1 | Relative dominance |
| `lognref1` | log(1 + reference set size) | Data quantity |
| `meansim` | Mean similarity across k-NN | Overall match quality |
| `kclasses` | Number of distinct species in k-NN | Distribution spread |
| `same_genus_12` | Binary: do top-1 and top-2 share genus? | Taxonomic coherence |
| `same_family_12` | Binary: do top-1 and top-2 share family? | Higher-level coherence |

Features are standardized (z-score) before logistic regression.

#### 3.6.3 Training and Evaluation

The calibrator is trained on 2,427 held-out samples from 972 species, stratified by observation ID to prevent data leakage (photos from the same observation have correlated errors).

##### Calibration Metrics

| Level | AUC | ECE | Brier Score | NLL |
|-------|-----|-----|------------|-----|
| Species | 0.845 | 0.045 | 0.151 | 0.473 |
| Genus | 0.862 | 0.049 | 0.135 | 0.430 |
| Family | 0.866 | 0.049 | 0.123 | 0.400 |

The Expected Calibration Error (ECE) of 0.045 indicates near-perfect calibration: when the model says "80% confident", it is correct approximately 80% of the time. This is a substantial improvement over raw cosine similarity (ECE=0.271 for uncalibrated scores).

##### Reliability by Confidence Bin

| Bin | N | Declared P | Actual Accuracy |
|-----|---|-----------|----------------|
| 0.0-0.1 | 23 | 0.07 | 0.043 |
| 0.1-0.2 | 54 | 0.15 | 0.130 |
| 0.2-0.3 | 42 | 0.25 | 0.167 |
| 0.3-0.4 | 53 | 0.35 | 0.340 |
| 0.4-0.5 | 46 | 0.44 | 0.478 |
| 0.5-0.6 | 57 | 0.55 | 0.544 |
| 0.6-0.7 | 68 | 0.66 | 0.515 |
| 0.7-0.8 | 70 | 0.76 | 0.729 |
| 0.8-0.9 | 96 | 0.85 | 0.865 |
| 0.9-1.0 | 219 | 0.96 | 0.922 |

The calibration is well-behaved across the entire probability range, with the largest deviation at 0.6-0.7 (declared 66%, actual 52%).

#### 3.6.4 Operating Points

**Production (ViT-H, k=15, 2026-08-10):** AutoID uses **p≥0.90 → 95.5% precision · 30.2% coverage**.

The table below is retained from an earlier ViT-L-era calibration export (different sample sizes). Use it only as historical methodology context for logistic operating curves — **not** as current production numbers.

| p_species ≥ | Precision (legacy export) | Coverage | N |
|-------------|---------------------------|----------|---|
| 0.50 | 78.8% | 70% | 510 |
| 0.60 | 81.9% | 62% | 453 |
| 0.70 | 87.3% | 53% | 385 |
| 0.75 | 88.7% | 49% | 354 |
| 0.80 | 90.5% | 43% | 315 |
| 0.85 | 92.1% | 38% | 277 |
| 0.90 | 92.2% | 30% | 219 |
| 0.95 | 91.4% | 22% | 163 |
| 0.98 | 95.8% | 7% | 48 |


### 3.7 Evaluation Protocol

All **headline accuracy numbers** use `harvest_calib.py`: photographs held out by **observation ID**, embedded with the production encoder, identified with production k-NN, then scored against curator/community labels. Current canonical file: `dataset/calib_raw_k15.jsonl` → `fit_calib.py` → `calibration.json` (**2026-08-10**, n=1,946, 810 species).

| Rule | Rationale |
|------|-----------|
| Observation stratification | Prevents burst/near-duplicate leakage across train/test |
| Fixed protocol across ablations | Same harvest when comparing techniques |
| Do not trust photo-level 80/20 | Inflates ArcFace/k grid by ~10pp |

## 4. Results

### 4.1 Headline Accuracy (ViT-H, k=15)

| Level | Accuracy |
|-------|----------|
| **Species (top-1)** | **71.7%** |
| Genus | **76.5%** |
| Family | **80.4%** |

Progression:

| System | Species | Notes |
|--------|---------|-------|
| ViT-L + k-NN (legacy) | 63.9% | Previous production baseline |
| ViT-H + k=25 | 70.6% | After full re-embedding |
| **ViT-H + k=15** | **71.7%** | Current production setting |

### 4.2 AutoID Operating Point

At calibrated **p ≥ 0.90**: **95.5% precision**, **30.2% coverage** (production config). Below threshold, FotoFauna dual-checks with iNaturalist CV before publishing.

Calibration quality (logistic on k-NN features): ECE ≈ **0.04**, AUC ≈ **0.845** at species level (aligned with earlier ViT-L-era calibration diagnostics; recalibrated after ViT-H / k=15).

### 4.3 Hierarchical Fallback

Margin / shared-taxon abstention plus production `MIN_RISK` / `FAMILY_MARGIN` yields approximately **+2pp weighted** taxonomic utility (correct genus/family when species is unsafe). Species top-1 remains the primary reported metric (71.7%).

### 4.4 Ablation Summary (Trusted Protocol)

| Technique | Species accuracy | Verdict |
|-----------|------------------|---------|
| ViT-L → ViT-H | 63.9% → 70.6% | ✅ Keep |
| k=25 → k=15 | 70.6% → 71.7% | ✅ Keep |
| Triplet (8 variants) | Degrades | ❌ |
| ArcFace (frozen backbone) | ~71.4% (tie) | ❌ no gain |
| LoRA+ArcFace (100 spp, fixed eval) | +0.0pp | ❌ |
| Dedup bursts | 70.1% | ❌ |
| Expert crops | 70.8% | ❌ |
| Hierarchical fallback | +2pp weighted | ✅ Keep |

### 4.5 Real-World Deployment

Deployed at https://fotofauna.yespi.es via `fauna_api` → BioFauna `:8090`.

- Inference typically <1s per crop on RTX 3060.
- Auto-publication only when calibrated confidence is high; otherwise iNaturalist CV cross-check.
- Early curator review of AutoID publications showed high confirmation rates (see deployment logs / Minka reviews); continuous curator-correction logging remains an open engineering task.

### 4.6 Failure Modes


#### 4.7.1 Common Failure Modes

Examining the 36% of samples where the top-1 species is incorrect reveals several recurring patterns:

1. **Cryptic species complexes** (most common): Species within the same genus that are visually nearly identical. Examples: *Actinia* species (distinguished by subtle tentacle patterns), *Cuthona/Trinchesia* species (require microscopic examination), *Berthella* species (described as "cannot be differentiated by sight alone" in field guides).

2. **Pose and occlusion**: Organisms photographed from unusual angles, partially hidden, or in non-standard orientations. The model relies on the training distribution of "typical" poses.

3. **Background confusion**: When the organism occupies a small portion of the image, the background (rocks, algae, sand) can dominate the embedding. Our organism detection (YOLOv8) mitigates but does not eliminate this.

4. **Life stage variation**: Juveniles, breeding coloration, or damaged specimens can look very different from the typical adult form represented in training data.

5. **Data scarcity**: Species with <30 training images (4 species) have substantially lower accuracy, though the effect is confounded with these species also being rare and atypical.

#### 4.7.2 Taxonomic Patterns

Accuracy varies systematically across taxonomic groups:

| Group | Accuracy | Notes |
|-------|----------|-------|
| Large distinctive species | >80% | Easily identifiable (Pinna nobilis, Octopus vulgaris) |
| Colorful nudibranchs | 60-80% | Good but confusable within genera |
| Small mollusks | 40-60% | Often require shell microscopy |
| Algae | 50-70% | High morphological plasticity |
| Fish | 55-75% | Pose variation is challenging |


## 5. Discussion

### 5.1 Backbone Scale Beats Light Fine-Tuning (Here)

The dominant gain came from **using a stronger frozen encoder** (ViT-H) and **tuning the retrieval hyperparameter k**, not from adapter training. This does not imply BioCLIP cannot be fine-tuned in general; it means that under a 12GB GPU, open_clip constraints, and an already large in-domain gallery, **retrieval on ViT-H saturates near ~72% species** on our Mediterranean held-out set.

### 5.2 Evaluation Hygiene Matters More Than Leaderboard Chasing

Photo-level splits and buggy reference filtering produced illusory LoRA gains (+3.4pp) that vanished after correction. We recommend observation-stratified harvest as the default for gallery systems fed by citizen-science bursts.

### 5.3 Taxonomic Abstention Remains Useful

Even when species top-1 plateaus, genus/family fallbacks and expert indistinguishability rules improve **decision usefulness** for citizen science.

### 5.4 Limitations

1. Species top-1 still far from expert performance on cryptic taxa.
2. Gallery coverage is uneven; some Mediterranean endemics remain scarce on iNaturalist.
3. Expert crops and OCR labels did not help k-NN — signal may need different fusion (e.g., VLM re-rank).
4. Curator-correction telemetry is not yet a closed training loop.
5. Geographic generalization outside the Mediterranean is untested.

### 5.5 Future Work

1. Calibrate / evaluate **DINOv3** embeddings already extracted (1,301 spp).
2. Try **QLoRA alternatives** compatible with open_clip (torchao / hqq) — only with harvest_calib gates.
3. **VLM re-ranker** on top-3 critical cases.
4. Production **curator correction log** as the true online accuracy metric.
5. Continue taxonomic synonym normalization (WoRMS).

## 6. Conclusion

BioFauna identifies Mediterranean marine species by retrieving neighbors in a BioCLIP-2.5 ViT-H embedding space. With k=15 and calibrated abstention, it reaches **71.7% / 76.5% / 80.4%** species/genus/family accuracy on observation-stratified held-out photos, and supports high-precision AutoID (95.5% at p≥0.90). Scaling the backbone and tuning k — not QLoRA — produced the measured gains. We release the system as open-source software for self-hosted citizen science and research use.

## Acknowledgments

We thank Xavier Salvador (xasalva), Miquel Pontes, and Manuel Ballesteros for their taxonomic expertise and decades of field work documenting Mediterranean opisthobranchs. Their published species lists (Ballesteros 2007; Salvador et al. 2022) and the GROC/OPK databases (opistobranquis.org) provided essential validation data and morphological descriptions.

We also thank the Minka and iNaturalist communities — particularly the photographers who contributed the hundreds of thousands of images in our gallery. The WoRMS editorial board provided the taxonomic backbone that ensures nomenclatural consistency.

The BioCLIP / BioCLIP-2.5 models were developed by Samuel Stevens and colleagues and are available via HuggingFace. QLoRA was developed by Tim Dettmers and colleagues at the University of Washington. Both lines of work are released under permissive open-source licenses that made these experiments possible.

## Data Availability

The BioFauna model package (gallery patterns, calibration data, species catalog, geo priors) is available at https://github.com/yespi/biofauna. The production backbone is auto-downloaded from HuggingFace (`hf-hub:imageomics/bioclip-2.5-vith14`). Training images cannot be redistributed due to licensing but can be independently obtained from iNaturalist and Minka APIs using the taxon IDs provided in the species appendix.

## References

1. Stevens, S., Wu, J., Thompson, M.J., Campolongo, E.G., Song, C.H., Carlyn, D.E., Dong, L., Dahdul, W.M., Stewart, C., Berger-Wolf, T., Chao, W.L., & Su, Y. (2024). BioCLIP: A Vision-Language Model for the Tree of Life. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*.

2. Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient Finetuning of Quantized Language Models. *Advances in Neural Information Processing Systems (NeurIPS)*.

3. Hu, E.J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W. (2021). LoRA: Low-Rank Adaptation of Large Language Models. *International Conference on Learning Representations (ICLR)*.

4. Radford, A., Kim, J.W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark, J., Krueger, G., & Sutskever, I. (2021). Learning Transferable Visual Models From Natural Language Supervision. *International Conference on Machine Learning (ICML)*.

5. Van Horn, G., Mac Aodha, O., Song, Y., Cui, Y., Sun, C., Shepard, A., Adam, H., Perona, P., & Belongie, S. (2018). The iNaturalist Species Classification and Detection Dataset. *CVPR*.

6. Van Horn, G., Cole, E., Beery, S., Wilber, K., Belongie, S., & Mac Aodha, O. (2021). Benchmarking Representation Learning for Natural World Image Collections. *CVPR*.

7. Schroff, F., Kalenichenko, D., & Philbin, J. (2015). FaceNet: A Unified Embedding for Face Recognition and Clustering. *CVPR*.

8. Dosovitskiy, A., Beyer, L., Kolesnikov, A., Weissenborn, D., Zhai, X., Unterthiner, T., Dehghani, M., Minderer, M., Heigold, G., Gelly, S., Uszkoreit, J., & Houlsby, N. (2021). An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. *ICLR*.

9. Hermans, A., Beyer, L., & Leibe, B. (2017). In Defense of the Triplet Loss for Person Re-Identification. *arXiv:1703.07737*.

10. Coll, M., Piroddi, C., Steenbeek, J., Kaschner, K., Ben Rais Lasram, F., et al. (2010). The Biodiversity of the Mediterranean Sea: Estimates, Patterns, and Threats. *PLoS ONE*, 5(8), e11842.

11. Bianchi, C.N. & Morri, C. (2000). Marine Biodiversity of the Mediterranean Sea: Situation, Problems and Prospects for Future Research. *Marine Pollution Bulletin*, 40(5), 367-376.

12. Ballesteros, M. (2007). Lista actualizada de los opistobranquios (Mollusca: Gastropoda: Opisthobranchia) de las costas catalanas. *SPIRA*, 2(3), 163-188.

13. Cervera, J.L., Calado, G., Gavaia, C., Malaquias, M.A.E., Templado, J., Ballesteros, M., García-Gómez, J.C., & Megina, C. (2004). An annotated and updated checklist of the opisthobranchs (Mollusca: Gastropoda) from Spain and Portugal. *Boletín del Instituto Español de Oceanografía*, 20(1-4), 1-122.

14. Salvador, X., Lázaro, J., & Fuentes, M.A. (2022). Invertebrats marins de la Vall del Ridaura. Postprint. Digital CSIC.

15. Hopkins, G.W. & Freckleton, R.P. (2002). Declines in the numbers of amateur and professional taxonomists: implications for conservation. *Animal Conservation*, 5(3), 245-249.

16. Kim, K.C. & Byrne, L.B. (2006). Biodiversity loss and the taxonomic bottleneck: emerging biodiversity science. *Ecological Research*, 21, 794-810.

17. Houlsby, N., Giurgiu, A., Jastrzebski, S., Morrone, B., De Laroussilhe, Q., Gesmundo, A., Attariyan, M., & Gelly, S. (2019). Parameter-Efficient Transfer Learning for NLP. *ICML*.

18. Li, X.L. & Liang, P. (2021). Prefix-Tuning: Optimizing Continuous Prompts for Generation. *ACL*.

19. He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep Residual Learning for Image Recognition. *CVPR*.

20. Fu, J., Zheng, H., & Mei, T. (2017). Look Closer to See Better: Recurrent Attention Convolutional Neural Network for Fine-Grained Image Recognition. *CVPR*.

21. Wah, C., Branson, S., Welinder, P., Perona, P., & Belongie, S. (2011). The Caltech-UCSD Birds-200-2011 Dataset. *Technical Report CNS-TR-2011-001*.

22. Sun, A. & Lim, E.P. (2001). Hierarchical Text Classification and Evaluation. *IEEE International Conference on Data Mining*.

23. Goëau, H., Bonnet, P., Joly, A., Bakić, V., Barbe, J., Yahiaoui, I., Selmi, S., Carré, J., Barthélémy, D., Boujemaa, N., Molino, J.F., Duché, G., & Péronnet, A. (2013). Pl@ntNet Mobile App. *ACM Multimedia*.

24. Khosla, P., Teterwak, P., Wang, C., Sarna, A., Tian, Y., Isola, P., Maschinot, A., Liu, C., & Krishnan, D. (2020). Supervised Contrastive Learning. *Advances in Neural Information Processing Systems (NeurIPS)*.

---

## Post-publication development (August 2026)

After the baseline results in this paper (~71.7% species accuracy on an observation-stratified calibration set of ~810 species), the reference gallery was expanded to **~3,000 Mediterranean target species** to improve coverage for citizen-science workflows. This expansion temporarily lowered tier-1 fresh accuracy (~51%) for species with sparse reference embeddings, traced to a photo-archival bug: re-embedding pipelines were reading only a fast-access SSD subset (~300 photos/species) while the rest of each species' photos sat on an HDD archive untouched by the encoder.

**Remediation closed (2026-08-21/23).** A full catalog re-embedding consolidated SSD + HDD archive per species and re-ran the frozen BioCLIP-2.5 ViT-H encoder end-to-end. On the full observation-stratified calibration set (`harvest_calib`, **n = 22,332**, all tiers), the system now measures:

| Metric | Accuracy |
|---|---|
| Species (top-1) | **75.4%** |
| Genus | **81.8%** |
| Family | **85.7%** |

This was the production baseline reported at the time — an improvement over the original paper's 71.7% species figure, on a much larger and more diverse gallery (~2,900 species with ≥2 embedded photos out of ~4,700 target species with at least one photo, vs. ~810 in the original evaluation cohort). It superseded the interim ~51% tier-1 number reported during the archive-gap incident. **It was later corrected (see "Calibration-set data leakage" below) to 75.8%/81.1%/84.5% on a deduplicated n=12,788 — the current figure to cite.**

**Further fine-tuning ablations (August 2026), all closed without production change:**

| Attempt | Result | Verdict |
|---|---|---|
| QLoRA on BioCLIP-2 ViT-L (768-dim) | Base-model mismatch vs. production ViT-H (1024-dim); architectures incompatible | ❌ discarded before evaluation |
| LoRA on ViT-H backbone, full catalog scale (1,358 of 2,934 species fine-tuned) | **−31.2pp** species accuracy on the full n=22,332 eval (75.4% → 44.2%; ~43% of that eval set was later found to be leaked duplicates of the reference gallery — see below — but a ~1pp-scale correction does not change a 31pp regression) | ❌ severe regression — overfit to the fine-tuned subset of species, degrading the shared embedding space for the rest |
| Linear projection head ("head sidecar") on frozen ViT-H embeddings, no backbone changes, trained on the full 3,878-species catalog | Species 74.8% (−0.6pp), genus 80.7% (−1.1pp), family 84.6% (−1.1pp) vs. baseline | ❌ net regression on all three levels, despite training-time validation suggesting a small gain (+2.6pp on a self-consistent mini-set that did not hold up on the full eval) |

All three attempts reinforce §5.1: at this backbone scale and dataset regime, further parameter-efficient fine-tuning has not beaten the frozen-encoder k-NN baseline, including a lower-risk head-only variant that leaves the backbone untouched. Production remains **frozen BioCLIP-2.5 ViT-H + k-NN (k=15) + calibrated hierarchical abstention**, unchanged since the original publication.

### Calibration-set data leakage — found and fixed (2026-08-25/26)

While grid-searching the k-NN neighbor count `k` to check whether 15 was still optimal on the
expanded catalog, the resulting accuracy curve improved monotonically toward k=1 — behavior a
healthy k-NN classifier should not show, since retrieval noise usually makes very small k
*worse*, not better without limit. Investigating this surfaced a real bug: **42.7% (9,544 of
22,332) of the calibration photos were also embedded in the reference gallery** — the same photo
served as both the query being classified and (with near-perfect similarity, >0.999) its own
nearest neighbor in the answer key. Root cause: the calibration harvester's "has this
observation already been used for training?" check pointed at a manifest file path abandoned
during an earlier image-directory migration, so the check silently matched nothing for the
current pipeline and deduplication stopped working from that point on.

**Fix:** replaced the manifest-path check with a direct embedding-similarity check against the
live reference catalog (same mechanism used to detect the leak), validated on a real harvest run
before merging (a small live test correctly flagged and skipped every already-embedded candidate
it encountered). The leaked and clean rows were also split out and kept for reference.

**Corrected baseline**, verified independently with the project's official metrics script on the
clean n=12,788 subset:

| Metric | Accuracy |
|---|---|
| Species (top-1) | **75.8%** |
| Genus | **81.1%** |
| Family | **84.5%** |

This is close to the previously-reported 75.4%/81.8%/85.7% — the leakage barely inflated the
production k=15 setting, since diluting a duplicate's trivial "self-match" across 15 neighbors'
votes mostly washes it out. The effect was much larger at low k (the leak alone explained why k=1
had appeared to outperform k=15), which is what made the anomaly visible in the first place. The
k-search itself, redone on the clean data, confirmed k=15 remains within noise of the true
optimum (k=10, 0.3pp apart on n=12,788) — no production change was warranted. **None of the
closed fine-tuning verdicts above change**: both regressions (LoRA −31.2pp, head sidecar
−0.6 to −1.1pp) are an order of magnitude larger than the leak's effect at k=15.

See the public [STATUS.md](../docs/STATUS.md) and [EXPERIMENTS.md](../docs/EXPERIMENTS.md) for the current project snapshot and full experiment log.

### Contamination audit and index rebuild (2026-08-26)

A single mislabeled species (`synalpheus_tumidomanus`, 74 photos, 49 of which were crops from a
scanned field guide plate containing several unrelated species on the same page, bulk-labeled
under one taxon at download time) was found to act as a spurious vector "magnet," pulling
false-positive votes from unrelated species whose embeddings happened to fall near the
contaminated prototype. A full-catalog audit for the same `guide_oa_*`/`lit_guide_oa_*` filename
pattern found **107 affected species, 1,088 contaminated photos (0.14% of the 767,878-photo
corpus)**. All were quarantined (kept, not deleted) and every affected species was re-embedded.
Of the 20 worst-performing Tier-1 species at the time, the 8 that were contaminated all improved
(mean **+33pp**, up to +56pp); the 12 that were not contaminated (including
`perforatus_perforatus`, `schizobrachiella_sanguinea`) did not change — confirming their low
accuracy is genuine visual confusion, not a labeling artifact. The production FAISS index was
rebuilt and promoted afterward (762,033 embeddings verified against the sanitized catalog).

### Test-time augmentation (TTA): the one technique that worked (2026-08-26/27)

Every attempt to improve species accuracy via backbone/head fine-tuning had failed by this point
(§3.3, and the further ablations below). We tested one **inference-time**, zero-training change:
averaging the L2-normalized embedding of each query photo with the embedding of its own 90%
center crop, then re-normalizing, before the k-NN search (frozen backbone, no retraining).

Two independent measurements, both positive:

| Evaluation | Species Δ | Genus Δ | Family Δ |
|---|---|---|---|
| Offline validation, k=15+ArcFace boost, geo omitted (methodology-matched grid-search protocol), n=12,788 | 75.13%→**75.88%** (+0.75pp) | 76.34%→77.11% (+0.77pp) | 83.86%→84.59% (+0.73pp) |
| Official production re-harvest (`harvest_calib.py` patched with the same TTA, full scorer incl. geo prior), n=12,788 | 75.76%→**75.97%** (+0.21pp) | 81.12%→81.29% (+0.17pp) | 84.53%→84.90% (+0.37pp) |

The two figures differ because they measure different things: the first is an isolated
ablation of TTA alone against a geo-free baseline (consistent with the grid-search protocol used
elsewhere in this paper); the second is the *full* production decision path (k-NN + ArcFace-style
prototype boost + multiplicative geo prior) before vs. after adding TTA, which is the number that
actually ships. Both are positive and of the same order of magnitude. TTA is now live in
production (`/identify` and `/biofauna` endpoints): each query image is encoded together with its
90% center crop in a single 2-image GPU batch, and the two embeddings are averaged and
re-normalized before retrieval. This is, to date, the **only technique in this project's history
that improved the trusted out-of-sample species metric** without a data-quality fix.

### Further negative ablations (2026-08-26/27): prototype cleaning, margin, epibiosis, and a
### scoped contrastive-learning trial

With TTA banked, we ran a structured, hypothesis-driven search for any remaining exploitable
signal, using an error-bucket decomposition of the full n=22,332 evaluation (3,215 species-level
errors) as a map of where effort could plausibly pay off:

| Bucket | Definition | Share of error |
|---|---|---|
| A — known biological association | Parasite/epibiont ↔ host pairs (e.g. isopod family Cymothoidae → the fish it parasitizes; the anemone *Calliactis parasitica* → the hermit crab *Dardanus calidus* it rides on) | 1.74% (56/3,215) |
| B — same-genus cripsis | True and predicted species share a genus, and are visually near-identical (e.g. *Hemimycale mediterranea* ↔ *H. columella*) | 6.19% (199/3,215 forced to species; **1,247 additional cases already correctly abstain to genus/family** under the existing margin rule and are not counted as species errors) |
| C — other | Everything else — mostly cross-genus visual look-alikes with no exploitable structure | 92.07% (2,960/3,215) |

Four follow-up experiments were run against this decomposition, all closed without a production
change:

1. **Prototype/embedding outlier filtering** (median-cosine distance, thresholds 0.5 and 0.7,
   applied to `embeddings.npy` before averaging into `prototype.npy`): both thresholds
   **degraded** species accuracy monotonically (73.93%, Δ−0.21pp at 0.5; 72.69%, Δ−1.45pp at
   0.7, against the same full-pipeline evaluation used for TTA above). The photos being filtered
   out as "outliers" were legitimate intra-species variation, not noise. ❌
2. **Widened genus-abstention margin for Bucket-B genera** (raising the shared-genus abstention
   threshold from the production 0.06 in steps up to 0.25, simulated directly against the
   evaluation jsonl, no retraining): even the smallest step tested (→0.10) turned **152 currently
   correct species predictions into abstentions** to recover only **17** genuine Bucket-B errors
   — a ≈9:1 cost/benefit ratio against. ❌
3. **Non-oracle "prefer the epibiont" re-ranking rule for Bucket-A pairs** (deployable version,
   not using the ground-truth label: whenever the current top-1 prediction is a known host
   species and its known epibiont/parasite partner is anywhere in the same query's own top-k
   candidate list, override to the epibiont): simulated over all 3,215 errors, this rule fired
   216 times, correcting 64 species predictions but breaking 116 that were genuine photos of the
   host with the epibiont only appearing as top-k noise — **net −0.23pp species, −0.26pp genus**.
   Below the pre-registered acceptance bar (+0.3pp). ❌
4. **Supervised Contrastive (SupCon) re-ranker, scoped to the 20 heaviest-weighted cryptic pairs**
   (see below) — the most substantial experiment of the four, designed as a strict, pre-registered
   hypothesis test rather than an exploratory tweak.

#### SupCon-scoped contrastive re-ranker: a pre-registered kill-switch protocol

Rather than repeat the earlier whole-catalog fine-tuning attempts (LoRA, head sidecar; both
already closed above with severe or mild regressions), this experiment was deliberately narrow
and mechanistically different, to test one specific question: *can a small amount of targeted
contrastive supervision, applied only to the hardest known confusion pairs, extract a
generalizable discriminative signal that the frozen k-NN retrieval is missing for those pairs
specifically?*

**Design.**
- **Backbone**: frozen BioCLIP-2.5 ViT-H (unchanged, no gradient ever flows into it).
- **Trainable component**: a small projection head, `Linear(1024→512) → ReLU → Dropout →
  Linear(512→256)`, L2-normalized output, trained with the standard Supervised Contrastive Loss
  (Khosla et al., 2020).
- **Scope**: the 20 heaviest-weighted pairs in the project's cryptic-pair confusion list (40
  unique species; per-species reference-embedding counts ranged 18–1,000).
- **Anti-leak guarantee by construction**: training data was drawn *exclusively* from
  `dataset/patterns/` (the reference gallery, already deduplicated against the calibration set by
  the embedding-similarity fix of 2026-08-25); the projection head never saw a single photo from
  the n=12,788 held-out evaluation set.
- **Batch sampler**: for each of several pairs per batch, an anchor+positives set from one member
  of the pair, a **hard negative** (its cryptic partner), and one **obligatory easy negative**
  batch drawn from a randomly chosen species of a *different* genus outside the 40 — specifically
  to discourage the head from learning to separate on confounds (substrate, background rock,
  photographer style) rather than genuine morphology.
- **Monitoring**: an 80/20 per-species train/validation split *within* the reference gallery
  (never touching the evaluation set), with per-pair validation loss tracked every few epochs —
  designed to catch memorization before any evaluation-set cost was spent.
- **Pre-registered acceptance criterion**: ≥+0.3pp global species accuracy on the n=12,788
  evaluation set (relative to the 75.97% TTA baseline above) **and** no degradation to genus
  accuracy outside the 20 scoped pairs.
- **Pre-registered kill criterion**: if per-pair validation loss showed memorization (val loss
  failing to track train loss) before ever reaching the evaluation set, the checkpoint would be
  discarded immediately and the model-retraining line of attack for cripsis closed without
  spending the evaluation-set compute budget.

**Result.** Two independent hyperparameter regimes were tried — (1) LR 1e-3, no regularization,
and (2) LR 5e-5 with dropout 0.3 and weight decay 1e-2 — and **both showed the identical failure
signature**: per-pair validation loss degraded monotonically from epoch 1 onward (run 1:
4.89→5.21 over 300 epochs; run 2: a smaller but still monotonic degradation under regularization),
while training loss continued to fall. The best validation checkpoint in both runs was **epoch 1
— i.e., before any real training had occurred.** This pattern was reproducible across two very
different optimization regimes, which rules out a simple learning-rate or regularization
misconfiguration as the explanation.

The kill criterion was invoked **before** the model was ever evaluated against the n=12,788 test
set — the per-pair monitoring caught the failure at negligible cost, exactly as designed. The
checkpoint was destroyed.

**Interpretation.** Combined with the LoRA and head-sidecar results in §3.3, this is now the
**third independent architecture** (full backbone+ArcFace fine-tune; frozen-backbone linear head;
frozen-backbone contrastive head) to fail to extract a generalizable improvement from this
embedding space under this data regime. The common factor across all three is not the loss
function or the amount of the network touched — it is that **any trainable component layered on
this catalog's per-species photo counts (many Tier-1 species have on the order of tens to a few
hundred images) tends to memorize rather than generalize.** We consider the line of attack
"retrain or fine-tune something on top of the frozen embedding to fix cripsis" **closed** for this
dataset regime, pending either substantially more images per confused species or a different
signal modality (see below).

### A cheap, informative but ultimately unhelpful check: geographic priors for cryptic pairs

Before closing the SupCon line, we checked whether the production geographic prior (`GEO_BOOST`,
a multiplicative bonus scaled by inverse distance to a species' known observation cluster,
`GEO_SIGMA≈200km`) already has, or could plausibly gain, discriminative power for the heaviest
cryptic pairs. For each pair we computed each species' geographic centroid (from up to 100 cached
observation coordinates per species) and the ratio of inter-centroid distance to mean intra-species
spread — a ratio ≳1.5 indicates geographically separable populations; ≲0.7 indicates habitat
overlap indistinguishable by location alone.

The two heaviest pairs by confusion weight — `Hemimycale mediterranea`/`H. columella` (ratio 0.42)
and `Halopteris filicina`/`H. scoparia` (ratio 0.29) — are **geographically fully overlapping**:
confirmation that these are genuine visual cripsis with no geographic shortcut, not a data
artifact. Twelve of the forty species in the cryptic-pair list had **zero** cached geographic
observations at all (a data gap, not a null geographic signal); backfilling these (a short,
low-cost Minka query per species) revealed a real, usable geographic separation for two further
pairs (`Mesophyllum lichenoides`/`M. expansum`, ratio 1.62; `Lutraria magna`/`L. lutraria`, ratio
2.28) — modest wins, not enough to move the global metric, but recorded as the only remaining
open thread on the cripsis question that does not require new training.

### Official baseline update (2026-08-27)

Following the TTA integration above, the production calibration artifact (`calibration.json`) was
regenerated end-to-end (re-harvest with the same TTA logic used in production, full re-fit of the
logistic calibrator) against the same clean, leak-free n=12,788 protocol used throughout this
paper since 2026-08-25/26. **This is the current citable baseline**, superseding the 75.8/81.1/84.5
figure reported above:

| Metric | Accuracy |
|---|---|
| Species (top-1) | **75.97%** |
| Genus | **81.29%** |
| Family | **84.90%** |

Separately, a real Tier-1 photo-count deficit — as opposed to genuine visual cripsis — was
confirmed and closed for exactly three species this session (`Aglaophenia acacia`, 46→62
reference embeddings; `Polycitor adriaticus`, 52→72; `Dagetichthys lusitanicus`, 100→113), after
checking that the great majority of the 20 worst-performing Tier-1 species are *not*
photo-starved (many of their confusion rivals hold 500–1,000+ reference embeddings already) and
therefore would not benefit from more of the same-species photography. The production FAISS index
was rebuilt to include the +49 new embeddings (762,033→762,082) and promoted with the standard
backup-and-verify procedure.

See the public [STATUS.md](../docs/STATUS.md) and [EXPERIMENTS.md](../docs/EXPERIMENTS.md) for the current project snapshot and full experiment log.

---

*Paper in preparation. Version 2026-08-27. Target journals: Biodiversity Data Journal, PeerJ, or Ecological Informatics.*
