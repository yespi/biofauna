# Origen nativo y vías de expansión — especie por especie

**Generado:** 2026-10-10 ~16:45 CEST (HanSolo / Cursor, orden Robotin–Gustavo).  
**Datos:** solo `SELECT` en `public_observations` (BioQuest / BD `fauna`) + series iNat/Minka ya publicadas en `presencia_cat_es.csv`.  
**Figuras:** [`figuras/expansion/`](figuras/expansion/). CSV: [`primera_obs_regiones_bq.csv`](primera_obs_regiones_bq.csv), [`tabla_origen_vias_resumen.csv`](tabla_origen_vias_resumen.csv).

**Convención.** Lo confirmado cita DOI verificados en Crossref (10-oct-2026). Lo no respaldado se marca explícitamente como **hipótesis**. Las «primeras citas» de ciencia ciudadana (iNat/BioQuest) **no** sustituyen el primer registro oficial de la literatura; se contrastan.

**Cajas geográficas (proxy):** Mediterráneo lat 30–46,5 / lng −6,5–37,5; España lat 36–44 / lng −10–5; Cataluña lat 40,45–42,95 / lng 0,1–3,4 (misma caja del paper).

---

## 1. Marco de vías (Mediterráneo)

Los inventarios de Zenetos y la infraestructura ELNAIS/EASIN documentan que el Mediterráneo es un hotspot de introducciones, con el **canal de Suez** (migración lessepsiana), el **transporte marítimo** (agua de lastre e incrustaciones) y la **acuicultura / acuariofilia** como vías dominantes, moduladas por el calentamiento ([Zenetos et al. 2005](https://doi.org/10.12681/mms.186); [Streftaris & Zenetos 2006](https://doi.org/10.12681/mms.180); [Katsanevakis et al. 2013 ELNAIS–EASIN](https://doi.org/10.12681/mms.362); [Katsanevakis et al. 2013 pathways](https://doi.org/10.1016/j.ocecoaman.2013.02.024); [Katsanevakis et al. 2014](https://doi.org/10.3389/fmars.2014.00032); [Galil et al. 2014](https://doi.org/10.1007/s10530-014-0778-y)). En Cataluña, García, Weitzmann y colaboradores sintetizan distribución e impacto en bentos ([García et al. 2015](https://doi.org/10.1007/698_2015_411)).

---

## 2. Caso especial — *Pterois miles* (pez león)

### 2.1 Bibliografía (vía confirmada)

- **Origen nativo:** Indo-Pacífico / Mar Rojo (complejo *Pterois miles*).
- **Vía principal al Mediterráneo:** migración **lessepsiana** por el canal de Suez. Primera cita mediterránea en **Israel, 1991** ([Golani & Sonin 1992](https://doi.org/10.1007/bf02906001)).
- **Expansión fuerte:** reaparición / establecimiento en Líbano y entorno oriental, y oleada posterior hacia Chipre y Egeo ([Bariche et al. 2013](https://doi.org/10.12681/mms.470); [Kletou et al. 2016](https://doi.org/10.1186/s41200-016-0065-y); [Azzurro & Bariche 2017](https://doi.org/10.1071/mf16358)).
- **Genética:** origen del linaje mediterráneo coherente con Mar Rojo / Indo-Pacífico occidental, no con la invasión atlántica de *P. volitans* ([Bariche et al. 2017](https://doi.org/10.1038/s41598-017-07326-1); genómica reciente [Bernardi et al. 2024](https://doi.org/10.1002/ece3.11087)).
- **Acuariofilia:** **hipótesis secundaria** (posible contribución local), no la explicación mayoritaria frente a Suez + genética.
- **Agua de lastre:** **hipótesis no respaldada** como vía principal; el patrón espacio-temporal y genético apunta a Suez.

### 2.2 Qué muestran nuestros datos (BioQuest)

| Indicador | Valor en `public_observations` (taxon_id 123459) |
|---|---|
| n total | 1.663 |
| n en caja Med | 895 |
| n España / Cataluña | **0 / 0** |
| Primera fila global | **2000-10**, lat 27,96 / lng 34,42 → **Mar Rojo** (fuera del Med) |
| Primera en caja Med | **2015-08**, costa israelí (32,10 / 34,77) |
| Frente | 2000–2014 casi solo Mar Rojo; desde ~2016–2017 aparece Egeo/Chipre; hacia 2020–2025 el centro Med (Italia/Jónico) gana peso; **sin** España |

Figuras: [`figuras/expansion/expansion_5y_Pterois_miles.png`](figuras/expansion/expansion_5y_Pterois_miles.png), [`pterois_miles_longitud_vs_ano.png`](figuras/expansion/pterois_miles_longitud_vs_ano.png).

### 2.3 Contraste con la lectura de los mapas (~2008 + lastre)

Gustavo observa en los mapas animados una «entrada» hacia **~2008** desde el Mar Rojo y sugiere **agua de lastre**. Nuestros puntos sí muestran un **nube densa en Mar Rojo desde ~2005–2010** y un salto mediterráneo visible en ciencia ciudadana **después de 2015**, no en 1991.

**Por qué difieren de la bibliografía (sin contradecirla):**

1. **Sesgo temporal de iNat/Minka:** casi no hay observaciones ciudadanas antes de ~2000–2008; el registro oficial de 1991 no está en la BD.
2. **Cobertura geográfica:** el sync Academy descarga el taxon, pero los buceadores/fotógrafos activos en BioQuest están sesgados a zonas con apps; Israel/Líbano/Chipre entran tarde y de forma irregular.
3. **El «frente 2008» en el mapa** es sobre todo **presencia nativa / Mar Rojo fotografiada**, no la primera invasión mediterránea.
4. Por tanto, inferir **lastre** desde ese patrón es **hipótesis visual no confirmada**; la literatura y la genética siguen apuntando a **Suez / lessepsiana**.

*Academy* (`academy_invasive`) ya etiqueta vector `suez` / «Migración lessepsiana» para este taxon — coherente con la bibliografía, no con lastre.

---

## 3. Exóticas marinas principales (Weitzmann + Academy)

### 3.1 *Caulerpa cylindracea*

| Campo | Contenido |
|---|---|
| Origen | Indo-Pacífico |
| Vía | Transporte marítimo (lastre / fragmentos en cascos) — alineado con `academy_invasive` (`lastre`) y revisiones de vías ([Katsanevakis et al. 2013](https://doi.org/10.1016/j.ocecoaman.2013.02.024)). Fenología/expansión NW Med: [Capiomont et al. 2005](https://doi.org/10.1515/bot.2005.006); [Ruitton et al. 2005](https://doi.org/10.1016/j.aquabot.2005.02.008). |
| 1ª cita Med (lit.) | Década 1990 como *C. racemosa* var. *cylindracea* (inventarios Zenetos); no re-fechamos aquí el primer paper. |
| BioQuest | Med **2005-07**; ES/CAT **2014-08** (n CAT 402) |
| iNat CAT (paper) | 2014-11-11 |
| Frente / velocidad | De Cerdeña/Córcega (~2005–2013 en BQ) a Cataluña **2014**; luego densificación 2021–2025 (mapa 5 años). |
| Causas | Fragmentación vegetativa, sustratos perturbados, calentamiento (**hipótesis** coadyuvante). |
| Figura | [`expansion_5y_Caulerpa_cylindracea.png`](figuras/expansion/expansion_5y_Caulerpa_cylindracea.png) |

### 3.2 *Caulerpa taxifolia*

| Campo | Contenido |
|---|---|
| Origen | Tropical; cepa mediterránea de acuario |
| Vía | **Acuariofilia** (liberación / escape) — evidencia molecular ([Jousson et al. 1998](https://doi.org/10.3354/meps172275)). |
| BioQuest / iNat CAT | **0** obs place Catalunya a 10-oct-2026 (ver §11 `RESULTADOS_v1.md`) |
| Tendencia CAT | Ausente en nuestras fuentes ciudadanas; no inventamos citas locales. |

### 3.3 *Oculina patagonica*

| Campo | Contenido |
|---|---|
| Origen | Atlántico SW (patagonia / templado); criptogénica en debates antiguos |
| Vía | Históricamente asociada a **transporte marítimo / estructuras**; expansión norte favorecida por **calentamiento y sustratos artificiales** ([Zibrowius 1974](https://doi.org/10.1007/bf01611381); [Serrano et al. 2013](https://doi.org/10.1371/journal.pone.0052739)). |
| BioQuest | Med/ES **2010-09** (Alicante ~38,5 / −0,13); CAT **2011-08** (n CAT 1.289) |
| Frente | Norteada a lo largo de la costa ibérica; Cataluña ya densa en BQ 2014–2026. |
| Causas | Calentamiento, puertos y diques (Serrano et al. 2013). |
| Figura | [`expansion_5y_Oculina_patagonica.png`](figuras/expansion/expansion_5y_Oculina_patagonica.png) |

### 3.4 *Lagocephalus sceleratus*

| Campo | Contenido |
|---|---|
| Origen | Mar Rojo / Indo-Pacífico |
| Vía | **Lessepsiana (Suez)** ([Kasapidis 2007](https://doi.org/10.3391/ai.2007.2.1.9); `academy_invasive` `suez`). |
| BioQuest | Primera Med **2005-06** (Egeo); **0** ES/CAT. Primera fila global 1985 (fuera / dudosa geográficamente — no usar como 1ª Med). |
| Frente | Este → centro Med en series BQ; sin costa española en la BD. |
| Causas | Suez + calentamiento / nicho de depredador (**hipótesis**). |
| Figura | [`expansion_5y_Lagocephalus_sceleratus.png`](figuras/expansion/expansion_5y_Lagocephalus_sceleratus.png) |

### 3.5 *Asparagopsis armata*

| Campo | Contenido |
|---|---|
| Origen | Hemisferio sur (Australia / NZ) |
| Vía | **Incrustación / transporte marítimo** (fouling) — patrón clásico de macrófitos alienígenas ([Katsanevakis et al. 2013](https://doi.org/10.1016/j.ocecoaman.2013.02.024); genética [Andreakis et al. 2004](https://doi.org/10.1080/0967026042000236436)). |
| BioQuest | Med/ES/CAT **2008-04** (n CAT 209) |
| Frente | Ya presente en CAT en la primera ventana con datos; densificación posterior. |
| Figura | [`expansion_5y_Asparagopsis_armata.png`](figuras/expansion/expansion_5y_Asparagopsis_armata.png) |

### 3.6 *Callinectes sapidus*

| Campo | Contenido |
|---|---|
| Origen | Atlántico oeste |
| Vía | **Agua de lastre** (vía típica de cangrejo azul; [Katsanevakis et al. 2013](https://doi.org/10.1016/j.ocecoaman.2013.02.024)). Primera cita Segura/España: [González-Wangüemert & Pujol 2016](https://doi.org/10.3906/zoo-1511-23). |
| BioQuest | Med/ES/CAT **2017-11** (Barcelona; n CAT 216) |
| Frente | Foco NE peninsular / deltas; expansión costera reciente. |
| Causas | Puertos, estuarios, calentamiento (**hipótesis** coadyuvante). |
| Figura | [`expansion_5y_Callinectes_sapidus.png`](figuras/expansion/expansion_5y_Callinectes_sapidus.png) |

### 3.7 *Rugulopteryx okamurae*

| Campo | Contenido |
|---|---|
| Origen | Pacífico NW (Japón/Corea) |
| Vía | **Transporte marítimo** (estrecho de Gibraltar; impacto extremo [García-Gómez et al. 2020](https://doi.org/10.1016/j.scitotenv.2019.135408)); avance este [Bottalico et al. 2024](https://doi.org/10.12681/mms.36947). |
| Datos paper | iNat ES **2019-08-16**; iNat CAT **2024-05-31** (101 obs); **no** en `public_observations` Academy (0 filas por nombre). |
| Frente | Gibraltar / Andalucía → este Med; Cataluña en fase reciente (ciudadana). |
| Causas | Fouling, competencia agresiva, posibles condiciones térmicas favorables (**hipótesis**). |

### 3.8 *Bursatella leachii*

| Campo | Contenido |
|---|---|
| Origen | Circuntropical / Indo-Pacífico |
| Vía | **Lessepsiana** (citada como migrante; p. ej. [Özvarol 2014](https://doi.org/10.3153/jfscom.201435)). |
| Datos paper | iNat CAT **2007-10-26**; BF galería **2013-10-06** |
| Causas | Suez + calentamiento (**hipótesis**). |

### 3.9 *Codium fragile* / *Magallana gigas*

| Especie | Origen | Vía | BQ 1ª Med / ES / CAT | Notas |
|---|---|---|---|---|
| *Codium fragile* | Pacífico NW | Fouling / acuicultura | 2010-08 / 2010-08 / 2010-08 | n CAT bajo (14) |
| *Magallana gigas* | Pacífico NW | **Acuicultura** | 1999-11 / 1999-11 / 2018-04 | Vector Academy «desconocido»; literatura general = ostricultura |

### 3.10 Otras Weitzmann (breve)

| Especie | Origen | Vía (lit. / hipótesis) | Datos nuestros |
|---|---|---|---|
| *Fistularia commersonii* | Mar Rojo | Lessepsiana ([Tenggardjaja et al. 2013](https://doi.org/10.1080/15659801.2013.898402)) | Sin filas BQ en este extracto |
| *Siganus luridus* / *S. rivulatus* | Mar Rojo | Lessepsiana ([Stergiou 1988](https://doi.org/10.1111/j.1095-8649.1988.tb05497.x); [Castriota & Andaloro 2008](https://doi.org/10.1017/s1755267205001223)) | Sin filas BQ |
| *Percnon gibbesi* | Atlántico | Shipping / fouling (**hipótesis** dominante en revisiones) | Sin filas BQ |
| *Halophila stipulacea* | Mar Rojo | Lessepsiana | Sin filas BQ |
| *Mnemiopsis leidyi* | Atlántico | **Lastre** (clásico) | Sin filas BQ |
| *Zebrasoma flavescens* / *Balistoides conspicillum* | Indo-Pacífico | **Acuariofilia** | iNat CAT 2008 / 2018; 0 BF |

Mapas multiespecie: [`expansion_multiespecie_2010-2014.png`](figuras/expansion/expansion_multiespecie_2010-2014.png) · [`2015-2019`](figuras/expansion/expansion_multiespecie_2015-2019.png) · [`2020-2024`](figuras/expansion/expansion_multiespecie_2020-2024.png).

---

## 4. Lista UE — especies con presencia en Cataluña (top y establecidas)

Para terrestres/dulceacuícolas, BioQuest Academy **casi no** tiene filas (salvo *Neogale*, *Trachemys*). Las primeras fechas CAT/ES son las de `presencia_cat_es.csv` (iNat/Minka). Orígenes/vías: literatura + `academy_invasive` cuando existe.

### 4.1 Terrestres

| Especie | Origen | Vía | 1ª CAT (ciudadana) | 1ª ES | Tendencia | Causa / fuente |
|---|---|---|---|---|---|---|
| *Ailanthus altissima* | China / Asia E | Ornamental / vías y suelos perturbados | 2008-06-08 | 2002-05-29 | en_expansion | Ornamental histórica; **hipótesis** facilitada por bordes urbanos |
| *Myocastor coypus* | Sudamérica | Peletería / escapes | 2012-06-25 | 2012-06-25 | establecida | [Bertolino CABI 2008](https://doi.org/10.1079/cabicompendium.73537) (ficha); escapes |
| *Broussonetia papyrifera* | Asia E | Ornamental | 2017-06-09 | 2016-04-15 | establecida | Ornamental; **hipótesis** |
| *Alopochen aegyptiaca* | África | Ornamental / escapes | 2010-04-16 | 2002-11-30 | establecida | Aves de colección; **hipótesis** |
| *Vespa velutina nigrithorax* | Asia SE | Comercio hortícola / accidental (Francia → Iberia) | 2017-11-22 | 2015-11-20 | en_expansion | [Monceau et al. 2013](https://doi.org/10.1007/s10340-013-0537-3) |
| *Neogale vison* | Norteamérica | Escapes granjas peleteras | 2010-08-08 | 2010-08-08 | establecida | `academy_invasive`; BQ CAT desde 2010 |
| *Pennisetum setaceum* | África | Ornamental | 2016-01-20 | 2000-09-06 | en_expansion | Jardinería; **hipótesis** |
| *Delairea odorata* | Sudáfrica | Ornamental | 2009-12-29 | 2009-05-15 | en_expansion | Jardinería; **hipótesis** |
| *Acacia saligna* | Australia | Forestación / ornamental | 2019-07-08 | 2006-02-13 | en_expansion | Plantaciones; **hipótesis** |
| *Obama nungara* | Argentina | Comercio de plantas | 2016-02-29 | 2016-02-29 | establecida | [Justine et al. 2020](https://doi.org/10.7717/peerj.8385) |
| *Threskiornis aethiopicus* | África | Zoos / escapes | 2005-03-25 | 2004-04-15 | establecida | Escapes; **hipótesis** |
| *Reynoutria japonica* | Asia E | Ornamental | 2018-07-20 | 2008-09-24 | establecida | Jardinería histórica; **hipótesis** |
| *Impatiens glandulifera* | Himalaya | Ornamental / ríos | 2022-08-21 | 2019-08-15 | en_expansion | Dispersión fluvial; **hipótesis** |

### 4.2 Agua dulce

| Especie | Origen | Vía | 1ª CAT | 1ª ES | Tendencia | Causa / fuente |
|---|---|---|---|---|---|---|
| *Procambarus clarkii* | Norteamérica | **Acuicultura** / arrozales | 2001-09-23 | 1990-09-01 | establecida | [Gherardi & Barbaresi 2000](https://doi.org/10.1127/archiv-hydrobiol/150/2000/153); [Rodríguez et al. 2003](https://doi.org/10.1023/b:hydr.0000008626.07042.87) |
| *Trachemys scripta elegans* | Norteamérica | **Mascotas** (liberación) | 2006-05-06 | 2004-03-20 | establecida | `academy_invasive`; BQ (*T. scripta*) CAT desde 1994-05 |
| *Gambusia holbrooki* | Norteamérica | Control biológico de mosquitos | 2007-07-13 | 2007-07-13 | en_expansion | Introducciones oficiales históricas; **hipótesis** detallada local |
| *Ludwigia peploides* | América | Ornamental acuática | 2009-08-02 | 2009-08-02 | en_expansion | Acuariofilia / estanques; **hipótesis** |
| *Lepomis gibbosus* | Norteamérica | Acuicultura / pesca | 2003-07-21 | 2003-07-21 | establecida | Introducciones deportivas; **hipótesis** |
| *Pacifastacus leniusculus* | Norteamérica | Acuicultura / cangrejería | 2018-08-27 | 2006-02-26 | establecida | Introducciones; **hipótesis** |

### 4.3 Marina UE

| Especie | Origen | Vía | 1ª CAT | 1ª ES | Tendencia | Fuente |
|---|---|---|---|---|---|---|
| *Rugulopteryx okamurae* | Pacífico NW | Shipping / fouling | 2024-05-31 | 2019-08-16 | en_expansion | [García-Gómez et al. 2020](https://doi.org/10.1016/j.scitotenv.2019.135408) |

---

## 5. Tabla resumen (ver CSV)

Archivo: [`tabla_origen_vias_resumen.csv`](tabla_origen_vias_resumen.csv) — columnas: `especie | origen | via | primera_med_lit_o_bq | primera_es | primera_cat | tendencia | causa | fuente_o_hipotesis`.

---

## 6. Referencias (DOI verificados Crossref, 10-oct-2026)

Solo se listan DOI que devolvieron metadatos válidos en `api.crossref.org/works/{doi}`.

1. Golani, D. & Sonin, O. (1992). https://doi.org/10.1007/bf02906001  
2. Bariche, M., Torres, M. & Azzurro, E. (2013). https://doi.org/10.12681/mms.470  
3. Kletou, D., Hall-Spencer, J.M. & Kleitou, P. (2016). https://doi.org/10.1186/s41200-016-0065-y  
4. Bariche, M. et al. (2017). https://doi.org/10.1038/s41598-017-07326-1  
5. Azzurro, E. & Bariche, M. (2017). https://doi.org/10.1071/mf16358  
6. Bernardi, G. et al. (2024). https://doi.org/10.1002/ece3.11087  
7. Poursanidis, D. et al. (2020). https://doi.org/10.1016/j.marpolbul.2020.111054  
8. Zenetos, A. et al. (2005). https://doi.org/10.12681/mms.186  
9. Streftaris, N. & Zenetos, A. (2006). https://doi.org/10.12681/mms.180  
10. Zenetos, A. (2010). https://doi.org/10.1007/s10530-009-9679-x  
11. Katsanevakis, S. et al. (2013). ELNAIS meets EASIN. https://doi.org/10.12681/mms.362  
12. Katsanevakis, S. et al. (2013). Pathways. https://doi.org/10.1016/j.ocecoaman.2013.02.024  
13. Katsanevakis, S. et al. (2014). https://doi.org/10.3389/fmars.2014.00032  
14. Katsanevakis, S. et al. (2014). Impacts pan-European. https://doi.org/10.3391/ai.2014.9.4.01  
15. Galil, B.S. et al. (2014). https://doi.org/10.1007/s10530-014-0778-y  
16. García, M., Weitzmann, B. et al. (2015). https://doi.org/10.1007/698_2015_411  
17. Serrano, E. et al. (2013). https://doi.org/10.1371/journal.pone.0052739  
18. Azzurro, E. et al. (2022). ClimateFish. https://doi.org/10.3389/fmars.2022.910887  
19. Jousson, O. et al. (1998). https://doi.org/10.3354/meps172275  
20. Capiomont, A. et al. (2005). https://doi.org/10.1515/bot.2005.006  
21. Ruitton, S. et al. (2005). https://doi.org/10.1016/j.aquabot.2005.02.008  
22. Zibrowius, H. (1974). https://doi.org/10.1007/bf01611381  
23. Kasapidis, P. et al. (2007). https://doi.org/10.3391/ai.2007.2.1.9  
24. García-Gómez, J.C. et al. (2020). https://doi.org/10.1016/j.scitotenv.2019.135408  
25. Bottalico, A. et al. (2024). https://doi.org/10.12681/mms.36947  
26. González-Wangüemert, M. & Pujol, J.A. (2016). https://doi.org/10.3906/zoo-1511-23  
27. Andreakis, N. et al. (2004). https://doi.org/10.1080/0967026042000236436  
28. Özvarol, Y. (2014). https://doi.org/10.3153/jfscom.201435  
29. Tenggardjaja, K. et al. (2013). https://doi.org/10.1080/15659801.2013.898402  
30. Stergiou, K.I. (1988). https://doi.org/10.1111/j.1095-8649.1988.tb05497.x  
31. Castriota, L. & Andaloro, F. (2008). https://doi.org/10.1017/s1755267205001223  
32. Gherardi, F. & Barbaresi, S. (2000). https://doi.org/10.1127/archiv-hydrobiol/150/2000/153  
33. Rodríguez, C.F. et al. (2003). https://doi.org/10.1023/b:hydr.0000008626.07042.87  
34. Monceau, K. et al. (2013). https://doi.org/10.1007/s10340-013-0537-3  
35. Justine, J.-L. et al. (2020). https://doi.org/10.7717/peerj.8385  

**No usados como prueba** (sin DOI Crossref válido en esta sesión): fichas CABI cuando solo aportan contexto general; AquaNIS/EASIN como portales (sin DOI de dataset citado aquí).

---

## 7. Limitaciones

1. BioQuest no cubre la lista UE completa → muchas series de expansión espacial solo existen vía iNat place, no como secuencia lat/lng en `public_observations`.  
2. Primera observación ciudadana ≠ primer registro oficial.  
3. Esfuerzo 2013→2024 infla densidades recientes (ver §9–10 de `RESULTADOS_v1.md`).  
4. Caja CAT ≠ Cataluña administrativa.
