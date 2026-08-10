## API Reference (Self-Hosted)

The identification service runs as a FastAPI server on port 8090 (`scripts/identify_service.py`).

### Endpoints

#### `POST /identify`

Upload an image for species identification.

**Request**: Multipart form with `file` field (JPEG/PNG)  
**Query params**: `topk` (default 5), `lat`, `lon`, `date`

**Response** (shape may vary slightly by build):
```json
{
  "source": "biofauna-local",
  "method": "knn",
  "prediction": {
    "rank": "species",
    "name": "Actinia striata",
    "confidence": 0.6973,
    "p_species": 0.9234,
    "calibrated": true
  }
}
```

**Fields**:
- `rank`: `species`, `genus`, or `family`
- `p_species`: Calibrated probability
- `confidence`: Raw k-NN score (not a calibrated probability)

#### `GET /health`

Reports device and loaded species count (active gallery size depends on `dataset/patterns/`).

#### `POST /reload`

Hot-reload patterns and calibration without restarting (when enabled).

### Auto-Publication Thresholds

Production recommendation: **`p_species >= 0.90`** → **95.5% precision**, **30.2% coverage** (ViT-H, k=15, 2026-08-10 calibration).

Below threshold, FotoFauna cross-checks with iNaturalist CV before publishing.
