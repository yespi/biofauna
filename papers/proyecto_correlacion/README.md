# Proyecto Correlación (BioFauna) — asociaciones entre especies y con el medio

**Estado:** 28-sep-2026 · **fase:** prueba de concepto completada y validada, con lista de candidatas para revisión biológica.

---

## 1. Qué es

Explotar **1.222.170 fotografías** de fauna y flora (mediterránea y de otras regiones) y **755.861 observaciones
con geolocalización y fecha** para descubrir **asociaciones entre especies** —documentadas y nuevas— y relaciones
con parámetros del medio. Los resultados son la base de un **artículo científico con fotografías** (en preparación,
ver `papers/proyecto_correlacion/` en el repositorio público).

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

## 3. Resultados principales (detalle en `RESULTADOS.md`)

- **Validación del método**: recupera asociaciones **ya documentadas** con alta repetibilidad
  (*Peltodoris atromaculata* + *Petrosia ficiformis*: 79 eventos, lift 11,1, **44 localidades y 74 días**).
- **70.971 pares** de especies con soporte y repetibilidad (soporte ≥8 eventos, ≥3 localidades, ≥3 días).
- **Candidatas nuevas** con lectura biológica plausible: medusa + anfípodo hiperídeo, gamba limpiadora +
  anémona, parejas de infauna, ctenóforos de la misma masa de agua, etc.
- **Línea ambiental** (turbidez/visibilidad): pipeline montado y evaluado; el índice de color **no** valida
  (r≈0,10 con lluvia/viento), el índice **físico** (tamaño aparente + talla conocida → distancia) **sí funciona**
  mecánicamente (1-5 m plausibles) y queda como línea a validar con satélite/sonda.

## 4. Documentos de esta carpeta

| Documento | Contenido |
|---|---|
| [`METODOS.md`](METODOS.md) | Definición de evento, filtros, métricas, nulo estadístico y límites |
| [`RESULTADOS.md`](RESULTADOS.md) | Asociaciones validadas + candidatas por grupo taxonómico (tablas por familia) |
| [`ANALISIS_AMBIENTAL.md`](ANALISIS_AMBIENTAL.md) | Turbidez/visibilidad desde las fotos: lo intentado, lo medido y lo que falta |
| [`coocurrencia_catalogo_20260928.md`](coocurrencia_catalogo_20260928.md) | Salida cruda del análisis (top de asociaciones) |
| [`coocurrencia_red_top12.svg`](coocurrencia_red_top12.svg) | Figura: red de las 12 asociaciones más fuertes |
| [`ARTICULO.md`](ARTICULO.md) / [`ARTICLE.md`](ARTICLE.md) | Borrador del artículo científico (ES / EN), con clasificación bibliográfica de las candidatas |
| `ARTICULO_v2_ES_20260928.pdf` / `ARTICLE_v2_EN_20260928.pdf` | PDFs del borrador (versión 2, 28-sep-2026, en el repo público) |

## 5. Siguientes pasos

1. **Nulo estratificado por localidad·fecha** → convierte la lista en resultados citables (fase en curso).
2. **Cruce con hábitat/sustrato** de la foto (mapas de hábitat desde los embeddings) → explica *por qué* coexisten.
3. **Revisión biológica** de las candidatas (curadores/especialistas) → separar simbiosis real de coincidencia.
4. **Artículo con fotografías** (PDF académico) organizado por grupos taxonómicos: incluir **láminas fotográficas**
   por caso (2-4 fotos con licencia reutilizable CC0/CC BY/CC BY-SA y atribución; las de *all rights reserved*
   se excluyen o se pide permiso). En preparación.
5. **Integración en BioQuest**: sugerencias «si ves X, busca Y» y redes de asociación por zona.
