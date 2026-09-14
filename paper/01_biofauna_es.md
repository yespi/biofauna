# BioFauna: identificación marina mediterránea por recuperación sobre BioCLIP-2.5 ViT-H congelado

**Autor**: Gustavo Zafra (Yespi)
**Aportación taxonómica**: Xavier Salvador, Miquel Pontes, Manuel Ballesteros
**Repositorio**: https://github.com/yespi/biofauna
**Sistema en vivo**: https://fotofauna.yespi.es
**Esta versión**: 2026-09-14 (corte de producción)

> **Nombre.** El proyecto se llamó YOLOFauna (2024–mediados de 2026); pasó a BioFauna cuando producción se quedó en recuperación BioCLIP, no en detectores YOLO. Origen: [`docs/HISTORY.md`](../docs/HISTORY.md).

---

## Resumen

BioFauna identifica taxones mediterráneos (y algunos adyacentes incidentales) a partir de fotografías por **recuperación** sobre una galería regional, no entrenando un clasificador cerrado. El encoder de producción es **BioCLIP-2.5 ViT-H/14** (632M parámetros, embeddings de 1024 dimensiones), **congelado**. La consulta se embebe (fusión del encuadre global con un recorte central al 65%), se busca con **k-NN (k=15)** y un agregador de votos temperado, se puede reponderar con un prior geográfico, se convierte en probabilidad calibrada y, si el margen es débil, se **abstiene** a género, familia o un grupo de indistinguibilidad curado.

**Corte de producción (2026-09-14, `/health` en vivo + `calibration.json`):**

| Magnitud | Valor |
|----------|-------|
| Galería | **848.883** embeddings / **4.702** especies, FAISS alineado |
| Catálogo (lista mediterránea) | **2.985** taxones (`dataset/catalog.json`) |
| Acierto fuera de muestra | **85,78%** especie / **89,15%** género / **91,41%** familia |
| Evaluación | n=**19.087** observaciones, **2.926** especies con ≥1 muestra |
| Hardware | NVIDIA RTX 3060 12 GB (~4,4 GB VRAM en inferencia) |

Esas cifras son **estratificadas por observación** y con control de fugas. **No** se pueden comparar a ciegas con el 75,97% de agosto de 2026 (n=12.788, otra cosecha). Mezclar cohortes es el error que este proyecto ya documentó. Ambos números aparecen abajo, etiquetados por protocolo.

Una búsqueda sistemática de más top-1 de especie **entrenando sobre este espacio** (QLoRA, LoRA, triplet, ArcFace, cabeza lineal, SupCon acotado) **no superó** la recuperación congelada. Lo que sí se quedó en producción: escala del backbone, completitud/calidad de galería, fusión en inferencia, agregador k-NN temperado y abstención taxonómica. Publicamos el libro de experimentos, los IDs de taxón, los centroides y un identificador autoalojable. **No se redistribuyen fotos ni `embeddings.npy` por foto**; se pueden reconstruir desde Minka / iNaturalist / GBIF.

**Palabras clave**: BioCLIP-2.5, ViT-H, k-NN, clasificación visual fina, biodiversidad marina, ciencia ciudadana, abstención taxonómica, calibración, mar Mediterráneo

---

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

### 2.2 Identificación (producción, 2026-09-14)

1. Embeber la consulta; fusionar **encuadre global + recorte central 65%**.
2. Recuperar **k=15** vecinos (FAISS si hay galería completa; centroide más cercano con los prototipos publicados si no).
3. Agregar votos **temperados** `Σ exp(max(s,0)/T)`, **T=0,05**, más un boost al prototipo.
4. Prior geográfico multiplicativo si hay GPS.
5. **Abstener** si el margen top-1/top-2 es pequeño y comparten género/familia, o si el par/género/grupo está en `dataset/taxonomic_exceptions.json`.
6. Pasar features k-NN → **P(acierto)** con regresión logística.

AutoID en FotoFauna publica si **p ≥ 0,80**. El estudio de umbral publicado (agosto 2026) estimó **~95,3% de precisión a ~57,4% de cobertura**. Esa curva no se ha vuelto a tabular como paper tras cada cambio de galería; el calibrador vivo es `created=2026-09-14T07:04:26`.

Este repositorio publica **centroides** (`data/patterns/<slug>/prototype.npy`): basta para un demo nearest-centroid. El k-NN completo exige reconstruir embeddings por foto en local ([`docs/dataset.md`](../docs/dataset.md)).

### 2.3 Datos (producción vs lo publicado)

| Capa | Producción | Este repo |
|------|------------|-----------|
| Fotografías | ~838 mil en disco | **No** (licencia) |
| Embeddings por foto | 848.883 vectores | **No** (tamaño + derivados de fotos) |
| Prototipo por especie | 4.702 × 1024 float32 | **Sí** (~15 MB) |
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

**Incidente (25/26-ago-2026).** La lista de IDs ya vistos apuntaba a una ruta abandonada y no coincidía con nada. El **42,7%** de una cosecha de 22.332 fotos ya estaba en la galería. Con k=15 el titular solo se movió ~1 pp; con k pequeño la curva era absurda. Arreglo: embeber cada candidato y tirar near-duplicates. Sigue como puerta de la cosecha.

**Dos métricas etiquetadas**

| Etiqueta | Cohorte | Top-1 especie | Uso |
|----------|---------|---------------|-----|
| **A — corte TTA** | `harvest_calib` n=12.788 (ago 2026, sin fuga) | 75,97% (luego 77,77% con pila de inferencia; 79,10% jsonl tras densificar) | Ablaciones comparables §4.1–4.2 |
| **B — calibrador vivo** | `calib_raw_t05` n=19.087 (2026-09-14) | **85,78%** | Informe de producción actual |

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

### 4.3 Fallos operativos (no son ideas de modelo; sí son públicos)

| ID | Fallo | Efecto | Aporte |
|----|-------|--------|--------|
| O1 | Cosecha de calibración filtrada a la galería | Curvas de k pequeño infladas | Dedup por similitud obligatorio. |
| O2 | Desync FAISS vs etiquetas tras `/reload` (1-sep-2026) | IDs vivos absurdas a 85–100%; **evals en disco válidas** | Recargar índice y labels juntos. |
| O3 | Métricas de admin leyendo snapshots congelados | Panel in-sample / viejo | Métricas desde el jsonl actual. |
| O4 | `--species` vacío tras SSH anidado (13-sep-2026) | Swap de calidad en taxones de más ~35 min | Pasar ficheros de slugs, nunca listas interpoladas. |

---

## 5. Informe de producción actual (cohorte B)

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

## 6. Limitaciones

1. El top-1 de especie no es nivel experto en invertebrados crípticos.
2. No hay estudio de generalización fuera del Mediterráneo.
3. El código público es un **identificador de reconstrucción**, no el volcado del servicio de 1.300 líneas de HanSolo.
4. La tabla precisión/cobertura de AutoID es anterior al calibrador del 14-sep.
5. Las correcciones de curadores aún no cierran un bucle de entrenamiento.

---

## 7. Reproducibilidad

```bash
git clone https://github.com/yespi/biofauna.git && cd biofauna
pip install -r requirements.txt
python -m uvicorn src.identify_service:app --host 0.0.0.0 --port 8090
```

Descarga BioCLIP-2.5 de Hugging Face al primer arranque. Usa prototipos en `data/patterns/`. Para reconstruir la galería completa: bajar fotos con los IDs de `dataset/catalog.json`, `scripts/reembed_vith.py`, dejar `embeddings.npy` junto a cada prototipo.

Licencia MIT para código y JSON/prototipos publicados. El copyright de las fotos sigue en observadores y plataformas.

---

## Agradecimientos

Xavier Salvador, Miquel Pontes y Manuel Ballesteros (GROC/OPK). Comunidades Minka e iNaturalist. WoRMS. BioCLIP (Stevens et al.).

---

## Disponibilidad de datos

Código, prototipos, catálogo, calibradores, priors, pares crípticos: este repositorio. Backbone: Hugging Face `imageomics/bioclip-2.5-vith14`. Imágenes: Minka/iNaturalist/GBIF por separado.

---

## Referencias

Las mismas que la versión inglesa (`01_biofauna.md`).

---

*Informe técnico del repositorio abierto. No es un envío a revista. Sedes posibles tras un PDF congelado: Ecological Informatics / Biodiversity Data Journal / PeerJ.*
