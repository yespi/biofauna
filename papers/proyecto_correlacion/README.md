# Proyecto Correlación (BioFauna) — asociaciones entre especies verificadas por proximidad real

**Estado:** 7-oct-2026 · **artículo v21** (v21: cada foto de las láminas indica localidad, zona y coordenadas) (reescrito: las conclusiones se basan solo en fotografías donde aparecen **las dos especies a la vez**, a escala de centímetros). Todo el material público está en **https://github.com/yespi/biofauna** (carpeta [`papers/proyecto_correlacion/`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/) y [`data/`](https://github.com/yespi/biofauna/blob/master/data/)).

---

## 1. Qué es

Un cribado de asociaciones entre especies sobre **1.222.170 fotografías** y **759.207 observaciones geolocalizadas** (Minka SDG, iNaturalist y otras fuentes), identificadas por BioFauna. Que dos especies se vean en la misma inmersión no prueba relación; por eso **solo cuenta como asociación la aparición de ambas en la misma fotografía**. La co-ocurrencia por eventos (observador × ~1 km × día × 3 h) se usa únicamente para **proponer** qué parejas verificar.

## 2. Crédito — de dónde salen los datos

Este proyecto ha sido posible **gracias al identificador BioFauna** (red neuronal BioCLIP-2.5 ViT-H/14 con
recuperación k-NN sobre FAISS, calibrator jerárquico y servicio de identificación en producción) y a las
**fuentes públicas de imágenes** que nutren su galería:

| Fuente | Fotografías en la galería |
|---|---:|
| **Minka SDG** (`minka-sdg.org`) — plataforma de ciencia ciudadana marina del ecosistema **FECDAS** | 377.476 |
| **iNaturalist** (`inaturalist.org`, incluye iNaturalist Open Data) | 779.411 |
| GBIF (`gbif.org`, multimedia de colecciones y ciencia ciudadana) | 39.570 |
| Wikimedia Commons | 6.677 |
| DORIS / FFESSM (`doris.ffessm.fr`) | 5.091 |
| SeaSlugForum | 3.147 |
| WoRMS (`marinespecies.org`, imágenes) | 1.320 |
| FishBase (`fishbase.se`) | 1.072 |
| Otras (legado, colecciones puntuales) | ~5.600 |
| **Total** | **≈1.222.170** |

Metadatos de observación enriquecidos (fecha, hora, coordenadas, observador, lugar) vía API de **iNaturalist**,
**Minka** y **GBIF** (759.207 observaciones; 92 % con hora).

**Agradecimientos.** Este proyecto se apoya en el trabajo diario de la comunidad observadora y, muy
especialmente, de las **personas curadoras** que revisan y corrigen las identificaciones de las especies más
difíciles (las **crípticas**, donde dos especies se distinguen por detalles anatómicos o por el hábitat):

**Miquel Pontes**, **Xavier Salvador** y **Berta Companys**— y al conjunto de la comunidad de curaduría de
**Minka SDG** e **iNaturalist**.

Menciones especiales también a la **FECDAS** (Federació Catalana d'Activitats Subaquàtiques) y a su **Projecte Aneris**,
por impulsar la ciencia ciudadana marina de la que se nutre **Minka SDG** —la plataforma que aporta el mayor
volumen de observaciones verificadas de este estudio— y por su labor de formación de buceadores-observadores.
Su trabajo (identificaciones *research grade*, correcciones y datos de campo) es lo que hace posible tanto el
identificador BioFauna como este análisis. Sin esa comunidad, ni el catálogo ni las asociaciones aquí
descritas existirían.

## 3. Resultados (detalle en [`RESULTADOS.md`](RESULTADOS.md))

- **Cribado por eventos (hipótesis):** 115.204 parejas con ≥5 eventos en común; 51.401 significativas con el esfuerzo controlado → la significación no discrimina; 3.108 con replicación y razón ≥3.
- **Lista corta de 138 parejas** (mayor efecto y soporte): 41 con al menos una foto candidata con ambas especies y 12 con ≥3 observaciones distintas; la revisión a ojo mostró **muchos falsos positivos entre especies parecidas**.
- **Confirmadas a ojo (ambas visibles):** *Peltodoris atromaculata* sobre *Petrosia ficiformis* y *Cratena peregrina* sobre hidrozoos (controles positivos, relaciones documentadas), *Condylactis aurantiaca* con *Periclimenes scriptus*, *Lysmata grabhami* con *Telmatactis cricoides* y *Electra posidoniae* con *Tridentata perpusilla* (misma hoja de *Posidonia*; microhábitat compartido, no interacción demostrada).
- **Sin foto conjunta:** *Felimare picta*–*Ircinia oros*, *Muraena helena*–*Ophidiaster ophidianus*, *Fistularia commersonii*–*Pterois miles* (no refuta nada: la galería son retratos centrados).
- La segunda especie de cada foto la propone el identificador y **no está confirmada por curadores**.

## 4. Documentos de esta carpeta

| Documento | Contenido |
|---|---|
| [`ARTICULO.md`](ARTICULO.md) / [`ARTICLE.md`](ARTICLE.md) | Artículo v21 (ES / EN), con tablas y láminas incrustadas |
| [`LAMINAS.md`](LAMINAS.md) | Láminas fotográficas con autor, licencia, fecha y hora, lugar y enlace |
| [`METODOS.md`](METODOS.md) / [`RESULTADOS.md`](RESULTADOS.md) | Métodos y resultados ampliados |
| [`NULO_EXACTO_TODOS_PARES_20261005.md`](NULO_EXACTO_TODOS_PARES_20261005.md) | Suplemento S1: cribado por eventos (solo hipótesis) |
| [`figuras/`](figuras/), [`lamina_fotos/`](lamina_fotos/) | Figuras (300 dpi) y fotografías de las láminas con su manifiesto |
| [`archivo_2026-09/`](archivo_2026-09/) | Material anterior (conclusiones por co-ocurrencia de eventos, retiradas en v20) y línea ambiental |
| `PLAN_PAPER_20261005.md`, `PAPER_DATOS_Y_FIGURAS_20261005.md` | Plan de trabajo y notas internas (solo en la documentación privada) |

PDF (en el repositorio público): versiones sin número que se actualizan siempre — `ARTICULO_ES_latest.pdf`, `ARTICLE_EN_latest.pdf`, `LAMINAS_latest.pdf` — y las dos últimas versiones numeradas.

## 5. Siguientes pasos

1. Revisión a ojo de más parejas de la lista corta y de nuevas listas (por grupo taxonómico).
2. Revisión bibliográfica y de curadores de cada pareja confirmada; sustituir las fotos † (no comerciales) si se publica en revista comercial.
3. Excluir automáticamente parejas visualmente confundibles (similitud de prototipos) antes de la revisión.
4. Comparación con modelos de referencia y propagación del error del identificador.
5. Integración en BioQuest («si ves X, busca Y») solo con parejas de nivel 1–2.
