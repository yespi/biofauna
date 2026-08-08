# Methodology — YOLOFauna

## Model Architecture

YOLOFauna uses **BioCLIP-2** (hf-hub:imageomics/bioclip-2), a ViT-L/14 vision transformer trained contrastively on 450M image-text pairs from the Tree of Life project. The model generates 768-dimensional embeddings from 224×224px input images.

### Fine-Tuning (QLoRA)

The BioCLIP backbone was fine-tuned on a dataset of Mediterranean marine species using:

- **4-bit NormalFloat quantization** (bitsandbytes) on MLP layers of the last 4 transformer blocks
- **LoRA adapters** (rank=8, alpha=16) on the quantized layers
- **Triplet loss** with margin=0.8 and batch size=16
- **30 epochs** on 5,845 same-species image pairs across 975 species
- **Hardware**: Single NVIDIA RTX 3060 12GB (VRAM usage: 1.65 GB)

## Identification Pipeline

1. **Embedding**: Input image → BioCLIP → 768-dim L2-normalized vector
2. **k-Nearest Neighbors**: k=25 search against 1,369 prototype embeddings
3. **Geographic Priors**: GPS-weighted scoring using Haversine distance (σ=200km)
4. **Calibration**: Multi-level logistic regression maps k-NN features to:
   - P(species correct) — AUC 0.845, ECE 0.045
   - P(genus correct) — AUC 0.862, ECE 0.049
   - P(family correct) — AUC 0.866, ECE 0.049
5. **Taxonomic Abstention**: When margin between top-1 and top-2 is small and they share genus/family, the system abstains to the higher taxonomic level

## Dataset

- **525,253 photographs** from Minka (56%), iNaturalist (43%), and other sources (1%)
- **1,369 Mediterranean marine species** across 8 phyla
- All identifications cross-referenced with WoRMS (World Register of Marine Species)
- Photos with curator validation from Minka receive higher training weight

## Validation

Calibration performed on 2,427 held-out samples from 972 species, stratified by observation to prevent data leakage. The logistic calibration model achieves well-calibrated probabilities (ECE=0.045 at species level).

## References

- Stevens et al. (2024). BioCLIP: A Vision-Language Model for the Tree of Life. CVPR 2024.
- Ballesteros, M. (2007). Lista actualizada de los opistobranquios de las costas catalanas. SPIRA 2(3):163-188.
- Cervera, J.L. et al. (2004). An annotated checklist of the opisthobranchs from the Iberian Peninsula. Bol. Inst. Esp. Oceanogr.
- Pontes, M. et al. Nudibranquios de la Isla de Tarifa. OPK/GROC.
