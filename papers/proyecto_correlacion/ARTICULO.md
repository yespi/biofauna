# Proximidad a escala de centímetros en la misma fotografía: un cribado de coexistencias con un identificador automático sobre 1,2 millones de fotografías de ciencia ciudadana marina

**Autor: Gustavo Zafra (gustavo.zafra@gmail.com)** · Creador y desarrollador de BioFauna (identificador BioCLIP-2.5 ViT-H/14 + FAISS) y de las aplicaciones FotoFauna y BioQuest; colaborador de la plataforma de ciencia ciudadana Minka SDG.

**Fecha:** 16-oct-2026. Manuscrito centrado en el criterio «ambas especies en la misma fotografía»; las series temporales esfuerzo-corregidas se publican aparte (véase `papers/especies_peligro_declives/` y `material/experimentos/AVANCE_cruzadas_20261011.md`).

---

## Resumen

Proponemos un criterio verificable de coexistencia a escala de centímetros: **ambas especies en la misma fotografía**. Partimos de **1,22 millones de fotografías** de ciencia ciudadana (Minka SDG, iNaturalist y otras fuentes), identificadas con **BioFauna** (índice **p19**, **3.061** taxones mediterráneos; **84,38 %** de acierto de especie en el panel oficial de evaluación fuera de muestra, octubre 2026). Un cribado por *eventos* (observador × celda ~1 km × día × franja de 3 h) solo **genera hipótesis** (115.204 parejas con soporte; 51.401 significativas con el esfuerzo controlado). De una lista corta de **138** parejas priorizadas, **41** tuvieron al menos una foto candidata del detector y **12** tres o más observaciones; la revisión a ojo mostró muchos falsos positivos entre especies parecidas. **Dos** parejas de la lista corta quedaron confirmadas con ambas especies visibles (*Condylactis aurantiaca*–*Periclimenes scriptus* y *Electra posidoniae*–*Tridentata perpusilla* en el Mediterráneo); el resto de láminas incluye controles positivos documentados o selecciones previas. El cribado por eventos no se enriquece frente a GloBI (Fisher *p* = 0,68 sin aves acuáticas). Frente a un *gold* de 51 parejas de literatura/GloBI, la precisión tipo Freilich es ≈0,2 % por eventos frente a ≈4,9 % en la misma foto (intervalos amplios). La proximidad en una imagen demuestra convivencia instantánea, **no interacción**; la segunda especie la propone el identificador sin confirmación de curadores.

**Palabras clave:** ciencia ciudadana, coexistencia, proximidad, aprendizaje profundo, Mediterráneo, fotografía submarina, co-ocurrencia.

## 1. Introducción

La fotografía submarina *amateur* es una fuente masiva de datos de biodiversidad. Las plataformas de ciencia ciudadana (**Minka SDG**, impulsada desde el ecosistema **FECDAS**; **iNaturalist**; **GBIF**) acumulan millones de observaciones, pero la mayoría de los análisis se limitan a inventarios y mapas de distribución. Inferir interacciones a partir de la co-ocurrencia en datos participativos tiene sesgos conocidos de esfuerzo y de observador (Isaac et al., 2014; Johnston et al., 2018; Milanesi et al., 2020; Boyd et al., 2021) y, de fondo, la co-ocurrencia espacial **no es evidencia de interacción ecológica** (Blanchet et al., 2020). En un sistema marino intermareal, redes construidas solo por co-ocurrencia recuperan mal las interacciones conocidas (sensibilidad 0,469; especificidad 0,527; Freilich et al., 2018). Los modelos probabilísticos de co-ocurrencia (Veech, 2013; Griffith et al., 2016) y los marcos jerárquicos de comunidad (Ovaskainen et al., 2017) formalizan el cribado por eventos, pero no sustituyen una verificación a escala de organismo. Proponemos un criterio más exigente y lo único que contamos como **evidencia visual de coexistencia**: la aparición de las dos especies en la misma fotografía, a escala de centímetros.

## 2. Material y métodos

### 2.1 Datos
1.222.170 fotografías de la galería BioFauna (Minka SDG 377.476; iNaturalist 779.411; GBIF, Wikimedia Commons, DORIS/FFESSM, SeaSlugForum, WoRMS, FishBase y otras) y 759.207 observaciones con coordenadas, fecha y (92 %) hora. Catálogo de **3.061** taxones mediterráneos embebidos en el índice **p19** (producción, 16-oct-2026). La galería incluye observaciones globales; las láminas del cuerpo ilustran el criterio con ejemplos mayoritariamente mediterráneos tras control biogeográfico (§3.3).

### 2.2 Identificador
BioFauna recupera, con k-NN sobre *embeddings* BioCLIP-2.5 ViT-H/14 con índice FAISS (k = 15, T = 0,05, máximo 3 votos por especie) y calibración jerárquica, la especie más probable de una imagen. En el panel oficial de evaluación rescore (congelado octubre 2026) el índice **p19** acierta el **84,38 %** de las especies (0,8438; **~1,29×10⁶** vectores / **3.061** spp); el acierto crece con las fotos de referencia de la especie (Figura 3). Esto condiciona el estudio: las especies con pocas fotos y las pequeñas o camufladas se reconocen peor, y la segunda especie en un recorte de cuadrante puede rondar peor que el retrato centrado usado para calibrar.

### 2.3 Cribado por eventos (solo generación de hipótesis)
Un *evento* es lo observado por el mismo observador en la misma celda de ~1 km, el mismo día y la misma franja de 3 h. Para cada pareja con ≥5 eventos en común se contrasta, con el esfuerzo local controlado (nulo condicionado al número y tamaño de eventos por bloque celda 0,1°·día, corrección de Benjamini-Hochberg sobre toda la familia), si co-ocurren más de lo esperado. **Este resultado no se interpreta como asociación**; solo ordena las parejas por tamaño de efecto y replicación (≥3 celdas, ≥3 días, ≥5 observadores) para elegir cuáles verificar. Detalle en el Suplemento.

### 2.4 Verificación por proximidad real (criterio principal)
Para cada pareja (A, B) de la lista corta se analizaron hasta 60 fotos de A y de B de la galería. Cada foto se divide en cinco vistas (entera y cuatro cuadrantes) y se calcula su *embedding*; se busca en el índice de producción (300 vecinos), excluyendo la observación consultada y las del mismo observador el mismo día cuando el identificador lo permite y una pareja tiene **foto candidata** si la otra especie aparece en alguna vista con similitud ≥ 0,82 (o como primera opción con ≥ 0,86). El detector solo propone: **cada candidata se revisa a ojo** y solo se acepta si ambas especies son visibles en la imagen. Las parejas de especies parecidas (mismo género o familia) producen falsos positivos y se descartan en la revisión.

### 2.5 Niveles de evidencia
**Nivel 0:** co-ocurrencia por evento (solo pista). **Nivel 1:** ambas especies en la misma foto en ≥3 observaciones independientes. **Nivel 2:** además, contacto visible (sobre, dentro, alimentándose). La ausencia de fotos conjuntas deja la pareja *sin confirmar*, no refutada: la galería son sobre todo retratos centrados de una especie.

### 2.6 Licencias y atribución
Se usan fotografías CC0, CC BY, CC BY-SA y CC BY-NC / CC BY-NC-SA; se excluyen las que no tienen licencia y las CC BY-NC-ND. Cada foto indica autor, licencia, fecha y hora local, lugar y enlace a la observación. Las marcadas con † (no comerciales) **deben sustituirse por fotos CC0, CC BY o CC BY-SA, o contar con permiso del autor, si el artículo se publica en una revista comercial**.

### 2.7 Modelo nulo Veech / `cooccur`
Se implementó en Python el modelo probabilístico de Veech (2013) tal como lo expone el paquete `cooccur` (Griffith et al., 2016): para cada par de especies, con *N* sitios, *N₁* y *N₂* ocupaciones y *j* co-ocurrencias observadas, se calculan P(*J*≥*j*) y P(*J*≤*j*) bajo la hipergeométrica, el esperado *N₁N₂/N* y el efecto *j*−esperado. Sitios = eventos (observador × celda ~1 km × día × franja 3 h) con ≥2 especies; especies = las 300 más frecuentes. Se reportan pares **positivos**, **negativos** y aleatorios, con FDR Benjamini-Hochberg. Figura observado frente a esperado: `material/figuras/fig_v25_veech_obs_vs_esperado.png`. Como paso intermedio sin covariables ambientales completas, exploramos una **red de precisión parcial (graphical lasso)** sobre la matriz de co-presencia en eventos (300 especies más frecuentes; aristas tras FDR), solo para visualizar clústeres taxonómicos — no sustituye un JSDM/HMSC con covariables (Ovaskainen et al., 2017), que **sigue pendiente**.

### 2.8 Covariables de esfuerzo y sensibilidad (Johnston)
Siguiendo las guías de Johnston et al. (2021) e Isaac et al. (2014): (i) longitud de lista por evento (nº de especies); (ii) submuestreo espacial de 1 evento por celda×día; (iii) exigencia de ≥5 observadores distintos por par. Tabla de sensibilidad: cuántos pares +/− sobreviven a cada filtro (`material/experimentos/v25_sensibilidad_johnston_20261011.csv`).

### 2.9 Red residual (graphical lasso; Harris)
Sobre la matriz binaria evento×especie (top 300, tras submuestreo espacial) se ajustó un *graphical lasso* (α = 0,005; Harris, 2016): las aristas de la precisión no nulas son asociaciones **condicionales** (quitan caminos indirectos). La red residual (45 aristas) es lista candidata, no evidencia de interacción.

### 2.10 Validación Freilich y tres escalas
Diseño Freilich et al. (2018): precisión y recall frente a GloBI + parejas de literatura del artículo, separando tróficas y no tróficas, con IC bootstrap 95 %. El análisis se repite a tres escalas: misma foto, evento de 3 h, celda de 1 km × mes (Blanchet et al., 2020).

### 2.11 Propagación del error del identificador
Con acierto de especie p = 0,8438, la probabilidad de que ambas especies de un co-evento estén bien identificadas es p² ≈ 0,693 si se asume independencia. Sobre la lista corta de 138 parejas, usando aciertos **por especie** del panel `calib_raw_t05.jsonl` (`ok_species`): media ponderada de acierto = **85,19 %** (142 taxones; CSV `material/experimentos/p4_acierto_por_especie_shortlist_20261010.csv`); media de P(ambas OK) por pareja = **71,51 %**; 138/138 tienen E[eventos limpios] ≥ 3 y 134/138 ≥ 8; ninguna de las 138 aparece como confusión directa A↔B en el top-50 del eval de 25-sep. Antes de la revisión a ojo se pierde del orden del **~29 %** de co-eventos por error de ID.

### 2.12 Cruce con GloBI
Para cada pareja se consultó la API de GloBI (Poelen et al., 2014). La lista corta tiene 9/138 documentadas (6,52 %), pero 7 de ellas son aves acuáticas con tipo genérico «interactsWith». **Sin aves:** lista corta 2/130 (1,54 %) frente a muestra solo-eventos 5/395 (1,27 %); odds ratio 1,219, p = 0,6849 (Fisher) → **sin enriquecimiento**. Los hits por género (≥3 pares) se concentran en *Anas*, *Gallinula* y *Ardea*; fuera de aves no hay señal por clúster.


## 3. Resultados

### 3.1 Del cribado por eventos a la lista corta
De 115.204 parejas con ≥5 eventos, 51.401 son significativas con el esfuerzo controlado y 3.108 combinan replicación y razón observado/esperado ≥3 (Figura 1). Como casi la mitad de las parejas con soporte son «significativas», la significación no discrimina y no se usa como conclusión.

<figure class="fig"><img src="material/figuras/fig1_cribado_hasta_misma_foto.png" alt="Figura 1. Del cribado por eventos a las parejas con fotograf"><figcaption><b>Figura 1. Del cribado por eventos a las parejas con fotografía conjunta.</b> Número de parejas que superan cada filtro (escala logarítmica). Gris: cribado por eventos (hipótesis); azul: lista corta de 138 parejas (las 70 de mayor puntuación y las 70 de mayor puntuación entre grupos taxonómicos distintos, con n ≥ 15 eventos y ≥ 8 observadores), parejas con al menos una foto candidata y parejas con tres o más observaciones distintas. Datos: <a href="https://github.com/yespi/biofauna/blob/master/data/copresencia_pares_20261006.csv">data/copresencia_pares_20261006.csv</a>.</figcaption></figure>

### 3.2 Detección de ambas especies en la misma foto
De las 138 parejas, 41 tuvieron al menos una foto candidata y 12 tres o más observaciones distintas (Figura 2). La revisión a ojo de las primeras mostró **falsos positivos entre especies parecidas** (por ejemplo dos almejas, *Polititapes aureus* y *Ruditapes decussatus*, o dos nudibranquios, *Caloria quatrefagesi* y *Luisella babai*): el identificador reconoce a la especie parecida en otra región de la imagen. Esto confirma que la detección automática solo propone y que muchas coincidencias «significativas» no resisten la revisión.

<figure class="fig"><img src="material/figuras/fig2_candidatas_por_pareja.png" alt="Figura 2. Fotos candidatas por pareja y resultado de la revi"><figcaption><b>Figura 2. Fotos candidatas por pareja y resultado de la revisión visual.</b> Observaciones distintas con foto candidata de ambas especies para las 14 parejas con más candidatas. Verde: confirmada a ojo con ambas especies visibles; rojo: falso positivo por especies parecidas; gris: sin revisar o por confirmar (<i>Echinolittorina</i>–<i>Melarhaphe</i>, <i>Cliona</i>/<i>Clavularia</i>–<i>Rocellaria</i>, <i>Anas</i>–<i>Gallinula</i>).</figcaption></figure>

### 3.3 Parejas con ambas especies visibles

**Frontera con el paper de nudibranquios.** Las asociaciones **nudibranquio–presa/sustrato** por misma fotografía (*Peltodoris atromaculata*–*Petrosia ficiformis*, *Cratena peregrina*–*Eudendrium racemosum*, *Felimare orsinii*–*Scalarispongia scalaris*; antiguas láminas 1, 2 y 7) se retiran de este manuscrito para evitar redundancia y se tratan en `papers/nudibranquios/` (Zafra, en preparación). Aquí permanecen el **método general** (cribado + detector + revisión a ojo) y las parejas **sin** opistobranquio como foco principal.

La Tabla 2 recoge las parejas confirmadas a ojo en este artículo; las láminas 3–6 y 8–9 ilustran un subconjunto (la lámina 5 incluye un nudibranquio pelágico como ejemplo de camuflaje, no como bloque de dietas). De las **138** parejas de la lista corta original del cribado, **dos** no nudibranquio–presa proceden del cribado y resisten la revisión visual con ambas especies visibles (*Condylactis*–*Periclimenes*, *Electra*–*Tridentata*). *Condylactis aurantiaca* con *Periclimenes scriptus* es coherente con el comensalismo conocido de los *Periclimenes* con anémonas [VERIFICAR cita específica para esta pareja]. *Lysmata grabhami* con *Telmatactis cricoides* (limpieza) y *Electra posidoniae* con *Tridentata perpusilla* (microhábitat en *Posidonia*) muestran proximidad real; en el segundo caso **no** hay interacción demostrada. La segunda especie de cada foto la identifica BioFauna y **no está confirmada por curadores**.

| Tabla 2. Parejas con fotografías de ambas especies en la misma imagen (cuerpo; sin bloque nudibranquio–presa) | Nivel | Fotos (obs. distintas) | Origen |
|---|---|---:|---|
| *Condylactis aurantiaca* con el camarón *Periclimenes scriptus* (comensalismo) | 2 | 4 (4) | lista corta del cribado |
| *Lysmata grabhami* y *Telmatactis cricoides* (limpieza) | 1 | 4 (4) | selección previa (limpiador) |
| *Scyllaea pelagica* sobre *Sargassum* flotante | 0–1 | 1 (1) | selección previa (ilustración; ver paper nudibranquios para dietas bentónicas) |
| *Electra posidoniae* y *Tridentata perpusilla* sobre hojas de *Posidonia* (microhábitat compartido) | 1 | 4 (4) | lista corta del cribado |
| *Parazoanthus axinellae* junto a *Spongia lamella* | 1 | 2 (2) | pares de misma foto (revisión a ojo 8-oct) |
| *Echinolittorina punctata* y *Melarhaphe neritoides* (zona de salpicadura) | 0–1 | 3 (3) | pares de misma foto (con cautela) |

### 3.4 Parejas sin foto conjunta
No apareció ninguna foto con ambas especies para *Felimare picta*–*Ircinia oros*, *Muraena helena*–*Ophidiaster ophidianus* ni *Fistularia commersonii*–*Pterois miles*. Eso no prueba que no convivan, y no permite afirmar ninguna relación: quedan *sin confirmar*.
### 3.5 Otras relaciones detectadas (candidatas del cribado)

El cribado dejó **41** parejas con al menos una foto candidata del detector (incluidas ocho de aves acuáticas de la lista corta). La mayoría no se han revisado a ojo o resultaron falsos positivos por especies parecidas. El listado completo con estado de revisión figura en la **Tabla S3** (`material/TABLA_S3_candidatas.md`).


<div class="lamina">
<p class="lt"><b>Lámina 3. <i>Condylactis aurantiaca</i> con el camarón <i>Periclimenes scriptus</i> (comensalismo).</b> <i>Camarón identificado por BioFauna como <i>Periclimenes scriptus</i>; sin confirmación de curadores.</i></p>
<div class="grid">
<figure><img src="material/lamina_fotos/par3__condylactis_aurantiaca__periclimenes_scriptus__1.jpg" alt="Lámina 3.1"><figcaption>Lámina 3.1: xavi salvador costa · CC BY-NC † · 2016-09-10 22:07 (Europe/Paris) · Begur, Bajo Ampurdán, Cataluña, España; Empordà Marítim, Girona, Cataluña · 41.9355° N, 3.2176° E (±185 m) · Minka obs 28492.</figcaption></figure>
<figure><img src="material/lamina_fotos/par3__condylactis_aurantiaca__periclimenes_scriptus__2.jpg" alt="Lámina 3.2"><figcaption>Lámina 3.2: Sylvain Le Bris · CC BY-NC † · 2026-04-08 22:17 (Europe/Paris) · Montredon, Marseille, France; Bouches-Du-Rhône, Bouches-du-Rhône, Provence-Alpes-Côte d'Azur; Francia · 43.2325° N, 5.3502° E (±101 m) · iNaturalist obs 348576200.</figcaption></figure>
<figure><img src="material/lamina_fotos/par3__condylactis_aurantiaca__periclimenes_scriptus__3.jpg" alt="Lámina 3.3"><figcaption>Lámina 3.3: xavi salvador costa · CC BY-NC † · 2016-07-09 22:18 (Europe/Paris) · Begur, Bajo Ampurdán, Cataluña, España; Empordà Marítim, Girona, Cataluña · 41.9366° N, 3.2201° E (±185 m) · Minka obs 28862.</figcaption></figure>
<figure><img src="material/lamina_fotos/par3__condylactis_aurantiaca__periclimenes_scriptus__4.jpg" alt="Lámina 3.4"><figcaption>Lámina 3.4: xavi salvador costa · CC BY-NC † · 2018-09-01 16:03 (Europe/Paris) · Begur, Bajo Ampurdán, Cataluña, España; Empordà Marítim, Girona, Cataluña · 41.9357° N, 3.2176° E (±142 m) · Minka obs 35885.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Lámina 4. <i>Lysmata grabhami</i> y <i>Telmatactis cricoides</i> (limpieza).</b> <i>Camarón limpiador y anémona identificados por BioFauna; en dos fotos el camarón es pequeño.</i></p>
<div class="grid">
<figure><img src="material/lamina_fotos/par4__lysmata_grabhami__telmatactis_cricoides__1.jpg" alt="Lámina 4.1"><figcaption>Lámina 4.1: jmturon · CC BY-NC † · 2023-12-05 10:57 (Atlantic/Canary) · Las Coloradas; LANZAROTE with iselets and seashore, Las Palmas, Islas Canarias; España · 28.8506° N, 13.7995° W (±662 m) · Minka obs 210346.</figcaption></figure>
<figure><img src="material/lamina_fotos/par4__lysmata_grabhami__telmatactis_cricoides__2.jpg" alt="Lámina 4.2"><figcaption>Lámina 4.2: jmturon · CC BY-NC † · 2023-12-06 20:06 (Atlantic/Canary) · Playa Flamingo; LANZAROTE with iselets and seashore, Las Palmas, Islas Canarias; España · 28.8552° N, 13.8439° W (±361 m) · Minka obs 210532.</figcaption></figure>
<figure><img src="material/lamina_fotos/par4__lysmata_grabhami__telmatactis_cricoides__3.jpg" alt="Lámina 4.3"><figcaption>Lámina 4.3: phil_newman · CC BY-NC † · 2025-11-22 11:50 (Atlantic/Canary) · Playa Flamingo Playa Blanca Lanzarote; LANZAROTE with iselets and seashore, Las Palmas, Islas Canarias; España · 28.8568° N, 13.8428° W (±100 m) · iNaturalist obs 329826704.</figcaption></figure>
<figure><img src="material/lamina_fotos/par4__lysmata_grabhami__telmatactis_cricoides__4.jpg" alt="Lámina 4.4"><figcaption>Lámina 4.4: whodden · CC BY-NC † · 2007-04-04 00:00 (Europe/Madrid) · Punta Prieta, Güímar, Canarias, España; TENERIFE with seashore, Santa Cruz de Tenerife, Islas Canarias · 28.2660° N, 16.3869° W (±14 m) · iNaturalist obs 2354980.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Lámina 5. <i>Scyllaea pelagica</i> sobre <i>Sargassum</i> flotante.</b> <i>Solo se ve con claridad el nudibranquio camuflado; <i>Latreutes</i> e <i>Hippolyte</i> no se distinguen a ojo.</i></p>
<div class="grid">
<figure><img src="material/lamina_fotos/par5__scyllaea_pelagica__latreutes_fucorum__1.jpg" alt="Lámina 5.1"><figcaption>Lámina 5.1: Ben Eddy · CC BY-NC † · 2023-06-27 13:52 (Atlantic/Bermuda) · Southampton, BM; Bermuda Marine, Sandys; Bermudas · 32.2556° N, 64.8742° W (±105 m) · iNaturalist obs 170761288.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Lámina 6. <i>Electra posidoniae</i> y <i>Tridentata perpusilla</i> sobre hojas de <i>Posidonia oceanica</i> (microhábitat compartido; tres fotos mediterráneas tras exclusión de la observación tropical errónea).</b> <i>Briozoo incrustante y hidrozoo sobre la misma hoja; microhábitat compartido, no interacción demostrada.</i></p>
<div class="grid">
<figure><img src="material/lamina_fotos/par6__electra_posidoniae__tridentata_perpusilla__1.jpg" alt="Lámina 6.1"><figcaption>Lámina 6.1: xavi salvador costa · CC BY-NC † · 2023-08-09 11:01 (Europe/Madrid) · Vegueria de Barcelona, Barcelona, Cataluña; España · 41.3957° N, 2.2114° E (±115 m) · Minka obs 153028.</figcaption></figure>
<figure><img src="material/lamina_fotos/par6__electra_posidoniae__tridentata_perpusilla__2.jpg" alt="Lámina 6.2"><figcaption>Lámina 6.2: conxi · CC BY-NC † · 2025-05-31 11:48 (Europe/Madrid) · Valldolig, Blanes, la Selva, Cataluña, España; Vegueria de Barcelona, Barcelona, Cataluña · 41.6732° N, 2.8022° E (±178 m) · Minka obs 511234.</figcaption></figure>
<!-- Excluida Lámina 6.3 (Costa Rica): incompatible con *Posidonia oceanica* / *Electra posidoniae* mediterráneos. -->
<figure><img src="material/lamina_fotos/par6__electra_posidoniae__tridentata_perpusilla__4.jpg" alt="Lámina 6.4"><figcaption>Lámina 6.4: Manel Ortega · CC BY · 2025-08-10 10:13 (Europe/Madrid) · Llançà, Alto Ampurdán, Cataluña, España; Orientales, Girona, Cataluña · 42.3875° N, 3.1612° E (±622 m) · Minka obs 544263.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Lámina 8. <i>Parazoanthus axinellae</i> junto a <i>Spongia lamella</i>.</b> <i>Esponja laminar gris junto a colonias de <i>Parazoanthus</i>: coexistencia en el mismo plano, sin interacción demostrada.</i></p>
<div class="grid">
<figure><img src="material/lamina_fotos/par8__parazoanthus_axinellae__spongia_lamella__1.jpg" alt="Lámina 8.1"><figcaption>Lámina 8.1: Sylvain Le Bris · CC BY-NC † · 2025-08-15 10:55 (Europe/Paris) · Pierre à Joseph, Marseille, France; Bouches-Du-Rhône, Bouches-du-Rhône, Provence-Alpes-Côte d'Azur · 43.1851° N, 5.3894° E · iNaturalist obs 307095607.</figcaption></figure>
<figure><img src="material/lamina_fotos/par8__parazoanthus_axinellae__spongia_lamella__2.jpg" alt="Lámina 8.2"><figcaption>Lámina 8.2: Sylvain Le Bris · CC BY-NC † · 2026-05-17 09:42 (Europe/Paris) · Pharillons, Marseille, France; Bouches-Du-Rhône, Bouches-du-Rhône, Provence-Alpes-Côte d'Azur · 43.2074° N, 5.3380° E · iNaturalist obs 362838925.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Lámina 9. <i>Echinolittorina punctata</i> y <i>Melarhaphe neritoides</i> (zona de salpicadura).</b> <i>Caracoles de la zona de salpicadura sobre la misma roca. Son especies muy parecidas: la separación depende de BioFauna y requiere confirmación de un experto (nivel 0–1).</i></p>
<div class="grid">
<figure><img src="material/lamina_fotos/par9__echinolittorina_punctata__melarhaphe_neritoides__1.jpg" alt="Lámina 9.1"><figcaption>Lámina 9.1: Golfopolikayak · CC BY · 2020-06-19 16:58 (Europe/Paris) · 87029 Scalea CS, Italia; Pollino, Cosenza, Calabria · 39.8191° N, 15.7775° E · iNaturalist obs 56350676.</figcaption></figure>
<figure><img src="material/lamina_fotos/par9__echinolittorina_punctata__melarhaphe_neritoides__2.jpg" alt="Lámina 9.2"><figcaption>Lámina 9.2: Mar Humet Caballero · CC BY-NC † · 2026-08-03 17:51 (Europe/Madrid) · Camping Cases, Carrer a l'Ombra del Montsià, les Cases d'Alcanar, Alcanar, Montsià, Tarragona, Catalunya, 43530, Espanya; RB ESP 44. Reserva de la Biosfera.Terras de L’Ebre. Cataluña. España., Castellón, Cataluña · 40.5557° N, 0.5335° E · Minka obs 834586.</figcaption></figure>
<figure><img src="material/lamina_fotos/par9__echinolittorina_punctata__melarhaphe_neritoides__3.jpg" alt="Lámina 9.3"><figcaption>Lámina 9.3: Calum McLennan · CC BY-NC † · 2021-08-25 11:24 (Europe/London) · Alicante, Spain; Javea - Xabia, Alicante, Comunidad Valenciana · 38.8169° N, 0.1688° E · iNaturalist obs 92485321.</figcaption></figure>
</div>
</div>


### 3.6 Veech/`cooccur`, esfuerzo y red residual

Sobre 37.710 eventos y las 300 especies más frecuentes, Veech clasifica **21.208** pares positivos y **9.405** negativos (q≤0,05). El diagrama observado frente a esperado está en el material suplementario (`material/figuras/fig_v25_veech_obs_vs_esperado.png`).

Tabla de sensibilidad (Johnston): la longitud de lista (≤ Q75 = 5 spp/evento) reduce los positivos q05 de 21.208 a **812**; con submuestreo espacial + ≥5 observadores quedan **431**.

| Filtro | + q05 | − q05 |
|---|---:|---:|
| A eventos ≥2 spp | 21.208 | 9.405 |
| B list length ≤ Q75 (5) | 812 | 0 |
| C 1 evento / celda×día | 20.953 | 7.859 |
| D B+C | 703 | 0 |
| E D + ≥5 observadores | **431** | 0 |

*Graphical lasso* (α = 0,005): **45** aristas residuales (hábitat bentónico: *Posidonia*–algas, esponjas, ascidias); solape con los 431 de Veech-E: 4 pares.

### 3.6bis Validación Freilich (GloBI + literatura) y tres escalas

Gold: 51 pares (GloBI documentados + literatura del artículo): 12 tróficas, 27 no tróficas y 12 de control o hábitat compartido sin relación trófica directa. IC bootstrap 95 %:

| Método | Gold | Precisión (IC) | Recall (IC) |
|---|---|---|---|
| Veech E (431) | all | 0,23 % (0–0,38) | 2,0 % (0–3,5) |
| glasso (45) | all | 0 % | 0 % |
| misma foto (41) | all | **4,9 %** (0–8,5) | 3,9 % (0–6,9) |
| misma foto | no tróficas | **4,9 %** (0–8,7) | **7,4 %** (0–13,3) |

| Escala | Unidades | + q05 | − q05 |
|---|---:|---:|---:|
| Misma foto (lista 138) | galería | 41* | — |
| Evento 3 h | 37.710 | 21.208 | 9.405 |
| Celda 1 km × mes | 13.800 | 30.796 | 5.785 |

\* hits del detector. Solape foto∩evento∩mes = 7. A escala mes crecen los positivos (hábitat/filtrado ambiental).

**Lectura:** el valor del trabajo no está en el cribado por eventos, sino en el criterio de la misma foto. JSDM/HMSC con covariables ambientales sigue pendiente.

### 3.7 Propagación del error del identificador
Con acierto de especie 84,38 %, P(ambas OK) ≈ 0,71 en la lista corta. Eso acota cuántas coincidencias por evento pueden ser identificaciones dobles correctas **antes** de la revisión visual; no sustituye esa revisión.

### 3.8 Revisión bibliográfica de parejas confirmadas

| Pareja | Notas |
|---|---|
|*Peltodoris* / *Cratena* / *Felimare*–presa|ver paper nudibranquios (retiradas de este manuscrito, §3.3)|
|*Condylactis aurantiaca*–*Periclimenes scriptus*|comensalismo coherente a nivel de género; pendiente cita de la pareja concreta|
|*Lysmata grabhami*–*Telmatactis cricoides*|limpieza documentada en *Lysmata*; literatura Atlántico E / Canarias pendiente|
|*Electra posidoniae*–*Tridentata perpusilla*|microhábitat compartido sobre *Posidonia*, no interacción demostrada|
|*Parazoanthus axinellae*–*Spongia lamella*|convivencia en el mismo plano; sin interacción demostrada|
|*Calystegia soldanella*–*Medicago marina*|hábitat dunar compartido (terrestre)|

Revisores expertos / curadores de la comunidad: pendiente el envío formal del material de láminas para revisión.


## 4. Discusión

**Qué demuestra y qué no.** Una foto con las dos especies demuestra proximidad a escala de centímetros en un instante; no demuestra que se busquen, se eviten o interactúen (Blanchet et al., 2020). Freilich et al. (2018) muestran que, incluso con muestreo de campo exhaustivo, la co-ocurrencia recupera mal las interacciones; nuestro cribado por eventos encaja en esa cautela (precisión Freilich ≈0,2 % frente a ≈4,9 % en la misma foto). Tres o más observaciones independientes con ambas visibles dan replicación, y el contacto visible (sobre, dentro, comiendo) apunta a una relación, que debe confirmarse con curadores y bibliografía. La co-ocurrencia por evento, en cambio, solo señala especies que comparten sitio y fecha y **no se usa como resultado**: al exigir la misma foto desaparecen la mayoría de las coincidencias.

**Objeciones de Blanchet et al. (2020) → respuesta**

| Objeción | Cómo lo abordamos |
|---|---|
| La co-ocurrencia mezcla filtrado ambiental, dispersión e interacción | Criterio principal = misma foto (cm); el cribado por eventos solo genera hipótesis |
| El patrón depende de la escala | Tres escalas (foto / evento 3 h / celda×mes): a mes crecen los + (hábitat); la foto es la más estricta |
| Inferir interacción sin condicionar por el resto de la comunidad | *Graphical lasso* (Harris): 45 aristas condicionales residuales como lista candidata |

**Sesgos.** La galería está formada sobre todo por retratos centrados de una especie, lo que subestima la proporción de fotos con una segunda especie; el identificador reconoce peor las especies pequeñas o camufladas, y confunde especies parecidas (falsos positivos); solo se han revisado a ojo las primeras candidatas; y el análisis parte de fotos con licencias muy diversas, lo que limita las láminas. La longitud de lista domina el nulo (Johnston): sin controlarla, miles de «positivos» Veech son esfuerzo compartido.

**Series temporales.** El análisis de correlaciones cruzadas y cascadas sobre series anuales en Cataluña se **retira del cuerpo** para mantener el foco en la misma foto; el material permanece en `material/experimentos/AVANCE_cruzadas_20261011.md` y en el manuscrito de especies en declive (`papers/especies_peligro_declives/`), evitando doble publicación del caso *Pinna nobilis*.

### 4.4 Autoevaluación editorial (16-oct-2026)

Tras revisión interna (octubre 2026), estimamos **~86 %** de completitud para envío interno: foco en la misma foto; lámina Costa Rica excluida; candidatas al suplemento; limitaciones explícitas (muestra ciega, láminas, JSDM, licencias NC, Zenodo). Pendiente: validación ciega del detector, confirmación taxonómica de segundas especies, permisos fotos NC.

## 5. Limitaciones

**Cifra del identificador.** El **84,38 %** es el acierto oficial fuera de muestra del índice **p19** (3.061 spp; panel rescore octubre 2026). Puede estar algo optimista para recortes de segunda especie y si el panel conserva filas muy similares a la galería; un índice congelado con DOI (Zenodo) está planificado.

**Modelo nulo Veech.** Veech/`cooccur` está implementado en Python (positivos y negativos, figura observado vs esperado, filtros Johnston, *graphical lasso*); un JSDM/HMSC con covariables ambientales (Ovaskainen et al., 2017) **sigue pendiente**.

**Validación externa (GloBI + Freilich).** GloBI no valida la lista corta (Fisher *p* = 0,68 sin aves); precisión Freilich del cribado ≈0,2 % frente a ≈4,9 % en la misma foto.

**Propagación de error.** Con *p* ≈ 0,84 se pierde ~29 % de co-eventos por error de ID antes de la revisión a ojo.

**Alcance geográfico.** Las láminas mezclan ejemplos mediterráneos y de otros mares para ilustrar el método; no implican que el cribado esté restringido a Cataluña.

**Validación del detector.** Pendiente una muestra aleatoria de ≥200 candidatas revisadas a ciegas por ≥2 personas (κ, precisión/recall); diseño en `biofauna/experimentos/PUBLICABILIDAD_CORRELACION_20261007.md`.

**Ampliación de láminas.** Búsqueda de parejas adicionales con foto conjunta en curso; Láminas 7–9 no se regeneran salvo error (aprobadas).

**Error lámina 6.3.** Una cuarta foto del par *Electra*–*Tridentata* entró en el manifiesto tras revisión superficial de la miniatura; al contrastar taxones declarados y coordenadas (Minka obs. 629063, Pacífico de Costa Rica) se **excluyó** del PDF por incompatibilidad con *Posidonia oceanica* y *Electra posidoniae* mediterráneos (error de identificación o de georreferencia en la fuente).

La proximidad en una foto no es interacción. La segunda especie es propuesta por el identificador. Revisión formal por curadores y sustitución de fotos CC BY-NC pendientes para revista comercial.

## 6. Conclusiones

1. El cribado por co-ocurrencia de eventos, aun con el esfuerzo controlado, no es evidencia de asociación: genera miles de coincidencias, de las que solo una pequeña parte resiste la revisión por proximidad real.
2. La proximidad real (ambas especies en la misma fotografía) es un criterio verificable por cualquier lector; con él se han confirmado a ojo unas pocas parejas (controles positivos documentados y candidatas de nivel 1–2 en las Láminas 1–9); eso es una base de evidencia visual, no una prueba de que el cribado «funcione» en general.
3. El método sirve para proponer parejas y fotografías que los curadores pueden verificar; no sustituye su criterio.
4. Las series anuales esfuerzo-corregidas (manuscrito aparte) pueden explorar comunidades que covarían y pares sincronizados u opuestos tras FDR; no forman parte de este artículo.

## Agradecimientos


A la comunidad observadora y, muy especialmente, a los **curadores de la comunidad** y **revisores expertos**
que sostienen la fiabilidad de las identificaciones en **Minka SDG** e **iNaturalist**. Mención especial a la
**FECDAS** y a su **Projecte Aneris** por impulsar la ciencia ciudadana marina y la formación de observadores;
a **Minka SDG** e **iNaturalist** por las plataformas y los datos; y a **GBIF**, **Wikimedia Commons**,
**DORIS/FFESSM**, **SeaSlugForum**, **WoRMS** y **FishBase** por las imágenes y los datos taxonómicos. Este
análisis ha sido posible gracias al **identificador BioFauna** (BioCLIP-2.5 ViT-H/14 + FAISS), creado y
desarrollado por **Gustavo Zafra** (autor de este manuscrito), con la colaboración del autor en la plataforma
Minka SDG.

**Uso de asistentes de IA.** Partes del borrador se redactaron con asistencia de modelos de lenguaje (2026), bajo revisión del autor.

## Referencias

- Aceves-Bueno, E., Adeleye, A. S., Feraud, M., Huang, Y., Tao, M., Yang, Y., & Anderson, S. E. (2017). The accuracy of citizen science data: a quantitative review. *The Bulletin of the Ecological Society of America*, 98(4), 278–290.
- Avila, C. (1996). The growth of *Peltodoris atromaculata* Bergh, 1880 (Gastropoda, Nudibranchia) in the laboratory. *Journal of Molluscan Studies*, 62, 151–157. — crecimiento en laboratorio con dieta basada en *Petrosia ficiformis*.
- Blanchet, F. G., Cazelles, K., & Gravel, D. (2020). Co-occurrence is not evidence of ecological interactions. *Ecology Letters*, 23(7), 1050–1063. https://doi.org/10.1111/ele.13525
- Freilich, M. A., Wieters, E., Broitman, B. R., Marquet, P. A., & Navarrete, S. A. (2018). Species co-occurrence networks: Can they reveal trophic and non-trophic interactions in ecological communities? *Ecology*, 99(3), 690–699. https://doi.org/10.1002/ecy.2142
- Griffith, D. M., Veech, J. A., & Marsh, C. J. (2016). cooccur: Probabilistic species co-occurrence analysis in R. *Journal of Statistical Software*, 69(Code Snippet 2). https://doi.org/10.18637/jss.v069.c02
- Harris, D. J. (2016). Inferring species interactions from co-occurrence data with Markov networks. *Ecology*, 97(11), 3304–3311. https://doi.org/10.1002/ecy.1605
- Boyd, R. J., Powers, M., & Pescott, O. L. (2021). occAssess: an R package for assessing potential biases in species occurrence data. *Ecology and Evolution*, 11(22).
- Isaac, N. J. B., van Strien, A. J., August, T. A., de Zeeuw, M. P., & Roy, D. B. (2014). Statistics for citizen science: extracting signals of change from noisy ecological data. *Methods in Ecology and Evolution*, 5(10), 1052–1060.
- Johnston, A., Fink, D., Hochachka, W. M., & Kelling, S. (2018). Estimates of observer expertise improve species distributions from citizen science data. *Methods in Ecology and Evolution*, 9(4), 880–890.
- Johnston, A., Hochachka, W. M., Strimas-Mackey, M. E., Ruiz Gutierrez, V., Robinson, O. J., Miller, E. T., Auer, T., Kelling, S. T., & Fink, D. (2021). Analytical guidelines to increase the value of community science data: An example using eBird data to estimate species distributions. *Diversity and Distributions*, 27(7), 1291–1303. https://doi.org/10.1111/ddi.13271
- Milanesi, P., Mori, E., & Menchetti, M. (2020). Observer-oriented approach improves species distribution models from citizen science data. *Ecology and Evolution*, 10(21), 12104–12114.
- Ovaskainen, O., Tikhonov, G., Norberg, A., Guillaume Blanchet, F., Duan, L., Dunson, D., Roslin, T., & Abrego, N. (2017). How to make more out of community data? A conceptual framework and its implementation as models and software. *Ecology Letters*, 20(5), 561–576. https://doi.org/10.1111/ele.12757
- Poelen, J. H., Simons, J. D., & Mungall, C. J. (2014). Global biotic interactions: An open infrastructure to share and analyze species-interaction datasets. *Ecological Informatics*, 24, 148–159.
- Veech, J. A. (2013). A probabilistic model for analysing species co-occurrence. *Global Ecology and Biogeography*, 22(2), 252–260. https://doi.org/10.1111/j.1466-8238.2012.00789.x
- Vázquez-Luis, M., Álvarez, E., Barrajón, A., García-March, J. R., et al. (2017). S.O.S. *Pinna nobilis*: A Mass Mortality Event in Western Mediterranean Sea. *Frontiers in Marine Science*, 4, 220. https://doi.org/10.3389/fmars.2017.00220
- Catanese, G., Grau, A., Valencia, J. M., Garcia-March, J. R., et al. (2018). *Haplosporidium pinnae* sp. nov., a haplosporidan parasite associated with mass mortalities of the fan mussel, *Pinna nobilis*, in the Western Mediterranean Sea. *Journal of Invertebrate Pathology*, 157, 9–24. https://doi.org/10.1016/j.jip.2018.07.006
- Garrabou, J., Gómez-Gras, D., Medrano, A., Cerrano, C., et al. (2022). Marine heatwaves drive recurrent mass mortalities in the Mediterranean Sea. *Global Change Biology*, 28(19), 5708–5725. https://doi.org/10.1111/gcb.16301
- Haddad-Boubaker, S., Boughdir, W., Sghaier, H., et al. (2014). Outbreak of Viral Nervous Necrosis in Endangered Fish species *Epinephelus costae* and *E. marginatus* in Tunisia. *Fish Pathology*. https://doi.org/10.3147/jsfp.49.53
- Peñalver, J., María-Dolores, E., García-Charton, J. A., et al. (2020). Mortality by nodavirus in grouper (*Epinephelus marginatus*) from the Cabo de Palos – Islas Hormigas Marine Reserve. *Anales de Biología*. https://doi.org/10.6018/analesbio.42.07
- Toffan, A., Volpe, E., Zrnčić, S., et al. (2026). Nodavirus in wild fish: addressing the Mediterranean grouper (*Epinephelus* spp.). https://doi.org/10.48045/001c.158446
- Kersting, D. K., & Ballesteros, E. (2021). Is the local extinction of *Pinna nobilis* facilitating *Pinna rudis* recruitment? *Mediterranean Marine Science*. https://doi.org/10.12681/mms.27809
- Barve, V. V., Brenskelle, L., Li, D., Stucky, B. J., Barve, N. V., Hamerlinck, L. M., … Guralnick, R. P. (2020). Methods for broad-scale plant phenology assessments using citizen scientists’ photographs. *Applications in Plant Sciences*, 8(1), e11315. https://doi.org/10.1002/aps3.11315

## Disponibilidad de datos

**Todo el material está en el repositorio público de GitHub: https://github.com/yespi/biofauna** (rama `master`). Rutas completas:
- Parejas de la lista corta y sus fotos candidatas: [`data/copresencia_pares_20261006.csv`](https://github.com/yespi/biofauna/blob/master/data/copresencia_pares_20261006.csv) y [`data/copresencia_hits_20261006.jsonl`](https://github.com/yespi/biofauna/blob/master/data/copresencia_hits_20261006.jsonl).
- Manifiesto de las láminas con autor, licencia, fecha y hora, lugar y enlace de cada foto: [`papers/proyecto_correlacion/lamina_fotos/lamina_manifest_20261008.json`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/lamina_fotos/lamina_manifest_20261008.json).
- Listados del cribado por eventos (solo hipótesis), con su descripción: [`data/README_correlacion.md`](https://github.com/yespi/biofauna/blob/master/data/README_correlacion.md) y los ficheros `data/nulo_exacto_pares_*.csv` y `data/pares_*_20261005.csv`.
- Métodos y resultados ampliados, figuras y láminas: carpeta [`papers/proyecto_correlacion/`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/) (artículo en español e inglés, `LAMINAS`, `METODOS.md`, `RESULTADOS.md`, `material/figuras/`, `lamina_fotos/`). PDFs compilados: `ARTICULO_COMPLETO_latest.pdf`, `LAMINAS_latest.pdf`. Notas de experimentos: [`material/experimentos/`](https://github.com/yespi/biofauna/tree/master/papers/proyecto_correlacion/material/experimentos/) (p. ej. [`AVANCE_P3_P4_P1_P9_20261009.md`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/material/experimentos/AVANCE_P3_P4_P1_P9_20261009.md), [`AVANCE_v25_20261011.md`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/material/experimentos/AVANCE_v25_20261011.md), [`AVANCE_cruzadas_20261011.md`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/material/experimentos/AVANCE_cruzadas_20261011.md)) y `material/figuras/cruzadas/`.
- Identificador BioFauna (código, prototipos, calibradores, scripts de evaluación): carpetas [`src/`](https://github.com/yespi/biofauna/blob/master/src/), [`scripts/`](https://github.com/yespi/biofauna/blob/master/scripts/), [`data/`](https://github.com/yespi/biofauna/blob/master/data/) y [`papers/biofauna/`](https://github.com/yespi/biofauna/blob/master/papers/biofauna/).
- **No redistribuibles**: las fotografías de la galería (licencias de Minka SDG, iNaturalist y otras fuentes; las de las láminas se incluyen con atribución) y los *embeddings* por foto.



## Material suplementario

**Suplemento S3. Candidatas del detector.** [`material/TABLA_S3_candidatas.md`](material/TABLA_S3_candidatas.md).

**Suplemento S2. Tendencias cruzadas (fuera del cuerpo).** [`material/experimentos/AVANCE_cruzadas_20261011.md`](material/experimentos/AVANCE_cruzadas_20261011.md).

**Suplemento S1. Cribado por eventos (hipótesis).** Descripción del contraste con esfuerzo controlado y listados completos en [`NULO_EXACTO_TODOS_PARES_20261005.md`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/NULO_EXACTO_TODOS_PARES_20261005.md). Figuras S1 y S2 en [`papers/proyecto_correlacion/figuras/`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/figuras/).


**Tabla S1. Las 30 parejas con mayor z entre las 3.108 robustas del cribado por eventos (razón observado/esperado ≥ 3, ≥ 5 observadores).** Son **hipótesis, no resultados**: un z alto indica que coinciden mucho más de lo que el esfuerzo local predice, pero no distingue interacción de hábitat compartido (p. ej. dos especies de playa), de especies plantadas o criadas juntas (*Phoenix*–*Washingtonia*) ni de especies tan parecidas que el observador las asigna a una u otra (*Nembrotha cristata*–*N. milleri*). Lista completa de las 3.108 y de las 2.312 mediterráneas de distinto género en `data/`.

| Pareja | Mismo género | Grupos | Eventos comunes | Esperado (esfuerzo) | Razón | z | Observadores |
|---|:-:|---|---:|---:|---:|---:|---:|
| *Limacia clavigera* – *Polycera quadrilineata* | no | Mollusca | 66 | 2.0 | 33.1 | 54.6 | 19 |
| *Cephalopholis miniata* – *Pseudanthias squamipinnis* | no | Actinopterygii | 102 | 4.6 | 22.3 | 54.5 | 55 |
| *Phoenix canariensis* – *Washingtonia robusta* | no | Plantae | 31 | 0.6 | 55.8 | 51.8 | 21 |
| *Limacia clavigera* – *Okenia nodosa* | no | Mollusca | 75 | 2.8 | 26.7 | 49.1 | 15 |
| *Chamelea striatula* – *Donax vittatus* | no | Mollusca | 80 | 4.0 | 19.8 | 45.4 | 57 |
| *Okenia nodosa* – *Polycera quadrilineata* | no | Mollusca | 38 | 0.9 | 41.0 | 44.1 | 8 |
| *Candiella lineata* – *Limacia clavigera* | no | Mollusca | 35 | 0.7 | 48.5 | 41.6 | 9 |
| *Nembrotha cristata* – *Nembrotha milleri* | sí | Mollusca | 76 | 6.3 | 12.2 | 40.7 | 57 |
| *Clibanarius aequabilis* – *Columbella adansoni* | no | Malacostraca / Mollusca | 34 | 1.1 | 32.2 | 38.8 | 30 |
| *Archidoris pseudoargus* – *Limacia clavigera* | no | Mollusca | 43 | 3.2 | 13.2 | 37.0 | 10 |
| *Sambucus nigra* – *Urtica dioica* | no | Plantae | 55 | 2.9 | 18.8 | 35.1 | 52 |
| *Sargassum muticum* – *Zostera marina* | no |  / Plantae | 37 | 1.3 | 27.7 | 34.6 | 29 |
| *Chthamalus stellatus* – *Tectarius striatus* | no | Crustacea / Mollusca | 44 | 2.4 | 18.4 | 34.4 | 34 |
| *Chthamalus stellatus* – *Clibanarius aequabilis* | no | Crustacea / Malacostraca | 38 | 1.8 | 20.9 | 33.2 | 32 |
| *Donax vittatus* – *Spisula subtruncata* | no | Mollusca | 20 | 0.4 | 53.1 | 33.1 | 14 |
| *Donax vittatus* – *Lutraria lutraria* | no | Mollusca | 50 | 2.9 | 17.3 | 32.1 | 35 |
| *Flexopecten glaber* – *Tritia nitida* | no | Mollusca | 18 | 0.4 | 47.3 | 30.5 | 5 |
| *Acanthurus dussumieri* – *Arothron hispidus* | no | Actinopterygii | 11 | 0.1 | 72.6 | 28.4 | 10 |
| *Solatopupa similis* – *Zonites algirus* | no | Mollusca | 18 | 0.8 | 22.1 | 26.7 | 12 |
| *Echium vulgare* – *Hypericum perforatum* | no | Plantae | 19 | 0.7 | 27.1 | 25.9 | 14 |
| *Cochlicella acuta* – *Trochoidea elegans* | no | Mollusca | 32 | 2.4 | 13.2 | 25.7 | 25 |
| *Helicodonta obvoluta* – *Solatopupa similis* | no | Mollusca | 14 | 0.8 | 17.7 | 25.3 | 6 |
| *Clibanarius aequabilis* – *Tectarius striatus* | no | Malacostraca / Mollusca | 28 | 1.8 | 15.7 | 24.4 | 24 |
| *Limacia clavigera* – *Trapania lineata* | no | Mollusca | 15 | 0.5 | 28.9 | 24.0 | 7 |
| *Chamelea striatula* – *Mactra stultorum* | no | Mollusca | 13 | 0.7 | 19.1 | 23.8 | 13 |
| *Solatopupa similis* – *Xerosecta cespitum* | no | Mollusca | 16 | 0.8 | 19.6 | 23.6 | 9 |
| *Chthamalus stellatus* – *Columbella adansoni* | no | Crustacea / Mollusca | 21 | 1.1 | 19.9 | 23.5 | 19 |
| *Acanthurus dussumieri* – *Cephalopholis miniata* | no | Actinopterygii | 9 | 0.1 | 59.4 | 23.1 | 9 |
| *Rocellaria dubia* – *Vermetus triquetrus* | no | Mollusca | 83 | 16.5 | 5.0 | 23.1 | 11 |
| *Donax vittatus* – *Turritellinella tricarinata* | no | Mollusca | 26 | 1.9 | 13.6 | 22.5 | 16 |

<figure class="fig"><img src="material/figuras/supl_S1_distribucion_efecto.png" alt="Figura S1. Distribución del tamaño de efecto. Razón entre ev"><figcaption><b>Figura S1. Distribución del tamaño de efecto.</b> Razón entre eventos observados y esperados por el esfuerzo local, para las parejas con q ≤ 0,05 (gris) y las replicadas (azul); escala logarítmica en ambos ejes y líneas en 2, 3, 5 y 10. Una gran parte de las parejas significativas tiene razones bajas.</figcaption></figure>
<figure class="fig"><img src="material/figuras/supl_S2_soporte_vs_efecto.png" alt="Figura S2. Soporte frente a efecto en las parejas replicadas"><figcaption><b>Figura S2. Soporte frente a efecto en las parejas replicadas.</b> Cada punto es una pareja: eventos con ambas especies (n) frente a razón observado/esperado, coloreado por observadores distintos; la línea roja marca razón 3.</figcaption></figure>

**Láminas fotográficas** (`LAMINAS_latest.pdf`): las mismas láminas que la sección 3.3, con atribución completa.
