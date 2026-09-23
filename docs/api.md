## API — reconstruction service

`src.identify_service:app` on port 8090. Encoder **BioCLIP-2.5 ViT-H**. Gallery: prototypes in `data/patterns/`; k-NN if `embeddings.npy` exist.

### `POST /embed`

Multipart `file`. Returns `{"vec": [1024 floats]}`: the global L2-normalised ViT-H embedding of the whole image (no ROI fusion), i.e. what the gallery stores. Used by `scripts/leak_audit_calib.py` (evaluation leak gate).

### `POST /identify`

Multipart `file` (JPEG/PNG). Optional query: `topk`, `lat`, `lon`.

```json
{
  "source": "biofauna-public",
  "method": "prototype",
  "prediction": {
    "rank": "species",
    "name": "Actinia striata",
    "confidence": 0.71,
    "p_species": 0.92,
    "calibrated": true
  }
}
```

`method` is `"knn"` when a local per-photo gallery is present. `rank` may be `species`, `genus`, `family`, or `group`. `confidence` is raw similarity, not a probability; `p_species` is the logistic calibrator.

### `GET /health`

Device, species count, k-NN vector count.

### `POST /reload`

Reload prototypes / embeddings without restarting.

Production FotoFauna AutoID uses **p≥0.80**. The public service does not publish to Minka.
