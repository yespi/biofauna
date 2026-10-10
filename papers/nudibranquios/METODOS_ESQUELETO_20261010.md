# Nudibranquios — esqueleto de métodos (10-oct-2026)

Paper separado del de correlaciones. **Borrador estructural; sin resultados GPU.**

## 1. Pregunta

¿Qué asociaciones nudibranquio–sustrato/presa están respaldadas por **ambas especies en la misma fotografía** en la galería mediterránea, y con qué acierto las identifica BioFauna frente a otros grupos?

## 2. Datos

| Fuente | Uso |
|---|---|
| Galería BioFauna | ≥1,22 M fotos; metadatos 759.207 obs (`enrich_obs_metadata_progress_20260919.json`) |
| Lista corta | `artifacts/nudi_shortlist_pares_20261006.csv` (150 parejas / 86 spp) |
| Eval | `calib_raw_t05.jsonl`, `bf_eval_error_confusion_pairs_20260925.csv` |
| Curación | Minka SDG, iNaturalist, GROC, SeaSlug Forum, DORIS |

## 3. Criterio de asociación

Igual que correlaciones v24: **misma fotografía** (escala cm); co-ocurrencia por eventos solo para generar hipótesis.

## 4. Métricas del identificador

- Acierto especie/género en Nudibranchia vs resto de heterobranquios (Tier 0).
- Escaneo GPU pendiente: segunda especie propuesta en misma foto sobre las 86 spp (≈40 min; no ejecutado en esta sesión).

## 5. Figuras previstas

- Láminas por pareja confirmada (autor, licencia, lugar, coordenadas).
- Matriz de confusión intra-Nudibranchia (top pares del eval).

## 6. Limitaciones

OOS global **83,22 %** (`dataset/stats.json`, promote invasoras 10-oct-2026; 1.216.896 vec / 4.643 spp); pares crípticos en `cryptic_pairs.jsonl`; sesgo de observadores costeros. El calendario fenológico (dóridos, esfuerzo estival, sustrato) lo mantiene otro agente — no se edita aquí.

## 7. Estado

Esqueleto listo; falta escaneo misma-foto, redacción resultados y revisión curadores.
