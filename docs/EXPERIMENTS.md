# BioFauna — Experiments

> Public ledger through **2026-09-16**. Trusted metric: observation-stratified harvest, not photo-level splits.
>
> **Live (cohort B, production, unchanged since 2026-09-14 09:29):** FAISS **855,548** / 4,702 spp, k-NN **T=0.05**. True species accuracy **90.52%** (n=16,676) — see O5 below for why this was reported as a stale 85.78% for most of a session before being caught and fixed; the underlying model never changed, only the measurement.
>
> **Candidate on disk (not yet promoted to production):** FAISS 864,806, `overall_accuracy` 87.44% (n covers 2,972/2,985 species — lower than 90.52% purely because coverage grew by 548 species that were previously invisible to the metric, see K18; not a regression). 68 species carry a verified strict improvement and are the only ones actually changed relative to production; everything else reverts to the pre-campaign backup automatically if it does not beat its own prior result.
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
| K15 | Lower quality floor for gallery growth (Q≥8.0 → Q≥6.0, ~13-pt scale) | Strict-improvement rate on grown species jumped 4.7%→20.5% (19/403 → 49/239) | Candidate scarcity, not encoder quality, was the bottleneck for most stuck species |
| K16 | API health circuit breaker for bulk harvest scripts | Caught and self-stopped a real production-impacting overload within seconds, across parallel workers, with zero human intervention | Any scripted bulk client of a third-party API needs this, not just this one incident |
| K17 | Leave-one-out synthetic eval (query = own gallery's top-quality photos, physically excluded before indexing) | 561 → 13 species now have zero eval coverage (down from ~562 uncovered at session start counting an earlier related backlog) | Cheap way to close "we have data but never tested it" gaps; see caveat under O9 |
| K18 | Per-observation calibrated decision threshold (from the hierarchical calibration already built) instead of one fixed global threshold | Real held-out case: p_species=0.8926 with its own calibrated threshold=0.8697 was being wrongly rejected by the fixed 0.90 floor | A single global confidence floor punishes species whose calibration already says a lower bar is safe |

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

## Candidates for re-test now that gallery quality/size has moved (2026-09-16)

The lesson that prompted this section: if bulk harvest had started with a lower, data-driven quality floor (K15) instead of the conservative Q≥8.0 used through mid-September, several rounds of "stuck at N candidates" investigation earlier in the project would have been unnecessary. Several `Rejected` results above were measured against the gallery as it existed *at the time* — some may have failed for reasons that a materially bigger or cleaner gallery removes, not because the underlying idea was wrong. Flagging rather than re-running silently, since re-testing costs real GPU time and should be prioritized on purpose:

| ID | Why it might behave differently now | What changed |
|----|----|----|
| R24 | Selective marine re-embed (36 spp, ~0pp) was tested on galleries an order of magnitude smaller for several of those species than what the Q≥6.0 growth pass (K15) now provides for many catalog species | Gallery size/quality floor |
| R25 | Seagrass VLM / generic densify: "quality helped Posidonia only" was true *given the Minka+iNat pool available that week* — Cymodocea's specific failure mode was diagnosed as cryptic confusion with Nanozostera, not gallery quality, so this one is a weaker re-test candidate than R24, flagged for completeness rather than expectation | Diagnosis was structural, not data — re-test unlikely to change the verdict |
| R9 | Burst dedup (cos>0.99, −1.6pp): the loss came from removing near-duplicate frames that still helped k-NN vote weight. Worth re-checking now that gallery sizes are less uniform across species — the effect may not hold the same way for species that only just crossed from <50 to several hundred photos | Gallery size distribution shifted |
| R10 | Embedding outlier filter (−0.21 to −1.45pp): outliers may have included legitimately hard/rare poses that were the *only* representative of that pose at the time; with denser galleries some of those poses may no longer be singletons | Gallery density |

None of these have been re-run yet — this is a prioritized list, not a result.

## Operational (read numbers with these in mind)

| ID | What broke | Lesson |
|----|------------|--------|
| O1 | 42.7% calib leak into gallery | Dedup by embedding similarity |
| O2 | FAISS vs label array after `/reload` | Load index and IDs together |
| O3 | Admin metrics from frozen files | Compute from current jsonl |
| O4 | Empty `--species` after nested SSH | Pass slug files |
| O5 | `gen_stats.py` scored against a `top` field frozen at harvest time in the eval jsonl; a full pipeline session ran without the refresh step that keeps it live | Reported 85.78% for a session; true concurrent accuracy was 90.52% — the encoder/gallery never changed, only the measurement. Chained with a second bug: even after refreshing predictions, the accuracy script preferred a calibration file field set *before* the refresh over the live number. Fix: refresh predictions before refitting calibration, not after |
| O6 | 3 parallel bulk-harvest workers overloaded a third-party API's production infrastructure (self-reported by the operator mid-incident) | Any scripted client hitting an API you don't control needs a latency/error circuit breaker (K16) before it needs more throughput |
| O7 | Backup script's global error trap fired on a transient third-party quota error inside a retry loop that was explicitly written to handle that exact failure gracefully — the trap fired before the retry logic's own exit-code check ran | A `trap ... ERR` and a hand-rolled retry loop for the same command will race; chain the exit-code capture (`cmd && ok=0 \|\| ok=$?`) so a transient failure can't short-circuit past logic written to tolerate it |
| O8 | A calibrated per-observation decision field existed in the serving API response and was being ignored in favor of a fixed constant one call site away | Second source of truth beats a hardcoded copy — if the calibrated value already ships in the response, use it, don't shadow it |
| O9 | Leave-one-out eval (K17) selects query photos by *highest quality score* per species, not at random | Likely optimistic relative to real incoming photo quality; partially offset by smaller-than-final reference galleries for low-photo-count species during the test. Net direction not yet quantified — would need a repeat with randomly-selected (not top-quality) held-out queries to bound it |

Do not reopen R1–R23 as-is on this gallery and 12 GB GPU. Reopen fine-tuning only with a different backbone or much more photos per confused pair. R24/R25/R9/R10 are re-test candidates (see above), not confirmed reversals.
