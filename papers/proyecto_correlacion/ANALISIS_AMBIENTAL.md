# Proyecto Correlación — Análisis ambiental (turbidez y visibilidad) desde las fotografías

Línea del proyecto que busca **relacionar las observaciones con parámetros del medio** (claridad/turbidez del
agua) usando las fotografías y sus metadatos. Estado: **dos pruebas de concepto hechas y evaluadas**.

---

## 1. Planteamiento

Con **755.861 observaciones geolocalizadas y fechadas**, la idea es obtener un valor ambiental por
**día × ubicación** (agregando todas las fotos de ese día en ese punto) y construir series temporales —
una gráfica por localidad, y una vista espacial por semanas para ver *hacia dónde se mueve*. Después, cruzar
esas series con:

- **meteorología histórica** (lluvia, viento) — Open-Meteo, sin clave;
- **color del océano por satélite** (Kd490/turbidez, NASA/MODIS-VIIRS vía ERDDAP) — como validación externa;
- **las especies observadas** (¿atrae o repele la turbidez?), controlando especie y estación.

## 2. PoC A — índice de color por foto (agregado día × celda)

- Índices por foto (sin GPU, ~25 ms): rojo/azul del agua (borde), *dark-channel* (velo/backscatter), nitidez,
  saturación → **mediana por celda·día** (≥3 fotos).
- Barcelona, 2023-07-01 → 2023-09-30: **94-96 puntos** (9-10 celdas, 55-57 días) desde **~5.600 fotos**.
- Entregables: `artifacts/turbidez_barcelona_2023-07-01_2023-09-30.{html,csv,json}`
  (HTML autocontenido con la serie por celda y la vista espacial por semana).
- **Validación contra lluvia/viento: r ≈ +0,10 → SIN señal clara.**

**Por qué falla**: el índice de una foto mezcla **sujeto** (un pez a 8 m sale más "velado" que una lapa a
20 cm), **cámara/exposición**, **profundidad** y **encuadre**; la mediana diaria no cancela ese sesgo porque
la mezcla de sujetos cambia de un día a otro. Corregido en parte con el **filtro nocturno** (13 % de las
observaciones son de noche con flash; 15 % en Barcelona) — implementado, excluido por defecto —, pero la
correlación sigue débil.

## 3. PoC B — distancia y visibilidad por el TAMAÑO APARENTE (línea recomendada)

Idea (Gustavo): si la talla real del sujeto es conocida, su **tamaño aparente** da la distancia:
`distancia ≈ talla_real × f_px / tamaño_aparente_px`. La **visibilidad** de una zona/día se estima con el
**percentil alto de las distancias** (el sujeto más lejano que aún se distingue) — un ancla **física**,
no de color.

- Detector **YOLOE-26n-seg** (open-vocabulary, descargado y funcionando en el contenedor de FotoFauna).
  Con prompts marinos variados etiqueta mal (confunde algas con "octopus"); usado con **un solo prompt y la
  caja mayor** da detecciones utilizables.
- Prueba con tallas reales y supuesto de cámara `f≈2000 px` (FOV 90° a 4000 px; la galería **no conserva EXIF**):

| especie | talla real | distancia implícita (mediana) | p10–p90 |
|---|---:|---:|---:|
| *Sparus aurata* | 35 cm | **1,4 m** | 1,0–1,9 |
| *Diplodus sargus* | 30 cm | **2,4 m** | 1,1–3,2 |
| *Oblada melanurus* | 23 cm | **3,5 m** | 2,0–4,9 |

Distancias de 1–5 m: **físicamente plausibles** para fotografía de buceo → el mecanismo funciona.

## 4. Qué falta para convertirlo en medida (plan)

1. **Máscara de agua**: medir solo el fondo (anillo periférico / sin flash) en el PoC A.
2. **Calibración de cámara**: **conservar EXIF** (`FocalLength`, `ExifImageWidth`) en los harvesters —
   hoy se pierde; sin ello la distancia absoluta depende del FOV supuesto (±2-3×), aunque las tendencias
   relativas (misma cámara/sitio) ya son válidas.
3. **Tabla de tallas** del catálogo: peces por FishBase/Wikidata (P2043), fanerógamas y algas con valores
   curados (p. ej. hojas de *Posidonia* 20-120 cm).
4. **Segmentación fiable del sujeto** (el sujeto está centrado en la galería → MobileSAM con prompt central).
5. **Validación externa** con satélite (Kd490) o sonda in situ, con **retardo 1-3 días** (la turbidez responde
   a la lluvia con demora).
6. **Filtro nocturno** ya implementado (se excluyen de la serie de visibilidad; el flash fija el alcance).

## 5. Valoración honesta

- **Turbidez absoluta (NTU) desde fotos: descartada** (sin calibración no es posible).
- **Visibilidad relativa por sitio: prometedora solo con validación**; el valor real está donde los satélites
  fallan — aguas someras y costeras — que es justo donde están nuestras fotos.
- **El «3D de movimiento de la turbidez» no se publicará** mientras la señal no pase el contraste externo.
- Las **asociaciones entre especies** (ver `RESULTADOS.md`) rinden mucho más por esfuerzo: están basadas en un
  ancla física (dos organismos en el mismo evento) y ya se validan con pares documentados.

## 6. Herramientas dejadas listas (reutilizables)

| script | qué hace |
|---|---|
| `(script del proyecto; disponible bajo petición)` | agrega índices por **día × celda**, filtro nocturno, gráficas y CSV |
| `(script del proyecto; disponible bajo petición)` | co-ocurrencia por evento (todas las fuentes) |
| `(script del proyecto; disponible bajo petición)` | co-ocurrencia con catálogo + soporte + repetibilidad |
| `volcado de metadatos de observación (iNaturalist/Minka/GBIF)` | 759.207 observaciones con geo, fecha, hora, observador |
