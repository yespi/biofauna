# BioFauna

**Mediterranean marine identification by retrieval.** Formerly YOLOFauna. Production: **frozen BioCLIP-2.5 ViT-H + k-NN (k=15, T=0.05)**.

Live: [fotofauna.yespi.es](https://fotofauna.yespi.es) · Paper: [EN](paper/01_biofauna.md) · [ES](paper/01_biofauna_es.md)

## Snapshot (2026-09-14)

| | |
|---|---|
| Gallery | **848,883** embeddings / **4,702** species (FAISS aligned) |
| Catalog | **2,985** taxa with Minka/iNat IDs ([`dataset/catalog.json`](dataset/catalog.json)) |
| OOS accuracy | **85.78%** species / **89.15%** genus / **91.41%** family (n=19,087) |
| This repo ships | Prototypes (4,702×1024), calibrator, geo priors, exceptions, taxon IDs |
| Not shipped | Photographs, per-photo `embeddings.npy` |

August 2026 papers quoted ~76–79% on a **different, smaller** harvest. Those rows stay in the experiment ledger; they are not the live number.

## Quick start (nearest-centroid demo)

```bash
git clone https://github.com/yespi/biofauna.git && cd biofauna
pip install -r requirements.txt
python -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090
# first run downloads imageomics/bioclip-2.5-vith14 from Hugging Face
curl -s http://127.0.0.1:8090/health
curl -X POST http://127.0.0.1:8090/identify -F "file=@photo.jpg"
```

Full k-NN (production-class) needs a local photo gallery + `embeddings.npy` per species. See [`docs/dataset.md`](docs/dataset.md) and [`docs/self_host.md`](docs/self_host.md).

## Docs

| | |
|---|---|
| [STATUS](docs/STATUS.md) | Current public snapshot |
| [EXPERIMENTS](docs/EXPERIMENTS.md) | Kept vs rejected trials |
| [HISTORY](docs/HISTORY.md) | YOLOFauna → BioFauna |
| [archive](docs/archive/README.md) | Stale August notes (e.g. closed archive gap) |

## Licence

MIT for code and released JSON/prototypes. Photo copyright stays with observers and Minka/iNaturalist.
