## Self-Hosting Guide — BioFauna

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | CPU-only possible (slow) | **8–12 GB** NVIDIA (RTX 3060 works) |
| RAM | 8 GB | 16 GB |
| Disk | ~5 GB (model + patterns) | 50+ GB if mirroring images |
| OS | Linux | Ubuntu 22.04+ |

Production inference (frozen **BioCLIP-2.5 ViT-H** + k-NN) uses ~**4.4 GB** VRAM on an RTX 3060. Fine-tuning experiments are optional and not required to run the identifier.

### Setup

1. **Clone + install dependencies**:
   ```bash
   git clone https://github.com/yespi/biofauna.git && cd biofauna
   pip install -r requirements.txt
   ```

2. **Gallery + calibration** — ship ready to run, no manual copy needed:
   `data/patterns/<slug>/prototype.npy` (4,702 species, nearest-centroid gallery) and `data/calibration.json` are already in the repo. This gives you a working nearest-centroid classifier out of the box. For the full k=15 k-NN gallery (per-photo `embeddings.npy`, much larger, not redistributed here — see [`dataset.md`](dataset.md)), rebuild it yourself with `src/embed_crop.py` / `src/reembed_vith.py` over your own photo set and drop `embeddings.npy` next to each species' `prototype.npy`.

3. **First run** (downloads BioCLIP-2.5 ViT-H from HuggingFace on first load):
   ```bash
   python -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090
   ```
   Reads `data/` and `dataset/` relative to the repo root by default; point `BIOFAUNA_ROOT` at a different directory if you keep your own copy elsewhere.

4. **Test**:
   ```bash
   curl -X POST http://localhost:8090/identify -F "file=@test_photo.jpg"
   curl -s http://localhost:8090/health
   ```

### Docker (sketch)

```dockerfile
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY data/ ./data/
COPY dataset/ ./dataset/
COPY src/ ./src/
CMD ["python", "-m", "uvicorn", "src.identify_service:app", "--host", "0.0.0.0", "--port", "8090"]
```

### Performance (typical RTX 3060)

- Inference: often **&lt;1 s** per crop after warm-up
- Cold start: tens of seconds (backbone download/load + index)
- Hot reload: `POST /reload` when patterns/calibration change (if enabled)

### Model updates

1. Update `data/patterns/` and/or `data/calibration.json`
2. Call `POST /reload` or restart the service
3. Re-validate with observation-stratified `harvest_calib` before trusting new numbers

### Monitoring

- `GET /health` — device + loaded species count
- `nvidia-smi` — VRAM
- Only trust accuracy from `harvest_calib` + `fit_calib` (observation ID stratification)
