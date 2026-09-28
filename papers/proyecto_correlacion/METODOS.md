# Proyecto Correlación — Métodos

## 1. Datos

| Elemento | Origen | Cobertura |
|---|---|---|
| Fotografías | galería BioFauna (las 1.222.170 imágenes de la galería pública de BioFauna) | **1.222.170** imágenes (8 fuentes públicas, ver README) |
| Observaciones con metadatos | API de iNaturalist, Minka y GBIF; volcado en `volcado de metadatos de observación (iNaturalist/Minka/GBIF)` | **759.207** obs · 100 % con geo y fecha · **92 % con hora** |
| Catálogo de especies | `catálogo curado de BioFauna (2.985 taxones)` | 2.985 taxones (checklist mediterránea curada) |

## 2. Unidad de análisis: el «evento»

Co-ocurrencia real (no "ambas especies en la base"):

**evento = (observador × celda de ~1 km × día × franja horaria de 3 h)**

Todas las especies identificadas en observaciones del mismo observador, en el mismo kilómetro cuadrado, el
mismo día y dentro de la misma franja de 3 h se consideran **vistas juntas**. Es la aproximación más cercana a
«la misma inmersión / el mismo paseo de muestreo» con los datos disponibles.

- Celda: `round(lat/0,01) × round(lon/0,01)` (≈1,1 km).
- Franja: `hora // 3` (las observaciones sin hora van a una franja propia).

## 3. Filtros aplicados

1. **Solo especies del catálogo** (fauna/flora mediterránea curada). Motivo: la primera pasada sin filtro
   quedaba dominada por especies exóticas que co-aparecían por estar **en el mismo viaje o lote de subida**
   (p. ej. nudibranquios del Pacífico), un artefacto y no una asociación ecológica.
2. **Soporte mínimo**: el par aparece en **≥8 eventos**.
3. **Repetibilidad**: el par aparece en **≥3 celdas distintas y ≥3 días distintos** (evita que un solo día o
   una sola inmersión generen la asociación).

## 4. Métricas

Para cada par (A, B):

- `n` = nº de eventos con ambas especies.
- `n_A`, `n_B` = nº de eventos con cada una; `N` = nº total de eventos con ≥2 especies del catálogo.
- **esperado** = `n_A · n_B / N` (si fueran independientes).
- **lift** = `n / esperado` (>1 = más juntas de lo esperado; 10 = diez veces más).
- **p** aproximado por Poisson (probabilidad de ver ≥n con media = esperado). Es un *screening*: el contraste
  definitivo es el **nulo estratificado** (siguiente apartado).

## 5. Validación interna (control de calidad del método)

El método se aplica **antes de mirar nada nuevo** a asociaciones **ya documentadas** en la bibliografía.
Si las recupera con fuerza, las candidatas nuevas merecen crédito:

| asociación documentada | n | lift | celdas | días | lectura |
|---|---:|---:|---:|---:|---|
| *Peltodoris atromaculata* + *Petrosia ficiformis* | 79 | 11,1 | 44 | 74 | el nudibranquio se alimenta de esa esponja y vive sobre ella |
| *Felimare picta* + *Ircinia oros* | 29 | 4,1 | 20 | 28 | depredación/esponja hospedadora |
| *Cratena peregrina* + *Eudendrium racemosum* | 5 | 10,5 | — | — | hidrozoo del que se alimenta |
| *Doto paulinae* + *Sertularella mediterranea* | 5 | 48,3 | — | — | hidrozoo hospedador |

## 6. Nulo estadístico (fase en curso)

El lift y el p de Poisson no controlan la **estratificación** (una localidad o un día con mucho esfuerzo
genera co-ocurrencias). Para el artículo se implementará:

1. **Nulo por permutación estratificada**: se conservan los eventos (localidad, día, observador, tamaño) y se
   permutan las especies dentro de la misma localidad·fecha (o dentro del mismo observador), generando miles de
   réplicas → distribución nula del lift para cada par y un **p empírico** (FDR de Benjamini-Hochberg).
2. **Control por esfuerzo**: se normaliza por el número de especies del evento.
3. **Cruce con hábitat/sustrato**: las asociaciones se cruzan con el sustrato de la foto (mapas de hábitat
   desde el espacio de embeddings de BioFauna) para separar "misma casa" de "interacción real".
4. **Revisión experta**: las candidatas se someten a curadores/especialistas antes de publicar.

## 7. Límites (declarados)

- **Co-ocurrencia ≠ interacción**: mismo hábitat, misma estación y mismo observador la producen. Mitigado con
  catálogo, soporte y repetibilidad; pendiente el nulo estratificado.
- **El lift premia pares raros**: mirar siempre `n`, celdas y días.
- **Sesgo de observador y de evento** (bioblitz con cientos de fotos/día): se controla con el diseño por evento
  y con la repetibilidad en días distintos.
- **Cobertura desigual**: peces, nudibranquios y algas están mucho mejor cubiertos que otros grupos.
