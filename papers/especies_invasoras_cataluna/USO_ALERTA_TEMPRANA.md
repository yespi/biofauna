# Uso práctico: alerta temprana con FotoFauna / AutoID

## Flujo operativo

1. **Cosecha** de observaciones *research grade* en la caja de estudio (iNaturalist + Minka local).
2. **Identificación** con BioFauna (índice de producción citado en el manuscrito; panel S6 para acierto por taxón UE).
3. **Publicación automática** (AutoID en FotoFauna) solo si `p ≥ 0,83` a nivel de especie (precisión histórica ≈96 % en eval cerrado; puede ser menor en observaciones nuevas).
4. **Alerta** manual o por umbral bajo para taxones de alto impacto (`ESPECIES_INVASORAS_ALTO_IMPACTO.md`): revisión curador antes de difundir.

## Precisión medida (lista UE, p19)

- Media ponderada de acierto en especie sobre taxones con `n_eval ≥ 1`: ver Tabla S6 y `material/cobertura_bf_ue_p19_20261016.csv`.
- **8** taxones sin eval independiente (Tabla S7): tratar como «sin métrica» hasta ampliar panel.
- Tendencias del paper usan **GBIF** con GLMM observador; AutoID no altera esas series.

## Mapa de esfuerzo

La Fig. 1 y `material/figuras/area_estudio_esfuerzo_heatmap_20261015.png` muestran densidad de observaciones 2018–2024 junto a mapas de presencia por década: leer presencia **siempre** con el mapa de esfuerzo (§3.3 RESULTADOS).
