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

## 2. Validación interna (asociaciones ya documentadas que el método recupera)

| asociación documentada | n | lift | celdas | días | interpretación |
|---|---:|---:|---:|---:|---|
| ***Peltodoris atromaculata*** + ***Petrosia ficiformis*** | 79 | 11,1 | 44 | 74 | el nudibranquio vive y se alimenta sobre esta esponja |
| *Felimare picta* + *Ircinia oros* | 29 | 4,1 | 20 | 28 | depredación sobre la esponja hospedadora |
| *Cratena peregrina* + *Eudendrium racemosum* | 5 | 10,5 | — | — | hidrozoo del que se alimenta |
| *Doto paulinae* + *Sertularella mediterranea* | 5 | 48,3 | — | — | hidrozoo hospedador de *Doto* |

Que el método redescubra estas cuatro —con decenas de localidades y días distintos— es la garantía de que
**las candidatas nuevas no son ruido estadístico** (quedan por pasar el nulo estratificado, ver `METODOS.md §6`).

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
[`coocurrencia_top40.md`](coocurrencia_top40.md)¹ y los **70.971 pares** en
`coocurrencia_top40.md` (muestra; el conjunto completo se solicita al autor).

> ¹ En el repositorio público se incluye una copia en `papers/proyecto_correlacion/`.

## 5. Figura

![Red de asociaciones](coocurrencia_red_top12.svg)

Red de las 12 asociaciones más fuertes (grosor del enlace ∝ lift). Copia navegable en esta carpeta:
[`coocurrencia_red_top12.svg`](coocurrencia_red_top12.svg).

## 6. Cómo leer la tabla y qué falta

1. **Co-ocurrencia ≠ simbiosis**: se han filtrado catálogo, soporte y repetibilidad, pero el paso que convierte
   esto en resultado citable es el **nulo estratificado por localidad·fecha** + **cruce con hábitat**.
2. El **lift** premia pares raros: mirar siempre `n`, celdas y días.
3. Uso inmediato: sugerencias «si ves X, busca Y» y redes de asociación por zona en **BioQuest**.
