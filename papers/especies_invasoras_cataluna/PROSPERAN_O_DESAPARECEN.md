# ¿Prosperan o desaparecen? — invasoras en Cataluña

**Generado:** 2026-10-11 ~19:50 CEST (addendum puntos 5–6). **Sin GPU.**

Tasa anual = `obs_especie / esfuerzo_grupo_o_caja × 1000`.
Esfuerzo: preferente por grupo taxonómico (ancestry iNat en caja CAT); si cobertura <5 % del total, se usa esfuerzo total de la caja.
IC: Poisson ±1,96√obs / esfuerzo. Tendencia: Mann–Kendall sobre la tasa desde la 1ª obs BioQuest.
1ª fecha de referencia: `material/primeras_fechas_20261011.csv` (mínimo lit./BQ/presencia; BF posterior no cuenta como hallazgo).

Clasificación:

- **en_expansion:** Z≥1,64 y ratio 2ª/1ª mitad ≥1,3
- **en_declive:** Z≤−1,64 y ratio ≤0,7
- **estable:** resto con serie suficiente
- **desaparecida:** 0 obs en últimos 5 años y potencia ≥0,95 de haber detectado la tasa histórica
- **desaparecida_proxy:** 0 obs recientes sin potencia suficiente
- **dato_escaso / sin_serie:** n insuficiente

## Resumen

| Categoría | N |
|---|---:|
| estable | 28 |
| dato_escaso | 5 |
| en_expansion | 4 |
| sin_serie | 3 |
| desaparecida_proxy | 1 |

CSV: [`material/prosperan_desaparecen_20261011.csv`](material/prosperan_desaparecen_20261011.csv). Figura principal (cuerpo): [`material/figuras/prosperan_panel_top8.png`](material/figuras/prosperan_panel_top8.png) (*Caulerpa cylindracea*, *Callinectes sapidus*, *Oculina patagonica*, *Magallana gigas*, *Asparagopsis armata*, *Ailanthus altissima*, *Vespa velutina nigrithorax*, *Procambarus clarkii*). Resto: [`material/figuras/prosperan_suplementario.pdf`](material/figuras/prosperan_suplementario.pdf) (1–2 gráficas/página). Series: [`material/figuras/prosperan/`](material/figuras/prosperan/).

## Destacadas: declive o desaparición

| Especie | Cat. | tau | Z | 1ª fuente | 1ª–últ. BQ | n | potencia | Nota |
|---|---|---:|---:|---:|---|---:|---:|---|
| *Reynoutria sachalinensis* | desaparecida_proxy | — | — | 2020 | 2020–2020 | 1 | 0.984 | 0 obs últimos 5 a; potencia/n insuficiente (p_miss=0.01584814973514668; n_hist=1) |

## Lectura

1. El esfuerzo caja crece ~84× (2013→2024): sin normalizar, casi todo «expande».
2. **desaparecida** exige potencia estadística; **desaparecida_proxy** es solo «no vista».
3. La 1ª fecha de literatura puede ser décadas anterior a BioQuest; la serie gráfica empieza en la 1ª obs BQ.
4. GLM Poisson formal con offset queda como mejora; aquí Mann–Kendall + IC Poisson + potencia de ausencia.

