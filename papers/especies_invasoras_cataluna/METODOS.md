# 2. Material y métodos

## 2.1 Lista de especies y estatus legal

Trabajamos con los 114 taxones de la lista UE definidos en el fichero `material/target_species.json` (copia de la lista de trabajo del proyecto, verificada contra los Reglamentos de Ejecución citados en la Introducción). El Catálogo Español (RD 630/2013, texto consolidado BOE-A-2013-8565) se usó para anotar inclusión en el anexo (columna CEEA en Tabla S1).

## 2.2 Área de estudio y fuentes de datos

El área de estudio es Cataluña. Las observaciones proceden de:

- **iNaturalist:** place Cataluña (61614) y España (6774) para comparaciones nacionales.
- **Minka:** registros dentro de una **caja rectangular** (0,1–3,4° E; 40,45–42,95° N), que incluye territorio no catalán (Aragón, Andorra, Francia) y mar; el recorte al polígono administrativo ICGC está pendiente (plan P1). La franja marina de 12 millas anunciada en versiones previas no se aplicó.

Para cada región reportamos el **máximo** entre fuentes, no la suma. Es una **cota inferior**, no una unión deduplicada a nivel de observación individual. En la caja de estudio, al agrupar por taxón, año y celda de ~1 km (coordenadas redondeadas), el solape iNaturalist–Minka representa ~0,4 % de las observaciones *research grade* (372.987 frente a 374.348); los conteos por especie siguen sin deduplicar entre plataformas.

**Filtros de calidad:** grado de investigación (*research grade*), exclusión de observaciones cautivas o cultivadas (`captive=false`) y precisión posicional ≤ 1 km «cuando el campo está disponible»; estos dos últimos filtros **no han sido auditados** en los ficheros finales. Fecha de descarga: octubre de 2026.

## 2.3 Categorías de presencia en Cataluña

Reglas aplicadas una sola vez en todo el manuscrito (no equivalen a estatus EASIN):

| Categoría | Criterio |
|---|---|
| Ausente | 0 observaciones en todas las fuentes |
| Ocasional | &lt; 10 observaciones, o &lt; 3 celdas UTM de 10 km, o &lt; 3 años con registros |
| Llegada reciente / serie insuficiente | Primer registro ≥ 2020 (serie < 5 años; no estimable) |
| En expansión | ≥ 10 obs, ≥ 5 años y razón de tasas > 1 con FDR &lt; 0,05 (ninguna especie la cumple) |
| Recurrente | Resto con ≥ 10 obs, ≥ 3 celdas y ≥ 3 años (describe detección repetida; no implica población establecida) |

Los valores centinela 99,0 del ratio de esfuerzo se sustituyeron por «n. d.» cuando no hay ventana previa suficiente.

## 2.4 Esfuerzo y tasa de detección

El esfuerzo anual del modelo se aproximó por el **número total de observaciones de la base BioQuest (694 taxones, iNaturalist + Minka) dentro de la caja de Cataluña** en cada año (Tabla S2). **No** es el total de iNaturalist/Minka ni coincide taxonómicamente con cada especie de la lista UE, y el numerador puede formar parte del denominador. Como sensibilidad descriptiva (plan P1, parcial), calculamos series paralelas por grupo taxonómico (*iconic*) para los taxones del catálogo en la misma caja (Fig. 2 cont.). El valor de 2008 (858) y el crecimiento 2021–2024 (10.939 → 102.301) sugieren efectos de ingesta de la base. 2026 es un año parcial y se excluye de los modelos. La tasa de detección es observaciones de la especie por 1000 observaciones de esfuerzo.

Para taxones ausentes en Cataluña pero presentes en España según EASIN, estimamos de forma exploratoria la probabilidad de cero registros locales si la especie estuviera presente (plan P3), usando la tasa relativa en España y el esfuerzo catalán de 2024 como referencia.

## 2.5 Tendencias temporales

Para cada taxón de la lista de la Unión con ≥ 10 observaciones y ≥ 5 años con registros en la ventana 2013–2025 (los años anteriores tienen < 1.300 observaciones de esfuerzo) ajustamos un modelo lineal generalizado binomial negativo (NB2, enlace log) con año centrado y offset log(esfuerzo): `obs ~ año + offset(log esfuerzo)`, con intervalos de confianza del 95 % para la razón de tasas anual y corrección de Benjamini–Hochberg (FDR) sobre el conjunto de especies. Sensibilidad: ventana 2016–2025. Código: `material/glm_tendencias_20261015.py` (`statsmodels`). **No** se realizó análisis de sensibilidad excluyendo a los observadores principales ni modelo con efectos aleatorios de observador o celda (datos de observador no disponibles en la serie agregada; plan P2). El análisis de «picos» por z-score se eliminó. Un análisis previo con tau/z sin FDR queda superado.

## 2.6 Hábitat

Para fauna acuática reclasificamos hábitat con indicadores WoRMS (`isMarine`, `isBrackish`, `isFreshwater`, `isTerrestrial`; consulta 15-oct-2026, `material/habitat_worms_20261015.json`, 29 taxones). Una consulta posterior (`material/verificacion_easin_worms_20261015.json`) encontró registro WoRMS para 58 de los 114 taxones; para el resto (plantas y vertebrados terrestres) WoRMS no es una fuente de hábitat, y su clasificación procede de la tabla interna del proyecto, sin verificación sistemática (plan P8). La clasificación **marina** (8 taxones) sí es coincidente con WoRMS. Las categorías son no excluyentes.

## 2.7 Origen, vías y primeras fechas

Origen nativo y vías se documentan en la Tabla 2 con categorías CBD/EASIN (una especie puede tener varias vías; EASIN consultado el 15-oct-2026) y, cuando no hay fuente, se marcan como hipótesis. Las «primeras fechas» ciudadanas se distinguen de las primeras citas publicadas (columnas separadas en Tabla 3). Las flechas de expansión en mapas siguen solo rutas marítimas plausibles o saltos humanos discontinuos (acuicultura, fouling), nunca expansión terrestre de especies estrictamente marinas.

## 2.8 Exóticas marinas no incluidas en la lista UE

Complementamos el análisis con un subconjunto de exóticas marinas documentadas en inventarios regionales (inventario ampliado facilitado por B. Weitzmann, provisional; García et al. 2015), contrastando primer registro ciudadano y primera cita bibliográfica. *Pterois miles* y *Lagocephalus sceleratus* se tratan en un recuadro de contexto mediterráneo (sin registros en Cataluña en nuestras fuentes).
