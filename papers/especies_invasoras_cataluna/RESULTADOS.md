# 3. Resultados

## 3.1 Presencia en Cataluña y España

De los 114 taxones analizados, **35** presentaron al menos una observación en Cataluña y **52** en España (máximo entre fuentes; Tabla S1). Setenta y nueve taxones figuraron como ausentes en Cataluña en octubre de 2026.

### Top 15 en Cataluña (observaciones combinadas)

| Especie | Obs CAT | Observadores | Celdas UTM 10 km | Categoría | Hábitat |
|---|---:|---:|---:|---|---|
| *Ailanthus altissima* | 1540 | 450 | 431 | recurrente | T |
| *Procambarus clarkii* | 646 | 386 | 441 | recurrente | D+S |
| *Myocastor coypus* | 498 | 301 | 242 | recurrente | T |
| *Trachemys scripta* | 263 | 138 | 177 | recurrente | D |
| *Broussonetia papyrifera* | 175 | 93 | 145 | recurrente | T |
| *Alopochen aegyptiaca* | 167 | 100 | 92 | recurrente | T |
| *Vespa velutina nigrithorax* | 156 | 88 | 143 | recurrente | T |
| *Gambusia holbrooki* | 128 | 89 | 93 | recurrente | D+S |
| *Neogale vison* | 109 | 64 | 76 | recurrente | T |
| *Cenchrus setaceus* | 109 | 50 | 75 | recurrente | T |
| *Delairea odorata* | 107 | 49 | 69 | recurrente | T |
| *Rugulopteryx okamurae* | 101 | 4 | 25 | llegada reciente | M |
| *Acacia saligna* | 65 | 49 | 55 | recurrente | T |
| *Ludwigia peploides* | 58 | 36 | 49 | recurrente | D |
| *Lepomis gibbosus* | 36 | 28 | 34 | recurrente | D+S |

Etiquetas de hábitat: M = marino, S = salobre, D = agua dulce, T = terrestre (no excluyentes; ver Métodos).

## 3.2 Composición por categoría y hábitat

| Categoría (Cataluña) | N |
|---|---:|
| ausente | 79 |
| ocasional | 15 |
| recurrente | 18 |
| llegada reciente (serie insuficiente) | 2 |

Ningún taxón cumple el criterio «en expansión» del GLM con FDR &lt; 0,05 (véase §3.4). Las etiquetas internas `ocasional_o_puntual` y `llegada_reciente_serie_insuficiente` se muestran en lenguaje natural en las tablas del cuerpo.

### Hábitat en la lista UE (114 taxones; categorías no excluyentes, WoRMS 15-oct-2026)

| Hábitat | N taxones |
|---|---:|
| terrestre | 75 |
| agua dulce | 35 |
| salobre | 12 |
| marino | 8 |
| mixto/diádromo | 11 |

De los taxones marinos o salobres de la lista de la Unión, solo *Rugulopteryx okamurae* tiene registros en Cataluña en las fuentes ciudadanas analizadas (101 observaciones desde 2024).

## 3.3 Esfuerzo de observación

El número de observaciones de la **base BioQuest** (694 taxones; no el total de iNaturalist/Minka) en la caja de Cataluña pasó de **1.220** (2013) a **102.301** (2024) y **105.404** (2025), factor ~84× entre 2013 y 2024 (Fig. 2; Tabla S2; 2026 es año parcial). El valor anómalo de 2008 (858, frente a 55 y 298 en los años contiguos) y el salto 2021–2024 sugieren efectos de ingesta de la base y no solo de actividad de observadores.

Como aproximación al plan de esfuerzo por grupo (P1), las observaciones *research grade* de los taxones del catálogo en la misma caja se desglosan por grupo taxonómico (plantas, aves, mamíferos, peces, invertebrados; Fig. 2 cont.). La densidad espacial del esfuerzo 2018–2024 se resume en la Fig. 1 (mapa de calor sobre celdas ~10 km).

En la caja, el solape iNaturalist–Minka a nivel de celda año–taxón–coordenada redondeada es pequeño: **372.987** observaciones tras deduplicar frente a **374.348** brutas (~0,4 %), pero el máximo por especie entre fuentes sigue sin deduplicar (Métodos).

## 3.4 Tendencias de detección

Ajustamos el modelo binomial negativo descrito en §2.5 a las 17 especies de la lista de la Unión con ≥10 observaciones y ≥5 años con registros en 2013–2025 (`material/glm_tendencias_20261015.csv`; Fig. 4). **Ninguna especie mostró un aumento significativo de su tasa de detección tras la corrección FDR**. Dos especies mostraron descenso: *Neogale vison* (razón de tasas anual 0,84; IC 95 % 0,76–0,92; q = 0,005) y *Trachemys scripta elegans* (0,86; 0,77–0,95; q = 0,026). *Ailanthus altissima* tuvo la estimación más alta con precisión (1,17; 1,03–1,32) pero q = 0,067; su serie contiene un salto 2020→2021 (18→134 registros) que no acompaña al esfuerzo (×1,4) y que puede deberse a un observador o campaña concretos, no analizado. Con la ventana 2016–2025 los resultados son cualitativamente iguales (descenso además de *Threskiornis aethiopicus* y *Alopochen aegyptiaca*). Un análisis previo con estadístico tau/z sin FDR, que clasificaba cuatro a seis especies «en expansión», queda **superado** y no debe citarse.

*Rugulopteryx okamurae* (primer registro 2024) e *Impatiens glandulifera* (primer registro 2022) se clasifican como «llegada reciente»: sus series son demasiado cortas para estimar tendencia. *Reynoutria sachalinensis* es un registro único (2020), sin potencia de ausencia estimable.

## 3.5 Concordancia con EASIN (España)

A escala de país, EASIN registra **76** taxones de la lista como presentes en España; nuestras fuentes ciudadanas dan **52**, con **50** coincidencias (Tabla 4; Tabla S4). **26** taxones figuran en EASIN sin registro ciudadano nuestro (falsos ausentes a escala España, sobre todo grupos infradetectados). **2** registros ciudadanos (*Mulinia lateralis*, *Andropogon virginicus*) no tienen respaldo en EASIN. La comparación con EXOCAT en Cataluña permanece pendiente de descarga del inventario autonómico.

## 3.6 Origen, vía y primeras fechas

La Tabla 2 resume origen, hábitat, vía y primer registro ciudadano para los **35** taxones presentes en Cataluña. Las fichas largas por especie marítima complementaria permanecen en la sección de origen y vías.

**Vigilancia — *Oxyura jamaicensis* (malvasía canela):** Norteamérica; agua dulce; escape de colecciones de aves ornamentales (Reino Unido, años 1950); Reg. 2016/1141; CEEA; amenaza por hibridación con *Oxyura leucocephala*; sin registros en Cataluña en este estudio (WoRMS AphiaID 159100: no marina).

## 3.7 Exóticas marinas no incluidas en la lista UE

*Callinectes sapidus*, *Caulerpa cylindracea*, *Oculina patagonica*, *Asparagopsis armata* y otras figuran en inventarios regionales con primeras citas publicadas anteriores al primer registro ciudadano en Cataluña (Fig. 7). Los registros de *Zebrasoma flavescens* y *Balistoides conspicillum* en iNaturalist (10 y 6 observaciones) se consideran **probables cautivos** (peces de acuario indopacíficos; WoRMS: solo marinos; sin población establecida conocida en el Mediterráneo noroccidental) y se excluyen de los conteos de presencia hasta verificación caso a caso.

### Recuadro — contexto mediterráneo sin registros en Cataluña

*Pterois miles* y *Lagocephalus sceleratus* no tienen observaciones en España ni en Cataluña en nuestras descargas. La primera cita mediterránea del pez león es Israel, 1991 (Golani & Sonin 1992), con vía lessepsiana; el patrón «entrada ~2008» en mapas ciudadanos refleja el inicio tardío de la ciencia ciudadana (ver Discusión).

## 3.8 *Rugulopteryx okamurae*

Único alga de la lista UE con registros marinos en Cataluña. Primer registro ciudadano: 31 mayo 2024 (iNaturalist). La literatura sitúa la primera cita mediterránea en la laguna de Thau (Francia; Verlaque et al. 2009), con importaciones de ostras como vía propuesta (EASIN: contaminante de animales), y la expansión explosiva en el Estrecho desde 2015 (García-Gómez et al. 2020). En Cataluña las **101** observaciones proceden de **cuatro** observadores y **25** celdas UTM de 10 km (sesgo extremo: media ~25 obs por observador). La cifra es el máximo entre fuentes (Minka 101, iNaturalist 83), no una unión deduplicada. No se ha localizado una primera cita catalana publicada previa a 2024 (plan P10). Fig. 6 (mapas por periodos de cinco años) y Fig. 3 (composición por categoría).

## 3.9 Sesgos de muestreo (cuantificación breve)

La Fig. 1 muestra la concentración del esfuerzo en la costa y el área metropolitana de Barcelona. Entre las especies con muchos registros, la participación del observador principal es baja en especies generalistas (*Ailanthus altissima*, cientos de observadores) y alta en *Rugulopteryx okamurae* (cuatro observadores para 101 registros). Para **19** taxones ausentes en Cataluña pero presentes en España según EASIN, la probabilidad de cero registros en Cataluña si la especie estuviera presente con la misma tasa relativa es &lt;0,05 en **7** casos (análisis de potencia de ausencia, P3; suplemento), lo que indica que la mayoría de ausencias locales son informativas solo de forma parcial.
