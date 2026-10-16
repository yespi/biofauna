# Tabla S5. GLMM de tendencias (GBIF-iNaturalist RG, Cataluña GADM, ventana 2013–2025)

Modelo Poisson con intercepto aleatorio de observador (§2.5); offset = log(registros del observador en el grupo taxonómico de la especie, excluidos los de la propia especie). FDR Benjamini–Hochberg sobre las 13 especies estimables (≥10 obs y ≥5 años con registro en GBIF). Script: `material/p2_glmm_observador_20261016.py`.

| Especie | Grupo | n GBIF | Años con obs. | Observ. | RR anual | IC 95 % | q | Clase | RR sin top-3 | q sin top-3 | Clase sin top-3 |
|---|---|---:|---:|---:|---:|---|---:|---|---:|---:|---|
| *Acacia mearnsii* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Acacia saligna* | Plantas | 18 | 4 | 16 | — | — | — | no estimable | — | — | — |
| *Acridotheres cristatellus* | Aves | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Acridotheres tristis* | Aves | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Ailanthus altissima* | Plantas | 847 | 11 | 276 | 0,929 | 0,849–1,017 | 0,1836 | sin_tendencia_significativa | 0,913 | 0,0660 | sin_tendencia_significativa |
| *Alopochen aegyptiaca* | Aves | 87 | 12 | 48 | 0,989 | 0,901–1,084 | 0,8667 | sin_tendencia_significativa | 0,966 | 0,5610 | sin_tendencia_significativa |
| *Alternanthera philoxeroides* | Plantas | 1 | 1 | 1 | — | — | — | no estimable | — | — | — |
| *Ameiurus melas* | Peces | 1 | 1 | 1 | — | — | — | no estimable | — | — | — |
| *Andropogon virginicus* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Arthurdendyus triangulatus* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Asclepias syriaca* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Asterias amurensis* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Axis axis* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Baccharis halimifolia* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Bipalium kewense* | Otros animales (invert. no insectos) | 2 | 2 | 2 | — | — | — | no estimable | — | — | — |
| *Brachyponera chinensis* | Insectos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Broussonetia papyrifera* | Plantas | 96 | 8 | 51 | 1,159 | 0,988–1,361 | 0,1312 | sin_tendencia_significativa | 1,199 | 0,0855 | sin_tendencia_significativa |
| *Cabomba caroliniana* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Callosciurus erythraeus* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Callosciurus finlaysonii* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Cardiospermum grandiflorum* | Plantas | 1 | 1 | 1 | — | — | — | no estimable | — | — | — |
| *Castor canadensis* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Celastrus orbiculatus* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Cervus nippon* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Channa argus* | Peces | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Cherax destructor* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Cipangopaludina chinensis* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Cortaderia jubata* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Corvus splendens* | Aves | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Crassula helmsii* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Delairea odorata* | Plantas | 66 | 7 | 31 | 1,058 | 0,879–1,274 | 0,6591 | sin_tendencia_significativa | 1,073 | 0,5610 | sin_tendencia_significativa |
| *Ehrharta calycina* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Eichhornia crassipes* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Elodea nuttallii* | Plantas | 2 | 1 | 1 | — | — | — | no estimable | — | — | — |
| *Eriocheir sinensis* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Faxonius immunis* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Faxonius rusticus* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Fundulus heteroclitus* | Peces | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Gambusia affinis* | Peces | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Gambusia holbrooki* | Peces | 73 | 9 | 46 | 1,236 | 1,052–1,453 | 0,0215 | creciente | 1,204 | 0,0671 | sin_tendencia_significativa |
| *Gunnera tinctoria* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Gymnocoronis spilanthoides* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Hakea sericea* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Heracleum mantegazzianum* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Heracleum persicum* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Heracleum sosnowskyi* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Herpestes javanicus* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Humulus scandens* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Hydrocotyle ranunculoides* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Impatiens glandulifera* | Plantas | 9 | 5 | 8 | — | — | — | no estimable | — | — | — |
| *Koenigia polystachya* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Lagarosiphon major* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Lampropeltis getula* | Herpetofauna | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Lepomis gibbosus* | Peces | 28 | 6 | 22 | 0,978 | 0,752–1,271 | 0,8667 | sin_tendencia_significativa | 1,154 | 0,4660 | sin_tendencia_significativa |
| *Lespedeza cuneata* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Limnoperna fortunei* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Lithobates catesbeianus* | Herpetofauna | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Ludwigia grandiflora* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Ludwigia peploides* | Plantas | 33 | 5 | 20 | 1,150 | 1,058–1,251 | 0,0035 | creciente | 1,110 | 0,0660 | sin_tendencia_significativa |
| *Lygodium japonicum* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Lysichiton americanus* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Marisa cornuarietis* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Microstegium vimineum* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Misgurnus anguillicaudatus* | Peces | 2 | 2 | 2 | — | — | — | no estimable | — | — | — |
| *Misgurnus bipartitus* | Peces | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Morone americana* | Peces | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Mulinia lateralis* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Muntiacus reevesi* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Myocastor coypus* | Mamíferos | 259 | 11 | 142 | 1,125 | 1,048–1,206 | 0,0035 | creciente | 1,120 | 0,0041 | creciente |
| *Myriophyllum aquaticum* | Plantas | 1 | 1 | 1 | — | — | — | no estimable | — | — | — |
| *Myriophyllum heterophyllum* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Nanozostera japonica* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Nasua nasua* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Neogale vison* | Mamíferos | 58 | 11 | 37 | 0,889 | 0,817–0,968 | 0,0168 | decreciente | 0,858 | 0,0013 | decreciente |
| *Nyctereutes procyonoides* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Obama nungara* | Otros animales (invert. no insectos) | 7 | 5 | 6 | — | — | — | no estimable | — | — | — |
| *Ondatra zibethicus* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Orconectes limosus* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Orconectes virilis* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Oxyura jamaicensis* | Aves | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Pacifastacus leniusculus* | Otros animales (invert. no insectos) | 21 | 7 | 15 | 1,071 | 0,851–1,348 | 0,6591 | sin_tendencia_significativa | 0,975 | 0,8027 | sin_tendencia_significativa |
| *Parthenium hysterophorus* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Pennisetum setaceum* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Perccottus glenii* | Peces | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Persicaria perfoliata* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Pistia stratiotes* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Platydemus manokwari* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Plotosus lineatus* | Peces | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Procambarus clarkii* | Otros animales (invert. no insectos) | 339 | 13 | 190 | 0,918 | 0,877–0,961 | 0,0016 | decreciente | 0,932 | 0,0463 | decreciente |
| *Procambarus virginalis* | Otros animales (invert. no insectos) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Procyon lotor* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Prosopis juliflora* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Pseudorasbora parva* | Peces | 2 | 2 | 2 | — | — | — | no estimable | — | — | — |
| *Pueraria montana var. lobata* | Otros (hongos, cromistas, etc.) | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Pycnonotus cafer* | Aves | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Pycnonotus jocosus* | Aves | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Reynoutria japonica* | Plantas | 5 | 4 | 4 | — | — | — | no estimable | — | — | — |
| *Reynoutria sachalinensis* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Reynoutria x bohemica* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Rugulopteryx okamurae* | Otros (hongos, cromistas, etc.) | 11 | 2 | 2 | — | — | — | no estimable | — | — | — |
| *Salvinia molesta* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Sciurus carolinensis* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Sciurus niger* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Solenopsis geminata* | Insectos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Solenopsis invicta* | Insectos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Solenopsis richteri* | Insectos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Tamias sibiricus* | Mamíferos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Threskiornis aethiopicus* | Aves | 7 | 4 | 7 | — | — | — | no estimable | — | — | — |
| *Trachemys scripta elegans* | Herpetofauna | 147 | 13 | 79 | 0,914 | 0,812–1,028 | 0,1911 | sin_tendencia_significativa | 0,957 | 0,4660 | sin_tendencia_significativa |
| *Triadica sebifera* | Plantas | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Vespa mandarinia* | Insectos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Vespa velutina nigrithorax* | Insectos | 96 | 6 | 57 | 1,358 | 1,181–1,562 | 0,0002 | creciente | 1,471 | 0,0001 | creciente |
| *Wasmannia auropunctata* | Insectos | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
| *Xenopus laevis* | Herpetofauna | 0 | 0 | 0 | — | — | — | no estimable | — | — | — |
