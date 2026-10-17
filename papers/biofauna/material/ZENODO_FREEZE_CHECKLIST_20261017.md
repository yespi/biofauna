# Zenodo — versión congelada BioFauna (checklist pre-depósito)

Fecha objetivo: envío del manuscrito principal. **DOI:** pendiente.

| Artefacto | Ruta / nota | SHA o versión |
|---|---|---|
| Índice FAISS producción citado | `versions/` o manifiesto promote p19 | pendiente hash en depósito |
| Panel rescore | `dataset/calib_raw_t05.jsonl` | commit git |
| Subconjuntos §5.6 | scripts que generan limpio v3 y sin fuga | `papers/biofauna/material/` |
| Catálogo | `dataset/catalog.json`, `target_species.json` | commit git |
| Calibradores / priors | `data/calibration*.json`, `geo_prior.json` | commit git |
| Código rescore mínimo | `scripts/` + `requirements.txt` | tag git `freeze-YYYY-MM-DD` |

**Excluido del ZIP Zenodo:** fotografías, `embeddings.npy` por foto, claves API.

**Post-depósito:** actualizar cabecera del manuscrito con DOI y enlace Zenodo.
