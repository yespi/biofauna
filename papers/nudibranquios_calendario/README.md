# Calendario de observación de los nudibranquios (Cataluña)

**Estado: artículo de divulgación 10-Oct-2026** (revisión láminas). Incluye **doridoideos** (*Felimare*, *Peltodoris*, …), no solo aeolideos.

## Entregables principales

| Documento | Descripción |
|---|---|
| [`ARTICULO_COMPLETO_20261010.pdf`](ARTICULO_COMPLETO_20261010.pdf) · [`ARTICULO_COMPLETO_latest.pdf`](ARTICULO_COMPLETO_latest.pdf) | **PDF único:** artículo + láminas 1–4 |
| [`ARTICULO_20261010.md`](ARTICULO_20261010.md) · [`ARTICULO_20261010.pdf`](ARTICULO_20261010.pdf) | Artículo naturalista |
| [`LAMINA1_calendario_fenologico_20261010.pdf`](LAMINA1_calendario_fenologico_20261010.pdf) · [`.png`](LAMINA1_calendario_fenologico_20261010.png) | Calendario A3: familia / miniatura / nombre + mapa de calor suavizado |
| [`LAMINA2_rosas_estaciones_20261010.pdf`](LAMINA2_rosas_estaciones_20261010.pdf) · [`.png`](LAMINA2_rosas_estaciones_20261010.png) | Rosas radiales (12 spp.) + panel estacional |
| [`LAMINA3_distribucion_espacial_20261010.pdf`](LAMINA3_distribucion_espacial_20261010.pdf) · [`.png`](LAMINA3_distribucion_espacial_20261010.png) | Distribución espacial A3: mapas CAT/Med-ES, tramos, tendencia, zonas calientes |
| [`LAMINA4_poster_guia_20261010.pdf`](LAMINA4_poster_guia_20261010.pdf) · [`.png`](LAMINA4_poster_guia_20261010.png) | Póster A3 guía (16 spp.) con recortes sin fondo |
| [`LAMINA5_carta_marina_20261010.pdf`](LAMINA5_carta_marina_20261010.pdf) · [`.png`](LAMINA5_carta_marina_20261010.png) | Póster A3 estilo Carta Marina (Olaus Magnus 1539): costa catalana + 16 spp. como criaturas |
| [`recortes/`](recortes/) | Recortes rembg estilo guía (CPU) + créditos |
| [`LAMINA4_poster_guia_20261010.pdf`](LAMINA4_poster_guia_20261010.pdf) · [`.png`](LAMINA4_poster_guia_20261010.png) | Póster A3 guía (16 spp.): foto grande CC, nombres CA/ES, calendario pic, mapa zonas |
| [`LICENCIAS_FOTOS.md`](LICENCIAS_FOTOS.md) · [`LICENCIAS_POSTER_LAMINA4.md`](LICENCIAS_POSTER_LAMINA4.md) | Atribución CC0 / CC BY / CC BY-SA |
| [`datos/`](datos/) | CSV mensual (conteos + índice suavizado) y esfuerzo |

## Método (resumen)

- **Fuente:** `public_observations` — iNaturalist + Minka; solo `SELECT`.
- **Área:** caja costera Cataluña (lat 40,45–42,95; lon 0,10–3,40).
- **Suavizado:** corrección parcial del esfuerzo (γ=0.35) + prior bayesiano débil; meses con poco esfuerzo tramados/gris.
- **Fotos:** iNat / Minka / láminas correlación con licencia libre; si no hay, silueta esquemática.

```bash
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_articulo_generar_20261010.py
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_lamina3_espacial_20261010.py
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_poster_a3_20261010.py
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_lamina5_carta_marina_20261010.py
papers/nudibranquios_calendario/.venv/bin/python scripts/build_pdf_papers_completos_20261010.py
```
```bash
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_recortes_rembg_20261010.py
papers/nudibranquios_calendario/.venv/bin/python scripts/nudibranquios_poster_a3_20261010.py
```
