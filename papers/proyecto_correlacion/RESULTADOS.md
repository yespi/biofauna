# Proyecto Correlación — Resultados

## 1. Cifras globales

| métrica | valor |
|---|---:|
| Fotografías en la galería | 1.222.170 |
| Observaciones con geo+fecha (+hora 92 %) | 759.207 |
| Eventos (observador × 1 km × día × 3 h) con ≥2 especies | 60.211 |
| Pares de especies con soporte ≥8, ≥3 celdas y ≥3 días | **70.971** |
| Pares intra-familia | 1.118 (2 %) |
| Pares inter-familia | 69.853 (98 %) |

## 2. Validación interna (corregida con el filtro de observadores)

| asociación | n | obs. distintos | localidades | días | veredicto |
|---|---:|---:|---:|---:|---|
| ***Peltodoris atromaculata*** + ***Petrosia ficiformis*** | 79 | **32** | 44 | 74 | ✅ documentada, robusta |
| *Felimare picta* + *Ircinia oros* | 29 | **16** | 20 | 28 | ✅ documentada, robusta |
| *Cratena peregrina* + *Eudendrium racemosum* | 5 | **5** | — | — | ✅ consistente |
| ~~*Doto paulinae* + *Sertularella mediterranea*~~ | 5 | **1** | — | — | ❌ **descartada** (una sola salida; corrección tras revisión experta) |

> **Nota de honestidad:** en la primera versión incluí el par de *Doto* como "documentado". **No lo era**; era
> una suposición mía. Un especialista lo detectó al no reconocerlo en su experiencia de campo, y los datos le
> dieron la razón (un único observador). El método se corrigió (`METODOS.md` §4 bis) y ahora se exige
> **≥5 observadores distintos** por par.

## 3. Grupos taxonómicos más implicados (familias con más pares asociados)

| familia | pares | | familia | pares |
|---|---:|---|---|---:|
| Sparidae (sargos, doradas) | 4.063 | | Trochidae (caracolillos) | 1.682 |
| Blenniidae (blenios) | 3.834 | | Dictyotaceae (algas pardas) | 1.638 |
| Gobiidae (gobios) | 3.377 | | Facelinidae (nudibranquios) | 1.624 |
| Labridae (lubinas, julias) | 3.326 | | Serpulidae (gusanos tubícolas) | 1.590 |
| Lithophyllaceae (algas coralinas) | 2.810 | | Sabellidae | 1.472 |
| Didemnidae (ascidias) | 2.016 | | Irciniidae (esponjas) | 1.448 |
| Holothuriidae (pepinos de mar) | 1.784 | | Hymedesmiidae (esponjas) | 1.426 |
| Actiniidae (anémonas) | 1.717 | | | |

La mayoría de pares son **inter-familia** (98 %), coherente con asociaciones tróficas/de hábitat
(un animal y su sustrato o su presa) más que con simples cohortes de parientes.

## 4. Candidatas nuevas (con repetibilidad; pendientes de revisión experta)

| A | B | n | lift | celdas | días | lectura biológica plausible |
|---|---|---:|---:|---:|---:|---|
| *Blackfordia virginica* (medusa) | *Phronima sedentaria* | 19 | 653 | 6 | 15 | anfípodo hiperídeo **comensal de medusas** |
| *Crepidula unguiformis* | *Rissoa auriscalpium* | 17 | 618 | 10 | 17 | gasterópodos del mismo microhábitat |
| *Fustiaria rubescens* (escafópodo) | *Loripinus fragilis* (bivalvo) | 16 | 892 | 7 | 15 | fauna infaunal del mismo sedimento |
| *Doris fontainii* | *Tyrinna delicata* | 14 | 1.277 | 9 | 12 | dos nudibranquios del mismo sustrato |
| *Abra alba* | *Abra longicallus* | 9 | 534 | 7 | 9 | dos bivalvos infaunales |
| ***Lysmata grabhami*** (gamba limpiadora) | ***Telmatactis cricoides*** (anémona) | 9 | 547 | 7 | 8 | **simbiosis de limpieza** clásica |
| *Callianira bialata* | *Vanadis formosa* | 9 | 645 | 7 | 9 | dos ctenóforos de la misma masa de agua |
| *Macrorhynchia philippina* (hidrozoo) | *Telmatactis cricoides* | 8 | 765 | 5 | 6 | fondo duro colonizado |
| *Blackfordia virginica* | *Brachyscelus crusculum* | 9 | 1.129 | 4 | 8 | medusa + anfípodo |
| *Neoturris pileata* | *Sulculeolaria quadrivalvis* | 13 | 555 | 5 | 12 | plancton gelatinoso |
| *Eurythoe complanata* (poliqueto) | *Mauligobius maderensis* (gobio) | 9 | 556 | 7 | 9 | mismo microhábitat de fondo |
| *Crepidula unguiformis* | *Nucula nucleus* | 8 | 515 | 7 | 8 | fauna de sedimento |

La lista completa (top 40 con familia y métricas) está en
[`coocurrencia_top40.md`](../../docker/biofauna/artifacts/coocurrencia_top40.md)¹ y los **70.971 pares** en
`artifacts/coocurrencia_catalogo_20260928.json`.

> ¹ En el repositorio público se incluye una copia en `papers/proyecto_correlacion/`.

## 4 bis. Candidatas con el filtro de **≥5 observadores distintos**

| A | B | n | obs. distintos | lift | lectura plausible |
|---|---:|---:|---:|---:|---|
| *Latreutes fucorum* (gamba del sargazo) | *Scyllaea pelagica* (nudibranquio del sargazo) | 11 | **10** | 344 | **comunidad del alga flotante *Sargassum*** |
| *Hippolyte coerulescens* | *Scyllaea pelagica* | 6 | 6 | 688 | idem (fauna asociada al sargazo) |
| *Doris fontainii* | *Tyrinna delicata* | 14 | 6 | 1.243 | nudibranquios del mismo sustrato |
| *Lysmata grabhami* (gamba limpiadora) | *Telmatactis cricoides* (anémona) | 9 | 6 | 594 | simbiosis de limpieza |
| *Macrorhynchia philippina* (hidrozoo) | *Telmatactis cricoides* | 8 | 6 | 774 | fondo duro colonizado |
| *Callianira bialata* | *Nanomia bijuga* | 13 | 6 | 389 | plancton gelatinoso |
| *Hippolyte coerulescens* | *Latreutes fucorum* | 5 | 5 | 396 | fauna del sargazo |
| *Leptogorgia ruberrima* | *Leptogorgia viminalis* | 6 | 5 | 754 | gorgonias simpátricas |
| *Abudefduf saxatilis* | *Kyphosus vaigiensis* | 8 | 8 | 445 | peces de arrecife |

## 4 ter. Verificación bibliográfica (28-sep-2026)

Cada par se clasifica tras revisar la literatura pública (WoRMS, Sea Slug Forum, FishBase,
JNCC/MarLIN, revistas revisadas por pares). **Nota metodológica:** la co-ocurrencia en *eventos* de
ciudadanos incluye observaciones de **todo el mundo** (no solo Mediterráneo); los pares cuyas especies
son de otros reinos/océanos suelen ser **fotos de viajes de buceo** (mismo grupo, misma inmersión) y se
marcan como *artefacto*, no como asociación ecológica válida del área de estudio.

### ✅ Documentadas (la literatura describe la interacción)

| A | B | n | obs. | interacción documentada | fuentes |
|---|---|---:|---:|---|---|
| *Peltodoris atromaculata* | *Petrosia ficiformis* | 79 | 32 | **predación**: el nudibranquio se alimenta de esa esponja (petroformynas como defensa) | literatura trófica de doridáceos |
| *Felimare picta* | *Ircinia* spp. | 29 | 16 | **dieta** del nudibranquio sobre esponjas del género *Ircinia* (y *Dysidea*) | McDonald & Nybakken 2001; OPK |
| *Cratena peregrina* | *Eudendrium racemosum* | 5 | 5 | **kleptopredación**: C. peregrina roba presas al hidrozoo | CNR (Di Camillo et al.) |
| *Latreutes fucorum* / *Hippolyte coerulescens* | *Scyllaea pelagica* | 11 | 10 | **comunidad del *Sargassum*** flotante (gambas y nudibranquio asociados al alga) | NOAA/Sargassum fauna; BAMZ |
| *Doto coronata* | *Sertularella gayi* | — | — | hidroides del género *Sertularella* como presa de *Doto* | literatura de Dotidae |
| *Phronima sedentaria* | salpas/zooplancton gelatinoso | 19 | — | **simbionte obligado** de salpas (barrica) y otros gelatinosos | Laval 1978; Diebel 1988; MBARI |
| *Lampea pancerina* | salpas | 12 | — | **depredador/parásito de salpas** (doble vida) | literature ctenóforos |

### 🟡 Plausibles (ecológicamente coherentes; no hay cita directa de la pareja)

| A | B | n | obs. | argumento |
|---|---|---:|---:|---|
| *Lysmata grabhami* | *Telmatactis cricoides* | 9 | 6 | *T. cricoides* hospeda **crustáceos simbiontes documentados** (*Thor amboinensis*, 65 % de anémonas; *Stenorhynchus lanceolatus*, mutualismo facultativo); las *Lysmata* son gambas limpiadoras. Co-ocurren real en **Canarias/Madeira** (territorio español). |
| *Callianira bialata* | *Vanadis formosa* / ctenóforos | 9 | 6 | ctenóforos y poliquetos alciópidos pelágicos de la misma masa de agua; gremio depredador planctónico (coexistencia). |
| *Blackfordia virginica* | *Phronima sedentaria* / *Brachyscelus crusculum* | 19 | — | los **hiperídeos se asocian a gelatinosos** (medusas incluidas); *Phronima* es el simbionte más común de salpas, *Brachyscelus* es hiperídeo comensal típico de medusas. Sin cita *Blackfordia*-específica. |
| *Abra alba* | *Abra longicallus* | 9 | — | **comunidades de *Abra*** en sedimentos blandos circalitorales (biotopo JNCC «Abra alba & Nucula nitidosa»); coexistencia de bivalvos infaunales del mismo género. |
| *Fustiaria rubescens* | *Loripinus fragilis* | 16 | — | **infauna del mismo sedimento**; *Loripinus* (Lucinidae) vive en sedimentos reducidos con simbiontes quimiosintéticos. |
| *Macrorhynchia philippina* | *Telmatactis cricoides* | 8 | 6 | **fondo duro esciáfilo compartido** (hábitat, no interacción); ambas especies termófilas en expansión en el Mediterráneo/Atlántico NE. |

### ❌ Descartadas / artefacto (especies de otros océanos → fotos de viaje)

| A | B | n | obs. | motivo |
|---|---|---:|---:|---|
| *Doris fontainii* + *Tyrinna delicata* | — | 14 | 6 | ambas son del **Pacífico sur** (lat −12 a −55; Chile/Perú/Argentina), no del Mediterráneo: co-ocurrencia por viaje de buceo, no por ecología del área de estudio. |
| *Chromodoris quadricolor* + *Hexabranchus sanguineus* | — | 8 | — | **Mar Rojo / Indo-Pacífico** (lat 20–29, lon 33–166): viajes de buceo. |
| *Abudefduf saxatilis* + *Kyphosus vaigiensis* | — | 8 | 8 | *A. saxatilis* es estrictamente **Atlántico** y *K. vaigiensis* del **Indo-Pacífico**: no coexisten en el Mediterráneo. |
| *Leptogorgia ruberrima* + *L. viminalis* | — | 6 | 5 | gorgonias **simpátricas** (sí co-ocurren en Canarias) pero la cita del par concreto no existe; revisar localidades. |

### ⚠️ Corrección taxonómica (28-sep-2026)

- **`loripinus_fragilis` NO es sinónimo de `limaria_fragilis`**: *Loripinus fragilis* (Philippi, 1836) es un
  bivalvo **Lucinidae** (quimiosimbionte) y *Limaria fragilis* (Gmelin, 1791) es un **Limidae** («file clam»).
  Son especies distintas de familias distintas; el slug del catálogo es correcto. (WoRMS: AphiaID 718970
  vs 216644.)

## 5. Figura

![Red de asociaciones](../../docker/biofauna/artifacts/coocurrencia_red_top12.svg)

Red de las 12 asociaciones más fuertes (grosor del enlace ∝ lift). Copia navegable en esta carpeta:
[`coocurrencia_red_top12.svg`](coocurrencia_red_top12.svg).

## 6. Cómo leer la tabla y qué falta

1. **Co-ocurrencia ≠ simbiosis**: se han filtrado catálogo, soporte y repetibilidad, pero el paso que convierte
   esto en resultado citable es el **nulo estratificado por localidad·fecha** + **cruce con hábitat**.
2. El **lift** premia pares raros: mirar siempre `n`, celdas y días.
3. Uso inmediato: sugerencias «si ves X, busca Y» y redes de asociación por zona en **BioQuest**.
