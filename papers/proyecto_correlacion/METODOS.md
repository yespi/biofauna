# Proyecto Correlación — Métodos (v20, 6-oct-2026)

## 1. Datos
1.222.170 fotografías de la galería BioFauna (Minka SDG, iNaturalist, GBIF, Wikimedia Commons, DORIS/FFESSM, SeaSlugForum, WoRMS, FishBase y otras) y 759.207 observaciones con coordenadas, fecha y (92 %) hora; catálogo de 2.985 taxones mediterráneos.

## 2. Identificador
BioCLIP-2.5 ViT-H/14 con k-NN sobre FAISS (k=15, T=0,05, máximo 3 votos por especie) y calibración jerárquica. Panel de campo fuera de muestra: 82,85 % de acierto de especie (78.145 filas, 2.970 especies); el acierto crece con las fotos de referencia (68,6 % con 0–25 fotos, 89,2 % con ≥1.000).

## 3. Criterio principal: proximidad real (misma fotografía)
Solo cuenta como asociación la aparición de las dos especies en la misma fotografía. Procedimiento: (1) cribado por eventos para elegir parejas; (2) por cada pareja, hasta 60 fotos de cada especie de la galería; (3) cada foto en 5 vistas (entera y 4 cuadrantes), *embedding* con `/embed` y búsqueda en el índice vivo (300 vecinos); (4) foto candidata si la otra especie aparece en una vista con similitud ≥0,82 (o primera con ≥0,86); (5) **revisión a ojo de cada candidata**: se acepta solo si ambas especies son visibles; (6) las parejas de especies parecidas generan falsos positivos y se descartan. Código: `scripts/scan_copresencia_20261006.py`, `scripts/analiza_copresencia_20261006.py`, `scripts/laminas_pares_20261006.py`.

**Niveles de evidencia.** 0: co-ocurrencia por evento (pista). 1: ambas en la misma foto en ≥3 observaciones independientes. 2: además contacto visible (sobre, dentro, alimentándose). Sin fotos conjuntas = *sin confirmar* (no refutada).

## 4. Cribado por eventos (solo generación de hipótesis)
Evento = observador × celda ~1 km × día × franja de 3 h. Para cada pareja con ≥5 eventos en común: esperado condicionado al esfuerzo local (en cada bloque celda 0,1°·día la probabilidad de que una especie esté en un evento es proporcional a su tamaño; el esperado es la suma sobre bloques y la varianza la de una suma de Bernoulli), p unilateral (normal con corrección de continuidad) y Benjamini-Hochberg sobre toda la familia (115.204 parejas). Replicación: ≥3 celdas, ≥3 días, ≥5 observadores. Lista corta: n ≥15, ≥8 observadores; 70 mejores por puntuación (ln razón · ln n · min(observadores,20)/20) y 70 mejores entre grupos distintos. Código: `scripts/nulo_exacto_todos_pares_20261005.py`. **No es una conclusión**: la significación no discrimina (44,6 % de las parejas con soporte salen significativas).

## 5. Licencias y atribución de las fotografías
CC0, CC BY, CC BY-SA y CC BY-NC / CC BY-NC-SA; se excluyen las sin licencia y las CC BY-NC-ND. Cada foto indica autor, licencia, fecha y hora local, lugar y enlace (script `scripts/meta_foto_20261006.py`). Las marcadas † (no comerciales) deben sustituirse por fotos CC0/CC BY/CC BY-SA, o contar con permiso del autor, si se publica en una revista comercial.

## 6. Límites
La proximidad en una foto no es interacción; la segunda especie la propone el identificador sin confirmación de curadores; la galería son sobre todo retratos centrados (subestima la presencia de segundas especies) y el identificador reconoce peor las especies pequeñas o camufladas; la lista corta se eligió por efecto y soporte, no al azar.

Material anterior (definición de evento y nulo con 2.000 permutaciones, análisis por grupos y línea ambiental): [`archivo_2026-09/`](archivo_2026-09/).
