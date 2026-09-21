# BioFauna — Experiments

> Public ledger through **2026-09-21**. Trusted metric: observation-stratified harvest, not photo-level splits.
>
> **Live (cohort B, production, unchanged since 2026-09-14 09:29):** FAISS **855,548** / 4,702 spp, k-NN **T=0.05**. True species accuracy **90.52%** (n=16,676) — see O5 below for why this was reported as a stale 85.78% for most of a session before being caught and fixed; the underlying model never changed, only the measurement.
>
> **Update 2026-09-21 (production).** Live: FAISS **1,072,233** / 4,705 species (K19–K20), k-NN T=0.05, calibration refit on n=24,475. Panel metric (out-of-sample overlay, n=24,475) **92.36%** — read it with O16: on 300 recent Minka research-grade observations the same system scores ~80% (in-catalog birds 84% vs 96% on the panel). Per-species panel distribution: 314 species <80%, 500 at 80–99%, 2,008 at 100%, 163 without eval. The two bullets below describe 2026-09-14/16 and are kept for history.
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
| K19 | Grow reference photos to ~1,000/species wherever the sources have them (quality floor 6.0) + full per-species re-embed | McNemar n=18,000 vs the previous index: **+0.57 pp** overall (313/211, p=1e-5). Dose-response by species: grew ≥+300 vectors **+7.7 pp**, +100–299 **+12.0 pp**, +1–99 +3.4 pp; species that did **not** grow −0.63 pp (dilution) | Data works where it exists; the aggregate hides it. 77% of the remaining errors sit in species that did not change (sources exhausted, <200 vectors) |
| K20 | Second growth wave (121 species, 21.9k photos) + rebuild (1,072,233 vectors) | McNemar n=21,000 early stop: **+0.22 pp** (84/38, p=5e-5); the 121 touched species **83.3%→89.5%** (83/1); 31 species improve, 0 worsen | Confirms K19 at species level. In production 2026-09-21 |
| K21 | Independent second opinion for a closed-set retriever: BioCLIP zero-shot over a regional checklist (birds, 366 labels) | 300 Mediterranean bird observations: BF≥0.85 **and** zero-shot≥0.80 agree → **98.5% precision at 69% coverage** (BF alone 91.2% at 79%; zero-shot alone 85.7%, BF 73.7%). All groups (3,257 labels, 300 obs): agreement 96.8% at 41%; adding a rescue tier (BF<0.80, zero-shot≥0.95 agrees) 95.9% at 49% vs BF alone 93.8% at 48% | Open-set guard. In production for birds (CPU sidecar, fail-closed); other groups pending |
| K22 | Promotion criterion counted in species, not only in observations | Previous→current index: 173 species improve / 153 worsen / 2,186 unchanged (n≈7 eval obs per species — noisy, so read touched species first) | Report the per-species balance next to Δ and p; promote when many species improve even if the pooled score does not |

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
| R9 | Burst dedup cos>0.99 | −1.6 pp originally; **re-tested 2026-09-16** on 18 species that had just grown from a few dozen to ~1,000 photos each (177 near-duplicate photos removed): 0/18 improved, 17/18 tied, 1/18 regressed (100%→92.3%, n=13); global accuracy unchanged (90.93%→90.93%) | Bursts help k-NN — confirmed again with denser, more recent galleries, not just small-sample noise from the original test |
| R10 | Embedding outlier filter | −0.21 to −1.45 pp originally; **re-tested 2026-09-17** on the same 18 densely-regrown species used for R9 (bottom 10% by mean cosine similarity to the rest of the species' own gallery removed, ~1,700 photos across 18 species): 0/18 improved, 14/18 tied, 4/18 regressed (worst: xerosecta_cespitum 100%→60%, n=5); reverted | Outliers still cost accuracy with denser galleries too — not a small-gallery artifact |
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
| R28 | Raise the confidence threshold to cut confident errors | Live backtest n=184: precision flat at 90–92% for p≥0.80…0.95; only coverage falls (52%→11%) | Calibration saturates; not a lever |
| R29 | Require iNaturalist CV agreement before AutoID publishes | Of 81 BF answers ≥0.85: iNat agreed on 51 (BF right 96%; the shared errors are the same), returned nothing on 29 (BF right 83%), disagreed on 1. The requirement blocked ~4 correct answers per error avoided (part of the “no result” were HTTP 429s caused by the test itself) | Replaced by domain guards + zero-shot consensus for birds (1-day trial, review pending) |

## Candidates for re-test now that gallery quality/size has moved (2026-09-16)

The lesson that prompted this section: if bulk harvest had started with a lower, data-driven quality floor (K15) instead of the conservative Q≥8.0 used through mid-September, several rounds of "stuck at N candidates" investigation earlier in the project would have been unnecessary. Several `Rejected` results above were measured against the gallery as it existed *at the time* — some may have failed for reasons that a materially bigger or cleaner gallery removes, not because the underlying idea was wrong. Flagging rather than re-running silently, since re-testing costs real GPU time and should be prioritized on purpose:

| ID | Why it might behave differently now | What changed |
|----|----|----|
| R24 | Selective marine re-embed (36 spp, ~0pp) was tested on galleries an order of magnitude smaller for several of those species than what the Q≥6.0 growth pass (K15) now provides for many catalog species | Gallery size/quality floor |
| R25 | Seagrass VLM / generic densify: "quality helped Posidonia only" was true *given the Minka+iNat pool available that week* — Cymodocea's specific failure mode was diagnosed as cryptic confusion with Nanozostera, not gallery quality, so this one is a weaker re-test candidate than R24, flagged for completeness rather than expectation | Diagnosis was structural, not data — re-test unlikely to change the verdict |

R24 and R25 have not been re-run yet; R9 and R10 have (both confirmed rejected again, see above).

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
| O10 | A rescore script's `obs_list` was the *intersection* of (query embeddings already cached) and (rows in the live eval file), then it rewrote that eval file from scratch with only what it processed | Rows added by a concurrent harvest process, lacking a cached query embedding yet, were silently excluded from the plan and then wiped when the file was overwritten — lost a day of held-out-eval harvest progress. Fixed two ways: the rescorer now computes any missing query embeddings before scoring, and every write in this chain (FAISS index, per-species embeddings, the query-embedding cache, and the eval file itself) now writes to a temp file and renames on success, so a process killed mid-write can no longer leave a truncated file for the next reader |
| O11 | A User-Agent fix applied to one Minka-calling file was not propagated to two sibling files (a shared photo-download helper and the AutoID scheduler's own client) that had the identical missing-header bug | AutoID published zero identifications for a full day; the failure mode (repeated "8 consecutive errors, aborting") looked like a Minka-side outage but was fully reproducible with a bare `curl` lacking the header. Fixing one call site for a third-party API quirk means finding every other call site to the same host, not just the one that happened to be reported |
| O12 | The serving process translated FAISS labels with the **live** species list (folders in `patterns/`), not the index's own `species_names.json`. Three new species folders appeared → every label shifted; `/health` still said `faiss_aligned=true` | Wrong species with 0.92 similarity (*Serranus cabrilla* → *Serpula concharum*) for hours; AutoID published nothing | Extends O2. Guard cron compares index names ↔ loaded species ↔ folders; rebuild+promote before any restart |
| O13 | An unattended keepalive job rebuilt the production FAISS directory (build without `--out`) and refit the calibration before validation finished | Production index overwritten by an unvalidated build | Unattended jobs never write production paths; always `--out` + explicit promotion |
| O14 | The Minka **web** host (not its API) returns 403 to the default `python-httpx` User-Agent on login and photo downloads | AutoID scored zero publications for days; second recurrence of O11 (fix not propagated to sibling clients) | One shared HTTP client with the header, and an alarm on zero-publication days |
| O15 | Two agent sessions ran the same re-embed/FAISS/calibration cycle in parallel; one promotion overwrote the other; GPU OOM when the VLM sidecar, the serving process and a re-embed coexisted | Duplicated compute, mismatched index/calibration for ~30 min | Single active session with a written registry; unload the VLM and use batch 8 before GPU jobs |
| O16 | The evaluation is closed-set and observer/site-correlated: panel 92.4% vs ~80% on 300 recent research-grade observations; 12% of bird observations are species outside the catalog (16 of 21 confident errors) | The panel overstates real-world accuracy | Keep both numbers; make a time- and observer-split recent-observation sample the operating KPI |
| O17 | Per-species accuracy shown in the admin panel and in the photo-download portal is read from a scored file that only changes when the eval is **re-scored** against the serving index | Numbers stayed frozen after promotions (same failure class as O5) | Daily automated re-score + stats refresh; re-score after every promotion |

Do not reopen R1–R23 as-is on this gallery and 12 GB GPU. Reopen fine-tuning only with a different backbone or much more photos per confused pair. R24 and R25 are re-test candidates (see above), not confirmed reversals.

## Candidate queue (2026-09-21)

| ID | Idea | How it will be judged |
|----|----|----|
| C1 | kNN-neighbourhood density / dispersion as an out-of-catalog score | AUROC on observations of species outside the catalog |
| C2 | High entropy + disagreement with zero-shot → publish at genus/family only | Precision/coverage vs species-level publication |
| C3 | Temporal (month) prior P(species \| month, location) next to the existing geographic prior | Paired McNemar, per-species balance |
| C4 | Class-size-compensated k-NN vote (cap/normalise per species) | Recover the ≈−0.6 pp dilution on species that did not grow without new photos |
| C5 | Zero-shot second opinion for non-bird groups (catalog + regional lists) and the rescue tier | Recent-observation KPI, 1-day AutoID trial audit against community IDs |
| C6 | Publish at genus for confusable complexes (gulls, warblers, shearwaters, Accipiter/Astur) | Precision at genus vs species abstention |
| C7 | Ablation: index without the 1,720 “no catalog” classes (19,460 vectors, 1.8%; median 16 vectors/species; 0.16% of eval observations land in one) | McNemar on catalog eval + recent-observation sample |

## Considered and declined (no GPU spent — reasoning only, not measured)

Ideas evaluated and set aside before running anything, with the specific reason each was dropped. Recorded so they aren't re-investigated later without new information.

| ID | Idea | Why declined |
|----|------|----|
| D1 | Generative AI upscaler (diffusion-based, e.g. Crystal/Clarity Upscaler) to improve gallery photo quality | Diffusion upscalers hallucinate plausible detail rather than recovering real information — a real risk for species ID, where invented texture/pattern could actively mislead the encoder. Also trained/optimized for portraits and faces, a domain mismatch with wildlife. Same failure family as R20 (background neutralization, −0.92 to −3.48pp) and R8 (weighted expert crops, −0.9pp): altering the image beyond what the sensor captured has consistently hurt here. Separately: if offered as a user-facing photo filter, the enhanced (not original) image is what gets published to the source observation platform — an accuracy risk becomes a data-integrity risk for the wider citizen-science record. Not tested. |
| D2 | pgvector (Postgres extension) to replace/complement FAISS for serving k-NN search | Would simplify operations (embeddings already live next to the rest of the app's data in Postgres; today every gallery change means rebuilding a separate FAISS index file and reloading the service) but does not change the underlying similarity computation — no accuracy path. The bottleneck this project has actually hit is embedding compute (GPU), not search latency. Queued as an infrastructure simplification, not prioritized against anything that moves accuracy. Not tested. |
| D3 | BIOSCAN-5M (5.15M-specimen multimodal insect dataset, image+DNA+taxonomy) as extra training/reference data | Checked against the actual catalog before assuming it would help: only 121/2,985 species (~4%) are insects, and they already average 95.3% accuracy (88/121 at 100%, none below 20%) — not an underperforming group with room to gain from extra data. The dataset's open-world/zero-shot classification methodology (recognizing "not any known class" rather than forcing a wrong label) may still be worth reading for the unrelated question of abstention on genuinely novel observations. Not tested. |
| D4 | Feature-space mixup/CutMix or ArcFace/CosFace heads to help small classes | With a frozen encoder and a k-NN there is no new information in interpolated features; margin heads already tied or lost (R4–R7) |
| D5 | CLIP text “negative anchors” (“an animal not in the catalog”) as the open-set detector | Contrastive text encoders represent absence/negation poorly; prefer a broader open vocabulary (zero-shot over a larger checklist) plus density/entropy signals (C1–C2) |
