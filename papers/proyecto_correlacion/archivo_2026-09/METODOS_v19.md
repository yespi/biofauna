# Proyecto Correlación — Métodos

## 1. Datos

| Elemento | Origen | Cobertura |
|---|---|---|
| Fotografías | galería BioFauna (`/mnt/gpu/fotofauna-images` + `archive`) | **1.222.170** imágenes (8 fuentes públicas, ver README) |
| Observaciones con metadatos | API de iNaturalist, Minka y GBIF; enriquecidas vía API (volcado disponible en el repositorio público) | **759.207** obs · 100 % con geo y fecha · **92 % con hora** |
| Catálogo de especies | el catálogo del proyecto (repositorio público) | 2.985 taxones (checklist mediterránea curada) |

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

## 4 ter. Formalización matemática (añadido 29-sep-2026, requisito de revista)

### Métrica de similitud del identificador (k-NN sobre FAISS)

Dada una foto consulta con embedding normalizado $\mathbf{q} \in \mathbb{R}^{1024}$ (BioCLIP-2.5 ViT-H/14,
normalización $L_2$), y la galería de referencia $\mathcal{G} = \{\mathbf{g}_i\}_{i=1}^{M}$ con etiquetas
$\{y_i\}$, el k-NN devuelve los $k=15$ vecinos más próximos por **similitud coseno** (equivalente al producto
escalar en vectores normalizados):

$$
s_i = \mathbf{q} \cdot \mathbf{g}_i = \frac{\mathbf{q}^\top \mathbf{g}_i}{\lVert \mathbf{q} \rVert \lVert \mathbf{g}_i \rVert}
$$

La **similitud de la especie** $c$ es la máxima sobre sus vecinos en la foto: $s_c = \max_{i: y_i = c} s_i$.
La confianza publicable es la probabilidad calibrada $p_c = f_\theta(s_c, s_{c'}, m, \mathbf{v})$ donde $c'$ es
la segunda especie, $m = s_c - s_{c'}$ el margen, y $\mathbf{v}$ incluye votos, cobertura y $n_{ref}$ (regresión
logística isotónica, ECE 0,0091 en validación). La abstención jerárquica degrada a género/familia cuando
$m < \tau_{fam}$ (margen fijo) o por regla de mínimo riesgo bayesiano.

### Co-ocurrencia y lift

Sea $\mathcal{E}$ el conjunto de *eventos* (observador × celda ~1,1 km × día × franja de 3 h). Para un par
(A, B):

$$
n_{AB} = \lvert \{e \in \mathcal{E} : A \in e \land B \in e\} \rvert
$$

$$
\mathbb{E}[n_{AB}] = \frac{n_A \, n_B}{N}, \qquad N = \lvert \mathcal{E} \rvert
$$

$$
\text{lift}_{AB} = \frac{n_{AB}}{\mathbb{E}[n_{AB}]}
$$

El p-valor aproximado por Poisson (cola superior):

$$
p_{AB} = P(X \ge n_{AB}), \quad X \sim \text{Poisson}(\mathbb{E}[n_{AB}])
$$

Filtros de robustez: $n_{AB} \ge 8$ (soporte), $\ge 3$ celdas, $\ge 3$ días y **$\ge 5$ observadores
distintos** (control de la «ruta del fotógrafo»). El lift premia pares raros; el contraste definitivo es el
**nulo estratificado por localidad·fecha** (permutación intra-bloque con FDR de Benjamini-Hochberg), en curso.


## 4 bis. Filtro de OBSERVADORES distintos (añadido 28-sep-2026, corrección por revisión experta)

La revisión de un especialista (*Doto paulinae* no aparece asociado a *Sertularella mediterranea*) destapó un
sesgo grave: **una única salida de buceo** de un fotógrafo produce muchas co-ocurrencias que parecen
ecológicas y no lo son (la "ruta del fotógrafo"). Al medirlo, el par *Doto paulinae* + *Sertularella
mediterranea* tenía `n=5` pero **un solo observador** → espurio.

**Regla añadida: exigir ≥5 OBSERVADORES distintos** para cada par (además de ≥3 localidades y ≥3 días).
Con ella, los pares que ya conocíamos ganan crédito y aparecen asociaciones con sentido:

| par | n | observadores distintos | lectura |
|---|---:|---:|---|
| *Peltodoris atromaculata* + *Petrosia ficiformis* | 79 | **32** | el nudibranquio vive sobre su esponja ✅ |
| *Felimare picta* + *Ircinia oros* | 29 | **16** | esponja hospedadora ✅ |
| *Cratena peregrina* + *Eudendrium racemosum* | 5 | **5** | hidrozoo presa ✅ |
| ~~*Doto paulinae* + *Sertularella mediterranea*~~ | 5 | **1** | ❌ **descartado**: una sola salida (mi error, no era documentado) |

**Lección metodológica**: la validación de estas asociaciones no puede hacerse con pares que uno *cree*
documentados; debe pasar por (a) revisión experta y (b) filtros que maten el sesgo de salida/observador.

## 4 ter. Filtro de CALIDAD por rango geográfico (añadido 28-sep-2026, tras verificación bibliográfica)

La revisión bibliográfica de los pares *top* reveló que varios estaban formados por especies **no
mediterráneas** co-ocurriendo en eventos de **viajes de buceo** (un mismo grupo fotografía la misma inmersión
en el Mar Rojo, el Pacífico o el Atlántico). Ejemplos medidos en los datos:

| par | latitud de las observaciones | veredicto |
|---|---:|---|
| *Doris fontainii* + *Tyrinna delicata* | −55…−12 (Pacífico sur) | ❌ artefacto de viaje |
| *Chromodoris quadricolor* + *Hexabranchus sanguineus* | 20…29 (Mar Rojo/Indo-Pacífico) | ❌ artefacto de viaje |
| *Abudefduf saxatilis* + *Kyphosus vaigiensis* | atlántico vs. indo-pacífico | ❌ no coexisten en el área |
| *Lysmata grabhami* + *Telmatactis cricoides* | 27…29 (Canarias/Madeira) | ✅ real en territorio español |

**Regla añadida**: antes de interpretar cualquier candidata como asociación ecológica del área de estudio, se
cruza el **rango geográfico (WoRMS/OBIS/GBIF)** de ambas especies; los pares con especies alópatricas al área
se marcan como **artefacto por viaje de buceo** y se excluyen del análisis ecológico (aunque se conservan como
señal de control de calidad del *dataset*).

## 5. Validación interna (control de calidad del método)

El método se aplica **antes de mirar nada nuevo** a asociaciones **ya documentadas** en la bibliografía.
Si las recupera con fuerza, las candidatas nuevas merecen crédito:

| asociación documentada | n | lift | celdas | días | lectura |
|---|---:|---:|---:|---:|---|
| *Peltodoris atromaculata* + *Petrosia ficiformis* | 79 | 11,1 | 44 | 74 | el nudibranquio se alimenta de esa esponja y vive sobre ella |
| *Felimare picta* + *Ircinia oros* | 29 | 4,1 | 20 | 28 | depredación/esponja hospedadora |
| *Cratena peregrina* + *Eudendrium racemosum* | 5 | 10,5 | — | — | hidrozoo del que se alimenta |
| *Doto paulinae* + *Sertularella mediterranea* | 5 | 48,3 | — | — | hidrozoo hospedador |

> **Nota de implementación (30-sep-2026, revisión):** el script del nulo (`nulo_estratificado_20260929.py`) define el evento como *celda de 0,1° (~10 km) · día · franja de 3 h* **sin observador** y estratifica por *celda·día* (47.302 bloques); el análisis principal usa *observador × ~1 km × día × 3 h*. Las dos definiciones no son idénticas: el nulo es más conservador en el espacio (bloques más grandes) y no controla al observador. La sensibilidad al observador se evalúa aparte (`experimentos/SESGO_OBSERVADOR_PARES_20260929.md`). **Hecho (30-sep):** el nulo se repitió con la definición del análisis principal y con 2.000 permutaciones para ambas definiciones (resultados en el artículo, §4.3). Lección de método: el número de permutaciones fija un suelo p=1/(N+1) y, con 3.000 tests, el mejor q de Benjamini-Hochberg alcanzable es p·3000/k (k = pares en el suelo); con N pequeño el FDR no puede dar resultados significativos por construcción, de modo que «0 pares con FDR» solo es informativo si k·(0,05/3000) > 1/(N+1).

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

## 4 quater. Contraste condicionado al esfuerzo sobre todos los pares (añadido 5-oct-2026)

El nulo de §6 solo cubría los 3.000 pares de mayor lift. Desde el 5-oct se contrasta **toda** la familia de pares con n ≥ 5 eventos (115.204): dentro de cada bloque celda 0,1°·día, la probabilidad de que una especie esté en un evento es proporcional al tamaño del evento (condicionada a su frecuencia en el bloque); el esperado de eventos con ambas especies es la suma sobre bloques y su varianza la de una suma de Bernoulli independientes; p unilateral (normal con corrección de continuidad) y Benjamini-Hochberg sobre toda la familia. Niveles de evidencia por tamaño de efecto (razón observado/esperado ≥ 3, ≥ 5, ≥ 10) con replicación (≥3 celdas, ≥3 días, ≥5 observadores), y filtros de ámbito (≥80 % de eventos en el Mediterráneo, géneros y grupos distintos). Código `scripts/nulo_exacto_todos_pares_20261005.py`; resultados en `NULO_EXACTO_TODOS_PARES_20261005.md` y artículo §3.10. Limitación declarada: el resultado depende del modelo nulo (p. ej. *Fistularia commersonii*–*Pterois miles* es significativo aquí y no con el nulo de §6).
