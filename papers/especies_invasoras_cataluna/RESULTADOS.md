# 3. Resultados

## 3.1 Presencia en Cataluña y España

De los 114 taxones analizados, **35** presentaron al menos una observación en Cataluña y **52** en España (máximo entre fuentes; Tabla S1). Setenta y nueve taxones figuraron como ausentes en Cataluña en octubre de 2026.

### Top 15 en Cataluña (observaciones combinadas)

| Especie | Obs CAT | Observadores | Celdas UTM 10 km | Primer registro | Última observación | Categoría | Hábitat |
| *Ailanthus altissima* | 1540 | 450 | 431 | 2008-06-08 | 2008-06-08 | recurrente | T |
| *Procambarus clarkii* | 646 | 386 | 441 | 2001-09-23 | 2007-08-26 | recurrente | D+S+X |
| *Myocastor coypus* | 498 | 301 | 242 | 2012-06-25 | 2026-10-01 | en expansión | T |
| *Trachemys scripta elegans* | 263 | 138 | 177 | 2006-05-06 | 2011-03-26 | recurrente | D |
| *Broussonetia papyrifera* | 175 | 93 | 145 | 2017-06-09 | 2019-04-13 | recurrente | T |
| *Alopochen aegyptiaca* | 167 | 100 | 92 | 2010-04-16 | 2010-08-23 | recurrente | T |
| *Vespa velutina nigrithorax* | 156 | 88 | 143 | 2017-11-22 | 2020-10-20 | en expansión | T |
| *Gambusia holbrooki* | 128 | 89 | 93 | 2007-07-13 | 2026-07-14 | recurrente | D+S+X |
| *Neogale vison* | 109 | 64 | 76 | 2010-08-08 | 2026-04-11 | recurrente | T |
| *Pennisetum setaceum* | 109 | 50 | 75 | 2016-01-20 | 2019-10-31 | recurrente | T |
| *Delairea odorata* | 107 | 49 | 69 | 2009-12-29 | 2021-05-14 | recurrente | T |
| *Rugulopteryx okamurae* | 101 | 4 | 25 | 2024-05-31 | 2026-10-01 | reciente | M |
| *Acacia saligna* | 65 | 49 | 55 | 2019-07-08 | 2026-04-25 | recurrente | T |
| *Ludwigia peploides* | 58 | 36 | 49 | 2009-08-02 | 2019-08-17 | recurrente | D |
| *Lepomis gibbosus* | 36 | 28 | 34 | 2003-07-21 | 2010-08-23 | recurrente | D+S+X |

Etiquetas de hábitat: M = marino, S = salobre, D = agua dulce, T = terrestre (no excluyentes; ver Métodos).

## 3.2 Composición por categoría y hábitat

| Categoría (Cataluña) | N |
|---|---:|
| ausente | 79 |
| ocasional | 15 |
| recurrente | 15 |
| en expansión (tasa de detección, GLMM robusto) | 2 |
| llegada reciente (serie insuficiente) | 2 |

La categoría «en expansión» exige RR &gt; 1 con FDR &lt; 0,05 **y** el mismo criterio al excluir a los tres observadores con más registros de la especie (§2.3–2.5). Con ello solo *Myocastor coypus* y *Vespa velutina nigrithorax* la cumplen; *Gambusia holbrooki* y *Ludwigia peploides* aumentan en el modelo completo pero dejan de ser significativas sin los tres principales observadores.

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

En la base local (iNaturalist + Minka, caja §2.2) el total *research grade* pasó de **1.220** (2013) a **102.052** (2024) y **105.050** (2025), factor ~84× (Fig. 2; Tabla S2; 2026 parcial). El pico de 2008 (847) y el salto 2021–2024 reflejan en parte sincronización de la base BioQuest, no solo actividad de campo.

Para las **tendencias** usamos un denominador independiente: observaciones anuales del mismo grupo taxonómico en Cataluña (GADM `ESP.6_1`) descargadas de GBIF (dataset iNaturalist *research grade*, 16-oct-2026; `material/esfuerzo_grupo_gbif_20261016.csv`). Entre 2013 y 2024 el esfuerzo de plantas pasa de ~1.400 a ~48.000 registros/año; aves, de ~1.100 a ~22.000; el total agregado no reproduce el artefacto de 2008 de la Tabla S2 (Fig. 2 cont.). La densidad espacial del esfuerzo local 2018–2024 sigue en la Fig. 1.

En la caja, el solape iNaturalist–Minka a nivel de celda año–taxón–coordenada redondeada es pequeño: **372.987** observaciones tras deduplicar frente a **374.348** brutas (~0,4 %), pero el máximo por especie entre fuentes sigue sin deduplicar (Métodos).

## 3.4 Tendencias de detección

Ajustamos el GLMM de §2.5 a las **13** especies de la lista de la Unión con ≥10 observaciones y ≥5 años con registro en GBIF-iNaturalist (Cataluña GADM) en 2013–2025 (Fig. 4; Tabla S5). La unidad es observador–año con offset del esfuerzo del observador en el grupo.

**Aumento robusto (q &lt; 0,05 y persistente sin los tres observadores principales):** *Myocastor coypus* (RR 1,13/año; IC 95 % 1,05–1,21; q = 0,004) y *Vespa velutina nigrithorax* (1,36; 1,18–1,56; q &lt; 0,001). **Aumento no robusto:** *Gambusia holbrooki* (1,24; q = 0,022) y *Ludwigia peploides* (1,15; q = 0,004) pierden significación al excluir a los tres observadores con más registros (Tabla S5). *Ailanthus altissima* (847 obs. en GBIF) no muestra tendencia significativa con efecto aleatorio de observador (RR 0,93; q = 0,18), coherente con campañas puntuales en la serie local.

**Descenso significativo:** *Neogale vison* (0,89; q = 0,017), *Procambarus clarkii* (0,92; q = 0,002) y, en sensibilidad sin top-3, *Ailanthus* (0,91; q = 0,066 en el modelo completo; 0,89 sin top-3 con q = 0,035). *Trachemys scripta elegans* y *Alopochen aegyptiaca* tienen pocas observaciones en GBIF-Cataluña y no entran en el panel estimable (presencia en Tabla 3 basada en iNat+Minka).

*Rugulopteryx okamurae* (primer registro 2024) e *Impatiens glandulifera* (2022) permanecen como «llegada reciente». *Reynoutria sachalinensis* es un registro único (2020).

## 3.5 Concordancia con EASIN (España)

A escala de país, EASIN registra **76** taxones de la lista como presentes en España; nuestras fuentes ciudadanas dan **52**, con **50** coincidencias (Tabla 4; Tabla S4). **26** taxones figuran en EASIN sin registro ciudadano nuestro (falsos ausentes a escala España, sobre todo grupos infradetectados). **2** registros ciudadanos (*Mulinia lateralis*, *Andropogon virginicus*) no tienen respaldo en EASIN. A escala catalana, la **Fig. 5** contrasta, para un subconjunto de taxones presentes con fuente verificable, el año de la primera cita en inventario o literatura (EXOCAT u otras referencias citadas en `material/concordancia_exocat_oficial_20261016.csv`) frente al primer registro ciudadano *research grade* en la caja. El retraso es nulo o pequeño en varias especies marinas ya inventariadas (*Oculina patagonica*, *Caulerpa cylindracea*) y puede superar una década en casos recientes de detección ciudadana (*Rugulopteryx okamurae*) o en taxones cuya primera fecha en plataforma no coincide con la primera presencia documentada (*Myocastor coypus*, *Trachemys scripta elegans*; ver Limitaciones). Una concordancia celda a celda con el inventario EXOCAT completo sigue pendiente de descarga masiva del portal de la Generalitat.

## 3.6 Origen, vía y primeras fechas

La Tabla 2 resume origen, hábitat, vía y primer registro ciudadano para los **35** taxones presentes en Cataluña. Las fichas largas por especie marítima complementaria permanecen en la sección de origen y vías.

**Vigilancia — *Oxyura jamaicensis* (malvasía canela):** Norteamérica; agua dulce; escape de colecciones de aves ornamentales (Reino Unido, años 1950); Reg. 2016/1141; CEEA; amenaza por hibridación con *Oxyura leucocephala*; sin registros en Cataluña en este estudio (WoRMS AphiaID 159100: no marina).

## 3.7 Exóticas marinas no incluidas en la lista UE

*Callinectes sapidus*, *Caulerpa cylindracea*, *Oculina patagonica*, *Asparagopsis armata* y otras figuran en inventarios regionales con primeras citas publicadas anteriores al primer registro ciudadano en Cataluña (Fig. 7). Los registros de *Zebrasoma flavescens* y *Balistoides conspicillum* en iNaturalist (10 y 6 observaciones) se consideran **probables cautivos** (peces de acuario indopacíficos; WoRMS: solo marinos; sin población establecida conocida en el Mediterráneo noroccidental) y se excluyen de los conteos de presencia hasta verificación caso a caso.

### Recuadro — contexto mediterráneo sin registros en Cataluña

*Pterois miles* y *Lagocephalus sceleratus* no tienen observaciones en España ni en Cataluña en nuestras descargas. La primera cita mediterránea del pez león es Israel, 1991 (Golani & Sonin 1992), con vía lessepsiana; el patrón «entrada ~2008» en mapas ciudadanos refleja el inicio tardío de la ciencia ciudadana (ver Discusión).

## 3.8 *Rugulopteryx okamurae*

Único alga de la lista UE con registros marinos en Cataluña. Primer registro ciudadano: 31 mayo 2024 (iNaturalist). La literatura sitúa la primera cita mediterránea en la laguna de Thau (Francia; Verlaque et al. 2009), con importaciones de ostras como vía propuesta (EASIN: contaminante de animales), y la expansión explosiva en el Estrecho desde 2015 (García-Gómez et al. 2020). En Cataluña las **101** observaciones proceden de **cuatro** observadores y **25** celdas UTM de 10 km (sesgo extremo: media ~25 obs por observador). La cifra es el máximo entre fuentes (Minka 101, iNaturalist 83), no una unión deduplicada. No se ha localizado una primera cita catalana publicada previa a 2024. Fig. 6 (mapas por periodos de cinco años) y Fig. 3 (composición por categoría).

La Fig. 4 resume las tendencias estimables; la Tabla 3 y el Material suplementario S6 enlazan presencia, fechas y acierto del identificador. Las fichas en prosa de las especies prioritarias continúan en el §3.10.

## 3.9 Sesgos de muestreo (cuantificación breve)

La Fig. 1 muestra la concentración del esfuerzo en la costa y el área metropolitana de Barcelona. Entre las especies con muchos registros, la participación del observador principal es baja en especies generalistas (*Ailanthus altissima*, cientos de observadores) y alta en *Rugulopteryx okamurae* (cuatro observadores para 101 registros). Para **19** taxones ausentes en Cataluña pero presentes en España según EASIN, la probabilidad de cero registros en Cataluña si la especie estuviera presente con la misma tasa relativa es &lt;0,05 en **7** casos (Material suplementario S3), lo que indica que la mayoría de ausencias locales son informativas solo de forma parcial.
