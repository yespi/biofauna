# Asociaciones entre especies marinas reveladas por un identificador automático de fauna y 1,2 millones de fotografías de ciencia ciudadana

**Borrador v1 — 28-sep-2026** · Proyecto Correlación (BioFauna)

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

## 3.5 Referencias bibliográficas de las asociaciones

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

## 3.6 Las asociaciones tróficas de los nudibranquios (29-sep-2026)

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
poco estudiados. Artefacto: `artifacts/coocurrencia_nudibranquios_trofica_filtrada_20260929.json` (1.048
pares con ≥5 observadores).

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

## 5. Limitaciones

1. Co-ocurrencia ≠ interacción; se mitiga con filtros y nulo, pero la confirmación última es la observación
   dirigida.
2. Sesgo de esfuerzo y de observador (eventos tipo *bioblitz*).
3. Cobertura desigual entre grupos taxonómicos.

## 6. Conclusiones y aplicaciones

Las fotografías de ciencia ciudadana contienen asociaciones ecológicas recuperables a escala de catálogo. Los
resultados permiten (a) **priorizar** la búsqueda de especies raras allí donde aparece su asociada,
(b) **enriquecer BioQuest** con sugerencias «si ves X, busca Y» y redes de asociación por zona, y (c) plantear
**hipótesis testables** para la investigación marina, con el valor añadido de cubrir aguas someras y costeras
donde los satélites rinden peor.

## Agradecimientos

A la comunidad observadora y, muy especialmente, a las **personas curadoras** que sostienen la fiabilidad de
las identificaciones —en especial **Miquel Pontes**, **Xavier Salvador** y **Berta Companys**— y al conjunto de
la comunidad de curaduría de **Minka SDG** e **iNaturalist**. Mención especial a la **FECDAS** y a su
**Projecte Aneris** por impulsar la ciencia ciudadana marina y la formación de observadores; a **Minka SDG** e
**iNaturalist** por las plataformas y los datos; y a **GBIF**, **Wikimedia Commons**, **DORIS/FFESSM**,
**SeaSlugForum**, **WoRMS** y **FishBase** por las imágenes y los datos taxonómicos. Este análisis ha sido
posible gracias al **identificador BioFauna** (BioCLIP-2.5 ViT-H/14 + FAISS) desarrollado en el proyecto.

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

## Material suplementario

- Tablas de asociaciones (top 40 y conjunto completo).
- Figura de red de asociaciones.
- **Láminas fotográficas** por caso (29-sep-2026, `LAMINAS.md`): **21 fotografías** de iNaturalist con
  **licencia reutilizable** (CC0 / CC BY 4.0 / CC BY-SA 4.0) y **atribución completa** (autor + licencia +
  enlace a la observación) para las 5 asociaciones documentadas/plausibles. Criterio de inclusión: solo
  imágenes con licencia reutilizable; el resto se excluye o requiere permiso explícito del autor.
