## API Reference (Self-Hosted)

The identification service runs as a FastAPI server on port 8090.

### Endpoints

#### `POST /identify`

Upload an image for species identification.

**Request**: Multipart form with `file` field (JPEG/PNG)
**Query params**: `topk` (default 5), `lat`, `lon`, `date`

**Response**:
```json
{
  "source": "yolofauna-local",
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
- `p_species`: Calibrated probability (well-calibrated, ECE=0.045)
- `confidence`: Raw k-NN cosine similarity (NOT calibrated)

#### `GET /health`

```json
{"ok": true, "device": "cuda", "species": 1369}
```

#### `POST /reload`

Hot-reload prototypes and calibration data without restarting.

### Auto-Publication Thresholds

| p_species >= | Precision | Coverage |
|-------------|-----------|----------|
| 0.90 | 92.2% | 30% |
| 0.85 | 92.1% | 38% |
| 0.80 | 90.5% | 43% |
| 0.75 | 88.7% | 49% |

Recommendation: use `p_species >= 0.90` for auto-publication to citizen science platforms.
