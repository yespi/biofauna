# BioFauna HTTP API

**Last updated:** 2026-09-23

BioFauna identifies Mediterranean marine species from photographs using BioCLIP-2.5 ViT-H + k-NN retrieval. Production traffic reaches the model through **FotoFauna**; the raw identify service on port 8090 stays on the private Docker network.

| Mode | Base URL | Authentication |
|------|----------|----------------|
| **Public (recommended)** | `https://fotofauna.yespi.es/vision/biofauna/identify` | `X-API-Key` (issued by admin) **or** FotoFauna session `Authorization: Bearer <JWT>` |
| **Self-hosted demo** | `http://127.0.0.1:8090` | No auth (local `src.identify_service` in this repo) |
| **Production internal** | `http://biofauna-proxy:8090` | Not exposed to the Internet |

FotoFauna’s full REST surface (PAT tokens `ff_pat_…`, Academy, Minka proxies): [fotofauna `docs/API.md`](https://github.com/yespi/fotofauna/blob/master/docs/API.md).

---

## Request an API key (`X-API-Key`)

`POST /vision/biofauna/identify` does **not** accept anonymous calls. For scripts, mobile apps, or research integrations:

1. Email the administrator: **[gustavo.zafra@gmail.com](mailto:gustavo.zafra@gmail.com)**.
2. Include: intended use, organisation/name, contact email, and whether you need expiry or separate dev/prod keys.
3. You will receive a secret once by email. Store it like a password.
4. Send it on every request:

```http
X-API-Key: <your-secret>
```

**Without a dedicated key:** log in at [fotofauna.yespi.es](https://fotofauna.yespi.es) and use the session JWT as `Authorization: Bearer …` on the same endpoint (fine for manual tests; not ideal for 24/7 automation).

In the FotoFauna UI: **Settings → Help → “API BioFauna y desarrolladores”** (Spanish) describes the same flow.

> **Note:** FotoFauna personal API tokens (`ff_pat_…` from Settings → API BQ) are **not** the same as the BioFauna `X-API-Key`.

---

## `POST /vision/biofauna/identify` (public)

| Part | Value |
|------|--------|
| Method | `POST` |
| URL | `https://fotofauna.yespi.es/vision/biofauna/identify` |
| Auth | `X-API-Key` or `Authorization: Bearer <FF JWT>` |
| Body | `multipart/form-data`, field **`file`** (JPEG/PNG, max 30 MB) |
| Query | `topk` (int, default `5`) |

### curl

```bash
export BF_API_KEY="…"

curl -sS -X POST "https://fotofauna.yespi.es/vision/biofauna/identify?topk=5" \
  -H "X-API-Key: ${BF_API_KEY}" \
  -F "file=@photo.jpg" | jq .
```

### Python

```python
import requests

with open("photo.jpg", "rb") as f:
    r = requests.post(
        "https://fotofauna.yespi.es/vision/biofauna/identify",
        headers={"X-API-Key": "YOUR_KEY"},
        files={"file": f},
        params={"topk": 5},
        timeout=60,
    )
r.raise_for_status()
pred = r.json()["prediction"]
print(pred["name"], pred.get("p_species"))
```

### Response (200)

```json
{
  "source": "biofauna-local",
  "method": "faiss",
  "top": {
    "slug": "octopus_vulgaris",
    "species": "Octopus vulgaris",
    "similarity": 0.694,
    "minka_taxon": 12345,
    "inat_taxon": 47120
  },
  "prediction": {
    "rank": "species",
    "name": "Octopus vulgaris",
    "id": 12345,
    "id_source": "minka",
    "confidence": 0.694,
    "p_species": 0.8234,
    "calibrated": true,
    "threshold": 0.75
  },
  "results": [{"species": "Octopus vulgaris", "similarity": 0.694}],
  "num_photos_processed": 1
}
```

| Field | Meaning |
|-------|---------|
| `prediction.confidence` | Raw k-NN cosine similarity — not calibrated |
| `prediction.p_species` | Calibrated probability — **use for thresholds** (e.g. auto-publish ≥ 0.80) |
| `prediction.rank` | `species`, `genus`, `family`, or `group` (cryptic clusters) |
| `method` | `faiss`, `knn`, `proto`, or `arcface` (internal only) |

### Errors

| HTTP | Cause |
|------|--------|
| `401` | Missing/invalid `X-API-Key` or session |
| `413` | File > 30 MB |
| `503` | Engine unavailable |

---

## Self-hosted service (`src.identify_service`)

This repository ships a **reconstruction** service (prototypes + calibrators, not the full production gallery).

```bash
git clone https://github.com/yespi/biofauna.git && cd biofauna
pip install -r requirements.txt
python -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090
curl -s http://127.0.0.1:8090/health
curl -X POST http://127.0.0.1:8090/identify -F "file=@photo.jpg"
```

### Endpoints (local / internal)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Device, species count, FAISS stats |
| `GET` | `/species` | Slug list |
| `POST` | `/reload` | Reload prototypes / FAISS / calibration |
| `POST` | `/embed` | Multipart `file` → 1024-d embedding vector |
| `POST` | `/identify` | Identify (alias `POST /biofauna`) |

**Internal-only query params** on `/identify`: `topk`, `lat`, `lon`, `date`, `classifier` (`knn` | `arcface`), multipart `files` for multi-photo fusion.

`POST /embed` returns the global L2-normalised ViT-H vector (used by leak-audit tooling).

Production FotoFauna AutoID uses **p_species ≥ 0.80**. The public reconstruction service does not publish to Minka.
