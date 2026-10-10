# Calendario de observación de los nudibranquios (Cataluña)

**Estado: artículo de divulgación 10-Oct-2026** (revisión láminas). Incluye **doridoideos** (*Felimare*, *Peltodoris*, …), no solo aeolideos.

## Entregables principales

| Documento | Descripción |
|---|---|
| [`ARTICULO_20261010.md`](ARTICULO_20261010.md) · [`ARTICULO_20261010.pdf`](ARTICULO_20261010.pdf) | Artículo naturalista |
| [`LAMINA1_calendario_fenologico_20261010.pdf`](LAMINA1_calendario_fenologico_20261010.pdf) · [`.png`](LAMINA1_calendario_fenologico_20261010.png) | Calendario A3: familia / miniatura / nombre + mapa de calor suavizado |
| [`LAMINA2_rosas_estaciones_20261010.pdf`](LAMINA2_rosas_estaciones_20261010.pdf) · [`.png`](LAMINA2_rosas_estaciones_20261010.png) | Rosas radiales (12 spp.) + panel estacional |
| [`LAMINA3_distribucion_espacial_20261010.pdf`](LAMINA3_distribucion_espacial_20261010.pdf) · [`.png`](LAMINA3_distribucion_espacial_20261010.png) | Distribución espacial A3: mapas CAT/Med-ES, tramos, tendencia, zonas calientes |
| [`LICENCIAS_FOTOS.md`](LICENCIAS_FOTOS.md) | Atribución CC0 / CC BY / CC BY-SA |
| [`datos/`](datos/) | CSV mensual (conteos + índice suavizado) y esfuerzo |

## Método (resumen)

- **Fuente:** `public_observations` — iNaturalist + Minka; solo `SELECT`.
- **Área:** caja costera Cataluña (lat 40,45–42,95; lon 0,10–3,40).
- **Suavizado:** corrección parcial del esfuerzo (γ=0.35) + prior bayesiano débil; meses con poco esfuerzo tramados/gris.
- **Fotos:** iNat / Minka / láminas correlación con licencia libre; si no hay, silueta esquemática.

```bash
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_articulo_generar_20261010.py
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_lamina3_espacial_20261010.py
```
