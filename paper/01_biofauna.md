# BioFauna: a frozen BioCLIP-2.5 ViT-H retrieval system for Mediterranean marine identification

**Author**: Gustavo Zafra (Yespi)
**Taxonomic contributors**: Xavier Salvador, Miquel Pontes, Manuel Ballesteros
**Repository**: https://github.com/yespi/biofauna
**Live system**: https://fotofauna.yespi.es
**This version**: 2026-09-14 (frozen snapshot of production)

> **Naming.** Developed as YOLOFauna (2024–mid-2026); renamed BioFauna when production settled on BioCLIP retrieval rather than YOLO detection. Provenance: [`docs/HISTORY.md`](../docs/HISTORY.md).

---

## Abstract

BioFauna identifies Mediterranean (and incidental adjacent) taxa from photographs by **retrieval** over a regional gallery, not by fine-tuning a new classifier. The production encoder is **BioCLIP-2.5 ViT-H/14** (632M parameters, 1024-d embeddings), **frozen**. Queries are encoded (with a 65% centre-crop fused into the global embedding), searched with **k-NN (k=15)** using a tempered vote aggregator, optionally re-weighted by a geographic prior, then mapped to calibrated probabilities and, when the margin is weak, **abstained** to genus, family, or a curated indistinguishability group.

**Production snapshot (2026-09-14, live `/health` + `calibration.json`):**

| Quantity | Value |
|----------|-------|
| Gallery | **848,883** embeddings / **4,702** species, FAISS row-aligned |
| Catalog (Mediterranean checklist) | **2,985** taxa (`dataset/catalog.json`) |
| Out-of-sample accuracy | **85.78%** species / **89.15%** genus / **91.41%** family |
| Evaluation size | n=**19,087** observations, **2,926** species with ≥1 eval sample |
| Hardware | NVIDIA RTX 3060 12 GB (~4.4 GB VRAM at inference) |

Those accuracy figures are **observation-stratified and leak-checked**. They are **not** comparable to the August 2026 headline of 75.97% on a smaller, earlier cohort (n=12,788) without re-running that same harvest; mixing cohorts is how this project previously overstated progress. Both numbers are kept below, labelled by protocol.

**Update 2026-09-21.** Production now serves **1,072,233** embeddings / **4,705** species (1,720 are gallery classes outside the 2,985-species catalog: 1.8% of vectors) after two growth waves (K19–K20). The panel (out-of-sample overlay, n=24,475) reads **92.36%** species; a check on 300 recent Minka research-grade observations gives **~80%** (in-catalog birds 84% vs 96% on the panel) — the panel is a closed-set evaluation and overstates real-world accuracy (O16). Closed-set retrieval answers confidently for species missing from the catalog; an independent BioCLIP zero-shot second opinion removes most of those errors in birds (K21).

A systematic search for extra species top-1 from **training on this embedding space** (QLoRA, LoRA, triplet, ArcFace, linear head, scoped SupCon) **did not beat frozen retrieval**. Gains that shipped were backbone scale, gallery completeness/quality, inference-time fusion, a tempered k-NN aggregator, and taxonomic abstention. We publish the experiment ledger, taxon IDs, prototype centroids, and a self-hostable identifier. **Photographs and per-photo `embeddings.npy` are not redistributed**; they can be rebuilt from Minka / iNaturalist / GBIF using the catalog.

**Keywords**: BioCLIP-2.5, ViT-H, k-NN, fine-grained visual classification, marine biodiversity, citizen science, taxonomic abstention, calibration, Mediterranean Sea

---

## 1. Introduction

The Mediterranean holds a disproportionate share of marine biodiversity in a small basin, while taxonomic capacity is scarce. Citizen-science networks (Minka, iNaturalist) collect photographs faster than experts can identify them. Global classifiers help, but regional endemics, cryptic invertebrates, and language-specific field knowledge remain a bottleneck.

BioFauna is the identifier behind FotoFauna. Design choice: **do not train a closed-set CNN**. Use a biology-pretrained vision encoder and a **regional reference gallery** that can grow species by species without retraining.

**Contributions**

1. A production retrieval stack (frozen ViT-H + k-NN + calibration + hierarchical abstention) running on consumer GPU and publishing high-confidence IDs to Minka.
2. An **observation-stratified** evaluation protocol, including a gallery-similarity leak check after a 42.7% self-duplicate incident.
3. A **ledger of experiments** (this paper §4 and [`docs/EXPERIMENTS.md`](../docs/EXPERIMENTS.md)): each trial has a hypothesis, a result, and whether it was kept.
4. Open reconstruction artefacts: taxon IDs, prototype centroids (4,702 × 1024), calibrators, geo priors, cryptic-pair lists — not the photo corpus.

---

## 2. System

### 2.1 Encoder

| Property | Value |
|----------|-------|
| Checkpoint | `hf-hub:imageomics/bioclip-2.5-vith14` |
| Architecture | ViT-H/14, ~632M params, 1024-d L2-normalized embeddings |
| Input | 224×224 |
| Training in BioFauna | **Frozen** |

### 2.2 Identification (production, 2026-09-14)

1. Embed the query; fuse **global frame + 65% centre crop** (ROI fusion; replaces an earlier 90% TTA).
2. Retrieve **k=15** gallery neighbours (cosine / inner product via FAISS when the full gallery is present; nearest-centroid over published prototypes otherwise).
3. Aggregate neighbour scores with **tempered votes** `Σ exp(max(s,0)/T)`, **T=0.05**, plus a prototype-similarity boost.
4. Optional **multiplicative geographic prior** when GPS is present.
5. **Abstain** when the top-1/top-2 margin is small and taxa share genus/family, or when the pair/genus/group is in `dataset/taxonomic_exceptions.json`.
6. Map k-NN features → **P(correct)** with logistic regression (`dataset/calibration.json`).

AutoID on FotoFauna publishes when calibrated **p ≥ 0.80**. The last published operating-point study on that threshold (August 2026 calibration split) estimated **~95.3% precision at ~57.4% coverage**. That curve has not been re-fit as a standalone paper table after every later gallery change; the live calibrator `created=2026-09-14T07:04:26` is what production uses.

This public repository ships **prototype centroids** (`data/patterns/<slug>/prototype.npy`). That is enough for a nearest-centroid demo. Full k-NN accuracy requires rebuilding per-photo embeddings locally (see [`docs/dataset.md`](../docs/dataset.md)).

### 2.3 Data (what exists vs what we release)

| Layer | Production | This repo |
|-------|------------|-----------|
| Photographs | ~838k on disk (Minka, iNaturalist, GBIF, …) | **Not released** (licence) |
| Per-photo embeddings | 848,883 vectors | **Not released** (size + derived from photos) |
| Prototype per species | 4,702 × 1024 float32 | **Released** (~15 MB) |
| Taxon IDs / names | 2,985 catalog rows | **Released** (`dataset/catalog.json`) |
| Calibrator, geo priors, cryptic pairs, exceptions | live JSON | **Released** |

Names are cross-checked with **WoRMS** (accepted name stored beside the stable slug). Images are filtered for format/resolution; field-guide plate crops that mixed several taxa under one label were quarantined (1,088 photos / 107 species in the August 2026 audit).

**Tiers** (catalog, not gallery size):

| Tier | Meaning | n taxa |
|------|---------|--------|
| 0 | Heterobranchs (expert collaborators’ core group) | 634 |
| 1 | Other marine | 1,527 |
| 2 | Terrestrial / incidental in marine photos | 824 |

---

## 3. Evaluation protocol

Headline numbers use held-out **observations** (an encounter, often several photos of one organism), not a random photo split. Photo-level 80/20 inflates k-NN and metric-learning numbers by ~10 pp because citizen-science bursts are near-duplicates.

| Rule | Why |
|------|-----|
| Stratify by observation ID | No burst leakage |
| Reject a candidate if it is too similar to the live gallery | Catches missing IDs after path migrations |
| Same protocol across ablations | Comparable McNemar |
| Do not mix harvests when citing a delta | Different species mix ≠ model gain |

**Incident (2026-08-25/26).** An observation-ID denylist pointed at an abandoned path and silently matched nothing. **42.7%** of a 22,332-photo harvest were already in the gallery. At k=15 the headline only moved ~1 pp; at small k the curve was absurd (accuracy rising toward k=1). Fix: embed each candidate and drop near-duplicates. Kept as a standing harvest gate.

**Two labelled metrics in this paper**

| Label | Cohort | Species top-1 | Use |
|-------|--------|---------------|-----|
| **A — TTA-era freeze** | `harvest_calib` n=12,788 (Aug 2026, leak-checked) | 75.97% (later 77.77% with inference stack; 79.10% jsonl after densification) | Comparable ablations in §4.1–4.2 |
| **B — live calibrator** | `calib_raw_t05` n=19,087 (2026-09-14) | **85.78%** | Current production report |

B is larger, covers more hard/rare species, and uses T=0.05 + later gallery quality work. **A is not “worse engineering”; B is not a 10-point magic leap on the same photos.**

---

## 4. Experiments

Each row: **hypothesis → result → contribution to the project.** Details and McNemar counts: [`docs/EXPERIMENTS.md`](../docs/EXPERIMENTS.md).

### 4.1 Kept (in production)

| ID | What we tried | Result | What it contributed |
|----|----------------|--------|---------------------|
| K1 | Replace ViT-L gallery with **frozen ViT-H** | +6.8 pp species (63.9% → 70.6% on the then cohort) | Largest single modelling gain. Production encoder. |
| K2 | k-NN grid, observation-stratified | **k=15** beats k=8 and k≥20 | Production k. |
| K3 | Unify SSD + HDD-archive photos and re-embed | 71.7% → 75.8% on leak-checked n=12,788 | Closed the archive gap (see `docs/archive/ARCHIVE_GAP.md`). Completeness > adapters. |
| K4 | Logistic calibration on 10 k-NN features | ECE ~0.03 vs ~0.09 raw cosine | Interpretable AutoID threshold. |
| K5 | Hierarchical abstention (margin + expert pairs/genera) | Genus/family fallbacks ~89% when used; species top-1 slightly conservative | Safer citizen-science output. |
| K6 | 90% centre-crop TTA, then **65% ROI fusion** | TTA +0.21–0.75 pp; ROI fusion +1.63 pp vs global-only on n=12,788 | Production query embedding. |
| K7 | Late fusion of multiple photos in one observation | +0.79 pp full set; +3.15 pp on the 25% multi-photo subset | Production when N>1. |
| K8 | Fisher / PCA+LDA **local subspace** on documented cryptic pairs | +0.14 to +0.36 pp on the official harvest | Scoped re-rank; not a new encoder. |
| K9 | Inter-genus same-family local subspace | Official re-harvest **77.77%** (cohort A + inference stack) | Production second trigger. |
| K10 | Gallery densification (more/better reference photos, frozen encoder) | Cohort A jsonl **79.10%**; later quality swaps (curators, Q≥8, seagrass) | Data, not weights. Live gallery 848,883. |
| K11 | Tempered k-NN aggregator T=0.05 | McNemar n=8,000: **+7.81 pp**, 671/46 | Production scorer (cumulative with K10). |
| K12 | MiniCPM gate on two confusion pairs (Branchiomma/Myxicola, Cerianthus/Pachycerianthus) | Small-n McNemar 12/1, p=0.003 | Gated sidecar, not a general VLM re-ranker. |
| K13 | Nomenclature audit (WoRMS + GBIF) | 85 accepted-name fields; 4 duplicate-slug merges | Catalog hygiene; slugs never used as WoRMS names. |
| K14 | Expert indistinguishability list + sponge group abstain | Extra pairs from eval confusion (≥33% reciprocal) | Decision layer where vision saturates. |
| K19 | Grow reference photos to ~1,000/species where the sources have them + full per-species re-embed | McNemar n=18,000: **+0.57 pp** (313/211, p=1e-5). By species: grew ≥+300 vectors **+7.7 pp**, +100–299 **+12.0 pp**, +1–99 +3.4 pp; species that did not grow −0.63 pp (dilution) | Data works where it exists; 77% of remaining errors sit in species that did not change. |
| K20 | Second growth wave (121 species, 21.9k photos), rebuild to 1,072,233 vectors | McNemar n=21,000: **+0.22 pp** (84/38, p=5e-5); touched species **83.3%→89.5%** (83/1); 31 improve, 0 worsen | In production 2026-09-21. |
| K21 | Independent second opinion for the closed-set retriever: BioCLIP zero-shot over a regional checklist | 300 Mediterranean bird observations: BF≥0.85 **and** zero-shot≥0.80 agree → **98.5% precision at 69% coverage** (BF alone 91.2% at 79%). All groups: 95.9% at 49% with a rescue tier vs BF alone 93.8% at 48% | Open-set guard for AutoID (birds in production; other groups pending). |
| K22 | Promotion criterion counted in species | 173 species improve / 153 worsen / 2,186 unchanged (previous→current index) | Report the per-species balance next to Δ and p. |

### 4.2 Rejected (do not repeat as-is)

| ID | What we tried | Result | What it contributed |
|----|----------------|--------|---------------------|
| R1 | QLoRA ViT-L, trainable projection | 1.7% species | Compatibility/fragility lesson; not a BioCLIP failure in general. |
| R2 | QLoRA BioCLIP-2 ViT-L vs ViT-H prod | Architecture mismatch (768 vs 1024-d) | Discarded before eval. |
| R3 | Triplet on ViT-H (8 variants) | −0.7 to −7 pp | Metric learning on this gallery memorizes. |
| R4 | ArcFace on frozen ViT-H | Tie with k-NN (~71.4 vs 71.6) | No reason to replace retrieval. |
| R5 | LoRA+ArcFace 100 spp | +0.0 pp OOS | Internal splits lied. |
| R6 | LoRA last-4-blocks + ArcFace, 1,358 spp | **−31.2 pp** on full eval | Fine-tuning a subset poisons the shared space. |
| R7 | Frozen-backbone linear head | −0.6 to −1.1 pp OOS (train mini-set had shown +2.6) | Train/eval disagreement; no cutover. |
| R8 | Weight expert-guide crops in the gallery | −0.9 pp | OCR plates ≠ underwater photos. |
| R9 | Near-duplicate burst removal (cos>0.99) | −1.6 pp | Bursts help k-NN. |
| R10 | Outlier filtering on embeddings | −0.21 to −1.45 pp | Removed intra-species variation. |
| R11 | Widen same-genus abstention margin | 9:1 cost of true species IDs vs recovered errors | Production τ stays tight. |
| R12 | “Prefer epibiont” re-rank | −0.23 pp (64 fixed / 116 broken) | Host photos look like the partner in top-k. |
| R13 | Scoped SupCon re-ranker on 20 cryptic pairs | Val loss diverged from epoch 1; kill-switch **before** the eval set | Third independent architecture, same failure mode. |
| R14 | Horizontal-flip TTA | −0.13 pp | Asymmetry is signal. |
| R15 | Per-species prototype weight by dispersion | −0.09 pp | Global dispersion ≠ this query. |
| R16 | Family-consensus penalty on k-NN | −0.41 pp, p=0.0005 | Majority vote is already wrong on convergent morphologies. |
| R17 | Attention-guided crop (Bucket B) | +0.04 pp, p=0.77 | Noise. |
| R18 | Phylum/class consensus filter | All thresholds net-negative | 80% of cross-group errors are already in k-NN. |
| R19 | Ancestral subspace for spp with &lt;5 refs | 1 addressable eval observation | Closed before GPU spend. |
| R20 | Background/substrate neutralization | −0.92 pp vs own control; −3.48 vs full stack | Habitat is signal for epibionts. |
| R21 | Extra geo prior from Minka point clouds on top of production geo | Not significant; 4/5 OOF folds chose strength 0 | Confusable species co-occur. |
| R22 | DINOv2 fusion (scripts misnamed “DINOv3”) | −6.75 pp vs production | Prototypes-only DINOv2 is far weaker here. |
| R23 | Morphological multi-prototypes (k-means) | Not significant; 4/5 folds blend=0 | Single centroid already sufficient for the boost term. |
| R24 | Selective marine re-embed (36 spp) | ~0 pp | No cutover. |
| R25 | Seagrass VLM / generic densification | Null | Quality swap helped *Posidonia*, not *Cymodocea*. |
| R26 | MiniCPM “pure subject” filter on fauna (16 spp) | 97.5% already “pure” | Does not transfer from seagrass. |
| R27 | Broad Q≥8 photo swap on already-exhausted taxa | Very low yield on some batches; high yield on others | Quality helps **when** better photos exist; not a universal lever. |
| R28 | Raise the confidence threshold to cut confident errors | Live backtest n=184: precision flat at 90–92% for p≥0.80…0.95; only coverage falls (52%→11%) | Calibration saturates; not a lever. |
| R29 | Require iNaturalist CV agreement before publishing | Of 81 BF answers ≥0.85: iNat agreed on 51 (BF right 96%), returned nothing on 29 (BF right 83%), disagreed on 1; ~4 correct answers blocked per error avoided | Replaced by domain guards + zero-shot consensus (1-day trial, audit pending). |

### 4.3 Operational failures (not model ideas, still public)

These are included because they change how numbers should be read.

| ID | Failure | Effect | Contribution |
|----|---------|--------|----------------|
| O1 | Calibration harvest leaked into the gallery (Aug 2026) | Inflated low-k curves | Similarity dedup is mandatory. |
| O2 | FAISS index vs `species_ids` desync after `/reload` (1 Sep 2026) | Live IDs assigned terrestrial queries marine names at 85–100% confidence; **disk evals valid** | Reload index and labels together. |
| O3 | Admin metrics reading frozen snapshot files | Panel showed stale/in-sample accuracy | Live metrics from the current jsonl. |
| O4 | Empty `--species` list after nested SSH (13 Sep 2026) | Quality-swap ran on extra taxa for ~35 min | Pass slug files, never interpolated lists. |
| O12 | The serving process translated FAISS labels with the live species folder list, not the index's own name list; three new folders shifted every label while `/health` still reported aligned | Wrong species at 0.92 similarity for hours (2026-09-20/21); AutoID published nothing | Guard cron compares index names ↔ loaded species ↔ folders (extends O2). |
| O13 | An unattended job rebuilt the production FAISS directory and refit calibration before validation finished | Production index overwritten by an unvalidated build | Unattended jobs never write production paths. |
| O14 | The Minka web host returns 403 to the default `python-httpx` User-Agent (login and photo downloads) | AutoID zero publications for days (second recurrence of the missing-header class) | One shared HTTP client; alarm on zero-publication days. |
| O15 | Two agent sessions ran the same cycle in parallel; one promotion overwrote the other; GPU OOM with sidecar + serving + re-embed | Duplicated compute; index/calibration mismatch for ~30 min | Single active session with a written registry. |
| O16 | Closed-set, observer-correlated evaluation: panel 92.4% vs ~80% on 300 recent research-grade observations; 12% of bird observations are species outside the catalog | Panel overstates real-world accuracy | Recent-observation sample as operating KPI. |
| O17 | Dashboard accuracy per species changes only when the eval is re-scored against the serving index | Numbers frozen after promotions | Daily automated re-score; re-score after every promotion. |

---

## 5. Current production report (cohort B)

| Level | Accuracy | n |
|-------|----------|---|
| Species | **85.78%** | 19,087 |
| Genus | **89.15%** | 19,087 |
| Family | **91.41%** | 19,087 |
| Tier 0 (heterobranchs) | 76.86% | 2,528 |
| Tier 1 (other marine) | 86.56% | 10,207 |
| Tier 2 (terrestrial/incidental) | 88.08% | 6,352 |

Remaining error is dominated by **visual cripsis and morphological convergence** (sponges, filamentous algae, some fishes, seagrass blades), not by “we need LoRA”. Coverage: most catalog species now have ≥1 held-out observation; a small tail is exhausted on Minka+iNaturalist (dozens of taxa with essentially no extra research-grade photos).

Seagrass (n=60 each, 14 Sep): *Posidonia oceanica* 73.3%; *Cymodocea nodosa* 70.0% (quality swap **not** shipped — confusion with *Nanozostera*); *Nanozostera noltii* 86.7%; *Zostera marina* 75.0%. The pair *Z. marina* ↔ *N. noltii* was added to expert abstention after 20/120 cross-confusions.

---

## 6. Limitations

1. Species top-1 is not expert-level on cryptic invertebrates.
2. No geographic generalization study outside the Mediterranean.
3. Public code is a **reconstruction identifier** (prototypes + optional local k-NN), not a dump of HanSolo’s 1,300-line service (sidecars, AutoID, GPU contention with MiniCPM).
4. AutoID precision/coverage table is older than the 14 Sep calibrator.
5. Curator corrections are not yet a closed training loop.
6. **Closed-set retrieval:** species absent from the catalog get a confident wrong answer; the calibrator only saw catalog species. Mitigated for birds by a zero-shot consensus guard (K21); not yet for other groups.
7. **Evaluation optimism:** the panel/OOS metric (92.4%) is closed-set and observer-correlated; a recent-observation sample (~80%) is the operating KPI (O16).
8. **AutoID without iNaturalist verification** has run for one day only (guards: Mediterranean bounding box, bird consensus, 15/h cap); the audit against community identifications is pending.

---

## 7. Reproducibility

```bash
git clone https://github.com/yespi/biofauna.git && cd biofauna
pip install -r requirements.txt
python -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090
```

Downloads BioCLIP-2.5 from Hugging Face on first run. Uses `data/patterns/` prototypes. To rebuild the full gallery: download photos with taxon IDs in `dataset/catalog.json`, run `scripts/reembed_vith.py`, place `embeddings.npy` beside each prototype.

Licence: MIT for code and released JSON/prototypes. Photograph copyright remains with original observers and platforms.

---

## Acknowledgments

Xavier Salvador, Miquel Pontes, and Manuel Ballesteros (GROC/OPK, published checklists). Minka and iNaturalist observers. WoRMS. BioCLIP (Stevens et al.).

---

## Data availability

Code, prototypes, catalog, calibrators, geo priors, cryptic pairs: this repository. Backbone: Hugging Face `imageomics/bioclip-2.5-vith14`. Images: obtain independently from Minka/iNaturalist/GBIF.

---

## References

1. Stevens, S. et al. (2024). BioCLIP: A Vision-Language Model for the Tree of Life. *CVPR*.
2. Dettmers, T. et al. (2023). QLoRA. *NeurIPS*.
3. Hu, E.J. et al. (2021). LoRA. *ICLR*.
4. Radford, A. et al. (2021). CLIP. *ICML*.
5. Van Horn, G. et al. (2018, 2021). iNaturalist datasets. *CVPR*.
6. Khosla, P. et al. (2020). Supervised Contrastive Learning. *NeurIPS*.
7. Coll, M. et al. (2010). Mediterranean marine biodiversity. *PLoS ONE*.
8. Bianchi, C.N. & Morri, C. (2000). Marine biodiversity of the Mediterranean Sea. *Mar. Pollut. Bull.*
9. Ballesteros, M. (2007). Opisthobranchs of the Catalan coasts. *SPIRA*.
10. Cervera, J.L. et al. (2004). Iberian opisthobranch checklist. *Bol. Inst. Esp. Oceanogr.*
11. Salvador, X., Lázaro, J. & Fuentes, M.A. (2022). Invertebrats marins de la Vall del Ridaura. Digital CSIC.
12. Schroff, F. et al. (2015). FaceNet. *CVPR*.
13. Hermans, A. et al. (2017). Triplet loss. arXiv:1703.07737.

---

*Technical report accompanying the open repository. Not a journal submission. Target venues after a frozen PDF cut: Ecological Informatics / Biodiversity Data Journal / PeerJ.*
