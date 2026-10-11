# Listados del proyecto de correlación (v20, 6-oct-2026)

**Criterio vigente:** una pareja solo cuenta como asociación si ambas especies aparecen en la **misma fotografía**. Los listados de co-ocurrencia por eventos son material de **hipótesis** (cribado), no conclusiones. Todo está en https://github.com/yespi/biofauna.

| Fichero | Contenido |
|---|---|
| `copresencia_pares_20261006.csv` | **138 parejas de la lista corta** con nº de fotos analizadas, fotos candidatas con ambas especies (en fotos de A y de B) y tasa de control |
| `copresencia_hits_20261006.jsonl` | fotos candidatas (nombre de fichero de la galería, vista y similitud) para la revisión a ojo |
| `nulo_exacto_pares_significativos_q05_20261005.csv` | cribado por eventos: 51.401 parejas con q ≤ 0,05 (esfuerzo local controlado) — solo hipótesis |
| `nulo_exacto_pares_robustos_razon3_20261005.csv` | cribado: 3.108 parejas replicadas con razón ≥ 3 |
| `pares_robustos_mediterraneos_distinto_genero_20261005.csv`, `pares_candidatos_nuevos_*_20261005.csv` | cribado: subconjuntos mediterráneos y «top 30» |
| `archivo_cribado_2026-09/` | listados del primer análisis por lift (obsoletos; no citar como resultado) |

Columnas del cribado: `a`, `b` (especies), `n` (eventos con ambas), `esperado_esfuerzo`, `ratio` = n/esperado, `z`, `p`, `q` (BH), `celdas`, `dias`, `observadores`, `med_frac`, `genero_*`, `grupo_*`, `score` = ln(ratio)·ln(n)·min(observadores,20)/20. Columnas de `copresencia_pares`: `fotos_a`/`fotos_b` (fotos escaneadas), `hits_b_en_a` (fotos de A con B detectada), `hits_a_en_b`, `obs_indep_hits` (nota: cuenta de ficheros, no de observaciones; usar el recuento por observación del artículo), `control_tasa_*`.

Las fotos de las láminas, con autor, licencia, fecha y hora, lugar y enlace: `papers/proyecto_correlacion/lamina_fotos/lamina_manifest_20261006.json`.
