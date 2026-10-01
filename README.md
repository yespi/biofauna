# BioFauna

**Mediterranean marine identification by retrieval.** Formerly YOLOFauna. Production: **frozen BioCLIP-2.5 ViT-H + k-NN (k=15, T=0.05)**.

Live: [fotofauna.yespi.es](https://fotofauna.yespi.es) · Paper: [EN](papers/biofauna/01_biofauna.md) · [ES](papers/biofauna/01_biofauna_es.md)

**Papers:** [BioFauna EN](papers/biofauna/01_biofauna.md) · [ES](papers/biofauna/01_biofauna_es.md) (PDF: [EN](papers/biofauna/BIOFAUNA_paper_EN_20261001.pdf) · [ES](papers/biofauna/BIOFAUNA_paper_ES_20261001.pdf)) · [Proyecto Correlación](papers/proyecto_correlacion/README.md) (PDF actual: [ES](papers/proyecto_correlacion/ARTICULO_v16_ES_20260930.pdf) · [EN](papers/proyecto_correlacion/ARTICLE_v16_EN_20260930.pdf) · previa: [ES v15](papers/proyecto_correlacion/ARTICULO_v15_ES_20260930.pdf) · [EN v15](papers/proyecto_correlacion/ARTICLE_v15_EN_20260930.pdf) · [Láminas](papers/proyecto_correlacion/LAMINAS_v5_20260929.pdf))

## Snapshot (2026-10-01)

| | |
|---|---|
| Gallery | **1,118,298** embeddings / **4,543** species (FAISS aligned) |
| Catalog | **2,985** taxa with Minka/iNat IDs ([`dataset/catalog.json`](dataset/catalog.json)) |
| Classifier | k-NN k=15, T=0.05, **max 3 votes per species** (K23), ROI fusion, calibrated abstention, zero-shot rescue |
| Field eval (out-of-sample, leak-purged) | **82.34%** species / 87.1% genus / 90.5% family (n=76,585, 2,946 species) |
| — of which original eval / mined extension | **81.18%** (n=60,743, comparable with earlier versions) / 85.5–89.9% (n=15,842; same-species accuracy equivalent: 86.8% vs 86.1%) |
| Real precision of AutoID publications | **96.6%** (n=493 verifiable; 85% in the 0.83–0.85 band, 99% at ≥0.95) |
| AutoID | 45/hour, 1,500/day, per-species calibrated threshold (≈0.83), margin + curator guards; **crop fallback** (since 2026-10-01) rescues photos the full image cannot identify: 35 → 48 publishable in 500 real queue photos, 85.7% of the added ones correct (n=49, ground truth) |
| Inference | exact k-NN on GPU (fp16, fp32 re-scoring): ≈0.2 s per call (was 0.7 s); six-crop identification of one photo 0.97 s (was 4.4 s) |
| This repo ships | Prototypes, calibrators, geo priors, exceptions, taxon IDs, evaluation/leak-audit scripts, papers |
| Not shipped | Photographs, per-photo `embeddings.npy` |

**2026-09-23:** an audit found that half of the evaluation rows were copies of gallery photos; they were removed and all earlier panel figures (85.78%, 90.52%, 92.36%, 93.4%) are superseded. See [paper](papers/biofauna/01_biofauna.md) (update box, O18) and [EXPERIMENTS](docs/EXPERIMENTS.md).

## Quick start (nearest-centroid demo)

```bash
git clone https://github.com/yespi/biofauna.git && cd biofauna
pip install -r requirements.txt
python -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090
# first run downloads imageomics/bioclip-2.5-vith14 from Hugging Face
curl -s http://127.0.0.1:8090/health
curl -X POST http://127.0.0.1:8090/identify -F "file=@photo.jpg"
```

Full k-NN (production-class) needs a local photo gallery + `embeddings.npy` per species. See [`docs/dataset.md`](docs/dataset.md), [`docs/self_host.md`](docs/self_host.md), [`docs/cron.md`](docs/cron.md), and [`scripts/README.md`](scripts/README.md).

## Docs

| | |
|---|---|
| [API](docs/api.md) | Public `X-API-Key` flow + `/vision/biofauna/identify` and self-hosted endpoints |
| [STATUS](docs/STATUS.md) | Current public snapshot |
| [EXPERIMENTS](docs/EXPERIMENTS.md) | Kept vs rejected trials |
| [HISTORY](docs/HISTORY.md) | YOLOFauna → BioFauna |
| [FotoFauna bulk photos](docs/ff_download.md) | Admin ZIP export from FotoFauna (photos not in this repo) |
| [cron](docs/cron.md) | Weekly jobs BF-01…BF-10 + systemd example |
| [archive](docs/archive/README.md) | Stale August notes (e.g. closed archive gap) |

## Licence

MIT for code and released JSON/prototypes. Photo copyright stays with observers and Minka/iNaturalist.
