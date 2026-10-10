# Revisión de alcance — calendario de nudibranquios (10-oct-2026)

## Hallazgo principal: faltan los dóridoideos

El borrador [`CALENDARIO_BORRADOR_20261008.md`](CALENDARIO_BORRADOR_20261008.md) cubre **133** especies = todas las del `target_species.json` con `order=Nudibranchia`.

En el catálogo vivo (`dataset/catalog.json`) hay **142** especies adicionales en familias **doridoideas** (*Discodorididae*, *Chromodorididae*, *Phyllidiidae*, etc.) con `in_live_gallery=true` que **no** están en esa lista corta de 133 (p. ej. *Peltodoris atromaculata*, *Felimare picta*, *Chromodoris*…).

**Conclusión:** el calendario actual describe sobre todo **aeolidaceos, dendronotidos y dotidos**, no el conjunto de nudibranquios del índice BF.

## Sesgo de esfuerzo estival

- Regla del script: caja mediterránea + deduplicación observador/fecha/coord.
- **54/133** especies con ≥20 obs → periodo reportable; el resto «sin dato suficiente».
- Picos en **abril–mayo** y **agosto** reflejan salidas de buceo (FECDAS/Minka), no necesariamente fenología reproductiva.
- **Sant Feliu de Guíxols** y **Marseille** dominan el ranking de localidades → sesgo geográfico.

## Sustrato

**No implementado** en v1 del script (`scripts/nudi_calendario_20261008.py`). Fuentes previstas: literatura, GloBI, fichas DORIS, parejas confirmadas del paper de correlaciones.

## Acciones propuestas

1. Regenerar lista de especies desde **catálogo vivo** (Nudibranchia sensu BF, ~275 spp potenciales) o subconjunto acordado con curadores.
2. Añadir columna **sustrato** (texto + «sin dato»).
3. Documentar sesgo estival en figura de esfuerzo mensual agregado (BioQuest + enrich).
4. Separar **periodo biológico** vs **periodo con datos** (dos columnas).
