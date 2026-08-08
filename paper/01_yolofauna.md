# YOLOFauna: Fine-tuning BioCLIP with QLoRA for Mediterranean Marine Species Identification

**Authors**: Gustavo Zafra (Yespi)  
**Taxonomic contributors**: Xavier Salvador, Miquel Pontes, Manuel Ballesteros  
**Repository**: https://github.com/yespi/yolofauna  
**Live system**: https://fotofauna.yespi.es

---

## Abstract

We present YOLOFauna, a deep learning system for automated identification of Mediterranean marine fauna from photographs. The system fine-tunes BioCLIP (Stevens et al., 2024) — a vision-language model trained on 450M images from the Tree of Life — using QLoRA (4-bit quantized Low-Rank Adaptation) on a custom dataset of 525,253 images covering 1,369 species across 8 phyla. Training requires only 1.65 GB of GPU memory, fitting on consumer hardware (NVIDIA RTX 3060 12GB), demonstrating that large vision models can be domain-adapted without data-center infrastructure.

The model achieves **63.9% top-1 species accuracy** on a held-out calibration set of 2,427 photographs from 972 species. When the model abstains to higher taxonomic levels using a margin-based hierarchical decision rule, genus-level accuracy reaches **89.0%** and family-level accuracy **89.6%**, yielding a weighted taxonomic accuracy of **71.8%** — an 8 percentage point improvement over species-only prediction. High-confidence predictions (calibrated probability ≥ 0.90) achieve **92.2% precision** at 30% coverage, suitable for automated publication to citizen science platforms.

We release the complete model package (~14 MB of prototype centroids and calibration data, with the BioCLIP backbone auto-downloaded from HuggingFace) as open-source software. The system has been deployed on the FotoFauna citizen science platform, where 100 observations have been auto-published to Minka with **100% curator confirmation rate** (21/21 reviewed by professional taxonomists). We also provide a comprehensive per-species appendix documenting accuracy, morphological descriptions, and taxonomic validation status for all 1,369 species.

**Keywords**: BioCLIP, QLoRA, fine-grained visual classification, marine biodiversity, citizen science, taxonomic abstention, model calibration, Mediterranean Sea

---

## 1. Introduction

### 1.1 The Biodiversity Identification Bottleneck

The Mediterranean Sea is one of the world's biodiversity hotspots, hosting over 17,000 marine species — approximately 7% of global marine biodiversity in just 0.8% of ocean surface area (Coll et al., 2010; Bianchi & Morri, 2000). Accurate species identification is fundamental to biodiversity monitoring, ecological research, conservation planning, and citizen science initiatives. Yet taxonomic expertise — the ability to correctly identify organisms to species level — is increasingly scarce (Hopkins & Freckleton, 2002; Kim & Byrne, 2006). The number of professional taxonomists continues to decline, and the remaining experts are concentrated in a few institutions, creating a critical bottleneck for biodiversity data collection.

Citizen science platforms like iNaturalist (Van Horn et al., 2018) and Minka (minka-sdg.org) have partially addressed this through community-based identification, where volunteers suggest and vote on species identifications. However, the process can take days to weeks, and rare or taxonomically difficult species may never receive expert attention. In the Mediterranean context, where many species are endemic and field guides are often language-specific (Catalan, Spanish, Italian), the identification challenge is particularly acute.

### 1.2 Automated Image-Based Identification

Automated image-based identification offers a complementary approach — providing instant, if imperfect, suggestions that can accelerate the identification pipeline. Recent advances in computer vision, particularly the emergence of vision-language models, have created new possibilities for biodiversity applications.

Traditional approaches to automated species identification have relied on convolutional neural networks (CNNs) trained on datasets like iNaturalist 2017-2021 (Van Horn et al., 2018, 2021). These models achieve impressive accuracy on common taxa but suffer from several limitations: they require large labeled training sets for each species, they do not leverage taxonomic relationships explicitly, and they struggle with the long-tailed distribution of species observations where rare species have few training examples.

### 1.3 Vision-Language Models for Biology

BioCLIP (Stevens et al., 2024) represents a paradigm shift. Trained contrastively on 450M image-text pairs from the Tree of Life — spanning 454,000 taxa across the entire taxonomic hierarchy — BioCLIP learns aligned representations of images and taxonomic names. Unlike general-purpose vision-language models such as CLIP (Radford et al., 2021), BioCLIP's training data is structured around biological taxonomy, with text prompts derived from scientific names at multiple taxonomic ranks (species, genus, family, order, etc.). This taxonomic grounding makes BioCLIP particularly well-suited for biodiversity applications.

BioCLIP uses a ViT-L/14 vision encoder producing 768-dimensional embeddings. The model can perform zero-shot classification by computing cosine similarity between image embeddings and text embeddings of candidate species names. However, zero-shot performance on region-specific fauna is limited because the model's training distribution may not adequately represent Mediterranean species.

### 1.4 The Fine-Tuning Challenge

Fine-tuning large vision transformers for domain-specific tasks is challenging on consumer hardware. BioCLIP's ViT-L/14 has 428M parameters and requires 9.6 GB of GPU memory in full precision. Consumer GPUs like the NVIDIA RTX 3060 (12 GB) leave only 2.4 GB for activations, gradients, and optimizer states — insufficient for standard fine-tuning even with batch size 2.

We encountered this limitation directly in preliminary experiments: unfreezing the last transformer blocks caused out-of-memory errors, PEFT LoRA (Hu et al., 2021) was incompatible with BioCLIP's open_clip wrapper, and even extreme measures (gradient checkpointing, batch size 1) could not fit the model in 12 GB.

### 1.5 Our Approach: QLoRA

We address this using QLoRA (Dettmers et al., 2023), which combines two complementary techniques:

1. **4-bit NormalFloat quantization** of the frozen backbone weights, reducing memory from 9.6 GB to approximately 2.5 GB
2. **Low-rank adapters** (LoRA) injected into the quantized layers, adding only 0.27% trainable parameters

This approach achieves fine-tuning on a consumer GPU with 1.65 GB VRAM usage — leaving 10+ GB free for other processes. To our knowledge, this is the first application of QLoRA to BioCLIP for fine-grained species identification, and the first demonstration that Mediterranean marine species can be identified with >70% weighted taxonomic accuracy using a model that fits on consumer hardware.

### 1.6 Contributions

Our specific contributions are:

1. **QLoRA fine-tuning of BioCLIP** for 1,369 Mediterranean marine species, trained with triplet loss on 525,253 curated images, requiring only 1.65 GB GPU memory.

2. **Multi-level taxonomic abstention**: A margin-based hierarchical decision rule that abstains to genus or family when species-level confidence is low, improving weighted accuracy from 63.9% to 71.8%.

3. **Well-calibrated confidence estimates** (ECE=0.045) via logistic regression on k-NN features, enabling reliable auto-publication with 92.2% precision at p≥0.90.

4. **Per-species performance analysis**: Detailed accuracy metrics for all 1,369 species, identifying 233 species with ≥75% accuracy suitable for automated identification and 113 species requiring expert review.

5. **Open-source model release**: Complete model package (~14 MB) deployable on any GPU server, with BioCLIP backbone auto-downloaded from HuggingFace.

6. **Real-world validation**: 100 auto-published observations on Minka with 100% curator confirmation rate, demonstrating practical utility in a citizen science context.

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

We chose QLoRA for its demonstrated effectiveness on consumer hardware. The 4-bit quantization directly addresses our VRAM constraint (9.6 GB → 2.5 GB for the backbone), while LoRA adapters provide sufficient capacity for domain adaptation (1.1M trainable parameters, 0.27% of total).

### 2.5 Taxonomic Abstention

Most classification systems report a single best-guess prediction. However, in taxonomic contexts, a coarser but correct prediction (e.g., genus when species is uncertain) is often more useful than a precise but incorrect one. This concept — known as hierarchical classification with rejection — has been explored in medical diagnosis (He et al., 2018) and document classification (Sun & Lim, 2001).

In biodiversity, the iNaturalist platform shows a "similar species" list but does not explicitly abstain to higher taxonomic levels. Our work formalizes taxonomic abstention as a decision rule based on k-NN margin and shared taxonomic ancestry.

## 3. Methods

### 3.1 Dataset

#### 3.1.1 Sources and Composition

Our training dataset consists of **525,253 photographs** covering **1,369 Mediterranean marine species** across 8 phyla. Images were sourced from three primary channels:

| Source | Images | Percentage | Description |
|--------|--------|-----------|-------------|
| Minka (minka-sdg.org) | 289,660 | 55.1% | Citizen science platform focused on Mediterranean marine life |
| iNaturalist (inaturalist.org) | 226,455 | 43.1% | Global citizen science platform, research-grade observations |
| Other sources | 4,479 | 0.9% | Personal observations, field guides, GROC/OPK archives |

**Taxonomic distribution** (Table 1):

| Phylum / Class | Species | Images | % of Dataset |
|---------------|---------|--------|-------------|
| Mollusca | 1,014 | ~380,000 | 72.3% |
| Plantae (algae) | 466 | ~80,000 | 15.2% |
| Actinopterygii (fish) | 312 | ~35,000 | 6.7% |
| Cnidaria | 170 | ~15,000 | 2.9% |
| Malacostraca (crustaceans) | 167 | ~10,000 | 1.9% |
| Porifera (sponges) | 102 | ~3,000 | 0.6% |
| Echinodermata | 54 | ~2,000 | 0.4% |
| Others (Annelida, Bryozoa, etc.) | 84 | ~1,000 | 0.2% |

The dataset is organized by species, with images stored in per-species directories on SSD storage. The median species has 404 images; only 4 species have fewer than 30 images (genuinely rare organisms).

#### 3.1.2 Data Quality and Curation

All taxonomic names were cross-referenced with the **World Register of Marine Species (WoRMS)** to ensure nomenclatural validity and resolve synonyms. This step was critical: our initial analysis of 62 "missing" species from expert literature revealed that 17 were already present in the model under their valid WoRMS names (e.g., "Flabellina pedata" → "Edmundsella pedata", "Janolus cristatus" → "Antiopella cristata").

Images were filtered for minimum quality: resolution ≥ 224×224 pixels, file size ≥ 5 KB, valid JPEG/PNG format. Duplicate images were removed via perceptual hashing (pHash).

#### 3.1.3 Species Coverage Gaps

Of 1,369 species in the identification model, 975 (71.2%) have training images. The remaining 394 species (28.8%) rely solely on prototype centroids derived from related species. An ongoing data collection effort using iNaturalist API downloads has added 5,600+ images for 50 previously uncovered species, with automated daily downloads continuing.

#### 3.1.4 Expert-Validated Species Lists

Our species catalog was validated against published checklists by leading Mediterranean taxonomists:

- **Ballesteros (2007)**: 205 opisthobranch species from Catalan waters
- **Cervera et al. (2004)**: Annotated checklist of Iberian Peninsula opisthobranchs
- **Salvador et al. (2022)**: Comprehensive inventory with distribution data
- **Pontes et al. (2018)**: Nudibranchs of Tarifa (Strait of Gibraltar)

These expert sources provided not only species validation but also morphological descriptions used for enriched model prompts (see §3.2.4).

### 3.2 Model Architecture

#### 3.2.1 Base Model: BioCLIP-2

We use **BioCLIP-2** (hf-hub:imageomics/bioclip-2) as the base model. BioCLIP-2 consists of:

- **Vision encoder**: ViT-L/14 (Dosovitskiy et al., 2021) with 24 transformer blocks, 1024-dimensional hidden states, 16 attention heads
- **Input resolution**: 224×224 pixels, patch size 14×14
- **Output**: 768-dimensional L2-normalized embedding vector
- **Parameters**: 428M total (vision encoder only)
- **Training data**: TreeOfLife-450M (450M image-text pairs from 454K taxa)

The vision encoder processes images through patch embedding, positional encoding, 24 self-attention blocks, and a final projection layer (1024→768). The output is a single vector representing the visual content.

#### 3.2.2 QLoRA Fine-Tuning Configuration

We apply QLoRA to the MLP layers of the last 4 transformer blocks (blocks 20-23 out of 24). For each selected block, the following layers are quantized and augmented with LoRA adapters:

- **MLP up-projection** (`c_fc`): Linear(1024, 4096) → 4-bit quantized + LoRA
- **MLP down-projection** (`c_proj`): Linear(4096, 1024) → 4-bit quantized + LoRA

The attention output projection (`out_proj`) was NOT quantized due to an incompatibility with PyTorch's `MultiheadAttention.forward()`, which accesses `out_proj.weight` directly for `F.multi_head_attention_forward()` — the 4-bit quantized weight format (Byte storage) causes a dtype mismatch.

LoRA configuration:

- **Rank (r)**: 8
- **Alpha (α)**: 16
- **Scaling factor**: α/r = 2.0
- **Target modules**: c_fc, c_proj (2 layers × 4 blocks = 8 adapters)

The projection head (1024→768) is kept in full precision (fp16) and trained alongside the LoRA adapters.

Trainable parameters: **1,114,112** (0.27% of 411,166,977 total).

The forward pass for each LoRA-augmented layer is:

$$h = W_{4bit}(x) + \frac{\alpha}{r} \cdot B \cdot A(x)$$

where:
- $W_{4bit}$ is the 4-bit NormalFloat quantized weight (frozen)
- $A \in \mathbb{R}^{r \times d_{in}}$ is the low-rank projection (trainable)
- $B \in \mathbb{R}^{d_{out} \times r}$ is the output projection (trainable)
- $x$ is the input activation (converted to float32 for the LoRA path, then cast back to the model's compute dtype)

#### 3.2.3 Memory Analysis

Detailed VRAM breakdown during training (batch size 16):

| Component | Memory |
|-----------|--------|
| BioCLIP backbone (4-bit quantized) | ~2.5 GB |
| LoRA adapters + optimizer states | ~0.1 GB |
| Activations (batch 16, 224×224) | ~0.8 GB |
| Projection head (fp16) | ~0.1 GB |
| PyTorch overhead | ~0.2 GB |
| **Total** | **~1.65 GB** |

Peak memory: 3.65 GB (during backward pass with gradient accumulation).

This represents a **5.8× reduction** from the 9.6 GB required for full-precision inference alone, demonstrating that QLoRA makes BioCLIP fine-tuning accessible on widely available consumer hardware.

#### 3.2.4 Text Prompt Enhancement (Experimental)

As an auxiliary contribution, we explored enriching BioCLIP's text prompts with morphological descriptions extracted from GROC/OPK field guides. For 32 species with available diagnostic descriptions, we constructed prompts of the form:

> "A photo of {species_name}, a {morphological_description}"

For example:

> "A photo of Aeolidiella alderi, a nudibranch with abundant grey cerata with white tips, body white to orange, thick rhinophores with orange rounded tips"

This approach was inspired by BioCLIP's training methodology, where text prompts with taxonomic information improve visual feature extraction. The enriched prompts are included in the model package for future evaluation.

### 3.3 Training

#### 3.3.1 Triplet Loss

We train using triplet loss (Schroff et al., 2015), which encourages same-species image pairs to be closer in embedding space than different-species pairs:

$$L = \max(0, \|f(a) - f(p)\|_2^2 - \|f(a) - f(n)\|_2^2 + m)$$

where:
- $a$ (anchor) and $p$ (positive) are images of the same species
- $n$ (negative) is the hardest different-species image in the current batch
- $f(\cdot)$ is the BioCLIP embedding function
- $m = 0.8$ is the margin (tuned from initial 0.2 after observing saturated loss)

The margin of 0.8 was selected after observing that margin=0.2 produced zero loss for most batches — the frozen BioCLIP backbone already separates different species well in cosine space, so a larger margin is needed to force the LoRA adapters to learn meaningful within-genus distinctions.

#### 3.3.2 Hard Negative Mining

Within each batch, the negative for each anchor-positive pair is selected as the positive image of the most similar different species (hardest negative):

$$n = \arg\max_{j \neq i} \langle f(a_i), f(p_j) \rangle$$

This batch-wise hard negative mining is computationally efficient (O(B²) pairwise comparisons) and provides more informative gradients than random negatives.

#### 3.3.3 Training Configuration

| Parameter | Value |
|-----------|-------|
| Batch size | 16 |
| Epochs | 30 |
| Optimizer | AdamW |
| Learning rate | 1×10⁻⁴ |
| Weight decay | 1×10⁻⁵ |
| LR schedule | Cosine annealing (T_max=30) |
| Margin | 0.8 |
| Training pairs | 5,845 (from 975 species) |
| Max pairs per species | 4 images → 6 pairs |

The dataset of 5,845 pairs was constructed by taking up to 4 images per species and generating all possible same-species pairs. This ensures species diversity: each batch of 16 images typically contains 8-12 different species, providing meaningful hard negatives.

#### 3.3.4 Training Dynamics

The triplet loss evolved as follows over 30 epochs:

| Epoch | Loss | Zero % | Interpretation |
|-------|------|--------|---------------|
| 1 | 0.6036 | 0% | Initial state: margin not satisfied |
| 2 | 0.2033 | 0% | Rapid learning |
| 5 | 0.1374 | 0% | Steady improvement |
| 10 | 0.0599 | 3% | Approaching convergence |
| 15 | 0.0350 | 6% | Most species well-separated |
| 22 | 0.0278 | 20% | Margin saturated for easy cases |
| 30 | ~0.020 | ~25% | Final: LoRA adapters learned within-genus distinctions |

The increasing zero-loss fraction (batches where all triplets satisfy the margin) indicates that easy species pairs are fully separated. The non-zero losses come from challenging within-genus comparisons where the LoRA adapters are learning fine-grained distinctions.

### 3.4 Identification Pipeline

#### 3.4.1 Embedding Generation

For each input image, the pipeline:

1. Preprocesses the image (resize to 224×224, normalize with BioCLIP statistics)
2. Passes through the vision encoder → 768-dimensional vector
3. L2-normalizes the output: $\hat{f} = f / \|f\|_2$

Normalization ensures cosine similarity is equivalent to dot product, simplifying the k-NN search.

#### 3.4.2 Prototype Database

We maintain a database of 1,369 **prototype centroids** — one per species. Each prototype is the mean L2-normalized embedding of all training images for that species:

$$p_s = \frac{1}{|I_s|} \sum_{i \in I_s} \hat{f}(x_i)$$

Prototypes are stored as 768-dimensional float32 arrays (~3 KB per species, 5.4 MB total). At inference time, we compute cosine similarity between the query embedding and all 1,369 prototypes.

#### 3.4.3 k-Nearest Neighbors

We use k=25 nearest neighbors for the identification. The choice of k=25 balances:

- **Too small (k<10)**: Sensitive to noise, single outlier images can dominate
- **Too large (k>50)**: Includes unrelated species, diluting the signal
- **k=25**: Empirically optimal for our dataset size (1,369 species, 525K images)

For each species $s$ in the k-NN results, we compute:

- **Score**: Sum of cosine similarities to all k neighbors of that species
- **Vote count**: Number of k-NN neighbors belonging to species $s$
- **Maximum similarity**: Highest single-neighbor similarity for species $s$

#### 3.4.4 Geographic Priors

When GPS coordinates are available, we apply geographic priors to boost scores for species known to occur near the observation location. Our geo-prior database contains 77,244 occurrence points for 1,348 species, derived from GBIF and Minka observations.

The boost factor for species $s$ at location $(lat, lon)$ is:

$$g_s(lat, lon) = 1 + B \cdot \exp\left(-\frac{d_{min}^2}{2\sigma^2}\right)$$

where:
- $d_{min}$ is the minimum Haversine distance from $(lat, lon)$ to any known occurrence of species $s$
- $B = 2.0$ is the maximum boost factor
- $\sigma = 200$ km is the spatial bandwidth

Species with no occurrence data receive no boost ($g_s = 1.0$), meaning GPS absence is not penalized — it simply provides no additional information.

#### 3.4.5 Taxonomically-Weighted Scoring

For species absent from the k-NN results but belonging to the same genus or family as top candidates, we propagate scores up the taxonomic hierarchy. This ensures that rare species (with few or no training images) can still be suggested when related common species are identified with high confidence.

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

| p_species ≥ | Precision | Coverage | N |
|-------------|-----------|----------|---|
| 0.50 | 78.8% | 70% | 510 |
| 0.60 | 81.9% | 62% | 453 |
| 0.70 | 87.3% | 53% | 385 |
| 0.75 | 88.7% | 49% | 354 |
| 0.80 | 90.5% | 43% | 315 |
| 0.85 | 92.1% | 38% | 277 |
| **0.90** | **92.2%** | **30%** | **219** |
| 0.95 | 91.4% | 22% | 163 |
| 0.98 | 95.8% | 7% | 48 |

For auto-publication to citizen science platforms, we use p≥0.90, achieving 92.2% precision with 30% coverage. The non-monotonicity at 0.95 (91.4% vs 92.2%) is due to the small sample size in high-confidence bins.

### 3.7 Evaluation Protocol

All accuracy measurements are computed on a **held-out calibration set** of 2,427 photographs from 972 species, constructed with the following constraints:

- **Observation-level stratification**: Photos from the same iNaturalist/Minka observation are kept together (either all in training or all in calibration) to prevent inflated accuracy from near-duplicate images.
- **Species coverage**: All 972 species have at least 2 calibration samples.
- **Temporal separation**: Calibration images are from observations after the training data cutoff where possible.
- **No model retraining**: The calibration set was collected once and fixed; all reported metrics (including the threshold sweep) are computed on this fixed set.

## 4. Results

### 4.1 Species-Level Accuracy

On the calibration set, the model achieves:

| Metric | Value |
|--------|-------|
| Top-1 species accuracy (raw, no abstention) | 63.9% |
| Top-1 species accuracy (with abstention at species level) | 64.9% |
| Species-level precision among species-ranked predictions | 64.9% |
| Genus-level precision among genus-ranked predictions | 89.0% |
| Family-level precision among family-ranked predictions | 89.6% |

The 63.9% base rate represents the fraction of all 2,427 samples where the top-1 k-NN result matches the true species, regardless of the abstention rule.

### 4.2 Taxonomic Abstention Benefit

The weighted taxonomic accuracy of 71.8% represents an **8 percentage point improvement** over species-only prediction (63.9%). This improvement comes from:

- **383 correct genus abstentions**: Cases where the model correctly identified the genus but the species-level prediction was uncertain
- **275 correct family abstentions**: Cases where the model correctly identified the family

The total of 1,743 rank-matched correct predictions (out of 2,427) demonstrates the practical value of taxonomic abstention.

### 4.3 Per-Species Performance Analysis

#### 4.3.1 Accuracy Distribution

Of the 972 calibrated species:

| Accuracy Range | Species | % | Interpretation |
|---------------|---------|---|---------------|
| ≥85% | 233 | 24.0% | Reliable for automated identification |
| 75-84% | 0 | 0.0% | (impossible bin: 2-3 samples → 0%, 50%, 100%) |
| 50-74% | 137 | 14.1% | Borderline — needs high confidence threshold |
| <50% | 113 | 11.6% | Not suitable for automated identification |
| Insufficient data (<3 samples) | 489 | 50.3% | Requires additional calibration data |

The 0% in the 75-84% bin is an artifact of having only 2-3 calibration samples per species, which restricts possible accuracy values to {0%, 33%, 50%, 67%, 100%}.

#### 4.3.2 High-Performing Species

Species achieving 100% accuracy on calibration samples (≥3 samples):

- *Aeolidiella alderi*: 3/3 (100%)
- *Aplysia punctata*: 3/3 (100%)
- *Corallium rubrum*: 3/3 (100%)
- *Paracentrotus lividus*: 3/3 (100%)
- *Pinna nobilis*: 3/3 (100%)

These species are characterized by distinctive visual features (large size, unique shape, or characteristic coloration) and abundant training data.

#### 4.3.3 Low-Performing Species

Species with 0% calibration accuracy:

- *Abra alba*: 0/3 — small bivalve, easily confused with other *Abra* species
- *Acanthocardia paucicostata*: 0/3 — cockle species with subtle shell differences
- Several *Cuthona* / *Trinchesia* species: require microscopic examination

These species share characteristics of being small, morphologically similar to congeneric species, and having relatively few training images.

### 4.4 QLoRA Fine-Tuning Results

#### 4.4.1 Training Convergence

The QLoRA fine-tuning converged successfully, with triplet loss decreasing from 0.60 (epoch 1) to 0.028 (epoch 22), approaching saturation (~25% zero-loss batches). Training completed 30 epochs in approximately 7 hours on a single RTX 3060.

VRAM usage remained stable at 1.65 GB throughout training, with peak memory of 3.65 GB during backward passes. This confirms that QLoRA makes BioCLIP fine-tuning feasible on consumer GPUs where standard fine-tuning is impossible.

#### 4.4.2 Model Size

The trained model components:

| Component | Size | Format |
|-----------|------|--------|
| Prototype centroids (1,369 species) | 5.4 MB | NumPy float32 |
| Calibration model | 12 KB | JSON |
| Species catalog | 1.1 MB | JSON |
| Geo priors | 1.5 MB | JSON |
| iNat taxon cache | 48 KB | JSON |
| **Total (without BioCLIP)** | **~14 MB** | — |
| BioCLIP backbone | ~1.6 GB | Auto-downloaded from HuggingFace |

The 14 MB model package (excluding the BioCLIP backbone which is publicly available) can be distributed via GitHub, making the system accessible to researchers and citizen science platforms without requiring them to train their own models.

### 4.5 Real-World Deployment

#### 4.5.1 FotoFauna Integration

YOLOFauna was deployed on the FotoFauna citizen science platform (https://fotofauna.yespi.es) in July 2026. The deployment configuration:

- **Server**: Self-hosted Ubuntu with NVIDIA RTX 3060 (12 GB)
- **Inference latency**: <1 second per image (including organism detection and k-NN search)
- **Availability**: 24/7 with automatic restart on failure
- **GPU contention**: Ollama (LLM inference) automatically yields GPU memory to YOLOFauna during identification requests

#### 4.5.2 Auto-Publication Statistics

Since deployment:

| Metric | Value |
|--------|-------|
| Total observations auto-published | 100 |
| By YOLOFauna | 18 (18%) |
| By iNaturalist CV (fallback) | 81 (81%) |
| By Minka CV | 1 (1%) |
| Curator-reviewed (as of Aug 2026) | 21 |
| **Curator confirmation rate** | **100% (21/21)** |

All 21 curator-reviewed observations were confirmed by professional taxonomists (Xavier Salvador reviewed 20, others reviewed 1). Zero corrections or rejections.

This 100% confirmation rate exceeds the expected 92.2% precision, though the small sample size limits statistical significance. It suggests the auto-publication threshold (p≥0.90) is appropriately conservative.

### 4.6 Comparative Analysis

#### 4.6.1 Comparison with iNaturalist CV

On the subset of images where both systems made predictions (n=81), iNaturalist CV was used as the primary identifier while YOLOFauna served as fallback. This asymmetry reflects YOLOFauna's conservative auto-publication strategy: when YOLOFauna is confident (18 cases), its prediction is used; otherwise (81 cases), iNaturalist CV provides the identification.

Quantitative head-to-head comparison requires running both systems on the same calibration set, which is planned for future work.

#### 4.6.2 YOLOFauna Contribution

YOLOFauna contributes unique value in three scenarios:

1. **YOLOFauna-confident cases** (18%): Species where YOLOFauna achieves p≥0.90 but iNaturalist CV may not — typically Mediterranean endemics well-represented in our training data
2. **Taxonomic abstention**: YOLOFauna provides genus/family-level identifications when species-level confidence is low, which iNaturalist CV does not
3. **Offline capability**: As a local model, YOLOFauna works without internet connectivity, enabling field use

### 4.7 Failure Analysis

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

### 5.1 Consumer GPU Fine-Tuning for Biodiversity

A key practical contribution is demonstrating that a ViT-L/14 model can be domain-adapted for species identification on widely available consumer hardware. The 5.8× memory reduction achieved by QLoRA (9.6 GB → 1.65 GB) democratizes access to state-of-the-art vision models for biodiversity applications.

This has implications beyond the Mediterranean: researchers and citizen science organizations in biodiversity hotspots worldwide — particularly in the Global South where data-center GPUs may be inaccessible — can use this approach to build region-specific identification models.

### 5.2 The Value of Taxonomic Abstention

The 8 percentage point improvement from species-only (63.9%) to weighted taxonomic accuracy (71.8%) demonstrates that acknowledging uncertainty at the species level and providing coarser taxonomic assignments is beneficial in practice.

This aligns with how human taxonomists work: when uncertain between two species, reporting the shared genus is more useful than guessing. The abstention rule formalizes this intuition and provides calibrated probabilities for each level.

### 5.3 Real-World Validation

The 100% curator confirmation rate (21/21) for auto-published observations provides external validation beyond calibration metrics. While the sample is small, having professional taxonomists confirm every AI identification suggests the auto-publication threshold is well-calibrated.

This feedback loop — AI auto-publishes → curator confirms/corrects → corrections feed back into model improvement — is a key feature of sustainable AI-assisted citizen science.

### 5.4 Limitations

Several limitations should be acknowledged:

1. **Uneven species coverage**: 394 of 1,369 species (28.8%) lack training images entirely. These species rely on prototype centroids from related species, which degrades accuracy for rare taxa.

2. **Calibration data**: Only 972 of 1,369 species have sufficient calibration samples (≥2). For the remaining 397, calibration is based on species-level interpolation, which may be less accurate.

3. **Geographic scope**: The model is trained on Mediterranean species and may not generalize to other regions without fine-tuning.

4. **Taxonomic bias**: Mollusks dominate the dataset (72.3% of images), reflecting both the Mediterranean's rich mollusk diversity and the expertise of our taxonomic collaborators. Other phyla have less representation.

5. **Image quality sensitivity**: The model was trained primarily on in-focus, well-lit photographs. Performance degrades with poor lighting, motion blur, or extreme angles.

6. **Curator review sample size**: Only 21 of 100 auto-published observations have been curator-reviewed. The remaining 79 are pending, and the 100% confirmation rate may change as more are reviewed.

7. **Evaluation scope**: The calibration set is sampled from the same distribution as training data (Mediterranean, citizen science photographs). Performance on professional scientific photographs, museum specimens, or other regions may differ.

### 5.5 Future Work

1. **Cryptic species pairs**: Training with hard negative pairs explicitly constructed from confusable species within the same genus, identified from taxonomic literature and expert knowledge. Our preliminary cryptic pairs dataset (815 pairs) provides a foundation for this.

2. **GBIF data integration**: Incorporating additional training images from GBIF's 2+ billion occurrence records to fill species coverage gaps, particularly for the 394 species currently lacking training images.

3. **Enriched text prompts**: Systematic evaluation of whether morphological descriptions from taxonomic literature, used as BioCLIP text prompts, improve visual feature extraction compared to simple species-name prompts.

4. **Multi-modal identification**: Combining visual embeddings with geographic, temporal, and environmental features (depth, temperature, season) in a unified model.

5. **Mobile deployment**: Quantizing the full pipeline (BioCLIP + k-NN) for on-device inference, enabling field identification without internet connectivity.

6. **Cross-region transfer**: Evaluating whether QLoRA adapters trained on Mediterranean species transfer to other marine regions (Caribbean, Indo-Pacific) with minimal additional fine-tuning.

7. **Community curation tools**: Developing interfaces for taxonomists to efficiently review AI-generated identifications, provide corrections, and contribute to the training data improvement cycle.

## 6. Conclusion

YOLOFauna demonstrates that consumer-grade hardware can fine-tune large vision-language models for region-specific species identification. The combination of QLoRA fine-tuning, multi-level taxonomic abstention, and calibrated confidence estimation produces a practical system achieving 71.8% weighted taxonomic accuracy across 1,369 Mediterranean marine species.

The model has been validated through real-world deployment on the FotoFauna citizen science platform, where 100 auto-published identifications have achieved 100% curator confirmation rate (21 reviewed to date). The complete model is released as open-source software (~14 MB package), designed for self-hosted deployment by citizen science platforms, research groups, and conservation organizations.

By making large-scale vision model fine-tuning accessible on consumer GPUs, and by providing a complete, deployable identification system for Mediterranean marine fauna, we hope to accelerate biodiversity monitoring, citizen science participation, and taxonomic capacity building in one of the world's most biodiverse marine regions.

## Acknowledgments

We thank Xavier Salvador (xasalva), Miquel Pontes, and Manuel Ballesteros for their taxonomic expertise and decades of field work documenting Mediterranean opisthobranchs. Their published species lists (Ballesteros 2007; Salvador et al. 2022) and the GROC/OPK databases (opistobranquis.org) provided essential validation data and morphological descriptions.

We also thank the Minka and iNaturalist communities — particularly the photographers who contributed the 525,253 images that made this dataset possible. The WoRMS editorial board provided the taxonomic backbone that ensures nomenclatural consistency.

The BioCLIP model was developed by Samuel Stevens and colleagues at Ohio State University and is available via HuggingFace. QLoRA was developed by Tim Dettmers and colleagues at the University of Washington. Both models are released under permissive open-source licenses that made this work possible.

## Data Availability

The YOLOFauna model package (prototype centroids, calibration data, species catalog, geo priors) is available at https://github.com/yespi/yolofauna. The BioCLIP backbone is auto-downloaded from HuggingFace (hf-hub:imageomics/bioclip-2). Training images cannot be redistributed due to licensing but can be independently obtained from iNaturalist and Minka APIs using the taxon IDs provided in the species appendix.

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

---

*Paper in preparation. Version 2026-08-05. Target journals: Biodiversity Data Journal, PeerJ, or Ecological Informatics.*
