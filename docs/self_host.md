## Self-Hosting Guide

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | None (CPU) | 8+ GB (NVIDIA) |
| RAM | 4 GB | 8 GB |
| Disk | 2 GB | 5 GB |
| OS | Linux/macOS | Ubuntu 22.04+ |

BioCLIP with QLoRA fine-tuning uses ~1.65 GB VRAM, fitting on consumer GPUs like RTX 3060 (12 GB).

### Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Obtain model weights**:
   Contact the repository owner for the model package (~75 MB). Extract to `./data/`.

3. **First run** (downloads BioCLIP backbone, ~1.6 GB):
   ```bash
   python -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090
   ```

4. **Test**:
   ```bash
   curl -X POST http://localhost:8090/identify \
     -F "file=@test_photo.jpg"
   ```

### Docker Deployment

```dockerfile
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY data/ ./data/
COPY src/ ./src/
CMD ["python", "-m", "uvicorn", "src.identify_service:app", "--host", "0.0.0.0", "--port", "8090"]
```

### Performance

- Inference speed: ~0.3s/image on RTX 3060
- First startup: 60-90s (model loading + Hot reloading)
- Hot reload: Instant (supports `POST /reload` for model updates)
- Batch processing: Handles concurrent requests via async FastAPI

### Model Updates

The model can be updated without downtime:
1. Place new prototype files in `data/patterns/`
2. Update `data/calibration.json` if recalibrated
3. Call `POST /reload` — the service hot-reloads in ~5 seconds

### Monitoring

- `GET /health` — returns `{"ok": true, "device": "cuda", "species": 1369}`
- Check VRAM usage: `nvidia-smi`
- Logs written to stdout (container-friendly)
