# Listados del proyecto de correlación (v18, 6-oct-2026)

Todas las tablas son de **pares de especies** (sin fotografías ni datos de observadores; solo recuentos). Evento = observador × celda ~1 km × día × franja de 3 h; bloque = celda 0,1°·día. Código: `scripts/nulo_exacto_todos_pares_20261005.py` (repositorio de producción) y `scripts/paper_figuras_20261005.py`.

| Fichero | Contenido | Filas |
|---|---|---:|
| `nulo_exacto_pares_significativos_q05_20261005.csv` | **lista completa** de pares con q ≤ 0,05 (BH sobre 115.204 pares con n ≥ 5; esperado condicionado al esfuerzo local y al tamaño del evento) | 51.401 |
| `nulo_exacto_pares_robustos_razon3_20261005.csv` | q ≤ 0,05, ≥3 celdas, ≥3 días, ≥5 observadores y razón n/esperado ≥ 3 | 3.108 |
| `pares_robustos_mediterraneos_distinto_genero_20261005.csv` | + ≥80 % de eventos en el Mediterráneo (lat 30-46, lon −6…37) y géneros distintos, con `score` | 2.312 |
| `pares_candidatos_nuevos_top30_20261005.csv` | top 30 por `score` (máx. 2 pares por especie) | 30 |
| `pares_candidatos_nuevos_intergrupo_top30_20261005.csv` | idem, solo grupos taxonómicos distintos | 30 |
| `asociaciones_mediterraneas_20260929.csv`, `asociaciones_top40_20260929.csv` | listados del análisis anterior (lift, 11.509 pares) | — |

Columnas: `a`, `b` (slugs de especie), `n` (eventos con ambas), `esperado_esfuerzo`, `ratio` = n/esperado, `z`, `p`, `q` (BH), `celdas`, `dias`, `observadores` (distintos), `med_frac` (fracción de eventos en el recuadro mediterráneo), `genero_*`, `grupo_*`. `score` = ln(ratio)·ln(n)·min(observadores,20)/20.

**Cómo leerlos.** La significación sola no discrimina (la mitad de los pares con soporte tiene q ≤ 0,05 porque las especies de un mismo hábitat se agregan dentro del bloque); usar el tamaño de efecto y la replicación. Los «nuevos» no están comprobados contra la bibliografía.
