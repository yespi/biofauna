# Scripts in this repository

Canonical reconstruction tools, synced from HanSolo production **logic** on 2026-09-23.
Hardcoded `/mnt/docker/biofauna` and `/work` paths are replaced by `BIOFAUNA_ROOT` (default: this repo). Photographs are **not** included.

| Script | Role |
|--------|------|
| `../src/identify_service.py` | Public identifier (ViT-H + prototypes; k-NN if you rebuild `embeddings.npy`) |
| `inference_decide.py` | Shared k-NN (k=15, **T=0.05**, max 3 votes per species) + prototype boost + geo blend |
| `reembed_vith.py` | Embed a local photo tree with BioCLIP-2.5 ViT-H |
| `build_faiss_index.py` | FAISS index from `embeddings.npy` (optional `faiss`) |
| `harvest_calib.py` | Observation-stratified Minka harvest + **leak gate on the global embedding** (≥0.98, fixed 2026-09-23 — O18) + ROI 65% |
| `leak_audit_calib.py` | Re-audits every evaluation row against its species' gallery (global embedding via `/embed`); run after any gallery growth |
| `purge_leaked_eval.py` | Moves leaked rows (≥0.98) out of the evaluation files into a side file, with backup |
| `fit_calib.py` | Logistic calibrator → `dataset/calibration.json` |
| `fit_calib_hierarchical.py` | Per-taxon AutoID thresholds |
| `build_geo_priors.py` | GPS priors from Minka |
| `build_cryptic_pairs.py` | Cryptic-pair list (OPK / Minka / iNat) |
| `taxonomy_nomenclature_audit.py` | WoRMS + GBIF name audit (`--dry-run` / `--apply-safe`) |
| `analyze_acc.py` | Cheap in-gallery nearest-centroid diagnostic (needs local embeddings) |
| `api_keys.py` | Env-only tokens (`HF_TOKEN`); no `/mnt/utils` |
| `package_model.sh` | Tarball of prototypes + JSON |
| `repesca_diaria.py` | BF-01 — fill species short of the photo cap (iNat) |
| `autoaprendizaje_minka.py` / `_inat.py` | BF-02 / BF-03 — research-grade downloads + manifests |
| `reverificar_minka.py` | BF-04 / BF-10 — taxon drift on Minka obs |
| `archive_processed.py` | BF-08 — keep ~300 photos/species locally |
| `renovar_especies.py` | BF-09 — drop oldest photos on saturated species |
| `audit_biofauna.sh` | BF-08 — disk / prototype dim / `/health` |
| `taxonomy_nomenclature_cron.sh` | Weekly WoRMS/GBIF **dry-run** |
| `api_http.py` | iNat/Minka User-Agent + optional env tokens |

Weekly schedule and install: [`../docs/cron.md`](../docs/cron.md) · templates: [`../deploy/`](../deploy/).

```bash
export BIOFAUNA_ROOT=$PWD
export IMAGES_DIR=/path/to/photos_by_slug   # optional
export HF_TOKEN=...                         # optional, avoids Hub rate limits
python3 scripts/reembed_vith.py
python3 scripts/harvest_calib.py 3
python3 scripts/fit_calib.py
```

**Not copied** (HanSolo-only): 400+ one-off staging jobs, AutoID, MiniCPM sidecars, GPU watchdogs.

**Archived:** `archive/negative/` (QLoRA / triplet — documented failures) and `archive/embed_crop_yolo_legacy.py` (YOLO crop + BioCLIP-2 ViT-L; production is CROP_OFF + ViT-H).
