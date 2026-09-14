# Scripts in this repository

Canonical reconstruction tools, synced from HanSolo production **logic** on 2026-09-14.
Hardcoded `/mnt/docker/biofauna` and `/work` paths are replaced by `BIOFAUNA_ROOT` (default: this repo). Photographs are **not** included.

| Script | Role |
|--------|------|
| `../src/identify_service.py` | Public identifier (ViT-H + prototypes; k-NN if you rebuild `embeddings.npy`) |
| `inference_decide.py` | Shared k-NN (k=15, **T=0.05**) + prototype boost + geo blend |
| `reembed_vith.py` | Embed a local photo tree with BioCLIP-2.5 ViT-H |
| `build_faiss_index.py` | FAISS index from `embeddings.npy` (optional `faiss`) |
| `harvest_calib.py` | Observation-stratified Minka harvest + **embedding leak check** (sim>0.999) + ROI 65% |
| `fit_calib.py` | Logistic calibrator → `dataset/calibration.json` |
| `fit_calib_hierarchical.py` | Per-taxon AutoID thresholds |
| `build_geo_priors.py` | GPS priors from Minka |
| `build_cryptic_pairs.py` | Cryptic-pair list (OPK / Minka / iNat) |
| `taxonomy_nomenclature_audit.py` | WoRMS + GBIF name audit (`--dry-run` / `--apply-safe`) |
| `analyze_acc.py` | Cheap in-gallery nearest-centroid diagnostic (needs local embeddings) |
| `api_keys.py` | Env-only tokens (`HF_TOKEN`); no `/mnt/utils` |
| `package_model.sh` | Tarball of prototypes + JSON |

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
