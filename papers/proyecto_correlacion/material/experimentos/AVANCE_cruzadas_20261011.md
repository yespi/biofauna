# Avance v26 — Tendencias cruzadas / comunidades / cascadas (11-oct-2026)

**Script:** `scripts/tendencias_cruzadas_correlacion_20261011.py`  
**Salidas:** `experimentos/cruzadas_*.csv|json` · `figuras/cruzadas/*.png`  
**Artículo:** `ARTICULO.md` / `ARTICLE.md` §2.10 y §3.9

## Método (resumen)
- Datos: `public_observations`, caja CAT, zonas Costa Brava / Barcelona / Tarragona–Ebro.
- Proporción esfuerzo-corregida \(n/E\times1000\); z-scores; breakpoints heurísticos.
- Xcorr de **primeras diferencias**, lag 0–3, BH-FDR, ≥8 años, ≥40 obs.
- Clustering jerárquico (correlación) + PCA sobre ~120 spp.
- Cascadas: antes/después permutacional en anclas documentadas + FDR.
- GloBI sobre especies en aumento; bibliografía detonantes con DOI Crossref.
- **Correlación ≠ causalidad.**

## Cifras
| Métrica | Valor |
|---|---:|
| Taxones marinos match | 267 |
| Elegibles (≥40 obs) | 255 |
| Series ≥8 años (cribado) | 120 |
| Pares xcorr | 7.140 |
| Top figuras | 20 |
| Clústeres / con ≥10 spp | 6 / ≥2 (C1=78, C3=21, C5=14, …) |
| Tests cascada / q≤0,05 | ver `cruzadas_cascadas_baci_20261011.csv` |

## Detonantes (DOI OK)
| Evento | Año ancla | DOI |
|---|---|---|
| *Pinna* MM España | **2016** (no 2014) | 10.3389/fmars.2017.00220 |
| *Haplosporidium pinnae* | 2018 | 10.1016/j.jip.2018.07.006 |
| MHW Med | 2022 (ctx) | 10.1111/gcb.16301 |
| VNN *Epinephelus* | 2014, 2020 | 10.3147/jsfp.49.53 · 10.6018/analesbio.42.07 |
| *Pinna rudis* tras *nobilis* | 2021 | 10.12681/mms.27809 |
| VNN 2023+ Cataluña | — | **sin DOI** → hipótesis |

## Casos de prueba
Ver `cruzadas_pares_prueba_20261011.csv` (Pinna–Pinna r≈−0,49; Pelagia–*Paracentrotus* r≈−0,63; *E. marginatus*–pulpo r≈−0,72).

## Pendiente
- JSDM/ocupación formal; BACI con zonas control limpias; curadores sobre top-20; DOI primarios para pares HIPÓTESIS.
