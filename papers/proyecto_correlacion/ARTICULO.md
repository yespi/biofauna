# Asociaciones entre especies marinas reveladas por un identificador automático de fauna y 1,2 millones de fotografías de ciencia ciudadana

**Autor: Gustavo Zafra** · Creador y desarrollador de BioFauna (identificador BioCLIP-2.5 ViT-H/14 + FAISS)
y de las aplicaciones FotoFauna y BioQuest; colaborador de la plataforma de ciencia ciudadana Minka SDG.

**Borrador v10 — 29-sep-2026** · Proyecto Correlación (BioFauna)

---

## Resumen

La ciencia ciudadana marina ha generado volúmenes de observaciones con fotografía que rara vez se explotan más
allá de la distribución de especies. Aquí presentamos un análisis de **1.222.170 fotografías** y **759.207
observaciones geolocalizadas y fechadas** (Minka SDG, iNaturalist y otras fuentes públicas), identificadas de
forma automática por **BioFauna** —un recuperador k-NN sobre *embeddings* de BioCLIP-2.5 ViT-H/14 con
calibración jerárquica— para descubrir **asociaciones entre especies**. Definimos un *evento* de muestreo
(observador × celda ~1 km × día × franja de 3 h) y evaluamos la co-ocurrencia de pares con soporte,
repetibilidad espacial y temporal, hallando **70.971 pares significativos**. El método **recupera asociaciones
ya documentadas** con alta robustez —por ejemplo *Peltodoris atromaculata* sobre la esponja *Petrosia
ficiformis* (79 eventos, lift 11,1, 44 localidades, 74 días)— y revela **candidatas no descritas** con lectura
biológica plausible, como medusas con anfípodos hiperídeos comensales, gambas limpiadoras con anémonas y
parejas de fauna infaunal. El trabajo subraya el papel de las personas curadoras en la verificación de las
especies crípticas y esboza su aplicación a la conservación y a la divulgación.

**Palabras clave:** ciencia ciudadana, asociaciones interespecíficas, *habitat use*, aprendizaje profundo,
Mediterráneo, fotografía submarina.

## 1. Introducción

La fotografía submarina *amateur* se ha convertido en una fuente masiva de datos de biodiversidad. Las
plataformas de ciencia ciudadana (**Minka SDG**, impulsada desde el ecosistema **FECDAS**; **iNaturalist**;
**GBIF**) acumulan millones de observaciones verificadas, y los identificadores automáticos permiten
consolidar ese archivo a escala de catálogo. Sin embargo, la mayoría de los análisis se limitan a inventarios
y mapas de distribución. Las fotografías contienen además **contexto ecológico**: qué especies aparecen
juntas, sobre qué sustrato y en qué condiciones. Este trabajo explora esa información latente.

*(Precedente: el uso de co-ocurrencia en datos participativos para inferir asociaciones, con sus conocidos
sesgos de esfuerzo y observador —ver §Límites.)*

## 2. Material y métodos

Resumen (detalle en [`METODOS.md`](METODOS.md) y en el material suplementario):

- **Datos**: 1.222.170 fotografías; 759.207 observaciones con coordenadas, fecha y (92 %) hora; catálogo curado
  de 2.985 taxones mediterráneos.
- **Identificación**: BioFauna (BioCLIP-2.5 ViT-H/14 + FAISS k-NN, k=15, agregador T=0,05 con tope de 3 votos
  por especie, calibración jerárquica), con guardas de publicación y auditoría de fugas.
- **Unidad de análisis**: *evento* = (observador × celda ~1,1 km × día × franja de 3 h); grupo de especies
  vistas juntas.
- **Filtros**: solo catálogo; soporte ≥8 eventos; repetibilidad en **≥3 localidades y ≥3 días** y **≥5 observadores distintos** (este último añadido tras detectar que una sola salida de buceo genera falsas asociaciones).
- **Métricas**: co-ocurrencia observada `n`, esperada por marginales y **lift**; p de Poisson para cribado.
- **Validación interna**: búsqueda ciega de asociaciones documentadas (§3.1).

## 3. Resultados

### 3.1 Validación del método (asociaciones documentadas recuperadas)

| asociación | n | lift | localidades | días | fuente |
|---|---:|---:|---:|---:|---|
| *Peltodoris atromaculata* — *Petrosia ficiformis* | 79 | 11,1 | 44 | 74 | bibliografía clásica |
| *Felimare picta* — *Ircinia oros* | 29 | 4,1 | 20 | 28 | esponja hospedadora |
| *Cratena peregrina* — *Eudendrium racemosum* | 5 | 10,5 | — | — | hidrozoo presa |
| ~~*Doto paulinae* — *Sertularella mediterranea*~~ | 5 | 48,3 | — | — | ❌ **descartada**: un único observador (corrección tras revisión experta) |

**La co-ocurrencia no es artefacto de la matriz de confusión** (29-sep-2026): los pares documentados muestran
**confusión cruzada nula** (0-1 casos de A→B o B→A en 3-19 muestras por especie), mientras los pares de
especies hermanas confundibles (control: *Elysia marginata/ornata*, *Spirobranchus lamarcki/triqueter*)
presentan confusión cruzada alta (13-26 %) y **no** aparecen como candidatas de co-ocurrencia. El sesgo de
observador se controla exigiendo ≥5 observadores distintos. Detalle:
(detalle en el material suplementario del repositorio público, `papers/proyecto_correlacion/`).

### 3.2 Grupos taxonómicos

Los pares se concentran en las familias mejor representadas fotográficamente (esparidos, blénidos, góbidos,
lábridos, algas coralinas, ascidias, holoturias, actinias, troquidos, dictyotáceas, facelínidos, serpúlidos,
sabelidos e ircínidos). El **98 % de los pares son inter-familia**, esperable en asociaciones de hábitat o
tróficas.

### 3.3 Candidatas nuevas (pendientes de revisión experta)

| grupo funcional | A — B | n | lift | localidades | días |
|---|---:|---:|---:|---:|---:|
| comensalismo en medusas | *Blackfordia virginica* — *Phronima sedentaria* | 19 | 653 | 6 | 15 |
| simbiosis de limpieza | *Lysmata grabhami* — *Telmatactis cricoides* | 9 | 547 | 7 | 8 |
| infauna (mismo sedimento) | *Fustiaria rubescens* — *Loripinus fragilis* | 16 | 892 | 7 | 15 |
| infauna | *Abra alba* — *Abra longicallus* | 9 | 534 | 7 | 9 |
| microhábitat de sustrato duro | *Macrorhynchia philippina* — *Telmatactis cricoides* | 8 | 765 | 5 | 6 |
| plancton gelatinoso | *Callianira bialata* — *Vanadis formosa* | 9 | 645 | 7 | 9 |

*(Tabla completa: material suplementario; figura principal: red top-12.)*

### 3.4 Verificación bibliográfica de las candidatas

Tras revisar la literatura pública (WoRMS, Sea Slug Forum, FishBase, JNCC/MarLIN, revistas revisadas por
pares) los pares se clasifican en tres categorías:

**Documentadas** (la interacción ya está descrita en la literatura): *Peltodoris atromaculata*—*Petrosia
ficiformis* (predación), *Felimare picta*—*Ircinia* spp. (dieta), *Cratena peregrina*—*Eudendrium
racemosum* (kleptopredación), la **comunidad del *Sargassum*** flotante (*Latreutes fucorum*,
*Hippolyte coerulescens* y *Scyllaea pelagica*), *Phronima sedentaria* como simbionte de salpas y
*Lampea pancerina* como depredador/parásito de salpas.

**Plausibles** (coherentes ecológicamente, sin cita directa de la pareja): *Lysmata grabhami*—
*Telmatactis cricoides* (la anémona hospeda crustáceos simbiontes documentados, *Thor amboinensis* en el
65 % de las anémonas y *Stenorhynchus lanceolatus* en mutualismo facultativo; ambas especies co-ocurren
realmente en Canarias/Madeira), los pares de plancton gelatinoso (ctenóforos, hiperídeos y medusas de la
misma masa de agua) y los pares de infauna de sedimento (*Abra* spp., *Fustiaria*—*Loripinus*, ambos
habitantes típicos de sedimentos blandos circalitorales).

**Artefacto por viaje de buceo** (especies de otros océanos que un mismo grupo fotografía en la misma
inmersión): *Doris fontainii*—*Tyrinna delicata* (ambas del **Pacífico sur**, lat −12…−55),
*Chromodoris quadricolor*—*Hexabranchus sanguineus* (Mar Rojo/Indo-Pacífico), *Abudefduf saxatilis*—
*Kyphosus vaigiensis* (Atlántico vs. Indo-Pacífico; no coexisten en el Mediterráneo). Estos pares quedan
**excluidos** del análisis ecológico del área de estudio; su detección es además una señal útil de control de
calidad del *dataset*.

**Corrección taxonómica**: `loripinus_fragilis` (Philippi, 1836, **Lucinidae**) y `limaria_fragilis`
(Gmelin, 1791, **Limidae**) son especies distintas; no son sinónimos (WoRMS AphiaID 718970 vs. 216644).

### 3.5 Referencias bibliográficas de las asociaciones

Las fuentes que sustentan la clasificación anterior, verificadas durante la revisión (28-sep-2026):

| Asociación / afirmación | Fuente |
|---|---|
| *Peltodoris atromaculata* se alimenta de la esponja *Petrosia ficiformis* | bibliografía trófica de doridáceos (revisión de dieta de nudibranquios; petroformynas como defensa química de la esponja) |
| *Felimare picta* (antes *Hypselodoris*) se alimenta de esponjas del género *Ircinia* | McDonald & Nybakken, 2001 — *A worldwide review of the food of nudibranch mollusks*; observaciones de campo (OPK) |
| *Cratena peregrina* practica kleptopredación sobre *Eudendrium racemosum* | Di Camillo et al. — *Eudendrium racemosum* como sustrato/presa y robos de presas (CNR, mar Adriático) |
| *Scyllaea pelagica*, *Latreutes fucorum* y *Hippolyte coerulescens* forman parte de la fauna asociada al *Sargassum* flotante | literatura de la comunidad pelágica del Sargassum (NOAA; BAMZ; Sea Slug Forum) |
| *Phronima sedentaria* es simbionte obligado de salpas (vive en el «barril») | Laval, 1978 — *The barrel of the pelagic amphipod Phronima sedentaria*; Diebel, 1988 — *Observations on the anatomy and behavior of Phronima sedentaria*; MBARI/Scripps |
| *Lampea pancerina* depreda o parasita salpas | *The double life of the ctenophore Lampea pancerina* (ResearchGate); literatura de ctenóforos (Carré & Carré) |
| Los hiperídeos (*Brachyscelus*, *Phronima*) se asocian a zooplancton gelatinoso (medusas, ctenóforos, salpas) | Keil & Osborn — *Associations between hyperiid amphipods and gelatinous zooplankton* (Smithsonian/MBARI, ROV) |
| *Telmatactis cricoides* hospeda crustáceos simbiontes (*Thor amboinensis* en el 65 % de las anémonas; *Stenorhynchus lanceolatus* en mutualismo facultativo) | *Crustacean symbionts of the sea anemone Telmatactis* (decapoda.nhm.org); Peraza et al., 2024 — *Exploring the association between Stenorhynchus lanceolatus and Telmatactis cricoides in the Canary Islands* (Regional Studies in Marine Science) |
| *Telmatactis cricoides* es especie termófila en expansión en el Mediterráneo occidental (Almería, Baleares) | Cambridge, J. Mar. Biol. Assoc. UK 104 (2024) — *The thermophilic sea anemone Telmatactis cricoides in the western Mediterranean* |
| *Macrorhynchia philippina* es hidrozoo invasor («stinging bush hydroid») | Riera et al., 2016 — *Progressing the invasion of the hydrozoan Macrorhynchia philippina in Atlantic archipelagos* (Vieraea 44) |
| Comunidades de sedimentos blandos con *Abra alba* y bivalvos del mismo género | JNCC Marine Habitat Classification (biotopo SS.SSa.CMuSa.AalbNuc); MarLIN |
| *Loripinus fragilis* (Lucinidae, quimiosimbiosis) ≠ *Limaria fragilis* (Limidae) | WoRMS AphiaID 718970 vs. 216644; Taylor & Glover, 2021 — *Biology, evolution and generic review of the Lucinidae* |
| *Abudefduf saxatilis* es estrictamente atlántico (sustituido por *A. vaigiensis* en el Indo-Pacífico) | FishBase — *Abudefduf saxatilis* (Sergeant-major) |
| *Doris fontainii* (antes *Anisodoris fontainei*) y *Tyrinna delicata* son del Pacífico sur | Sea Slug Forum (Australian Museum); Valdés & Muniain, 2002 |
| *Eurythoe complanata* es complejo de ≥3 especies crípticas | Barroso et al., 2010 — *Eurythoe complanata, the 'cosmopolitan' fireworm, consists of at least three cryptic species* (Marine Biology) |

### 3.6 Las asociaciones tróficas de los nudibranquios (29-sep-2026)

Los nudibranquios son un grupo ideal para validar el método: su dieta es **especialista y bien documentada**
(cada especie come una o pocas presas coloniales —esponjas, hidrozoos, briozoos, ascidias, algas—; Wägele &
Klussmann-Kolb, 2005; McDonald & Nybakken, 2001; Sea Slug Forum). De los **70.971 pares** robustos, **9.539
(13,4 %) implican al menos un nudibranquio**, y **1.048** son pares *nudibranquio→posible presa/sustrato* con
**≥5 observadores distintos** (esponjas, hidrozoos, briozoos, ascidias y algas del catálogo). El método
**recupera las dietas publicadas** como las asociaciones más fuertes:

| Nudibranquio (familia) | Presa/sustrato co-ocurrente | n | obs. | lift | celdas | fuente bibliográfica |
|---|---|---|---:|---:|---:|---:|---|
| *Doto floridicola* (Dotidae) | *Aglaophenia elongata* (hidrozoo) | 9 | 5 | 59,1 | 7 | ✅ documentado: *Doto* spp. se alimentan de hidrozoos *Aglaophenia* (Picton, Sea Slug Forum) |
| *Felimare orsinii* (Chromodorididae) | *Scalarispongia scalaris* (esponja) | 12 | 5 | 65,3 | 10 | ✅ documentado: «se alimenta principalmente de la esponja *Scalarispongia scalaris*» (Sea Slug Forum; SEASLUG.WORLD) |
| *Trinchesia caerulea* (Trinchesiidae) | *Sertularella crassicaulis* (hidrozoo) | 19 | 6 | 83,4 | 15 | ✅ coherente: los aeólidos comen hidrozoos sertuláridos |
| *Trinchesia caerulea* | *Turbicellepora avicularis* (briozoo) | 17 | 5 | 44,6 | 14 | coherente (briozoos como sustrato/presa secundaria) |
| *Aeolidiella alderi* (Aeolidiidae) | *Tedania anhelans* (esponja) | 14 | 6 | 74,2 | 6 | coherente (aeólidos sobre esponjas/hidrozoos) |
| *Dendrodoris limbata* (Dendrodorididae) | *Aplidium turbinatum* (ascidia) | 23 | 9 | 62,6 | 8 | coherente (doridáceos sobre ascidias coloniales) |
| *Siphonaria pectinata* (Siphonariidae) | *Bifurcaria bifurcata* (alga parda) | 26 | 14 | 61,1 | 16 | ✅ coherente: las *Siphonaria* son lapas pulmonadas herbívoras |
| *Taringa armata* (Discodorididae) | *Aplysilla sulfurea* (esponja) | 12 | 4 | 89,4 | 4 | coherente (doridáceos esponjófagos) |
| *Haminoea navicula* (Haminoeidae) | *Aplidium turbinatum* (ascidia) | 14 | 6 | 186,2 | 3 | coherente (cephalaspideos en sustrato duro) |

La concordancia entre la co-ocurrencia medida y las dietas publicadas es **la validación externa más fuerte
del método**: no solo recupera pares documentados de la literatura clásica, sino que **ordena por lift**
primero los casos con dieta conocida (*Doto*→*Aglaophenia*, *Felimare orsinii*→*Scalarispongia*). El resto de
la lista (1.039 candidatas) constituye hipótesis testables de dieta/sustrato para nudibranquios mediterráneos
poco estudiados. El listado completo de las 1.048 candidatas (con soporte, celdas y observadores) se
incluye en el material suplementario.

### 3.7 Relaciones adicionales fuera de los nudibranquios (29-sep-2026)

El mismo análisis aplicado a **todo el catálogo** (no solo nudibranquios) con filtro anti-«hub» (se excluyen
las 39 especies que co-ocurren con >400 taxones, que solo aportan ruido de fondo) produce **11.509 pares
específicos mediterráneos** con ≥5 observadores. Destacan tres grupos de relaciones con valor ecológico y de
conservación:

**a) Co-ocurrencia de invasores lessepsianos** (especies del mar Rojo que entraron por el canal de Suez):

| A | B | n | obs. | lift | contexto |
|---|---:|---:|---:|---:|---|
| *Fistularia commersonii* (pez flauta) | *Pterois miles* (pez león) | 25 | 16 | 261,7 | ambos invasores documentados; *Fistularia* es uno de los pocos depredadores naturales de *Pterois* |
| *Fistularia commersonii* | *Siganus rivulatus* (pez conejo) | 15 | 13 | 123,9 | invasores coexistentes en el Levante |
| *Pterois miles* | *Taeniura lymma* (raya de manchas azules) | 11 | 7 | 233,2 | invasores del mar Rojo |

La co-ocurrencia de invasores lessepsianos es **consistente con la literatura** (Kondylatos et al., 2023:
*Fistularia, Pterois miles y Siganus* capturados juntos en Rodas; CIESM Atlas of Exotic Fishes). Implicación
de conservación: las fotos de ciencia ciudadana permiten **monitorear la expansión conjunta** de estas
especies invasoras. **Salvedad (nulo estratificado, §4.3):** estos tres pares no superan el nulo de esfuerzo local (p<sub>emp</sub>=0,52–0,76); su lift alto
se debe a que las especies son raras y coinciden en pocos enclaves y días de la invasión.

**b) Plancton gelatinoso** (ctenóforos, sifonóforos y sus depredadores/comensales):

| A | B | n | obs. | lift |
|---|---:|---:|---:|---:|
| *Forskalia edwardsii* (sifonóforo) | *Lampea pancerina* (ctenóforo) | 8 | 5 | 209,9 |
| *Cestum veneris* (ctenóforo cinturón de Venus) | *Hippopodius hippopus* (sifonóforo) | 18 | 7 | 102,6 |
| *Callianira bialata* (ctenóforo) | *Cestum veneris* | 16 | 5 | 97,7 |
| *Callianira bialata* | *Forskalia edwardsii* | 14 | 5 | 177,1 |

Los ctenóforos depredan salpas y zooplancton gelatinoso (Carré & Carré); su co-ocurrencia con sifonóforos
en la misma masa de agua es coherente con un **gremio depredador planctónico compartido** (Current Biology,
2025).

**c) Invertebrados bentónicos** (asociaciones de hábitat con sentido biológico):

| A | B | n | obs. | lift |
|---|---:|---:|---:|---:|
| *Astroides calycularis* (coral naranja) | *Clavelina dellavallei* (ascidia) | 16 | 8 | 135,6 |
| *Aeolidiella alderi* (nudibranquio) | *Berthella perforata* (pleurobranco) | 41 | 8 | 129,8 |
| *Petalifera petalifera* (liebre de mar) | *Placida tardyi* (sacogloso) | 22 | 5 | 110,7 |
| *Codium coralloides* (alga verde) | *Placida verticilata* (sacogloso) | 18 | 5 | 101,0 |
| *Oestergrenia digitata* (pepino de mar) | *Virgularia mirabilis* (pluma de mar) | 8 | 5 | 212,9 |

El par *Codium coralloides*—*Placida verticilata* es especialmente notable: los **sacoglosos se alimentan
de algas verdes del género *Codium*** (quedándose con sus cloroplastos; Wägele & Klussmann-Kolb, 2005) —
relación trófica documentada que el método recupera sin conocimiento previo.
**Salvedad (análisis de sensibilidad al observador, 29-sep-2026):** un único observador aparece en el 72 % de los 18 eventos de
este par y solo 5 sobreviven al retirarlo; el resultado es coherente con la biología, pero debe leerse como *hipótesis pendiente de
replicación* y no como validación independiente del método. Lo mismo vale para *Forskalia edwardsii*—*Lampea pancerina* (71 %; 2 eventos
restantes). Los pares lessepsianos (*Fistularia*, *Pterois*, *Siganus*, *Taeniura*) no dependen de un observador (≥8 observadores, dominante ≤33 %).

### 3.8 Rigor de la evaluación: ablación, long-tail y leakage (29-sep-2026)

Para responder a los estándares de revisión por pares se añadieron tres análisis:

**a) Benchmark de ablación** (sobre la misma muestra aleatoria de 300 fotos del eval):

| Modelo | Top-1 | Top-5 |
|---|---:|---:|
| k-NN simple (BioCLIP-2.5 ViT-H puro, coseno al prototipo) | 69,0 % | 91,0 % |
| **BioFauna producción** (agregador temperado + tope por especie + Cubo B + subespacio local + zero-shot + abstención) | **77,7 %** | 90,0 % |
| iNaturalist Computer Vision (API pública, solo imagen, sin ubicación; 285 de las 300 fotos disponibles) | 53,7 % | 70,2 % |
| Ganancia de los mecanismos de decisión | **+8,7 pp** | −1,0 pp |

*Nota:* iNaturalist CV no cubre todas las especies del catálogo (su vocabulario es más limitado en invertebrados marinos poco fotografiados), por lo que la cifra mide también esa cobertura; BioFauna se evaluó con su configuración de producción (incluye prior geográfico cuando hay coordenadas), iNaturalist solo con la imagen. Muestra pequeña (n≈300): las diferencias entre kNN puro y producción deben leerse con IC amplios.

**b) Métricas de long-tail** (eval purgado, 76.585 filas): Micro-accuracy **82,34 %** vs Macro-accuracy
**75,71 %** (2.946 especies); por frecuencia de clase, las especies **raras (<10 filas) aciertan 53,5 %**
frente al 85,8 % de las comunes — sesgo de frecuencia esperable en identificadores de biodiversidad. Top-5
93,7 % · género 87,1 % · familia 90,5 %.

**c) Aislamiento de leakage**: el 2,17 % de las filas del eval compartía observación u observador con la
galería de su especie; excluirlas cambia el resultado solo **−0,14 pp** (82,5 % → 82,34 %), lo que confirma
que la cifra operativa no está inflada de forma material.

**d) Composición del conjunto de evaluación**: la cifra de 82,34 % agrupa tres bloques: el eval original (60.743 filas, **81,18 %**, comparable con
versiones anteriores) y dos ampliaciones por minado dirigido hasta 30 fotos por especie (11.154 filas, 85,5 %; 4.688 filas, 89,9 %). A igualdad de especie
(1.785 especies con filas de ambos tipos) la precisión es equivalente (86,8 % en filas minadas frente a 86,1 % en las originales), de modo que el aumento global
procede de la composición por especies (solo las especies con reserva de fotos ampliaron) y **no de una mejora del modelo**, que no cambió. Todas las filas
minadas pasaron el mismo filtro de fuga (observación, observador y similitud de embedding ≥ 0,98 con la galería).

## 4. Discusión

### 4.1 Marco teórico: co-ocurrencia y sesgos de la ciencia ciudadana

La co-ocurrencia de especies es una señal ecológica clásica (hábitat compartido, depredación, simbiosis,
comensalismo), pero su lectura en datos de ciencia ciudadana exige controlar sesgos bien documentados:
**sesgo geográfico** (las zonas accesibles se muestrean más), **de esfuerzo** (los eventos tipo *bioblitz*
inflacionan ciertas localidades), **de observador** (varía la habilidad de detectar e identificar) y **de
reporte** (preferencia por especies carismáticas). Los datos oportunistas carecen de plan de muestreo y de
ausencias explícitas, por lo que cualquier inferencia debe mitigar explícitamente estos sesgos
(Isaac et al., 2014; Johnston et al., 2018; Aceves-Bueno et al., 2017; Boyd et al., 2021; Milanesi et al.,
2020). Nuestro diseño responde con: (1) *evento* = unidad de esfuerzo por observador y franja de 3 h
(controla el sesgo de esfuerzo), (2) repetibilidad exigida en ≥3 localidades, ≥3 días y **≥5 observadores**
(controla el sesgo de observador y de salida), y (3) el **filtro por rango geográfico** de las especies
(elimina el artefacto de viajes de buceo detectado en esta revisión). El sesgo geográfico se aborda con el
nulo estratificado por localidad·fecha en curso (§6 de Métodos).

Las candidatas se agrupan en tres clases de interpretación: **comensalismo/foresia** (medusa—anfípodo),
**simbiosis de limpieza** (gamba—anémona) y **co-habitación de sustrato** (fauna infaunal, fondo duro, algas coralinas). El reto metodológico central es distinguir **interacción** de
**coincidencia** por hábitat, estación o esfuerzo de observación; de ahí la exigencia de repetibilidad
espacial y temporal y el nulo estratificado en curso.

La revisión bibliográfica aporta dos resultados de interés general. Primero, **el método recupera
asociaciones ya documentadas** (predación en doridáceos, comunidad del *Sargassum*, simbiontes de
gelatinosos), lo que valida la señal ecológica frente al ruido de esfuerzo. Segundo, la clasificación de los
pares *top* por distribución geográfica de las especies revela un **artefacto sistemático de la ciencia
ciudadana**: los pares de mayor lift con especies extra-mediterráneas (*Doris fontainii*—*Tyrinna delicata*,
*Chromodoris quadricolor*—*Hexabranchus sanguineus*) corresponden a **viajes de buceo** de un mismo grupo y no
a interacciones ecológicas del área de estudio. El cruce con el rango geográfico de cada taxón es, por tanto,
un filtro de calidad necesario antes de interpretar cualquier candidata como asociación ecológica.

### 4.2 Hipótesis biológicas contrastadas (el mayor aporte científico)

Las candidatas robustas se confrontan aquí con la literatura biológica marina previa. Cada caso se clasifica
como **documentado** (la interacción ya está descrita), **plausible** (coherente ecológicamente, sin cita
directa de la pareja) o **artefacto** (sesgo de muestreo, descartado).

**(a) *Peltodoris atromaculata* — *Petrosia ficiformis* (predación).** Documentado. El doridáceo se alimenta
exclusivamente de esa esponja, acumula sus petroformynas y vive sobre ella; el método lo recupera con 79
eventos, 44 localidades y 74 días (lift 11,1). *Doto floridicola*—*Aglaophenia* y *Felimare orsinii*—
*Scalarispongia scalaris* confirman el patrón general: **los doridáceos y dotidos se co-ocurren con su
esponja/hidrozoo presa** (Sea Slug Forum; McDonald & Nybakken, 2001).

**(b) *Cratena peregrina* — *Eudendrium racemosum* (kleptopredación).** Documentado (CNR, mar Adriático): el
aeólido roba presas al hidrozoo. Nuestro par (n=5, 5 observadores) es consistente con la literatura.

**(c) Comunidad del *Sargassum* flotante (*Scyllaea pelagica*, *Latreutes fucorum*, *Hippolyte
coerulescens*).** Documentado: las tres especies son fauna asociada al alga flotante *Sargassum* (NOAA;
BAMZ). El método las agrupa con 10-11 observadores distintos y lift >300, sin necesidad de conocer la
relación a priori.

**(d) *Lysmata grabhami* — *Telmatactis cricoides* (limpieza/simbiosis).** Plausible. La anémona *T.
cricoides* hospeda crustáceos simbiontes documentados (*Thor amboinensis* en el 65 % de las anémonas;
*Stenorhynchus lanceolatus* en mutualismo facultativo — Peraza et al., 2024); las *Lysmata* son gambas
limpiadoras. Co-ocurren real en Canarias/Madeira (lat 27-29). Requiere validación in situ.

**(e) *Blackfordia virginica* — *Phronima sedentaria* / *Brachyscelus crusculum* (comensalismo en
gelatinosos).** Plausible. Los hiperídeos se asocian a medusas y salpas (Keil & Osborn; *Phronima* es
simbionte obligado de salpas — Laval, 1978). No hay cita específica *Blackfordia*-hiperídeo; hipótesis
testable.

**(f) Pares de infauna (*Fustiaria rubescens*—*Loripinus fragilis*; *Abra alba*—*Abra longicallus*).**
Plausible. Co-habitación de sedimentos blandos circalitorales (biotopo JNCC «Abra alba & Nucula nitidosa»;
*Loripinus* vive en sedimentos reducidos con simbiontes quimiosintéticos).

**Descartadas por artefacto**: los pares de mayor lift con especies extra-mediterráneas (*Doris fontainii*—
*Tyrinna delicata*, Pacífico sur; *Chromodoris quadricolor*—*Hexabranchus sanguineus*, Mar Rojo) son fotos de
viajes de buceo del mismo grupo, no asociaciones del área de estudio; su detección es además señal de control
de calidad del *dataset*.

**Implicación**: cinco hipótesis (d, e, f y sus variantes) requieren **validación in situ** por biólogos —
inmersiones dirigidas, cámaras fijas o revisión de fotografías de parejas. Esa es la línea de trabajo que
convierte el resultado en aporte científico citable.

### 4.3 Control del esfuerzo local: nulo estratificado por localidad·fecha (29-30-sep-2026)

Para responder a la crítica de que el lift puede reflejar **esfuerzo de muestreo local** (una localidad o un
día con muchas observaciones) en lugar de co-ocurrencia biológica, se implementó un **nulo por permutación
estratificada**: se conservan los eventos (localidad ~0,1°, día, tamaño) y se barajan las especies dentro de
cada bloque localidad·día. Se ejecutó con **dos definiciones de evento**, 2.000 permutaciones y los 3.000 pares de mayor lift:
(i) *gruesa* (celda 0,1° · día · franja 3 h, sin observador; 58.283 eventos, 47.302 bloques) y (ii) *del análisis principal*
(observador × ~1 km × día × 3 h; 60.650 eventos, 40.982 bloques).

Resultado: con la definición gruesa **387 de 3.000 pares (12,9 %) tienen p<sub>emp</sub><0,05 y ninguno supera el FDR** de Benjamini-Hochberg
(q≤0,05); con la definición del análisis principal **1.017 (33,9 %) tienen p<sub>emp</sub><0,05 y 214 superan el FDR**. Dos salvedades de lectura:
(a) con 2.000 permutaciones el p mínimo es 0,0005; en la definición gruesa solo 13 pares llegan a ese suelo, de modo que el mejor q alcanzable
(0,115) queda por encima de 0,05 y **la ausencia de pares con FDR en esa definición no es concluyente en la cola** (una primera ejecución con
200 permutaciones tenía un suelo aún mayor y no podía haber dado ningún resultado significativo); (b) varios de los pares que superan el FDR con
la definición principal son de especies indo-pacíficas fotografiadas en viajes de buceo (p. ej. *Cephalopholis miniata*—*Pseudanthias
squamipinnis*), es decir, co-ocurrencia de **expedición**, no mediterránea; el filtro de especies mediterráneas (§3.7) debe aplicarse antes de
interpretarlos.

**Consecuencias para los pares de las secciones anteriores.** *Branchellion torpedinis*—*Torpedo marmorata* (parasitismo documentado) es el más
sólido: p<sub>emp</sub>=0,0005 con ambas definiciones (q=0,021 con la principal, 0,115 con la gruesa). *Cestum veneris*—*Hippopodius hippopus*:
p=0,0215 (gruesa) y 0,0005 con q=0,021 (principal). *Codium coralloides*—*Placida verticilata*: p=0,029 (gruesa) y 0,014 (principal; q=0,089, no
supera el FDR). **Los pares lessepsianos (*Fistularia commersonii*—*Pterois miles*, *Fistularia*—*Siganus rivulatus*, *Pterois miles*—*Taeniura
lymma*) NO son más frecuentes de lo que predice el esfuerzo local** (p<sub>emp</sub>=0,52–0,76 con ambas definiciones): su lift alto refleja que
ambas especies son raras y coinciden en los mismos pocos enclaves y días de la invasión, no una asociación específica. Siguen siendo útiles como
señal de que las invasoras aparecen en los mismos lugares (monitoreo), pero **no** como evidencia de interacción o de co-ocurrencia
estadísticamente excepcional.

1. **El lift premia pares raros**: los pares *documentados* de la literatura (*Peltodoris*—*Petrosia*,
   *Doto*—*Aglaophenia*) tienen co-ocurrencia abundante pero no "rara", y ni siquiera entran en el top 3.000
   por lift. **El lift no es la métrica adecuada para validar asociaciones comunes**; para ellas la señal es
   su abundancia y repetibilidad (n, celdas, días, observadores), no el lift.
2. **Los pares con p<sub>emp</sub><0,05 y n alto son candidatas** con sentido biológico (*Corallium rubrum*—*Paramuricea clavata*, p=0,04 en la
   ejecución inicial de 500 permutaciones, no repetida con 2.000).

**Posición metodológica**: los pares con hipótesis a priori (tróficos y documentados) se validan con su
**p individual** (pocas hipótesis concretas, práctica estándar); los descubrimientos exploratorios se
reportan como candidatas con p<sub>emp</sub><0,05 y **advertencia explícita** de que su significación depende de la definición
de evento y (con la definición gruesa) no supera el FDR global; requieren validación independiente. Detalle: `experimentos/NULO_ESTRATIFICADO_20260929.md`.

## 5. Limitaciones

1. Co-ocurrencia ≠ interacción; se mitiga con filtros y nulo, pero la confirmación última es la observación
   dirigida.
2. Sesgo de esfuerzo y de observador (eventos tipo *bioblitz*).
3. Cobertura desigual entre grupos taxonómicos.

## 6. Conclusiones

Este trabajo demuestra que las fotografías de ciencia ciudadana, identificadas automáticamente a escala de
catálogo, contienen **asociaciones ecológicas recuperables y verificables**. Las conclusiones principales:

1. **El método valida la señal ecológica**: recupera asociaciones documentadas de la literatura clásica con
   alta robustez — *Peltodoris atromaculata* sobre *Petrosia ficiformis* (79 eventos, lift 11,1), la
   kleptopredación de *Cratena peregrina* sobre *Eudendrium racemosum*, las dietas de doridáceos sobre
   esponjas y la comunidad del *Sargassum* flotante — y lo hace **sin conocimiento previo de las dietas**.

2. **Descubre relaciones nuevas con datos estadísticos**: 1.048 pares tróficos de nudibranquios (≥5
   observadores) y 11.509 pares específicos mediterráneos en todo el catálogo, entre los que destacan:
   - **Invasores lessepsianos co-ocurrentes** (*Fistularia commersonii*, *Pterois miles*, *Siganus rivulatus*,
     *Taeniura lymma*) con lifts de 124-262 — su co-ocurrencia coincide con lo que predice el esfuerzo
     local (§4.3), por lo que es una señal de **coincidencia espacial de la invasión** útil para el monitoreo, no una asociación estadísticamente
     excepcional.
   - **Gremio depredador planctónico** (ctenóforos y sifonóforos en la misma masa de agua: *Cestum veneris* +
     *Hippopodius hippopus*, lift 103).
   - **Relaciones tróficas bentónicas** no descritas (*Codium* — sacoglosos, *Astroides* — ascidias).

3. **La co-ocurrencia no es un artefacto del identificador**: los pares documentados muestran confusión
   cruzada nula (0-1 casos), frente a los pares de especies crípticas (control) con 13-26 % de confusión que
   no aparecen como candidatas.

4. **Aplicaciones directas**: (a) priorizar la búsqueda de especies raras donde aparece su asociada;
   (b) generar hipótesis testables de dieta y hábitat para validación in situ por biólogos; (c) vigilar la
   expansión de especies invasoras; y (d) alimentar herramientas de divulgación y ciencia ciudadana con
   sugerencias «si ves X, busca Y» y redes de asociación por zona.

La combinación de identificación automática, co-ocurrencia a escala de catálogo y **contraste con la
literatura biológica** convierte un archivo fotográfico participativo en una fuente de hipótesis ecológicas
citables, con el valor añadido de cubrir aguas someras y costeras donde otros métodos rinden peor.

## Agradecimientos

A la comunidad observadora y, muy especialmente, a las **personas curadoras** que sostienen la fiabilidad de
las identificaciones —en especial **Miquel Pontes**, **Xavier Salvador** y **Berta Companys**— y al conjunto de
la comunidad de curaduría de **Minka SDG** e **iNaturalist**. Mención especial a la **FECDAS** y a su
**Projecte Aneris** por impulsar la ciencia ciudadana marina y la formación de observadores; a **Minka SDG** e
**iNaturalist** por las plataformas y los datos; y a **GBIF**, **Wikimedia Commons**, **DORIS/FFESSM**,
**SeaSlugForum**, **WoRMS** y **FishBase** por las imágenes y los datos taxonómicos. Este análisis ha sido
posible gracias al **identificador BioFauna** (BioCLIP-2.5 ViT-H/14 + FAISS), creado y desarrollado por
**Gustavo Zafra** (autor de este manuscrito), con la colaboración del autor en la plataforma Minka SDG.

**Agradecimiento a los modelos de inteligencia artificial (2026).** Este trabajo se ha beneficiado del
acompañamiento de los principales asistentes de IA disponibles en 2026, que participaron en el desarrollo del
identificador, el diseño experimental, el análisis de co-ocurrencia, la revisión de la literatura biológica y
la redacción del manuscrito: **Claude (Anthropic)**, **Grok (xAI)**, **Gemini (Google)**, **DeepSeek** y
otros modelos de lenguaje y visión de la época. Su contribución fue la de herramientas de asistencia a la
investigación bajo la supervisión y dirección del autor.

## Referencias

- Aceves-Bueno, E., Adeleye, A. S., Feraud, M., Huang, Y., Tao, M., Yang, Y., & Anderson, S. E. (2017). The
  accuracy of citizen science data: a quantitative review. *The Bulletin of the Ecological Society of
  America*, 98(4), 278–290.
- Avila, C. (1996). The growth of *Peltodoris atromaculata* Bergh, 1880 (Gastropoda, Nudibranchia) in the
  laboratory. *Journal of Molluscan Studies*, 62, 151–157. — dieta exclusiva sobre *Petrosia ficiformis*;
  acumulación de petroformynas.
- Barroso, R., Klautau, M., Solé-Cava, A. M., & Paiva, P. C. (2010). *Eurythoe complanata* (Polychaeta:
  Amphinomidae), the 'cosmopolitan' fireworm, consists of at least three cryptic species. *Marine Biology*,
  157(1), 69–80.
- Boyd, R. J., Powers, M., & Pescott, O. L. (2021). occAssess: an R package for assessing potential biases in
  species occurrence data. *Ecology and Evolution*, 11(22).
- Diebel, C. E. (1988). Observations on the anatomy and behavior of *Phronima sedentaria* (Forskål)
  (Amphipoda: Hyperiidea). *Journal of Crustacean Biology*, 8(1), 79–90.
- Isaac, N. J. B., van Strien, A. J., August, T. A., de Zeeuw, M. P., & Roy, D. B. (2014). Statistics for
  citizen science: extracting signals of change from noisy ecological data. *Methods in Ecology and
  Evolution*, 5(10), 1052–1060.
- Johnston, A., Fink, D., Hochachka, W. M., & Kelling, S. (2018). Estimates of observer expertise improve
  species distributions from citizen science data. *Methods in Ecology and Evolution*, 9(4), 880–890.
- Keil, K. E., & Osborn, K. J. Associations between hyperiid amphipods and gelatinous zooplankton
  (Smithsonian Institution, NMNH; MBARI ROV footage).
- Laval, P. (1978). The barrel of the pelagic amphipod *Phronima sedentaria* (Forsk.). *Journal of
  Experimental Marine Biology and Ecology*, 33(3), 187–211.
- McDonald, G. R., & Nybakken, J. W. (2001). A worldwide review of the food of nudibranch mollusks. II. The
  suborder Doridacea. *The Veliger*.
- Milanesi, P., Mori, E., & Menchetti, M. (2020). Observer-oriented approach improves species distribution
  models from citizen science data. *Ecology and Evolution*, 10(21), 12104–12114.
- Peraza, E., Pérez, J. A., Abdul-Jalbar, B., Chinea, J., & Clemente, S. (2024). Exploring the association
  between the arrow crab *Stenorhynchus lanceolatus* and the sea anemone *Telmatactis cricoides* in the
  Canary Islands. *Regional Studies in Marine Science*.
- Riera, R., Espina, F., & Moro, L. (2016). Progressing the invasion of the hydrozoan *Macrorhynchia
  philippina* (Kirchenpauer, 1872) in Atlantic archipelagos. *Vieraea*, 44, 117–120.
- Taylor, J., & Glover, E. (2021). *Biology, evolution and generic review of the chemosymbiotic bivalve
  family Lucinidae*. The Ray Society, London.
- Valdés, Á., & Muniain, C. (2002). Revision and taxonomic reassessment of Magellanic species assigned to
  *Anisodoris* Bergh, 1898 (Nudibranchia: Doridoidea). *Journal of Molluscan Studies*, 68, 345–351.

## Disponibilidad de datos (Data Availability)

Los datos y el código se publican en el repositorio público del proyecto
(https://github.com/yespi/biofauna):

- **Identificador BioFauna**: código completo (servicio, prototipos, calibradores, prior geográfico, pares
  crípticos, scripts de evaluación y auditoría de fugas) y taxon IDs — `papers/biofauna/`.
- **Tabla de asociaciones anonimizada** (sin fotografías ni datos de observadores): `data/
  asociaciones_mediterraneas_20260929.csv` (11.509 pares con especies, familias, nº de eventos, celdas,
  días, observadores y lift) y `data/asociaciones_top40_20260929.csv`.
- **Manuscritos y láminas**: `papers/proyecto_correlacion/` (artículo ES/EN y PDFs).
- **No redistribuibles**: las fotografías (sujetas a licencias de Minka SDG, iNaturalist y demás fuentes) y
  los `embeddings.npy` por foto; pueden reconstruirse desde Minka/iNaturalist/GBIF usando el catálogo.

## Material suplementario

- Tablas de asociaciones (top 40 y conjunto completo; accesibles en el repositorio público del proyecto).
- Figura de red de asociaciones (SVG navegable en el repositorio).
- **Láminas fotográficas** (`LAMINAS_v4_20260929.pdf`, 22 páginas): **22 fotografías** seleccionadas de la
  **galería BioFauna** (1,2 M imágenes) con el **clasificador de calidad del sistema** (`obs_score`:
  grado de investigación, nº de curadores, curador de confianza y resolución; 0-13) y filtro de nitidez
  (varianza Laplaciano). Cada foto incluye su **atribución** (autor + licencia + enlace a la observación).
  Solo imágenes con licencia reutilizable (CC0 / CC BY / CC BY-SA); el resto se excluye o requiere permiso
  explícito del autor.
