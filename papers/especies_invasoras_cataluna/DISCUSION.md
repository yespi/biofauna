# 4. Discusión

## 4.1 Respuesta a las preguntas

**Pregunta (i) — presencia frente a listas oficiales:** La ciencia ciudadana detecta un subconjunto de la lista UE centrado en plantas y vertebrados conspicuos. A escala de país, EASIN da 76 taxones presentes en España y nuestras fuentes 52 (50 coincidentes); 26 taxones citados en España por EASIN no tienen registro ciudadano nuestro (sobre todo invertebrados, anfibios y mamíferos crípticos o de distribución muy local). A escala catalana, la **Fig. 5** y `material/concordancia_exocat_oficial_20261016.csv` contrastan primeras citas EXOCAT/literatura con primer registro ciudadano en **12** taxones documentados (retraso nulo en *Oculina* o *Caulerpa*, &gt;10 años en *Rugulopteryx*). No es una concordancia celda a celda con el inventario EXOCAT completo (descarga masiva del portal pendiente).

**Pregunta (ii) — tendencias:** Con esfuerzo independiente por grupo (GBIF, GADM Cataluña) y un GLMM Poisson con intercepto aleatorio de observador, *Myocastor coypus* y *Vespa velutina nigrithorax* aumentan de forma robusta (persisten al quitar los tres observadores principales). *Neogale vison* y *Procambarus clarkii* descienden. *Ailanthus altissima* deja de ser «en expansión» respecto al GLM previo con denominador BioQuest: el salto 2020→2021 encaja mejor con campañas que con un aumento poblacional. Las tendencias de presencia usan solo GBIF (observador reproducible); los *n* de Tabla 3 pueden ser mayores al incluir Minka.

**Pregunta (iii) — retraso en marinas:** Para *Oculina patagonica*, *Caulerpa cylindracea* y *Callinectes sapidus* (no incluidas en la lista UE), el primer registro ciudadano en Cataluña es posterior a la primera cita publicada. Es una observación descriptiva en tres especies, **no una prueba** de retraso de la ciencia ciudadana: la diferencia puede deberse a que la plataforma empezó a usarse después.

## 4.2 Hipótesis sobre vías y cronología (selección)

Los contrastes con datos propios son limitados; la mayoría se resuelven con literatura y EASIN. Resumen en la Tabla S3.

| Cuestión | Resultado |
|---|---|
| Entrada de *Pterois miles* «hacia 2008 por lastre» (lectura de mapas ciudadanos) | No compatible con la primera cita mediterránea (Israel, 1991) ni con la genética (Bariche et al. 2017): refleja el inicio de la ciencia ciudadana en la región |
| *Magallana gigas* vía Cantábrico o Mar Menor | Sin evidencia; introducción acuícola directa (Grizel & Héral 1991) |
| Aumento de blooms de medusas | No contrastable con ratios relativos |
| Vías ornamentales de plantas | Soportadas por EASIN (horticultura, jardines botánicos); varias siguen como hipótesis |
| *Gambusia* por control de mosquitos | Documentada (EASIN: control biológico; España, 1921) |
| Retraso ciudadano frente a literatura en marinas | Descriptivo en tres especies; no contrastado (§4.1) |

## 4.2bis Nativas en expansión y clima

Especies nativas marinas en expansión (p. ej. cambios de distribución ligados a **SST** u olas de calor) no son el foco de este manuscrito; el paper de **declives** y trabajos de divulgación del repositorio tratan señales en especies emblemáticas. Las tendencias «crecientes» aquí se limitan a la **lista UE de invasoras** con GLMM; no interpretar un aumento de detección como expansión biológica sin inventario independiente.

## 4.3 Implicaciones para la gestión

Priorizar vigilancia de *Rugulopteryx okamurae* en roca infralitoral, *Callinectes sapidus* en delta y lagunas, y *Oxyura jamaicensis* en humedales interiores (riesgo de hibridación con *O. leucocephala*) aunque aún no haya registros en Cataluña.

## 4.4 Comparación con otros estudios

Los atlas y listas basados en ciencia ciudadana en Europa (p. ej. Azzurro et al. 2022, ClimateFish) muestran que peces costeros y especies conspicuas se detectan antes que invertebrados crípticos, un patrón que reproducimos con la lista UE en Cataluña. García et al. (2015) y los inventarios EXOCAT/EASIN documentan muchas de las marinas que aquí solo aparecen con retraso en iNaturalist (Fig. 7), lo que refuerza la hipótesis de sesgo temporal de plataforma más que de ausencia biológica. Los modelos de tendencia con offset de esfuerzo por grupo y efecto observador siguen la práctica recomendada para iNaturalist (Isaac et al. 2014). El denominador GBIF alinea taxón, año y región administrativa con los registros modelados, a diferencia del total rectangular de BioQuest usado antes. Las fechas «sin datos» en Tabla 3 siguen indicando ausencia de fila fechada en la base local (§2.2).

El acierto medio del identificador BioFauna para los taxones UE con eval (Tabla S6; índice **p19**) es comparable al global del índice (**84,38 %** según `stats.json`), lo que apoya su uso como capa de etiquetado en FotoFauna, pero no sustituye la validación experta en grupos difíciles (cangrejos, planarias, algas).

## 4.5 Limitaciones

Cobertura taxonómica desigual; polígono GADM terrestre-costero puede excluir buceo marino alejado de la costa; sesgo espacial (Fig. 1); concentración en pocos observadores (*Rugulopteryx*); primer registro ciudadano ≠ introducción; concordancia EXOCAT solo en subconjunto citado; tendencias solo en GBIF-iNat (Minka fuera del GLMM); GADM ≠ polígono ICGC fino; identificaciones no auditadas sistemáticamente; presencia sin deduplicar entre fuentes; categorías de detección, no de estatus ecológico. El GLMM con observador (§2.5) actúa como **modelo de detectabilidad** con unidad observador–año; un modelo de **ocupación** en cuadrícula × año con efecto aleatorio de celda queda para trabajo futuro (datos demasiado escasos por especie en la lista UE).
