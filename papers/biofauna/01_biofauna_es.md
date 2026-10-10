# BioFauna: identificación de taxones mediterráneos por recuperación sobre BioCLIP-2.5 ViT-H congelado

**Autor:** Gustavo Zafra (Yespi)  
**Aportación taxonómica:** Xavier Salvador, Miquel Pontes, Manuel Ballesteros  
**Repositorio:** https://github.com/yespi/biofauna  
**Sistema en vivo:** https://fotofauna.yespi.es  
**Versión del manuscrito:** 2026-10-10 (artículo para Biodiversity Data Journal / PeerJ; OOS 83,22 %)

> **Nombre.** El proyecto se llamó YOLOFauna (2024–mediados de 2026); pasó a BioFauna cuando producción se quedó en recuperación BioCLIP, no en detectores YOLO. Origen: [`docs/HISTORY.md`](../docs/HISTORY.md).

---

## Resumen

BioFauna identifica taxones mediterráneos (y algunos adyacentes) a partir de fotografías por **recuperación** sobre una galería regional, sin entrenar un clasificador cerrado. El encoder de producción es **BioCLIP-2.5 ViT-H/14** (congelado; embeddings de 1024 dimensiones). La consulta se embebe (fusión del encuadre global con un recorte central al 65 %), se busca con **k-NN (k = 15)** y un agregador de votos temperado, se puede reponderar con un prior geográfico, se convierte en probabilidad calibrada y, si el margen es débil, se **abstiene** a género, familia o un grupo de indistinguibilidad curado.

**Cifras vigentes** (`dataset/stats.json` tras promote invasoras *todoselmejB* 09:51 + *invfull2* 11:51, 10-oct-2026): galería en vivo **1.216.896** embeddings / **4.643** especies; panel de campo **78.145** filas con acierto de especie fuera de muestra **83,22 %** (género **87,96 %**, familia **91,04 %**; `calibration.field_acc`). AutoID publica con umbral de especie **0,83** (precisión ≈96 %, cobertura ≈66,5 % en el eval completo; precisión auditada histórica **96,6 %**, n=493). Líneas base sobre 78.180 filas (2026-10-03): centroide más cercano **74,73 %**; k-NN simple **79,86 %**. Una búsqueda sistemática de mejoras entrenando sobre este espacio (LoRA, QLoRA, ArcFace, etc.) **no superó** la recuperación congelada. Publicamos el libro de experimentos, IDs de taxón, centroides y un identificador autoalojable; **no** se redistribuyen fotos ni embeddings por foto.

**Palabras clave:** BioCLIP-2.5, ViT-H, k-NN, clasificación visual fina, biodiversidad marina, ciencia ciudadana, abstención taxonómica, calibración, mar Mediterráneo

## 1. Introducción

El Mediterráneo concentra mucha biodiversidad marina en poca superficie, y hay pocos taxónomos. Minka e iNaturalist recogen fotos más rápido de lo que se identifican. Los clasificadores globales ayudan, pero endemismos, invertebrados crípticos y guías locales siguen siendo un cuello de botella.

BioFauna es el identificador de FotoFauna. Decisión de diseño: **no entrenar una CNN de conjunto cerrado**. Usar un encoder preentrenado en biología y una **galería regional** que puede crecer especie a especie sin reentrenar.

**Aportaciones**

1. Pila de recuperación en producción (ViT-H congelado + k-NN + calibración + abstención jerárquica) en GPU de consumo, con publicación automática a Minka cuando la confianza es alta.
2. Protocolo de evaluación **por observación**, con control de similitud a la galería tras un incidente de 42,7% de autoduplicados.
3. Un **libro de experimentos** (este texto §4 y [`docs/EXPERIMENTS.md`](../docs/EXPERIMENTS.md)): hipótesis, resultado y si se conservó.
4. Artefactos para reconstruir: IDs, centroides (4.702 × 1024), calibradores, priors geográficos, pares crípticos — no el corpus de fotos.

---

## 2. Sistema

### 2.1 Encoder

| Propiedad | Valor |
|-----------|-------|
| Checkpoint | `hf-hub:imageomics/bioclip-2.5-vith14` |
| Arquitectura | ViT-H/14, ~632M params, 1024-d L2-normalizados |
| Entrada | 224×224 |
| Entrenamiento en BioFauna | **Congelado** |

### 2.2 Identificación (producción, 2026-09-23)

1. Embeber la consulta; fusionar **encuadre global + recorte central 65%**.
2. Recuperar **k=15** vecinos (FAISS si hay galería completa; centroide más cercano con los prototipos publicados si no).
3. Agregar votos **temperados** `Σ exp(max(s,0)/T)`, **T=0,05**, más un boost al prototipo. Cada especie aporta **como máximo 3** de los 15 vecinos al voto (`KNN_CLASS_CAP=3`, K23), para que una especie con una galería enorme no gane a una escasa solo por número.
4. Prior geográfico multiplicativo si hay GPS.
5. **Abstener** si el margen top-1/top-2 es pequeño y comparten género/familia, o si el par/género/grupo está en `dataset/taxonomic_exceptions.json`.
6. Pasar features k-NN → **P(acierto)** con regresión logística.

AutoID en FotoFauna publica si **p ≥ 0,80**. Con el calibrador reajustado sobre datos sin fuga (`created=2026-09-23T08:22`, ajuste 8.509 / test 3.864 filas, partición disjunta por especie) ese umbral da **97,0% de precisión con 80,6% de cobertura** en el test (conjunto cerrado; el KPI de observaciones recientes es más bajo, O16). La estimación de agosto (95,3% al 57,4%) queda superada.

Este repositorio publica **centroides** (`data/patterns/<slug>/prototype.npy`): basta para un demo nearest-centroid. El k-NN completo exige reconstruir embeddings por foto en local ([`docs/dataset.md`](../docs/dataset.md)).

### 2.3 Datos (producción vs lo publicado)

| Capa | Producción | Este repo |
|------|------------|-----------|
| Fotografías | ~1,06 M en disco | **No** (licencia) |
| Embeddings por foto | 1.118.353 vectores | **No** (tamaño + derivados de fotos) |
| Prototipo por especie | 4.543 × 1024 float32 | **Sí** (~15 MB) |
| IDs / nombres | 2.985 filas | **Sí** (`dataset/catalog.json`) |
| Calibrador, geo, pares, excepciones | JSON vivo | **Sí** |

Nombres contrastados con **WoRMS** (nombre aceptado junto al slug estable). Recortes de láminas de guía que mezclaban taxones bajo una etiqueta se cuarentenaron (1.088 fotos / 107 especies, auditoría de agosto 2026).

**Tiers** del catálogo: 0 heterobranquios (634), 1 resto marino (1.527), 2 terrestre/incidental (824).

---

## 3. Protocolo de evaluación

Los números de cabecera usan **observaciones** retenidas (un encuentro, a menudo varias fotos del mismo organismo), no un split aleatorio por foto. Un 80/20 a nivel foto infla k-NN y metric learning ~10 pp por ráfagas casi duplicadas.

| Regla | Por qué |
|-------|---------|
| Estratificar por ID de observación | Sin fuga de ráfagas |
| Rechazar si es demasiado similar a la galería | Caza IDs perdidos tras migraciones |
| Mismo protocolo entre ablaciones | McNemar comparable |
| No mezclar cosechas al citar un delta | Otro mix de especies ≠ ganancia de modelo |

**Incidente (23-sep-2026).** La puerta de agosto de abajo tampoco funcionaba: comparaba un embedding promediado con TTA (original + recorte 90%) con los de la galería a coseno >0,999; una foto idéntica da ~0,99 así. El 50,8% del eval había vuelto a entrar en la galería. La puerta compara ahora el embedding **global** (el mismo que guarda la galería) a **≥0,98**, y un script de auditoría revisa todas las filas de eval tras cada crecimiento de galería (O18).

**Incidente (25/26-ago-2026).** La lista de IDs ya vistos apuntaba a una ruta abandonada y no coincidía con nada. El **42,7%** de una cosecha de 22.332 fotos ya estaba en la galería. Con k=15 el titular solo se movió ~1 pp; con k pequeño la curva era absurda. Arreglo: embeber cada candidato y tirar near-duplicates. Sigue como puerta de la cosecha.

**Dos métricas etiquetadas**

| Etiqueta | Cohorte | Top-1 especie | Uso |
|----------|---------|---------------|-----|
| **A — corte TTA** | `harvest_calib` n=12.788 (ago 2026, sin fuga) | 75,97% (luego 77,77% con pila de inferencia; 79,10% jsonl tras densificar) | Ablaciones comparables §4.1–4.2 |
| **B — calibrador vivo** | `calib_raw_t05` n=19.087 (2026-09-14) | **85,78%** | Histórico (afectado por la fuga O18) |
| **C — sin fuga** | `calib_raw_t05` n=12.373 (2026-09-23, auditado, copias ≥0,98 fuera) | **88,11%** | Informe de producción actual (§5) |

B es más grande, cubre más especies difíciles y usa T=0,05 y campañas de calidad posteriores. **A no es “peor ingeniería”; B no es un salto mágico de 10 puntos sobre las mismas fotos.**

---

## 4. Experimentos

Cada fila: **hipótesis → resultado → qué aportó.** Detalle y McNemar: [`docs/EXPERIMENTS.md`](../docs/EXPERIMENTS.md).

### 4.1 Conservados (en producción)

| ID | Qué se probó | Resultado | Aporte |
|----|----------------|-----------|--------|
| K1 | Galería ViT-L → **ViT-H congelado** | +6,8 pp (63,9% → 70,6% en aquella cohorte) | Mayor ganancia de modelo. Encoder de producción. |
| K2 | Barrido k-NN estratificado | **k=15** | k de producción. |
| K3 | Unificar SSD + archivo HDD y re-embeber | 71,7% → 75,8% en n=12.788 limpio | Cerró el *archive gap*. Completitud > adapters. |
| K4 | Calibración logística (10 features k-NN) | ECE ~0,03 vs ~0,09 coseno crudo | Umbral AutoID interpretable. |
| K5 | Abstención jerárquica + pares/géneros expertos | Fallback género/familia ~89% cuando aplica | Salida más segura. |
| K6 | TTA 90% y luego **fusión ROI 65%** | TTA +0,21–0,75 pp; ROI +1,63 pp vs solo global | Embedding de consulta. |
| K7 | Fusión tardía de varias fotos de una observación | +0,79 pp global; +3,15 pp en el 25% multi-foto | Producción si N>1. |
| K8 | Subespacio local Fisher / PCA+LDA en pares crípticos | +0,14 a +0,36 pp | Re-ranking acotado. |
| K9 | Mismo mecanismo inter-género / misma familia | Re-cosecha oficial **77,77%** (cohorte A + pila) | Segundo disparo en producción. |
| K10 | Densificar galería (más/mejores fotos, encoder congelado) | jsonl cohorte A **79,10%**; swaps de calidad posteriores | Datos, no pesos. Galería viva 848.883. |
| K11 | Agregador k-NN temperado T=0,05 | McNemar n=8.000: **+7,81 pp**, 671/46 | Scorer de producción (acumulativo con K10). |
| K12 | Gate MiniCPM en dos pares | McNemar pequeño 12/1, p=0,003 | Sidecar acotado, no VLM general. |
| K13 | Auditor de nomenclatura WoRMS+GBIF | 85 nombres aceptados; 4 fusiones de slug duplicado | Higiene de catálogo. |
| K14 | Lista de indistinguibles + grupo esponjas | Pares extra desde confusión de eval | Capa de decisión donde la visión satura. |
| K19 | Crecer las fotos de referencia hasta ~1.000/especie donde las fuentes lo permiten + re-embed completo por especie | McNemar n=18.000: **+0,57 pp** (313/211, p=1e-5). Por especies: crecen ≥+300 vectores **+7,7 pp**, +100–299 **+12,0 pp**, +1–99 +3,4 pp; las que no crecen −0,63 pp (dilución) | Los datos funcionan donde existen; el 77% de los errores restantes está en especies que no cambiaron. |
| K20 | Segunda oleada de crecimiento (121 especies, 21,9k fotos), reconstrucción a 1.118.353 vectores | McNemar n=21.000: **+0,22 pp** (84/38, p=5e-5); especies tocadas **83,3%→89,5%** (83/1); 31 mejoran, 0 empeoran | En producción el 21-sep-2026. |
| K21 | Segunda opinión independiente para el recuperador de conjunto cerrado: BioCLIP zero-shot sobre una lista regional | 300 observaciones de aves mediterráneas: BF≥0,85 **y** zero-shot≥0,80 coinciden → **98,5% de precisión con 69% de cobertura** (BF solo 91,2% con 79%). Todos los grupos: 95,9% al 49% con nivel de rescate frente a BF solo 93,8% al 48% | Guarda open-set de AutoID (aves en producción; resto de grupos pendiente). |
| K23 | Tope de votos por especie en el agregador k-NN (`KNN_CLASS_CAP=3`) | McNemar n=12.000 obs held-out: **+1,13 pp** (92,33%→93,47%; 228 arreglos / 92 roturas); **177 especies mejoran / 70 empeoran**; más ganancia en especies con <25 fotos de galería (+3,2–3,5 pp). cap1 −0,19, cap2 +0,82, cap4 +1,08, cap5 +0,94 pp | En producción el 22-sep-2026 07:17 CEST. (Medido antes de la purga O18; cuenta la ganancia relativa.) |
| K22 | Criterio de promoción contado en especies | 173 especies mejoran / 153 empeoran / 2.186 sin cambio (índice anterior→actual) | Reportar el balance por especie junto a Δ y p. |

### 4.2 Rechazados (no repetir tal cual)

| ID | Qué se probó | Resultado | Aporte |
|----|----------------|-----------|--------|
| R1 | QLoRA ViT-L + proyección entrenable | 1,7% especie | Fragilidad; no es “BioCLIP no se puede afinar” en general. |
| R2 | QLoRA BioCLIP-2 ViT-L vs ViT-H | 768 vs 1024-d | Descartado antes de evaluar. |
| R3 | Triplet sobre ViT-H (8 variantes) | −0,7 a −7 pp | Este régimen memoriza. |
| R4 | ArcFace sobre ViT-H congelado | Empate con k-NN | No sustituye la recuperación. |
| R5 | LoRA+ArcFace 100 spp | +0,0 pp OOS | Los splits internos mentían. |
| R6 | LoRA 4 bloques + ArcFace, 1.358 spp | **−31,2 pp** | Afinar un subconjunto envenena el espacio compartido. |
| R7 | Cabeza lineal, backbone congelado | −0,6 a −1,1 pp OOS | Mini-set de train engañaba. |
| R8 | Pesar recortes de guías | −0,9 pp | Lámina ≠ foto submarina. |
| R9 | Quitar ráfagas near-duplicate | −1,6 pp | Las ráfagas ayudan al k-NN. |
| R10 | Filtrar outliers de embedding | −0,21 a −1,45 pp | Se iba variación intraespecífica. |
| R11 | Ensanchar margen de abstención same-genus | Coste 9:1 | τ de producción se queda estrecho. |
| R12 | Re-rank “preferir epibionte” | −0,23 pp (64/116) | El huésped real entra como ruido top-k. |
| R13 | Re-ranker SupCon en 20 pares | Loss de val diverge desde época 1; kill-switch **antes** del eval | Tercera arquitectura, mismo fallo. |
| R14 | TTA con flip horizontal | −0,13 pp | La asimetría es señal. |
| R15 | Peso de prototipo por dispersión de especie | −0,09 pp | Lo global no describe esta foto. |
| R16 | Penalizar vecinos fuera de la familia consenso | −0,41 pp, p=0,0005 | El voto mayoritario ya está mal en convergencia morfológica. |
| R17 | Recorte guiado por atención | +0,04 pp, p=0,77 | Ruido. |
| R18 | Filtro por filo/clase | Todos los umbrales netos negativos | El 80% del error cruzado ya viene del k-NN. |
| R19 | Subespacio ancestral si &lt;5 refs | 1 observación abordable | Cerrado antes de gastar GPU. |
| R20 | Neutralizar fondo/sustrato | −0,92 pp vs control; −3,48 vs pila completa | El hábitat es señal en epibiontes. |
| R21 | Prior geo extra (nubes Minka) encima del de producción | No significativo; 4/5 folds fuerza=0 | Las confundibles conviven. |
| R22 | Fusión DINOv2 (scripts mal llamados DINOv3) | −6,75 pp vs producción | DINOv2 solo-prototipo es mucho más débil aquí. |
| R23 | Multi-prototipos k-means | No significativo; 4/5 folds blend=0 | Un centroide basta para el boost. |
| R24 | Re-embed marino selectivo (36 spp) | ~0 pp | Sin cutover. |
| R25 | VLM / densificación genérica en fanerógamas | Nulo | El swap de calidad ayudó a *Posidonia*, no a *Cymodocea*. |
| R26 | Filtro MiniCPM “sujeto puro” en fauna (16 spp) | 97,5% ya “puro” | No transfiere desde fanerógamas. |
| R27 | Swap Q≥8 en taxones ya agotados | Rendimiento muy desigual | La calidad ayuda **si** hay fotos mejores. |
| R28 | Subir el umbral de confianza para reducir errores confiados | Backtest vivo n=184: precisión plana 90–92% para p≥0,80…0,95; solo cae la cobertura (52%→11%) | La calibración satura; no es palanca. |
| R29 | Exigir acuerdo de iNaturalist CV antes de publicar | De 81 respuestas BF ≥0,85: iNat coincidió en 51 (BF acierta 96%), no devolvió nada en 29 (BF acierta 83%), discrepó en 1; ~4 aciertos bloqueados por cada error evitado | Sustituido por guardas de dominio + consenso zero-shot (prueba de 1 día, auditoría pendiente). |

### 4.3 Fallos operativos (no son ideas de modelo; sí son públicos)

| ID | Fallo | Efecto | Aporte |
|----|-------|--------|--------|
| O1 | Cosecha de calibración filtrada a la galería | Curvas de k pequeño infladas | Dedup por similitud obligatorio. |
| O2 | Desync FAISS vs etiquetas tras `/reload` (1-sep-2026) | IDs vivos absurdas a 85–100%; **evals en disco válidas** | Recargar índice y labels juntos. |
| O3 | Métricas de admin leyendo snapshots congelados | Panel in-sample / viejo | Métricas desde el jsonl actual. |
| O4 | `--species` vacío tras SSH anidado (13-sep-2026) | Swap de calidad en taxones de más ~35 min | Pasar ficheros de slugs, nunca listas interpoladas. |
| O12 | El servicio traducía las etiquetas de FAISS con la lista viva de carpetas de especies, no con la lista de nombres del propio índice; tres carpetas nuevas desplazaron todas las etiquetas mientras `/health` seguía diciendo alineado | Especie equivocada con similitud 0,92 durante horas (20/21-sep-2026); AutoID no publicó nada | Cron guardián compara nombres del índice ↔ especies cargadas ↔ carpetas (amplía O2). |
| O13 | Un trabajo desatendido reconstruyó el directorio FAISS de producción y refiteó la calibración antes de validar | Índice de producción sobrescrito por una build sin validar | Los trabajos desatendidos nunca escriben rutas de producción. |
| O14 | La web de Minka devuelve 403 al User-Agent por defecto de `python-httpx` (login y descargas de fotos) | AutoID sin publicar durante días (segunda recurrencia de la clase «cabecera ausente») | Un único cliente HTTP compartido; alarma de días sin publicaciones. |
| O15 | Dos sesiones de agente ejecutaron el mismo ciclo en paralelo; una promoción sobrescribió la otra; OOM de GPU con sidecar + servicio + reembed | Cómputo duplicado; desajuste índice/calibración ~30 min | Sesión activa única con registro escrito. |
| O16 | Evaluación de conjunto cerrado y correlada por observador: panel 92,4% frente a ~80% en 300 observaciones recientes research grade; el 12% de las observaciones de aves son especies fuera del catálogo | El panel sobreestima la precisión real | Muestra de observaciones recientes como KPI operativo. |
| O18 | La puerta de fuga del eval comparaba un embedding promediado con TTA con umbral 0,999; una foto idéntica da ~0,99 y la puerta nunca saltaba. Las búsquedas ad hoc posteriores (Wikimedia/GBIF/iNat de cualquier grado) no tenían puerta | El 50,8% de las filas de eval eran copias de la galería; panel 92,4–93,4% frente a 88,1% limpio; el 24% real en especies raras con fotos no vistas aparecía como 57% | Puerta con embedding global ≥0,98 en todas las cosechas; `leak_audit_calib.py` tras cada crecimiento; filas con fuga apartadas y calibrador reajustado (23-sep-2026). |
| O17 | La precisión por especie de los paneles solo cambia cuando el eval se re-puntúa contra el índice servido | Cifras congeladas tras promociones | Re-score diario automático; re-score tras cada promoción. |

---


## 5. Informe de producción actual (cohorte C, sin fuga, 2026-09-23)

| Nivel | Acierto | n |
|-------|---------|---|
| Especie | **88,11%** | 12.373 |
| Género | **90,55%** | 12.373 |
| Familia | **92,46%** | 12.373 |
| Tier 0 (heterobranquios) | 85,12% | 2.446 |
| Tier 1 (otros marinos) | 87,72% | 5.633 |
| Tier 2 (terrestres/incidentales) | 90,34% | 4.294 |

Por especie (2.091 con eval limpio): 1.429 al 100%, 431 por debajo del 80%. 894 especies del catálogo perdieron sus únicas filas de eval en la purga y se están volviendo a cosechar con la puerta arreglada. La cohorte B de abajo se conserva como histórico; estaba afectada por la misma fuga.

### Cohorte B (histórico, 14-sep)

| Nivel | Acierto | n |
|-------|---------|---|
| Especie | **85,78%** | 19.087 |
| Género | **89,15%** | 19.087 |
| Familia | **91,41%** | 19.087 |
| Tier 0 (heterobranquios) | 76,86% | 2.528 |
| Tier 1 (resto marino) | 86,56% | 10.207 |
| Tier 2 (terrestre/incidental) | 88,08% | 6.352 |

El error que queda es sobre todo **cripsis y convergencia morfológica**, no “hace falta LoRA”. Casi todo el catálogo tiene ≥1 observación retenida; una cola pequeña está agotada en Minka+iNaturalist.

Fanerógamas (n=60, 14-sep): *Posidonia oceanica* 73,3%; *Cymodocea nodosa* 70,0% (swap de calidad **no** pasado a producción); *Nanozostera noltii* 86,7%; *Zostera marina* 75,0%. El par *Z. marina* ↔ *N. noltii* pasó a abstención experta (20/120 confusiones cruzadas).

---

## 5.1 Informe de campo por bloques (2026-10-02, todas las cifras medidas)

**Galería.** 1.118.321 vectores / 4.543 especies de iNaturalist 733.789 fotos, Minka 372.347, GBIF 39.570, DORIS/FFESSM 5.091, Wikimedia 4.197, WoRMS 1.319, SeaSlugForum 817, FishBase 646. Vectores por especie: 775 especies tienen menos de 10, 1.058 tienen 10–29, 450 tienen 30–99, 1.123 tienen 100–299, 935 tienen 300–999 y 202 tienen 1.000 o más (mediana 97, máximo 3.223); la galería es de cola larga muy marcada.

**Acierto de campo (especie).**

| Bloque | Filas | Acierto | Salvedad |
|---|---|---|---|
| Conjunto de evaluación original (comparable con todas las versiones anteriores) | 60.743 | **81,18 %** | correlado por observador, conjunto cerrado |
| Ronda 1 de minería (tras purga) | 11.154 | 85,49 % | especies con más pool |
| Ronda 2 de minería (tras purga) | 4.688 | 89,87 % | ídem |
| **Todo purgado** | **76.585** | **82,34 %** | la subida sobre 81,18 % es sobre todo composición |
| Panel por reino (78.180 filas, sin purga por observador): marino | 65.813 | 80,54 % | el reino es metadato, no filtra la publicación |
| terrestre | 9.853 | 93,30 % | |
| aves | 2.027 | 92,25 % | |
| foráneas (lessepsianas, etc.) | 487 | 82,34 % | n pequeño |

Sobre las 76.585 filas purgadas, por reino: marino 80,37 %, terrestre 93,37 %, aves 92,22 %, foráneas 82,08 %.

**AutoID en la práctica.** En 493 publicaciones históricas auditadas el 2026-09-29 la precisión fue **96,6 %**, por banda de confianza calibrada: 0,83–0,85 → 85,2 % (n=27), 0,85–0,90 → 93,2 % (n=59), 0,90–0,95 → 95,5 % (n=155), ≥ 0,95 → 99,2 % (n=252). Una repetición sobre 726 publicaciones dio 94,6 % de acierto top-1 y 97,96 % de precisión con p ≥ 0,83 (n=589). Las fotos que AutoID no publica no son errores: en la última hora medida, de 1.429 observaciones candidatas 1.373 quedaron por debajo del umbral, 50 se omitieron porque el mismo observador ya tenía ese taxón en un álbum ese día y 81 no pasaron la puerta de calidad de foto.

**Dónde están los errores.** Peores especies del panel (todas con ≥ 11 fotos de evaluación): *Treptacantha nodicaulis* 0/20 (confundida con *Gongolaria barbata*), *Turbonilla pusilla* 0/18 (con *T. lactea*), *Pegusa nasuta* 0/18 (con *Solea solea*), *Forskalia tholoides* 0/13 (con *F. edwardsii*), *Arion rufus* 0/29 (con *A. ater*), *Phyllidiella granulata* 0/16 (con *Phyllidiopsis krempfi*), *Carduelis carduelis* 35 % de 40 (con *Spinus spinus*). Confusiones más frecuentes (errores): *Petalifera petalifera* → *P. ramosa* 31, *Patella aspera* → *P. ulyssiponensis* 27, *Tamarix africana* → *T. gallica* 26, *Elysia marginata* → *E. ornata* 24, *Pyracantha coccinea* → *P. crenulata* 24, *Dictyota implexa* → *D. dichotoma* 23, *Ulva rigida* → *U. lactuca* 22, *Diplodus sargus* → *D. cadenati* 21. La mayoría son pares congenéricos de morfología muy parecida; este informe no analiza por qué falla cada par.

**Lo que estas cifras no dicen.** Son de conjunto cerrado y correladas por observador; el KPI operativo es la reacción posterior de terceros a lo publicado, que para los rescates por recorte aún no existe. En este informe no se desglosó el acierto por especie según el tamaño de su galería.

**Acierto útil con abstención jerárquica (2026-10-03, offline, probabilidades calibradas).** Sobre las mismas 78.180 filas de campo, con las probabilidades calibradas de los tres niveles (especie, género, familia; calibración ajustada sobre estas filas, por tanto algo optimista), una cascada «publicar especie si p ≥ 0,83; si no, género si p_género ≥ τ; si no, familia si p_familia ≥ τ» da:

| Política | Fotos con ID publicable | Precisión de ese conjunto |
|---|---|---|
| Solo especie, p ≥ 0,83 | 65,1 % | 95,9 % |
| + género, τ = 0,83 | 77,2 % (+12,1 pp) | 95,6 % (añadidas: 93,7 %) |
| + género, τ = 0,90 | 74,1 % (+9,0 pp) | 95,9 % |
| + género 0,83 + familia 0,83 | 83,8 % (+18,7 pp) | 95,3 % (familia añadida: 91,7 %) |
| + género 0,90 + familia 0,90 | 79,9 % (+14,8 pp) | 95,9 % |

Publicar a nivel de familia solo compensa con τ ≥ 0,90; con 0,83 su precisión baja al 91,7 %. El acierto top-1 de especie (82,46 % del panel, 77,5 % en Tier 1) no cambia por construcción: la ganancia está en fotos que reciben una identificación correcta en el rango más grueso que el modelo puede defender. Las publicaciones reales de AutoID por recorte y por género son aún pocas y casi sin revisión de terceros para validar estas cifras. **Comprobación fuera de muestra (2026-10-03):** sobre 575 observaciones recientes de Minka de grado investigación no usadas en la calibración (excluidas las fugas con similitud top-1 ≥ 0,98), p de especie ≥ 0,83 cubrió el 73,2 % de las fotos con una precisión del 91,7 % (4 pp por debajo del 95,9 % en muestra), y el paso a género añadió +7,3 pp de fotos con 85,7 % de precisión (p_género ≥ 0,83), +4,3 pp con 88,0 % (≥ 0,90) y +2,4 pp con 92,9 % (≥ 0,95). La tabla en muestra es por tanto optimista; solo la regla p_género ≥ 0,95 alcanza la precisión de especie fuera de muestra. Una segunda muestra independiente (692 observaciones más) dio la misma imagen; conjuntamente (n = 1.267): p de especie ≥ 0,83 cubre el 71,1 % con 91,2 % de precisión, y el paso a género añade +7,4 pp con 88,3 % (≥ 0,83), +4,4 pp con 87,5 % (≥ 0,90) y +2,4 pp con 90,3 % (≥ 0,95; n = 31 fotos añadidas), de modo que la ganancia de la abstención jerárquica es real pero pequeña (≈ +2 a +7 pp de fotos) y algo menos precisa que publicar a nivel de especie.

## 5.2 Trabajos relacionados y líneas base

**Posición.** BioFauna se sitúa entre dos líneas de trabajo. Los modelos visión-lenguaje preentrenados sobre el árbol de la vida (BioCLIP [1], construido sobre CLIP [4]) dan embeddings que separan especies sin entrenamiento específico; los grandes corpus de ciencia ciudadana (iNaturalist [5]) aportan las fotografías etiquetadas. Muchos sistemas desplegados ajustan un clasificador con esos datos; BioFauna, en cambio, mantiene el codificador congelado y hace **recuperación k-NN sobre una galería regional** con abstención calibrada, de modo que añadir o corregir una especie es editar la galería, no reentrenar. Las pérdidas de aprendizaje métrico (triplet [13], FaceNet [12], contrastiva supervisada [6]) y el ajuste fino eficiente (LoRA [3], QLoRA [2]) eran las alternativas obvias; el §4.2 recoge que ninguna superó a la recuperación congelada sobre esta galería.

**Líneas base de este informe.** (a) *Centroide más cercano* sobre los prototipos publicados (demo pública): **74,73 %** top-1 sobre las 78.180 filas de campo (2026-10-03). (b) *k-NN simple con voto mayoritario* (k = 15, búsqueda exacta sobre el índice de producción), sin el agregador con temperatura, el tope por clase, el prior geográfico ni la calibración: **79,86 %** (1-NN simple: 79,10 %), frente a 82,46 % del sistema completo de producción sobre las mismas filas; es decir, la capa de decisión suma unos 2,6 pp sobre el voto simple y la recuperación en sí unos 5,1 pp sobre un clasificador solo de prototipos. (c) *Cabezas ajustadas o de aprendizaje métrico*: puntuadas en el §4.2 sobre conjuntos de evaluación anteriores, descartadas. (d) *La sugerencia de visión por computador de iNaturalist*, como línea base de AutoID: medida **parcialmente** el 2026-10-03 (n = 98 fotos de campo; la ejecución se detuvo por un límite HTTP 429 antes de las 300 previstas y no se reintentó): iNaturalist CV da **55,1 %** de acierto top-1 en especie y **67,3 %** en género, frente a **84,7 %** de BioFauna sobre las mismas fotos (BioFauna acierta y iNaturalist no: 31; al revés: 2). Con n = 98 el intervalo es amplio (unos ±8 pp), por lo que es orientativo, no una cifra principal; falta completar a n = 300.

| Línea base | Evaluación (filas) | Acierto especie | Estado |
|---|---|---|---|
| BioFauna completo (producción, panel 5-oct) | 78.180 | 82,46 % | medida |
| Centroide más cercano (prototipos publicados) | 78.180 (2026-10-03) | **74,73 %** | medida |
| k-NN simple, voto mayoritario (k = 15) | mismas filas | **79,86 %** (1-NN: 79,10 %) | medida |
| BioFauna vigente (panel tras invasoras 10-oct) | 78.145 | **83,22 %** | medida (`stats.json` 0,8322) |
| Sugerencia CV de iNaturalist | 98 (parcial; objetivo 300) | 55,1 % (BF 84,7 % en las mismas) | parcial |

La capa de decisión suma ≈2,6 pp sobre el voto k-NN simple y la recuperación ≈5,1 pp sobre solo prototipos (medido el 2026-10-03 sobre 78.180 filas). La línea base iNat sigue incompleta (n = 98 por HTTP 429).

---

## 5.3 Evaluación limpia, promociones del índice y métodos no adoptados

**Conjunto de evaluación.** El panel de campo (78.145 filas, acierto de especie 82,463 % el 2026-10-05) contenía fotos duplicadas (12.416 filas), fotos con varios sujetos (2.933) y filas cuya propia foto estaba en la galería. La evaluación *limpia v2* (62.796 filas) da 82,841 % (Tier 1 77,93 %). Una auditoría de fuga completa deja **54.878 filas sin fuga (índice vivo 80,63 %, Tier 1 76,42 %)**; todo candidato se informa también sobre las filas sin fuga (umbrales 0,95 y 0,995).

**Promociones a producción** (cada una con copia previa y script de marcha atrás; McNemar sobre filas emparejadas y guardia por especie: ninguna con n≥10 pierde ≥3 fotos ni >30 puntos).

| Fecha | Cambio | Panel (78.145) | Sin fuga | Arreglos / roturas | Guardia |
|---|---|---|---|---|---|
| 2026-10-05 18:45 | *Combo limpio*: tanda de reembed de 58 especies + bloque E + cosecha pequeña, sin 4 especies de guardia y sin los vectores responsables de 3 especies «ladronas» | 82,463 → 82,626 % (+0,163 pp, p=2e-11) | +0,261 pp (≥0,95) / +0,212 pp (≥0,995) | 240 / 113 (panel); 212 / 69 y 213 / 81 (sin fuga) | limpia |
| 2026-10-06 02:50 | *Lotes de cosecha 01+02* (71 especies, fotos añadidas de iNat, ladronas retiradas iterativamente) | 82,626 → 82,85 % (+0,223 pp, p=7e-27) | +0,503 pp (≥0,95) / +0,424 pp (≥0,995) | 217 / 43 | limpia |

Índice tras ambas: 4.543 especies, 1.132.767 vectores, alineado. Los lotes de cosecha medidos contra la base nueva dan rendimientos decrecientes (lote 03: +0,088 pp; lote 04: +0,024 pp): cada especie aporta solo 8–44 fotos nuevas aceptadas porque el límite es el número de observaciones research grade no vistas, no los filtros. **Efecto hermana**: añadir fotos a una especie baja el acierto de sus parientes cercanos (p. ej. *Pyracantha coccinea* → *P. crenulata* 32→19 de 40), de modo que los lotes se combinan y se retiran iterativamente las especies «ladronas» hasta que la guardia queda limpia.

**Hallazgo sobre la cobertura de la galería.** A 2026-10-06 los discos contienen 1.223.506 fotos (SSD + archive) pero el índice tiene 1.132.767 vectores: **96.392 fotos de 867 especies nunca se embebieron** (fotos cosechadas después del último embed de cada especie; p. ej. *Papaver rhoeas* 33 vectores frente a 1.000 fotos). Está en curso el reembed completo por especie de las 715 que siguen por debajo del 100 % (72.298 fotos, 3.845 errores del panel), con los mismos filtros de fuga (similitud de embedding ≥0,98 con la galería, ≥0,95 con cualquier foto de evaluación y toda su observación, comprobaciones de centroide y de prototipo propio).

**Acierto según el tamaño de la galería** (panel limpio, 62.248 filas): 0–25 fotos 68,6 %; 25–50 76,0 %; 50–100 65,7 %; 100–200 82,0 %; 200–500 82,2 %; 500–1.000 86,1 %; ≥1.000 89,2 %.

**Resultados nulos o negativos (no adoptados).**

| Idea | Resultado |
|---|---|
| Quitar vectores de prototipo discordantes (1.188) | −0,023 pp (25 arreglos / 43 roturas, p=0,039 en contra; 32 especies empeoran) |
| DINOv3 como desempate en 16 pares confundibles | 58,9 % frente a 59,6 % de BioFauna; desempate nulo en todos los δ |
| Comparador visión-lenguaje (MiniCPM-V) | 51,9 % frente a 58,3 % de BioFauna (108/579 respuestas válidas) |
| Grounding DINO y YOLO26n afinado para el recorte de atención | Peores que la fusión actual (GDINO 74,0 frente a 80,85 % en 4.000 fotos; YOLO + mejor = idéntico, 14/14) |
| Filtro de subexposición en las fotos que la foto entera no publica | Publicarían 17 de 392; 15 aciertos y 2 errores (88,2 %); casi todas ya cubiertas por el rescate de atención |
| Color (histogramas Lab, paleta k-means) como desempate | Neto negativo en todo δ; en las publicadas arregla 0 y rompe 4–13 |
| Prior de zona (conteos locales de especies) como desempate | El argmax simple pierde; con condición ≥10× da +3/−0 en la muestra de terceros (demasiado pequeña para concluir) |
| Reembed de Posidonia/fanerógamas; cosecha local de galerías pequeñas | +0,005 pp (3/0); +0,008 pp |

**Cambios en la identificación automática (AutoID).** La regla de «evitar observaciones hermanas del mismo usuario y día» se retiró el 2026-10-04: sobre 349 observaciones publicadas, las 42 (12 %) sustituidas por una alternativa acertaron 3 de 11 juzgadas (27 %) frente a 102 de 105 (97 %) de las no sustituidas; además, la similitud cruda de la alternativa se comparaba con el mínimo como si fuera una probabilidad calibrada (causa de una identificación errónea real). Un replay de 14 días (500 publicaciones) de la cascada actual (foto entera; si no, corrección de dominante azul; si no, recorte de atención con guardia estricta) da 97 % de acierto (77/79 juzgadas) donde publica la misma especie, y corrige 4 de 7 cambios juzgados rompiendo 2. El umbral de especie sigue en 0,83; la publicación a nivel de género con p≥0,95 está activa; la publicación por mezcla de recortes está en pausa.

**Límites de estas cifras.** Las observaciones juzgadas son las que tienen identificación de otro usuario; los replays usan el modelo de hoy, no el de la fecha de publicación; las ganancias de la cosecha se miden sobre un panel construido con las mismas fuentes que la galería, así que las filas sin fuga son la estimación más fiable.

## 5.4 Cifras vigentes tras el promote invasoras (OOS 83,22 %)

**Panel vigente** (`dataset/stats.json`, `updated=2026-10-10T11:50:11` tras *invfull2*):

| Magnitud | Valor | Fuente |
|---|---|---|
| Filas del eval | **78.145** | `stats.json` → `calibration.n_samples`; `calib_raw_t05.jsonl` |
| Acierto especie OOS | **83,22 %** (0,8322) | `stats.json` `overall_accuracy` / `calibration.field_acc.species` |
| Género | **87,96 %** (0,8796) | `stats.json` `calibration.field_acc.genus` |
| Familia | **91,04 %** (0,9104) | `stats.json` `calibration.field_acc.family` |
| Índice live (health) | **1.216.896** vectores / **4.643** spp | `stats.json` `faiss_vectors` / `live_health.species` (promote invasoras 10-oct) |

**Serie del panel (78.145 filas):**

| Hito | OOS especie | Fuente |
|---|---|---|
| Pre–combo limpio (5-oct) | 82,463 % | §5.3 |
| Tras *combo limpio* | 82,626 % (+0,163 pp) | §5.3 |
| Tras lotes de cosecha 01+02 | 82,85 % (+0,223 pp) | §5.3 |
| Tras *all08it2* (8-oct 23:42) | **83,14 %** (0,8314) | `agent-bus/inbox/claude/20261008-234238-robotin.md` |
| Tras invasoras *todoselmejB* (10-oct 09:51) / *invfull2* (11:51) | **83,22 %** (0,8322) | `logs/cola_gpu_4b_20261010.log.promote_*`; `stats.json` |

El promote *all08it2* midió delta **+0,294 pp** (fix 353 / break 123; `artifacts/decide_promote_calib_raw_t05_stg_all08it2_20261005.json`). El promote invasoras 10-oct usó el **criterio invasoras** (delta +0,083 pp en *todoselmejB*; backup `dataset/bak_promote_invasoras_20261010_090651`).

**AutoID (umbral de especie 0,83).** En el eval completo, con el calibrador logístico vigente (`calibration.json` coef/mu/sd sobre features del k-NN en `calib_raw_t05.jsonl`):

| Umbral | Cobertura | Precisión | n |
|---|---|---|---|
| p ≥ 0,83 (eval completo) | **66,42 %** (≈ 66,5 %) | **95,97 %** (≈ 96 %) | 51.906 / 78.145 |
| p ≥ 0,80 (operating_points, split test) | 69,9 % | 95,4 % | 16.409 |
| p ≥ 0,85 (operating_points, split test) | 65,3 % | 96,2 % | 15.326 |

La tabla `operating_points` del calibrador **no** incluye exactamente 0,83 (salta de 0,80 a 0,85); el punto 0,83 del eval completo es el que usa producción. Precisión real de publicaciones históricas auditadas: **96,6 %** (n=493; `stats.json` `kpi_referencia.autoid_real`).

**Métodos descartados (cifras medidas; no adoptados).** Complementa §4.2 y §5.3:

| Método | Resultado | Fuente |
|---|---|---|
| SigLIP (2.º backbone, desempate top-5) | 27 arreglos / 36 roturas, n=12.298, p=0,31 (neto negativo) | `artifacts/exp_altbackbone_siglip_20260930.json` |
| DINOv2 (fusión; scripts mal llamados DINOv3) | **−6,75 pp** vs producción | §4.2 R22 |
| DINOv3 como desempate (16 pares) | 58,9 % frente a 59,6 % de BioFauna; desempate nulo en todos los δ | `artifacts/exp_dinov3_pares_20261005.json`; §5.3 |
| VLM (MiniCPM-V) | 51,9 % frente a 58,3 % BF (108/579 respuestas válidas) | `artifacts/exp_vlm_compara_pares_20261005_minicpm-v_latest.json`; §5.3 |
| BioCLIP-2 ViT-L (2.º backbone) | +0,40 pp en las filas tocadas (+0,064 pp sobre el eval), p=0,06 | `artifacts/exp_altbackbone_bioclip2_20260930.json`; `experimentos/EXPERIMENTOS_HACIA_100_20260930.md` E9 |
| YOLO crop (YOLO26n vs fusión actual) | 74,97 % frente a 80,85 % (n=4.000) | `artifacts/exp_det_ab_20261005_yolo.json`; §5.3 |
| ArcFace / LoRA | R4 empate con k-NN; R5 +0,0 pp OOS (100 spp); R6 **−31,2 pp** (1.358 spp) | §4.2 R4–R6 |
| Poda de outliers de embedding | −0,21 a −1,45 pp | §4.2 R10 |
| Limpieza de prototipos discordantes | −0,023 pp | §5.3 |

Figuras generadas (matplotlib, 2026-10-09): `figures/fig_serie_oos_promotes.png`, `fig_acc_especie_genero_familia.png`, `fig_autoid_precision_cobertura.png`, `fig_metodos_descartados.png` (fuentes en `figures/fuentes_cifras_20261009.json`).

### 5.5 Cola de confirmación iNaturalist (`inat_review_decisions`)

Para cerrar el bucle AutoID → comunidad, FotoFauna registra decisiones de revisión sobre observaciones de iNaturalist en la tabla **`inat_review_decisions`** (BD compartida `fauna`, contenedor `postgres-global`). A **10-oct-2026** hay **72** filas (solo lectura; sin escribir en producción desde este informe).

| Métrica | Valor | Fuente |
|---|---|---|
| Filas totales | **72** | `SELECT COUNT(*) FROM inat_review_decisions` |
| `action=confirm` | **27** | idem |
| `action=discard` | **45** | idem |

**Apartado reservado para el manuscrito:** cuando la cola supere ~200 decisiones con taxón final verificado, publicaremos una tabla resumen (precisión de la propuesta BF vs taxón acordado, latencia, observadores) en PeerJ/BDJ. Hasta entonces, citar solo el conteo anterior y no inferir precisión de la cola.

## 6. Limitaciones

1. El top-1 de especie no es nivel experto en invertebrados crípticos; las especies con poca galería o evaluación fina son mucho más difíciles que la media del panel.
2. El catálogo y la evaluación están **centrados en el mar Mediterráneo** (y costas adyacentes en la galería); no hay estudio sistemático fuera de esa región.
3. El código público es un **identificador de reconstrucción** (prototipos + k-NN local opcional), no el volcado del servicio de producción en HanSolo.
4. El panel de campo vigente da **83,22 %** de acierto de especie (78.145 filas; `dataset/stats.json`); una fracción de filas puede seguir correlacionada con la galería, y el KPI operativo sobre observaciones recientes suele ser más bajo que el panel cerrado.
5. Las correcciones de curadores aún no cierran un bucle de entrenamiento automático.
6. **Recuperación de conjunto cerrado:** las especies ausentes del catálogo reciben una respuesta errónea con confianza; mitigado en aves con guarda zero-shot, no aún en todos los grupos.
7. La precisión/cobertura de AutoID al umbral 0,83 (≈96 % / ≈66,5 % en el eval completo) es del calibrador vigente; la precisión real de los rescates por recorte publicados sigue pendiente de reacciones de terceros.
8. La línea base de iNaturalist CV está medida solo en n = 98 (HTTP 429); falta completar a n = 300.
9. Varias ideas de mejora (SigLIP, DINOv2/v3, VLM, YOLO crop, ArcFace/LoRA, poda de outliers) se midieron y **no** se adoptaron (§5.3–5.4); el margen sobre k-NN simple (79,86 %) y centroides (74,73 %) es real pero modesto.

## 7. Reproducibilidad

```bash
git clone https://github.com/yespi/biofauna.git && cd biofauna
pip install -r requirements.txt
python -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090
```

Descarga BioCLIP-2.5 de Hugging Face al primer arranque. Usa prototipos en `data/patterns/`. Para reconstruir la galería completa: bajar fotos con los IDs de `dataset/catalog.json`, `scripts/reembed_vith.py`, dejar `embeddings.npy` junto a cada prototipo.

Licencia MIT para código y JSON/prototipos publicados. El copyright de las fotos sigue en observadores y plataformas.

---

## 8. Cómo identifica BioFauna una especie

![Pipeline: de la fotografía a una respuesta calibrada y con guardas](figure_pipeline.svg)

BioFauna es un clasificador por **recuperación**, no una red entrenada de extremo a extremo:

1. **Encoder congelado.** Cada foto de la galería se embebe con **BioCLIP-2.5 ViT-H/14** (congelado). La consulta se embebe igual: vector global **más fusión ROI al 65 %** (recorte centrado en el sujeto), normalizado L2.
2. **Búsqueda aproximada.** Un índice **FAISS** guarda los vectores de galería (hoy **≈1,20 M vectores / 4.543 especies**, alineados fila a especie).
3. **k-NN con agregador temperado.** Los *k*=15 vecinos votan con pesos `exp(similitud / T)`, `T=0,05`, **tope de 3 votos por especie**.
4. **Correcciones de contexto.** Prior **geográfico** y manejo de **pares crípticos** corrigen el ranking cuando dos especies son casi idénticas a la vista.
5. **Calibración jerárquica.** Un modelo logístico por especie convierte la puntuación k-NN en **probabilidad calibrada**, con respaldo a género/familia; bajo el umbral el servicio **se abstiene**.
6. **Rescate zero-shot (2026).** Si la similitud top-1 es baja (< 0,85), se consulta un zero-shot a todo el catálogo (2.985 etiquetas); si coincide con *otra* especie a p ≥ 0,90, gana. Efecto medido: **+0,91 pp** en la evaluación de campo.
7. **Guardas de publicación (AutoID).** No se publica a especie si el **margen** top-1/top-2 es < 0,02, si la observación queda fuera de dominio o hay desacuerdo vocal; una **guarda de curadores** retira identificaciones cuando un curador corrige a nivel de clase o superior.

## 9. Cómo ha mejorado el modelo, paso a paso

![Cronología de mejoras](figure_mejoras.svg)

| etapa | cambio | efecto |
|---|---|---|
| YOLOFauna (2024–2026) | BioCLIP ViT-L + k-NN | 63.9 % |
| Aug 2026 | full re-embedding with **BioCLIP-2.5 ViT-H/14** | 70.6 % |
| Aug 2026 | **k=15** + hierarchical fallback + calibration hygiene | 71.7 % |
| Aug 2026 | **hierarchical calibration** (species/genus/family) | 74.1 % |
| Sep 2026 | **3-vote cap** per species, ROI fusion, geographic prior | 77.9 % |
| Sep 2026 | **evaluation leak fixed** → honest panel (near-100 % of the drop was leakage, not error) | 79.4 % |
| Sep 2026 | **gallery hygiene**: 135 duplicate synonym slugs merged (Minka authority), ~1,000 mislabelled photos relocated, 57 quarantined | 79.6 % |
| Sep 2026 | **zero-shot rescue** + publication guards | 79.6 % *(+0.91 pp on the same rows; the headline moves with the evaluation)* |

Dos lecciones que marcaron el proyecto: (a) **la evaluación forma parte del modelo** — an unfixed leak in the
evaluation made the system look better than it was; (b) **la calidad de la galería gana a la complejidad del modelo** — synonyms,
contamination and mislabelled observations cost more accuracy than any hyper-parameter we tuned (LoRA/QLoRA/
triplet/ArcFace/SupCon on this embedding space were all rejected by measurement).

## 10. Datos, evaluación y operación

![Flujo de datos y operación](figure_datos.svg)

- **Fuentes** (imágenes públicas): **Minka SDG** 377,476 · **iNaturalist** 779,411 · GBIF 39,570 · Wikimedia Commons
  6,677 · DORIS/FFESSM 5,091 · SeaSlugForum 3,147 · WoRMS 1,320 · FishBase 1,072 → **≈1.22 M photographs**.
- **Una copia de cada foto**, nunca se borra; cada reubicación lleva manifiesto y script de marcha atrás.
- **Evaluación de campo**: solo fotos de campo (iNaturalist/Minka research grade), 20–30 por especie, auditadas contra fugas antes de fusionar.
- **Todo cambio de producción se mide** (McNemar + guardia por especie); el índice anterior queda como **marcha atrás 24 h**.
- **QA continua**: contaminación de galería (diaria), auditoría de fuga del eval minado (semanal, con purga) y alineación índice↔catálogo (cada 10 min).

## Agradecimientos

Xavier Salvador, Miquel Pontes y Manuel Ballesteros (GROC/OPK). Comunidades Minka e iNaturalist. WoRMS. BioCLIP (Stevens et al.).

---

## Disponibilidad de datos

Código, prototipos, catálogo, calibradores, priors, pares crípticos: este repositorio. Backbone: Hugging Face `imageomics/bioclip-2.5-vith14`. Imágenes: Minka/iNaturalist/GBIF por separado.

---

## Referencias

Las mismas que la versión inglesa (`01_biofauna.md`).

---

*Manuscrito orientado a Biodiversity Data Journal / PeerJ. Artefactos y cifras en este repositorio.*

---

