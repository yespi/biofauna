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

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Gallery + calibration**:
   Place species pattern directories under `dataset/patterns/` (each with `embeddings.npy`) and copy `results/calibration.json` (or your own) to `dataset/calibration.json`.

3. **First run** (downloads BioCLIP-2.5 ViT-H from HuggingFace on first load):
   ```bash
   python -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090
   ```
   Prefer the maintained service entrypoint from your deployment (`scripts/identify_service.py` on HanSolo) with **k=15** and hierarchical fallback enabled.

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
COPY dataset/ ./dataset/
COPY src/ ./src/
CMD ["python", "-m", "uvicorn", "src.identify_service:app", "--host", "0.0.0.0", "--port", "8090"]
```

### Performance (typical RTX 3060)

- Inference: often **&lt;1 s** per crop after warm-up
- Cold start: tens of seconds (backbone download/load + index)
- Hot reload: `POST /reload` when patterns/calibration change (if enabled)

### Model updates

1. Update `dataset/patterns/` and/or `dataset/calibration.json`
2. Call `POST /reload` or restart the service
3. Re-validate with observation-stratified `harvest_calib` before trusting new numbers

### Monitoring

- `GET /health` — device + loaded species count
- `nvidia-smi` — VRAM
- Only trust accuracy from `harvest_calib` + `fit_calib` (observation ID stratification)
