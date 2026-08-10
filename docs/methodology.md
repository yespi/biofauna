# Methodology — BioFauna

## Model Architecture

BioFauna uses **BioCLIP-2.5 ViT-H/14** (`hf-hub:imageomics/bioclip-2.5-vith14`), a vision transformer producing **1024-dimensional** L2-normalized embeddings. In production the backbone is **frozen**.

### Identification Pipeline

1. **Embedding**: Input crop → ViT-H → 1024-dim vector  
2. **k-Nearest Neighbors**: **k=15** over the species gallery (`dataset/patterns/`)  
3. **Geographic priors** (optional): GPS-weighted boost when coordinates exist  
4. **Calibration**: Logistic regression on k-NN features → P(species/genus/family correct)  
5. **Taxonomic abstention / hierarchical fallback**: When the top-1/top-2 margin is small and taxa share genus/family, report the coarser rank (`MIN_RISK`, `FAMILY_MARGIN`)

### What We Tried and Did Not Ship

| Technique | Result |
|-----------|--------|
| QLoRA on ViT-L (proj head trainable) | Catastrophic (1.7%) |
| Triplet on ViT-H | Degrades |
| ArcFace (frozen ViT-H) | Ties k-NN out-of-sample |
| LoRA+ArcFace (eval corrected) | +0.0pp |
| Expert-guide crops / burst dedup | Slightly worse on `harvest_calib` |

## Dataset

- ~**584K–587K** photographs under ~**3,000** species folders (Mediterranean focus)  
- Gallery: ~**1,158** active species / ~**454K** embeddings in production patterns  
- Sources: Minka, iNaturalist, expert guides (Pontes / Salvador / Ballesteros)  
- Taxonomy: WoRMS cross-checks for synonyms

## Validation

Headline metrics come only from **`harvest_calib`** (held-out by **observation ID**, not by photo) + `fit_calib.py`.

Canonical result (**2026-08-10**): **71.7% / 76.5% / 80.4%** species / genus / family (n=1,946; 810 species).  
AutoID operating point: **p≥0.90 → 95.5% precision, 30.2% coverage**.

## References

- Stevens et al. (2024). BioCLIP: A Vision-Language Model for the Tree of Life. CVPR 2024.
- Ballesteros, M. (2007). Lista actualizada de los opistobranquios de las costas catalanas. SPIRA 2(3):163-188.
- Cervera, J.L. et al. (2004). An annotated checklist of the opisthobranchs from the Iberian Peninsula.
- Pontes, M. et al. Nudibranquios de la Isla de Tarifa. OPK/GROC.
