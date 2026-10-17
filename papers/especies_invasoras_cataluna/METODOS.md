# 2. Material y métodos

## 2.1 Lista de especies y estatus legal

Trabajamos con los 114 taxones de la lista UE (Material suplementario S1), verificados contra los Reglamentos de Ejecución citados en la Introducción. El Catálogo Español (RD 630/2013, texto consolidado BOE-A-2013-8565) se usó para anotar inclusión en el anexo (columna CEEA en Tabla S1).

## 2.2 Área de estudio y fuentes de datos

El área de estudio es Cataluña. Las observaciones proceden de:

- **iNaturalist:** place Cataluña (61614) y España (6774) para comparaciones nacionales.
- **Minka:** registros dentro de una **caja rectangular** (0,1–3,4° E; 40,45–42,95° N), que incluye territorio no catalán (Aragón, Andorra, Francia) y mar. Para mapas y descripción del área usamos además un **contorno provincial aproximado** (`material/geo/catalunya_icgc_admin.geojson`: unión de Barcelona, Girona, Lleida y Tarragona a partir de `spain-provinces.geojson`, más una franja marina rectangular ~12 mn al este; sustituto hasta disponer de la capa ICGC oficial).

**Última observación en Cataluña (Tablas 2–3, S1, Top 15):** fecha más reciente *research grade* en la caja, obtenida en este orden: (1) tablas locales `public_observations` e `inat_backfill_20261011` en PostgreSQL; (2) si no hay fecha, consulta a la API de Minka (máximo 1 petición cada 5 s, sin llamadas a iNaturalist). Donde ninguna fuente devuelve fecha utilizable se anota «sin datos» (p. ej. conteos agregados de iNaturalist de octubre de 2026 sin filas fechadas en la base local).

Para cada región reportamos el **máximo** entre fuentes, no la suma. Es una **cota inferior**, no una unión deduplicada a nivel de observación individual. En la caja de estudio, al agrupar por taxón, año y celda de ~1 km (coordenadas redondeadas), el solape iNaturalist–Minka representa ~0,4 % de las observaciones *research grade* (372.987 frente a 374.348); los conteos por especie siguen sin deduplicar entre plataformas.

**Filtros de calidad:** grado de investigación (*research grade*), exclusión de observaciones cautivas o cultivadas (`captive=false`) y precisión posicional ≤ 1 km cuando el metadato está disponible. Fecha de descarga: octubre de 2026.

## 2.3 Categorías de presencia en Cataluña

Reglas aplicadas una sola vez en todo el manuscrito (no equivalen a estatus EASIN):

| Categoría | Criterio |
|---|---|
| Ausente | 0 observaciones en todas las fuentes |
| Ocasional | &lt; 10 observaciones, o &lt; 3 celdas UTM de 10 km, o &lt; 3 años con registros |
| Llegada reciente / serie insuficiente | Primer registro ≥ 2020 (serie < 5 años; no estimable) |
| En expansión | ≥ 10 obs, ≥ 5 años y razón de tasas > 1 con FDR &lt; 0,05 (ninguna especie la cumple) |
| Recurrente | Resto con ≥ 10 obs, ≥ 3 celdas y ≥ 3 años (describe detección repetida; no implica población establecida) |

Los valores centinela 99,0 del ratio de esfuerzo se sustituyeron por «sin datos» cuando no hay ventana previa suficiente. En las tablas por especie, «sin datos» indica fechas no recuperables con las fuentes locales descritas en §2.2.

## 2.4 Esfuerzo y tasa de detección

**Esfuerzo independiente por grupo (P1).** Para las tendencias (§2.5) el denominador no es el total de la base BioQuest ni un total común a todas las especies, sino el **número anual de observaciones *research grade* del mismo grupo taxonómico** que la especie, obtenido de GBIF (conjunto de datos *iNaturalist Research-grade Observations*, `datasetKey` 50c9509d-22c7-4a22-a47d-8c48425ef4a7; `basisOfRecord = HUMAN_OBSERVATION`, `occurrenceStatus = PRESENT`, con coordenadas) en la región administrativa de Cataluña (GADM `ESP.6_1`), descargado el 16-oct-2026 por la API pública de GBIF (no se usó la API de iNaturalist ni de Minka). Grupos: plantas (Plantae), aves, mamíferos, herpetofauna (anfibios, escamosos y tortugas), peces (Chordata menos aves, mamíferos, herpetofauna y ascidias), insectos, otros animales (invertebrados no insectos) y otros (hongos, cromistas, etc.); cada taxón de la lista se asigna por su clase. Ventana 2013–2025 (2008–2012 tienen < 4.000 registros/año y se muestran pero no se modelan); **2026 es año parcial y se excluye**. Los filtros del esfuerzo y de las especies son idénticos y el offset excluye los registros de la propia especie. Scripts y datos: `material/p1_gbif_esfuerzo_y_registros_20261016.py`, `p1_observer_year_gbif_20261016.py`, `esfuerzo_grupo_gbif_20261016.csv` (Fig. 2). No se aplicó filtro de incertidumbre posicional ni se auditó `captive` más allá de la definición de *research grade* del conjunto. Los totales de la caja iNaturalist+Minka (Tabla S2, Fig. 2 a) se conservan solo como descriptivo de la base local; su salto de 2008 (847) y el crecimiento 2021–2024 sugieren efectos de sincronización de la base. La región GADM es terrestre-costera: los registros marinos alejados de la costa (buceo) pueden quedar fuera, por lo que el análisis de tendencias es menos informativo para taxones marinos.

La tasa de detección de una especie es el cociente entre sus observaciones y el esfuerzo del grupo. Las **cifras de presencia** (Tablas 2–3, S1, Top 15) siguen basadas en iNaturalist + Minka en la caja de estudio (§2.2); las **tendencias** usan únicamente GBIF-iNaturalist (la única fuente con observador y esfuerzo por grupo reproducibles), por lo que los *n* de la Tabla S5 son menores que los de presencia.

Para taxones ausentes en Cataluña pero presentes en España según EASIN, estimamos de forma exploratoria la probabilidad de cero registros locales si la especie estuviera presente, usando la tasa relativa en España y el esfuerzo catalán de 2024 como referencia (Material suplementario S3).

## 2.5 Tendencias temporales

Para cada taxón de la lista de la Unión con ≥ 10 observaciones y ≥ 5 años con registros en 2013–2025 (GBIF-iNaturalist; 13 especies estimables) ajustamos un **modelo lineal generalizado mixto (GLMM) de Poisson con intercepto aleatorio de observador**. La unidad es el par observador–año (todos los observadores activos en el grupo de la especie ese año, de modo que los ceros se incluyen):

`y_jt ~ Poisson(μ_jt),  log μ_jt = log(n_jt − y_jt) + β0 + β1·(año − año central) + u_j,  u_j ~ N(0, σ²)`

donde *y* son los registros de la especie del observador *j* en el año *t* y *n* sus registros totales en el grupo (el offset es el esfuerzo del propio observador, excluida la especie). La verosimilitud marginal se evalúa por cuadratura de Gauss–Hermite (40 nodos) y se maximiza con BFGS (convergencia comprobada con Nelder–Mead y gradiente < 10⁻²); el error estándar de β1 es de tipo *sandwich* agrupado por observador, robusto a la sobredispersión. Reportamos la razón de tasas anual RR = exp(β1), su IC 95 % y p; se aplica la corrección de Benjamini–Hochberg (FDR) sobre el conjunto de especies estimables de cada ventana. **Sensibilidad:** (i) mismo modelo sin efecto aleatorio; (ii) mismo modelo **sin los tres observadores con más registros de la especie**; (iii) ventana 2016–2025. **Criterio de categoría:** una especie se clasifica «en expansión» solo si RR > 1 con q < 0,05 **y** el aumento se mantiene (q < 0,05) al excluir a los tres principales observadores; un aumento que desaparece sin ellos se informa como «creciente no robusto». No se modeló efecto aleatorio de celda (la serie por celda es demasiado escasa para estas especies). Script y salida: `material/p2_glmm_observador_20261016.py`, `glm_tendencias_glmm_20261016.csv` (Tabla S5, Fig. 4). Se implementó en Python (R/glmmTMB no disponible en el servidor); el mismo modelo es reproducible con `glmmTMB(y ~ año + offset(log(esf)) + (1|obs), family = poisson)`.

## 2.6 Hábitat

Para fauna acuática reclasificamos hábitat con indicadores WoRMS (`isMarine`, `isBrackish`, `isFreshwater`, `isTerrestrial`; consulta 15-oct-2026; Material suplementario S4). WoRMS devolvió registro para 58 de los 114 taxones; para el resto (plantas y vertebrados terrestres) WoRMS no es una fuente de hábitat y la clasificación procede de fuentes secundarias del proyecto. La clasificación **marina** (8 taxones) es coincidente con WoRMS. Las categorías son no excluyentes.

## 2.7 Origen, vías y primeras fechas

Origen nativo y vías se documentan en la Tabla 2 con categorías CBD/EASIN (una especie puede tener varias vías; EASIN consultado el 15-oct-2026) y, cuando no hay fuente, se marcan como hipótesis. Las «primeras fechas» ciudadanas se distinguen de las primeras citas publicadas (columnas separadas en Tabla 3). Las flechas de expansión en mapas siguen solo rutas marítimas plausibles o saltos humanos discontinuos (acuicultura, fouling), nunca expansión terrestre de especies estrictamente marinas.

## 2.8 Modelo de ocupación (extensión)

El GLMM de §2.5 estima la tendencia de detección con intercepto aleatorio de observador y offset de esfuerzo del grupo: es el núcleo reproducible del paper. Como extensión planificada, un modelo de **ocupación** con unidad celda UTM 10 km × año, detectabilidad ligada al esfuerzo del grupo y presencia latente ψ, requeriría series por celda que hoy solo son fiables para un puñado de taxones conspicuos (*Myocastor*, *Vespa velutina*). No sustituye las tablas de presencia actuales.

## 2.9 Alerta temprana (FotoFauna / AutoID)

Ver `USO_ALERTA_TEMPRANA.md`: umbrales de publicación automática, taxones sin eval (Tabla S7) y relación con el acierto por especie (Tabla S6).

## 2.10 Exóticas marinas no incluidas en la lista UE

Complementamos el análisis con un subconjunto de exóticas marinas documentadas en inventarios regionales (inventario ampliado facilitado por B. Weitzmann, provisional; García et al. 2015), contrastando primer registro ciudadano y primera cita bibliográfica. *Pterois miles* y *Lagocephalus sceleratus* se tratan en un recuadro de contexto mediterráneo (sin registros en Cataluña en nuestras fuentes).
