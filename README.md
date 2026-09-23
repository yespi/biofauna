# BioFauna

**Mediterranean marine identification by retrieval.** Formerly YOLOFauna. Production: **frozen BioCLIP-2.5 ViT-H + k-NN (k=15, T=0.05)**.

Live: [fotofauna.yespi.es](https://fotofauna.yespi.es) · Paper: [EN](paper/01_biofauna.md) · [ES](paper/01_biofauna_es.md)

## Snapshot (2026-09-23)

| | |
|---|---|
| Gallery | **1,072,233** embeddings / **4,705** species (FAISS aligned) |
| Catalog | **2,985** taxa with Minka/iNat IDs ([`dataset/catalog.json`](dataset/catalog.json)) |
| Classifier | k-NN k=15, T=0.05, **max 3 votes per species** (K23), ROI fusion, calibrated abstention |
| OOS accuracy (leak-free) | **88.11%** species / **90.55%** genus / **92.46%** family (n=12,373, 2,091 species) |
| Real-world check | ~80% on recent research-grade Minka observations (operating KPI) |
| This repo ships | Prototypes, calibrators, geo priors, exceptions, taxon IDs, evaluation/leak-audit scripts |
| Not shipped | Photographs, per-photo `embeddings.npy` |

**2026-09-23:** an audit found that half of the evaluation rows were copies of gallery photos; they were removed and all earlier panel figures (85.78%, 90.52%, 92.36%, 93.4%) are superseded. See [paper](paper/01_biofauna.md) (update box, O18) and [EXPERIMENTS](docs/EXPERIMENTS.md).

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
| [STATUS](docs/STATUS.md) | Current public snapshot |
| [EXPERIMENTS](docs/EXPERIMENTS.md) | Kept vs rejected trials |
| [HISTORY](docs/HISTORY.md) | YOLOFauna → BioFauna |
| [FotoFauna bulk photos](docs/ff_download.md) | Admin ZIP export from FotoFauna (photos not in this repo) |
| [cron](docs/cron.md) | Weekly jobs BF-01…BF-10 + systemd example |
| [archive](docs/archive/README.md) | Stale August notes (e.g. closed archive gap) |

## Licence

MIT for code and released JSON/prototypes. Photo copyright stays with observers and Minka/iNaturalist.
