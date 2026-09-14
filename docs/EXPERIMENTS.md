# BioFauna — Experiments

> Public ledger through **2026-09-14**. Trusted metric: observation-stratified harvest, not photo-level splits.
>
> **Live (cohort B):** 85.78% species / 89.15% genus / 91.41% family, n=19,087, FAISS **848,883** / 4,702 spp, k-NN **T=0.05**.
>
> **August freeze (cohort A):** leak-checked n=12,788; TTA-era 75.97% → inference stack 77.77% → densification jsonl 79.10%. Ablations below that cite 75–78% are cohort A unless noted.
>
> Short form: [paper §4](../paper/01_biofauna.md#4-experiments).

## Kept

| ID | Change | Effect | Contribution |
|----|--------|--------|----------------|
| K1 | ViT-L → frozen ViT-H | +6.8 pp (63.9→70.6, then cohort) | Production encoder |
| K2 | k=15 | Beat k=8 and k≥20 | Production k |
| K3 | SSD+HDD re-embed (archive gap closed) | 71.7→75.8% on clean n=12,788 | Data completeness |
| K4 | 10-feature logistic calibration | ECE ~0.03 | AutoID probabilities |
| K5 | Hierarchical + expert abstention | Safer genus/family/group output | Decision layer |
| K6 | 90% TTA then 65% ROI fusion | TTA +0.21–0.75; ROI +1.63 vs global | Query embedding |
| K7 | Multi-photo late fusion | +0.79 pp full; +3.15 on 25% subset | N>1 observations |
| K8–K9 | Local PCA/LDA on cryptic / inter-genus pairs | +0.14–0.36 pp; official 77.77% | Scoped re-rank |
| K10 | Gallery densification / quality swaps | Cohort A jsonl 79.10%; live 848,883 | Frozen encoder, more photos |
| K11 | Tempered k-NN T=0.05 | McNemar n=8,000 +7.81 pp (671/46) | Production aggregator |
| K12 | MiniCPM gate on 2 pairs | 12/1, p=0.003 | Sidecar, not general VLM |
| K13 | WoRMS/GBIF nomenclature | 85 accepted names; 4 slug merges | Catalog hygiene |
| K14 | Extra indistinguishability pairs + sponge group | From eval confusion | Where vision saturates |

## Rejected

| ID | Experiment | OOS result | Contribution |
|----|------------|------------|----------------|
| R1 | QLoRA ViT-L + proj head | 1.7% | Fragility |
| R2 | QLoRA ViT-L vs ViT-H | Dim mismatch | Discarded pre-eval |
| R3 | Triplet ViT-H (8 variants) | −0.7 to −7 pp | Memorizes |
| R4 | ArcFace frozen ViT-H | Tie vs k-NN | No replace retrieval |
| R5 | LoRA+ArcFace 100 spp | +0.0 pp | Internal splits lied |
| R6 | LoRA full-catalog scale | **−31.2 pp** | Subset FT poisons space |
| R7 | Linear head, frozen backbone | −0.6 to −1.1 pp | Train mini-set lied |
| R8 | Expert-guide crops weighted | −0.9 pp | Plates ≠ field photos |
| R9 | Burst dedup cos>0.99 | −1.6 pp | Bursts help k-NN |
| R10 | Embedding outlier filter | −0.21 to −1.45 pp | Removed variation |
| R11 | Wider same-genus abstention | ~9:1 cost | Keep tight τ |
| R12 | Prefer-epibiont re-rank | −0.23 pp (64/116) | Hosts in top-k |
| R13 | Scoped SupCon (20 pairs) | Val loss ↑ epoch 1; killed pre-eval | Same failure mode |
| R14 | Horizontal-flip TTA | −0.13 pp | Asymmetry is signal |
| R15 | Per-species arc by dispersion | −0.09 pp | Global ≠ this query |
| R16 | Family-consensus k-NN penalty | −0.41 pp, p=0.0005 | Majority already wrong |
| R17 | Attention crop (Bucket B) | +0.04 pp, p=0.77 | Noise |
| R18 | Phylum/class filter | All thresholds net-negative | Error is in k-NN |
| R19 | Ancestral subspace &lt;5 refs | 1 addressable obs | Closed pre-GPU |
| R20 | Background neutralization | −0.92 / −3.48 pp | Habitat is signal |
| R21 | Extra Minka geo on confusable pairs | n.s.; 4/5 folds strength 0 | Species co-occur |
| R22 | DINOv2 fusion (“DINOv3” scripts) | −6.75 pp vs prod | Weak prototypes |
| R23 | k-means multi-prototypes | n.s.; 4/5 blend=0 | One centroid enough |
| R24 | Selective marine re-embed 36 spp | ~0 pp | No cutover |
| R25 | Seagrass VLM / generic densify | Null | Quality helped Posidonia only |
| R26 | MiniCPM purity on fauna | 97.5% already pure | No transfer |
| R27 | Q≥8 on exhausted taxa | Uneven yield | Only if better photos exist |

## Operational (read numbers with these in mind)

| ID | What broke | Lesson |
|----|------------|--------|
| O1 | 42.7% calib leak into gallery | Dedup by embedding similarity |
| O2 | FAISS vs label array after `/reload` | Load index and IDs together |
| O3 | Admin metrics from frozen files | Compute from current jsonl |
| O4 | Empty `--species` after nested SSH | Pass slug files |

Do not reopen R1–R23 as-is on this gallery and 12 GB GPU. Reopen fine-tuning only with a different backbone or much more photos per confused pair.
