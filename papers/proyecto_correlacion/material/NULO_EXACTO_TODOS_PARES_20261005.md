# Contraste de co-ocurrencia condicionado al esfuerzo local, todos los pares (5-oct-2026)

Script `scripts/nulo_exacto_todos_pares_20261005.py` (PLAN_PAPER hueco 1). Evento = observador × celda 0,01° × día × franja 3 h; bloque = celda 0,1° × día. Esperado bajo independencia condicionado al esfuerzo (nº de eventos del bloque y su tamaño); BH sobre **todos** los pares con n≥5 (115,204), no solo el top por lift.

| | pares |
|---|---:|
| testeados (n≥5) | 115,204 |
| q≤0,05 | 51,401 |
| q≤0,05 y ≥3 celdas, ≥3 días, ≥5 observadores | 27,444 (de 58,022 robustos) |
| …además razón n/esperado ≥2 | 10.586 |
| …razón ≥3 | 3.108 |
| …razón ≥5 | 803 |
| …razón ≥10 | 198 |

**Lectura (honesta):** la significación por sí sola NO discrimina: la mitad de los pares con soporte salen q≤0,05, porque las especies de un mismo hábitat se agregan dentro del mismo bloque aunque el esfuerzo esté controlado (es biología compartida, no interacción). Hay que reportar **tamaño de efecto + replicación** (razón n/esperado, nº de bloques/observadores independientes), no el p. Propuesta para el artículo: niveles de evidencia (razón ≥3 y robusto = candidato; ≥5 = fuerte; ≥10 = muy fuerte) y validación externa de cada nivel contra asociaciones documentadas.

Control con asociaciones documentadas:
- peltodoris_atromaculata + petrosia_ficiformis: n=78 esperado=38.85 razón=2.01 z=8.32 q=7.92e-15 obs=31
- felimare_picta + ircinia_oros: no supera q<=0,05 / no testeado
- cratena_peregrina + eudendrium_racemosum: no supera q<=0,05 / no testeado
- fistularia_commersonii + pterois_miles: n=25 esperado=3.43 razón=7.29 z=13.4 q=6.48e-37 obs=16

Top por z entre los robustos con razón ≥3:

| A | B | n | esperado | razón | z | obs |
|---|---|---:|---:|---:|---:|---:|
| *limacia_clavigera* | *polycera_quadrilineata* | 66 | 2.0 | 33.06 | 54.58 | 19 |
| *cephalopholis_miniata* | *pseudanthias_squamipinnis* | 102 | 4.58 | 22.29 | 54.54 | 55 |
| *phoenix_canariensis* | *washingtonia_robusta* | 31 | 0.56 | 55.8 | 51.78 | 21 |
| *limacia_clavigera* | *okenia_nodosa* | 75 | 2.81 | 26.7 | 49.12 | 15 |
| *chamelea_striatula* | *donax_vittatus* | 80 | 4.05 | 19.76 | 45.4 | 57 |
| *okenia_nodosa* | *polycera_quadrilineata* | 38 | 0.93 | 40.99 | 44.11 | 8 |
| *candiella_lineata* | *limacia_clavigera* | 35 | 0.72 | 48.52 | 41.61 | 9 |
| *nembrotha_cristata* | *nembrotha_milleri* | 76 | 6.26 | 12.15 | 40.69 | 57 |
| *clibanarius_aequabilis* | *columbella_adansoni* | 34 | 1.06 | 32.21 | 38.81 | 30 |
| *archidoris_pseudoargus* | *limacia_clavigera* | 43 | 3.25 | 13.23 | 37.01 | 10 |
| *sambucus_nigra* | *urtica_dioica* | 55 | 2.92 | 18.82 | 35.11 | 52 |
| *sargassum_muticum* | *zostera_marina* | 37 | 1.34 | 27.67 | 34.57 | 29 |
| *chthamalus_stellatus* | *tectarius_striatus* | 44 | 2.39 | 18.42 | 34.42 | 34 |
| *chthamalus_stellatus* | *clibanarius_aequabilis* | 38 | 1.81 | 20.95 | 33.18 | 32 |
| *donax_vittatus* | *spisula_subtruncata* | 20 | 0.38 | 53.14 | 33.06 | 14 |
| *donax_vittatus* | *lutraria_lutraria* | 50 | 2.89 | 17.32 | 32.1 | 35 |
| *flexopecten_glaber* | *tritia_nitida* | 18 | 0.38 | 47.34 | 30.5 | 5 |
| *acanthurus_dussumieri* | *arothron_hispidus* | 11 | 0.15 | 72.6 | 28.36 | 10 |
| *solatopupa_similis* | *zonites_algirus* | 18 | 0.81 | 22.09 | 26.7 | 12 |
| *echium_vulgare* | *hypericum_perforatum* | 19 | 0.7 | 27.07 | 25.85 | 14 |
| *cochlicella_acuta* | *trochoidea_elegans* | 32 | 2.42 | 13.22 | 25.67 | 25 |
| *helicodonta_obvoluta* | *solatopupa_similis* | 14 | 0.79 | 17.68 | 25.33 | 6 |
| *clibanarius_aequabilis* | *tectarius_striatus* | 28 | 1.78 | 15.74 | 24.41 | 24 |
| *limacia_clavigera* | *trapania_lineata* | 15 | 0.52 | 28.85 | 23.97 | 7 |
| *chamelea_striatula* | *mactra_stultorum* | 13 | 0.68 | 19.12 | 23.76 | 13 |
