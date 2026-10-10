# Calendario de observación de los nudibranquios (Cataluña)

**Estado: artículo de divulgación 10-oct-2026** (Robotin / OK Gustavo). Incluye **doridoideos** (*Felimare*, *Peltodoris*, *Hypselodoris*, *Dendrodoris*, …), no solo aeolideos.

## Entregables principales

| Documento | Descripción |
|---|---|
| [`ARTICULO_20261010.md`](ARTICULO_20261010.md) · [`ARTICULO_20261010.pdf`](ARTICULO_20261010.pdf) | Artículo naturalista (resumen, métodos, resultados, discusión, referencias) |
| [`LAMINA1_calendario_fenologico_20261010.pdf`](LAMINA1_calendario_fenologico_20261010.pdf) · [`.png`](LAMINA1_calendario_fenologico_20261010.png) | Calendario ~30 especies, familias, 12 meses, normalizado por esfuerzo |
| [`LAMINA2_rosas_estaciones_20261010.pdf`](LAMINA2_rosas_estaciones_20261010.pdf) · [`.png`](LAMINA2_rosas_estaciones_20261010.png) | Rosas radiales (12 spp.) + panel estacional |
| [`LICENCIAS_FOTOS.md`](LICENCIAS_FOTOS.md) | Atribución CC BY / BY-SA / CC0 |
| [`datos/`](datos/) | CSV mensual y esfuerzo marino |

## Datos y método (resumen)

- **Fuente:** `public_observations` (BD `fauna`, contenedor `postgres-global`) — iNaturalist + Minka; **solo `SELECT`**.
- **Área:** caja costera Cataluña (lat 40,45–42,95; lon 0,10–3,40; definición BioQuest 8-oct-2026).
- **Taxonomía:** 351 especies con `order` ∈ {Nudibranchia, Doridida, Dendronotida} en `dataset/target_species.json`.
- **Normalización:** por mes, obs. de la especie ÷ obs. de **taxones marinos del catálogo BioFauna** en la misma caja (proxy de esfuerzo de buceo; el verano tiene más denominador y numerador).

Reproducir figuras y PDF:

```bash
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_articulo_generar_20261010.py
```

## Histórico

- [`CALENDARIO_BORRADOR_20261008.md`](CALENDARIO_BORRADOR_20261008.md): borrador mediterráneo (133 aeolideos-only); [`REVISION_ALCANCE_20261010.md`](REVISION_ALCANCE_20261010.md).
- Script anterior: [`../../scripts/nudi_calendario_20261008.py`](../../scripts/nudi_calendario_20261008.py).
