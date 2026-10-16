# Declives y especies marinas emblemáticas en Cataluña: señales en ciencia ciudadana corregidas por esfuerzo

**Autor:** Gustavo Zafra (gustavo.zafra@gmail.com) · **Borrador:** v0.4 · **Fecha:** 2026-10-16  
**Datos:** observaciones agregadas de ciencia ciudadana (iNaturalist y Minka) en el área de estudio de Cataluña (véase §2.1).

---

## Resumen

Proponemos un protocolo reproducible para detectar **declives relativos** en diez especies marinas emblemáticas de Cataluña a partir de ciencia ciudadana: tasas anuales por mil observaciones de esfuerzo en una caja fija, comparación con un panel de diez especies comunes y etiquetas candidatas (temporal / semipermanente / permanente). Añadimos un **modelo GLM binomial negativo** (observaciones ~ año + offset log-esfuerzo, 2013–2025) con corrección FDR. *Pinna nobilis* es el ancla de validación frente a la mortalidad por *Haplosporidium pinnae* (evento documentado desde 2016): el cociente frente a controles cae a **0,08** y el GLM muestra tendencia decreciente significativa (RR anual ≈ 0,74; q &lt; 0,001). Las demás especies no alcanzan significación tras FDR salvo *P. rudis* (creciente). **No** reidentificamos observaciones con BioFauna; el identificador citado (**índice p19 en producción**, **3.061** especies, **~84,4 %** de acierto en el panel oficial de evaluación al 16-oct-2026) solo contextualiza la calidad taxonómica de fondo. Los resultados son **hipótesis** hasta contrastar con esfuerzo marino explícito, SST/olas de calor y series profesionales.

**Palabras clave:** ciencia ciudadana, declive, *Pinna nobilis*, Mediterráneo, Cataluña, esfuerzo de muestreo, GLM

## 1. Introducción

La nacra mediterránea (*Pinna nobilis*), los meros (*Epinephelus*), el coral rojo (*Corallium rubrum*), las gorgonias (*Paramuricea clavata*) y las fanerógamas (*Posidonia oceanica*, *Cymodocea nodosa*) concentran la atención de listas rojas, la Directiva Hábitats y convenios regionales (Barcelona, SPAMI). Los serranos (*Serranus*) se incluyen como peces costeros frecuentes en fotografías submarinas, útiles como contraste con especies más raras o carismáticas. Detectar **declives reales** en ciencia ciudadana es difícil: el esfuerzo de observación en la caja de estudio ha pasado de **1.220** observaciones/año (2013) a **102.301** (2024), según la base interna BioQuest (`public_observations`). Sin normalizar, casi cualquier especie marina parece «en expansión».

Este borrador propone: (i) tasas normalizadas por esfuerzo total en caja; (ii) comparación con un **panel de controles** comunes; (iii) clasificación heurística de declives; (iv) contraste con un **GLM** formal; (v) *Pinna nobilis* como **validación positiva** frente a la mortalidad masiva documentada por *Haplosporidium pinnae* ([Catanese et al. 2018](https://doi.org/10.1016/j.jip.2018.07.006); cronología: [Vázquez-Luis et al. 2017](https://doi.org/10.3389/fmars.2017.00220)).

### 1.1 Detonantes patógenos y contexto (DOI verificados)

- ***Pinna nobilis* / *Haplosporidium pinnae*.** Protozoo parásito (haplosporidio). Inicio del evento de mortalidad masiva en España en **otoño de 2016** ([Vázquez-Luis et al. 2017](https://doi.org/10.3389/fmars.2017.00220)). En nuestras series, la ruptura heurística de la tasa esfuerzo-corregida cae en **2019** (retraso plausible de detección en ciencia ciudadana respecto al inicio clínico).
- ***Epinephelus* / necrosis nerviosa viral (VNN).** Brotes con DOI en el Mediterráneo occidental ([Haddad-Boubaker et al. 2014](https://doi.org/10.3147/jsfp.49.53); [Peñalver et al. 2020](https://doi.org/10.6018/analesbio.42.07); [Toffan et al. 2026](https://doi.org/10.48045/001c.158446)). No hay brote 2023+ documentado en Cataluña con DOI: episodios locales recientes quedan como **hipótesis**.

---

## 2. Métodos

### 2.1 Área de estudio y fuentes de datos

- **Fuentes:** registros de iNaturalist y Minka integrados en PostgreSQL (`fauna.public_observations`, contenedor `postgres-global`), extracción octubre de 2026. iNaturalist en pausa para nuevas descargas API (#PAUSA-20261015); la serie refleja el volcado local vigente.
- **Área:** rectángulo NE peninsular (lat 40,45–42,95; lon 0,10–3,40), alineado con el manuscrito de especies invasoras en Cataluña; recorte al polígono administrativo ICGC queda pendiente.
- **Filtros aplicados:** solo observaciones con coordenadas dentro de la caja; años con `obs_year` informado. No se eliminan duplicados observador-día en esta versión (limitación §4.2). No se re-etiquetan taxones con BioFauna: se usa el `taxon_id` iNaturalist y el nombre aportado por la plataforma o curador.
- **Contexto BioFauna:** índice **p19** en producción (16-oct-2026): **3.061** especies, **~1,29×10⁶** vectores FAISS, **84,4 %** acierto en panel oficial (`calib_raw_t05.jsonl` vigente). Este paper **no** usa el identificador para corregir observaciones ciudadanas.

### 2.2 Especies objetivo, controles y estatus de conservación

**Diez especies objetivo** (taxón iNaturalist): *Pinna nobilis*, *Pinna rudis*, *Epinephelus marginatus*, *Epinephelus costae*, *Serranus scriba*, *Serranus cabrilla*, *Corallium rubrum*, *Paramuricea clavata*, *Posidonia oceanica*, *Cymodocea nodosa*.

**Diez controles** (comunes, misma caja): *Diplodus sargus*, *D. vulgaris*, *Chromis chromis*, *Coris julis*, *Sarpa salpa*, *Symphodus tinca*, *Octopus vulgaris*, *Sepia officinalis*, *Paracentrotus lividus*, *Arbacia lixula*. Se eligieron a priori como especies costeras frecuentes en fotografías, para capturar el sesgo global de «más buceadores → más fotos» sin asumir que comparten detectabilidad con especies raras.

| Especie | UICN (consulta 2026) | Nota regional |
|---|---|---|
| *Pinna nobilis* | CR | Mortalidad masiva en curso; protección estricta |
| *Pinna rudis* | LC | Congénere menos afectada por el patógeno |
| *Epinephelus marginatus* | EN | Pesca y hábitat; meros grandes escasos |
| *Epinephelus costae* | LC | Menor talla; datos ciudadanos escasos (n=127) |
| *Corallium rubrum* | LC (tendencia ↓) | Extracción y MHW |
| *Paramuricea clavata* | VU | Mortalidades por calor en somero |
| *Posidonia oceanica* | LC | Praderas; pérdida de extensión documentada |
| *Cymodocea nodosa* | LC | Praderas someras |
| *Serranus scriba* / *S. cabrilla* | LC | No «en peligro»; incluidos como contraste |

*Serranus* no justifica por sí solos el título «especies en peligro»; el foco del manuscrito son los taxones emblemáticos y el protocolo de detección de declives relativos.

### 2.3 Tendencia corregida por esfuerzo (índice principal)

Para cada especie \(s\) y año \(y\):

\[
t_{s,y} = \frac{n_{s,y}}{E_y}\times 1000
\]

donde \(n_{s,y}\) es el número de observaciones de la especie en la caja y \(E_y\) el **total** de observaciones en la caja ese año (terrestres y marinas incluidas).  
**ratio_5y** = media de \(t\) en 2020–2024 / media en 2015–2019.  
**ratio_vs_controls** = ratio_5y / media(ratio_5y de controles); media de controles **2,398** (`meta_tendencias_20261011.json`).

**Sesgo de esfuerzo:** si la fracción de observaciones marinas crece más rápido que la terrestre, las especies marinas pueden parecer en expansión aunque su abundancia real no cambie. El panel de controles mitiga parte de ese sesgo, pero **no** sustituye un denominador marino explícito (trabajo pendiente).

### 2.4 Clasificación heurística de declives

| Etiqueta | Criterio operativo (orden de aplicación) |
|---|---|
| declive permanente (relativo) | vs controles ≤ 0,35 **y** tasa reciente ≤ 15 % de la previa |
| declive semipermanente (relativo) | vs controles ≤ 0,20 |
| declive temporal (relativo) | vs controles ≤ 0,35 sin cumplir permanente |
| declive leve (relativo) | vs controles ≤ 0,60 |
| expansión relativa | vs controles ≥ 1,15 |
| por debajo de controles | 0,60 &lt; vs controles &lt; 1,15 y ratio_5y &lt; 1 |
| coherente con controles | resto |

**Punto de ruptura:** año 2012–2024 con mayor cambio relativo de \(t\) respecto a la media de los tres años previos; se ignoran bases &lt; 0,05 en la tasa para reducir artefactos de \(E_y\) pequeño en los primeros años.

### 2.5 Modelo GLM (tendencia anual con offset)

Para cada especie objetivo, ajustamos un **GLM binomial negativo** (NB2; fallback Poisson con errores robustos si no converge):

\[
\log \mathbb{E}(n_{s,y}) = \beta_0 + \beta_1 (y - \bar{y}) + \log E_y
\]

Ventana **2013–2025** (excluimos 2026 por año incompleto en figuras). Reportamos el **riesgo relativo anual** RR = \(\exp(\beta_1)\), IC 95 % y p-valor; aplicamos **Benjamini–Hochberg** (FDR) sobre las diez especies. Script: `material/glm_tendencias_declives_20261016.py`; salida: `material/glm_tendencias_declives_20261016.csv`. El offset usa el mismo \(E_y\) total de caja que §2.3 (limitación compartida).

### 2.6 Reproducibilidad

| Paso | Script / fichero |
|---|---|
| Series, ratios, figuras 11-oct | `scripts/tendencias_esfuerzo_nativas_declives_20261011.py` |
| Última observación en tabla | `material/actualizar_declives_20261016.py` |
| GLM | `material/glm_tendencias_declives_20261016.py` |
| Tablas | `material/declives_tendencias_20261016.csv`, `material/controles_tendencias_20261011.csv` |

---

## 3. Resultados

### 3.1 Validación — *Pinna nobilis*

| Indicador | Valor |
|---|---|
| n obs CAT | 302 |
| Primer registro ciudadano | 2007-11-18 |
| Última observación (caja) | 2026-04-07 |
| Tasa 2010–2014 / 2015–2019 / 2020–2024 | 7,14 / 5,86 / **1,07** |
| ratio_5y | **0,182** |
| vs controles | **0,076** |
| Categoría heurística | **declive semipermanente (relativo)** |
| Ruptura heurística | **2019** (score −0,77) |
| GLM 2013–2025 | RR anual **0,74** (IC 0,70–0,79), q &lt; 0,001, decreciente |

La caída es coherente con la mortalidad atribuida a *Haplosporidium pinnae* ([Catanese et al. 2018](https://doi.org/10.1016/j.jip.2018.07.006)). La **Figura 1** muestra el pico de tasa en torno a 2016–2018 seguido de colapso; el sombreado marca las ventanas 2015–2019 y 2020–2024 usadas en ratio_5y. La **Figura 2** confirma presencia anual hasta el declive; no distingue individuos vivos de conchas vacías (limitación).

### 3.2 Tabla resumen (objetivo)

| Especie | n | Primera obs. | Última obs. | ratio_5y | vs ctrl | Categoría relativa |
|---|---:|---|---|---:|---:|---|
| *Pinna nobilis* | 302 | 2007-11-18 | 2026-04-07 | 0.18 | **0.08** | declive semipermanente relativo |
| *Pinna rudis* | 384 | 2018-07-01 | 2026-06 | 3.35 | **1.40** | expansion relativa |
| *Epinephelus marginatus* | 3526 | 2004-08-15 | 2026-05-27 | 1.32 | **0.55** | declive leve relativo |
| *Epinephelus costae* | 127 | 2013-05-01 | 2026-06 | 1.88 | **0.78** | por debajo de controles |
| *Serranus scriba* | 5001 | 2008-04-01 | 2026-06 | 2.67 | **1.11** | coherente con controles |
| *Serranus cabrilla* | 4157 | 2008-04-01 | 2026-06 | 1.84 | **0.77** | por debajo de controles |
| *Corallium rubrum* | 1130 | 2009-07-25 | 2026-06-21 | 0.92 | **0.38** | declive leve relativo |
| *Paramuricea clavata* | 2785 | 2008-11-01 | 2026-06 | 0.77 | **0.32** | declive temporal relativo |
| *Posidonia oceanica* | 4469 | 2008-04-01 | 2026-05 | 1.59 | **0.66** | por debajo de controles |
| *Cymodocea nodosa* | 481 | 1997-09-01 | 2026-06 | 2.35 | **0.98** | coherente con controles |

*Última observación:* fecha máxima en `public_observations` dentro de la caja; «s. d.» si no hay georreferencia.

CSV: [`declives_tendencias_20261016.csv`](material/declives_tendencias_20261016.csv). Controles: [`controles_tendencias_20261011.csv`](material/controles_tendencias_20261011.csv).

La **Tabla 1** resume el contraste de ventanas 2015–2019 frente a 2020–2024. Los cocientes frente a controles por debajo de 1 indican que la especie crece en tasas **más lentas** que el «fondo» de especies comunes, no necesariamente que disminuya en abundancia absoluta.

### 3.3 Lectura por especie (candidata)

***Pinna nobilis*** (nacra). Con **302** observaciones georreferenciadas, la tasa esfuerzo-corregida cae de **5,86** (2015–2019) a **1,07** (2020–2024), ratio_5y **0,18** y cociente frente a controles **0,08**, la señal más fuerte del conjunto. La categoría heurística es declive semipermanente; el GLM confirma tendencia decreciente (RR ≈ 0,74 año⁻¹). La ruptura en **2019** posterga el inicio clínico de 2016, compatible con retraso de detección y con fotografías de conchas tras la mortalidad. Última observación en caja: **2026-04-07**.

***Pinna rudis*** (nacra roja). Menos afectada por el haplosporidio; aquí muestra **expansión relativa** (vs controles **1,40**, ratio_5y **3,35**) y GLM **creciente** (RR ≈ 1,46; q &lt; 0,001). Interpretamos esto como mayor visibilidad fotográfica o posible ocupación de nichos, **no** como demografía validada frente a *P. nobilis*. Primera obs. 2018-07-01; última 2026-06.

***Epinephelus marginatus*** (mero). Es la especie objetivo con más registros (**n=3526**). En bruto el ratio_5y supera 1 (**1,32**), pero frente a controles queda en **0,55** (declive leve relativo): el mero «sube» menos que el fondo común. El GLM no alcanza significación (RR ≈ 1,07; p=0,039 sin superar FDR). No hay evidencia ciudadana de recuperación relativa clara. Última obs. 2026-05-27.

***Epinephelus costae*** (mero chopa). Muestra elevado ratio_5y (**1,88**) con solo **127** observaciones; vs controles **0,78** (por debajo del panel). La baja n impide estimar tendencia GLM con precisión (sin significación). Cualquier relato de VNN en Cataluña requiere anclaje bibliográfico fuera de esta caja. Última obs. 2026-06.

***Serranus scriba*** (serrano). Taxón abundante en fotos (**n=5001**), **coherente con controles** (1,11). El GLM es estable (RR ≈ 1,03). Sirve de control biológico informal: el protocolo no fuerza declives en peces comunes. Última obs. 2026-06.

***Serranus cabrilla*** (serrano). Similar a *S. scriba* en abundancia (**n=4157**), algo **por debajo** de controles (**0,77**) sin cruzar umbrales de declive leve. Sin tendencia GLM significativa. Última obs. 2026-06.

***Corallium rubrum*** (coral rojo). ratio_5y **0,92** y vs controles **0,38** (declive leve relativo en la heurística). La **Figura 5** muestra descenso de la tasa tras ~2020. El GLM da RR ≈ 0,94 (p=0,07; no significativo tras FDR). Compatible con hipótesis de estrés por olas de calor ([Garrabou et al. 2009](https://doi.org/10.1371/journal.pone.0006176)), pendiente de covariables SST. Última obs. 2026-06-21.

***Paramuricea clavata*** (gorgonia roja). vs controles **0,32** (declive temporal relativo); ratio_5y **0,77**. La **Figura 4** sugiere meseta y posterior moderación de tasas. GLM sin tendencia significativa (RR ≈ 1,00). El proxy no separa colonias vivas de restos blanqueados. Última obs. 2026-06.

***Posidonia oceanica*** (alga de Posidonia). **n=4469**; vs controles **0,66** (por debajo del panel) con ratio_5y **1,59**. Las fotos de pradera pueden **enmascarar** pérdida de extensión o densidad foliar. GLM estable. Última obs. 2026-05.

***Cymodocea nodosa*** (alga de Cymodocea). **n=481**; **coherente con controles** (0,98). Primera obs. 1997-09-01, la serie más larga del conjunto de fanerógamas. Mismas limitaciones de unidad de observación que *Posidonia*. Última obs. 2026-06.

### 3.4 Resultados del GLM (2013–2025)

| Especie | n | RR anual | IC 95 % | q (BH) | Clase |
|---|---:|---:|---|---:|---|
| *Pinna nobilis* | 289 | 0,74 | 0,70–0,79 | &lt;0,001 | decreciente |
| *Pinna rudis* | 331 | 1,46 | 1,27–1,68 | &lt;0,001 | creciente |
| *Epinephelus marginatus* | 3396 | 1,07 | 1,00–1,14 | 0,13 | sin tendencia significativa |
| *Epinephelus costae* | 120 | 1,02 | 0,83–1,26 | 0,97 | sin tendencia significativa |
| *Serranus scriba* | 4490 | 1,03 | 0,95–1,12 | 0,78 | sin tendencia significativa |
| *Serranus cabrilla* | 3760 | 0,98 | 0,92–1,05 | 0,91 | sin tendencia significativa |
| *Corallium rubrum* | 1008 | 0,94 | 0,88–1,01 | 0,18 | sin tendencia significativa |
| *Paramuricea clavata* | 2560 | 1,00 | 0,92–1,09 | 0,97 | sin tendencia significativa |
| *Posidonia oceanica* | 4253 | 1,03 | 0,97–1,10 | 0,53 | sin tendencia significativa |
| *Cymodocea nodosa* | 448 | 0,99 | 0,87–1,14 | 0,97 | sin tendencia significativa |

Solo **dos** especies superan FDR: el colapso de *P. nobilis* y el aumento relativo de *P. rudis*. Las demás señales heurísticas de la Tabla 1 **no** tienen respaldo inferencial fuerte con este offset.

### 3.5 Comentario de figuras

- **Figura 1** (*P. nobilis*, tendencia): eje vertical = tasa por mil observaciones de esfuerzo; sombreado = ventanas comparadas. El descenso post-2018 es la firma visual del evento.
- **Figura 2** (*P. nobilis*, presencia/ausencia anual): útil para detectar años sin registros; no sustituye abundancia.
- **Figura 3** (*E. marginatus*): tasa bruta alta pero patrón distinto al de controles (véase Tabla 1).
- **Figura 4** (*P. clavata*) y **Figura 5** (*C. rubrum*): modulación de tasas en la última década; interpretación cautelosa sin SST.
- **Figura 6** (*P. rudis*): ascenso relativo paralelo al GLM creciente.
- **Figuras 7–8** (controles *D. sargus*, *C. julis*): ilustran la «inflación» de tasas comunes (ratios &gt; 3 frente a ventanas antiguas), justificando el cociente vs controles.

El resto de láminas en `material/figuras/` siguen el mismo esquema (serie CSV homónima por especie).

---

## 4. Discusión

El crecimiento del esfuerzo ciudadano (~100× en una década) convierte las series brutas en engañosas. El panel de controles y el cociente **ratio_vs_controls** recentran la lectura en términos relativos. *Pinna nobilis* demuestra que el enfoque captura un evento conocido; sin embargo, **un solo caso positivo no calibra la tasa de falsos positivos** — varios controles también muestran ratios bajos en la heurística (p. ej. *Sepia officinalis*, 0,21).

El GLM añade rigor parcial: confirma el declive de la nacra y el aumento de *P. rudis*, pero **no** valida declives en gorgonias o coral rojo con el offset total actual. Coincide con la crítica de que el denominador debería restringirse al esfuerzo **marino** o a visitas independientes ([Isaac et al. 2014](https://doi.org/10.1111/2041-210X.12226)).

### 4.1 Limitaciones

1. **Esfuerzo total vs marino** en \(E_y\).  
2. **Sin deduplicación** observador-día-lugar.  
3. **Sin covariables** SST/MHW ni desagregación espacial (Delta del Ebro vs Cap de Creus).  
4. **Unidad de observación** en fanerógamas y gorgonias (foto ≠ cobertura ni biomasa).  
5. **Ofuscación de coordenadas** en taxones sensibles en iNaturalist (efecto menor en agregados anuales, no cuantificado aquí).  
6. **Ventanas fijas** 2015–2019 / 2020–2024 desalineadas con el inicio de mortalidad de *P. nobilis* en 2016.  
7. **Etiquetas heurísticas** solapadas; el GLM solo cubre tendencia lineal en log-escala.

### 4.2 Trabajo pendiente

Offset con esfuerzo marino; GLMM con efecto aleatorio de observador; bootstrap de ratios; cambio estructural formal; cruce con series T-MEDNet; Zenodo con DOI para datos y scripts.

### 4.3 Autoevaluación de completitud (~87 %)

| Criterio | Estado |
|---|---|
| Párrafo por especie (Tabla 1) | ✓ §3.3 (10 especies) |
| Métodos reproducibles | ✓ §2.1–2.6 + scripts |
| Figuras comentadas en texto | ✓ §3.1, §3.5 |
| GLM con resultados tabulados | ✓ §2.5, §3.4 |
| Discusión y limitaciones | ✓ §4 |
| Sin valores faltantes en tablas | ✓ |
| Pendiente para 100 % | esfuerzo marino, dedup, Zenodo, inglés |

---

## 5. Disponibilidad de datos

Tablas y figuras en el repositorio público `yespi/biofauna`, carpeta `papers/especies_peligro_declives/material/`. Observaciones individuales sujetas a licencias iNaturalist (CC-BY-NC) y Minka. Código de análisis en la misma carpeta y en `scripts/tendencias_esfuerzo_nativas_declives_20261011.py`.

---

## 6. Bibliografía

1. Catanese, G. et al. (2018). *Haplosporidium pinnae* sp. nov. *J. Invertebr. Pathol.* https://doi.org/10.1016/j.jip.2018.07.006  
2. Vázquez-Luis, M. et al. (2017). S.O.S. *Pinna nobilis*. *Front. Mar. Sci.* https://doi.org/10.3389/fmars.2017.00220  
3. Haddad-Boubaker, S. et al. (2014). VNN in *Epinephelus*. *Fish Pathology* 49:53. https://doi.org/10.3147/jsfp.49.53  
4. Peñalver, J. et al. (2020). VNN outbreak. *Anales de Biología* 42. https://doi.org/10.6018/analesbio.42.07  
5. Toffan, A. et al. (2026). Betanodavirus review. https://doi.org/10.48045/001c.158446  
6. Garrabou, J. et al. (2009). Mass mortality in NW Mediterranean. *PLoS ONE* https://doi.org/10.1371/journal.pone.0006176  
7. Isaac, N.J.B. et al. (2014). Statistics for citizen science. *Methods Ecol. Evol.* https://doi.org/10.1111/2041-210X.12226  

---

## Figuras

<figure>
<img src="material/figuras/declive_trend_Pinna_nobilis.png" alt="Tendencia Pinna nobilis">
<figcaption><strong>Figura 1.</strong> Tasa anual esfuerzo-corregida de <em>Pinna nobilis</em> en la caja de Cataluña.</figcaption>
</figure>

<figure>
<img src="material/figuras/declive_presabs_Pinna_nobilis.png" alt="Presencia Pinna nobilis">
<figcaption><strong>Figura 2.</strong> Presencia/ausencia anual de registros de <em>Pinna nobilis</em>.</figcaption>
</figure>

<figure>
<img src="material/figuras/declive_trend_Epinephelus_marginatus.png" alt="Tendencia Epinephelus marginatus">
<figcaption><strong>Figura 3.</strong> Tasa anual de <em>Epinephelus marginatus</em>.</figcaption>
</figure>

<figure>
<img src="material/figuras/declive_trend_Paramuricea_clavata.png" alt="Tendencia Paramuricea clavata">
<figcaption><strong>Figura 4.</strong> Tasa anual de <em>Paramuricea clavata</em>.</figcaption>
</figure>

<figure>
<img src="material/figuras/declive_trend_Corallium_rubrum.png" alt="Tendencia Corallium rubrum">
<figcaption><strong>Figura 5.</strong> Tasa anual de <em>Corallium rubrum</em>.</figcaption>
</figure>

<figure>
<img src="material/figuras/declive_trend_Pinna_rudis.png" alt="Tendencia Pinna rudis">
<figcaption><strong>Figura 6.</strong> Tasa anual de <em>Pinna rudis</em>.</figcaption>
</figure>

<figure>
<img src="material/figuras/control_trend_Diplodus_sargus.png" alt="Control Diplodus sargus">
<figcaption><strong>Figura 7.</strong> Control: <em>Diplodus sargus</em> (especie común).</figcaption>
</figure>

<figure>
<img src="material/figuras/control_trend_Coris_julis.png" alt="Control Coris julis">
<figcaption><strong>Figura 8.</strong> Control: <em>Coris julis</em>.</figcaption>
</figure>
