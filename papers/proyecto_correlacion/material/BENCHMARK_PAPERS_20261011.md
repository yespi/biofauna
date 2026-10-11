# Benchmark de papers publicados — Proyecto Correlación (11-oct-2026)

Preparado por Robotin. Todos los DOI comprobados en la API de Crossref el 11-oct-2026. El resumen de métodos es de lectura de los papers; conviene repasar los detalles en el original antes de citar cifras concretas.

## Parte A — Correlaciones (co-ocurrencia, redes, JSDM, sesgo de esfuerzo)

### 1. Blanchet, Cazelles & Gravel (2020). Co-occurrence is not evidence of ecological interactions. *Ecology Letters*. https://doi.org/10.1111/ele.13525
- Método: revisión crítica y simulaciones. Muestra que la co-ocurrencia mezcla filtrado ambiental, dispersión e interacciones, y que depende de la escala.
- Esfuerzo/espacio: insiste en controlar el ambiente compartido y la escala espacial antes de interpretar.
- Aporta: marco conceptual y simulaciones con interacciones conocidas.
- Ideas para nuestro paper: (a) usar nuestro criterio de “misma foto” como respuesta explícita a sus 3 objeciones, con una tabla “objeción → cómo lo resolvemos”; (b) repetir el análisis a 3 escalas (foto, evento de 3 h, celda de 1 km × mes) y mostrar cómo cambian los pares.

### 2. Veech (2013). A probabilistic model for analysing species co-occurrence. *Global Ecology and Biogeography*. https://doi.org/10.1111/j.1466-8238.2012.00789.x
- Método: probabilidad exacta (hipergeométrica) de observar ≥ o ≤ co-ocurrencias, sin aleatorizar matrices.
- Esfuerzo: implícito en el número de sitios; no corrige heterogeneidad entre sitios.
- Aporta: clasificación de pares en positivos, negativos y aleatorios.
- Ideas: (a) reportar también los pares **negativos** (exclusión), que no tenemos; (b) tabla de pares positivos, negativos y aleatorios por grupo taxonómico.

### 3. Griffith, Veech & Marsh (2016). cooccur: Probabilistic species co-occurrence analysis in R. *Journal of Statistical Software*. https://doi.org/10.18637/jss.v069.c02
- Método: implementación del modelo de Veech; tamaño de efecto observado − esperado.
- Aporta: el heatmap estándar de pares y el gráfico observado frente a esperado.
- Ideas: (a) instalar R + `cooccur` (o portar a Python) y sustituir el proxy “Veech-lite” por el modelo real; (b) añadir la figura observado frente a esperado, que los revisores reconocen al instante.

### 4. Pollock et al. (2014). Understanding co-occurrence by modelling species simultaneously with a Joint Species Distribution Model (JSDM). *Methods in Ecology and Evolution*. https://doi.org/10.1111/2041-210X.12180
- Método: JSDM probit multivariante; separa la correlación explicada por el ambiente de la correlación residual.
- Esfuerzo/espacio: covariables ambientales; la correlación residual es la candidata a interacción.
- Aporta: matrices de correlación ambiental frente a residual.
- Ideas: (a) JSDM sobre las ~200 especies con más registros, con SST, profundidad, mes y esfuerzo como covariables; (b) comparar la correlación residual con los pares “misma foto”; si coinciden, es nuestra validación.

### 5. Ovaskainen et al. (2017). How to make more out of community data? A conceptual framework and its implementation as models and software. *Ecology Letters*. https://doi.org/10.1111/ele.12757
- Método: HMSC (jerárquico bayesiano) con rasgos, filogenia y efectos aleatorios espaciales y temporales.
- Esfuerzo/espacio: efectos aleatorios espaciales y covariable de esfuerzo.
- Aporta: partición de varianza (ambiente, espacio, tiempo) y redes de asociación residual con soporte posterior > 0,95.
- Ideas: (a) figura de partición de varianza por especie; (b) red residual con soporte posterior como sustituto de los 51.401 pares “significativos”, que no discriminan; (c) añadir efecto aleatorio de **observador**.

### 6. Harris (2016). Inferring species interactions from co-occurrence data with Markov networks. *Ecology*. https://doi.org/10.1002/ecy.1605
- Método: redes de Markov (modelos gráficos), que condicionan por las demás especies y evitan correlaciones indirectas.
- Aporta: comparación con simulaciones de interacciones conocidas; supera a los métodos de pares.
- Ideas: (a) red de Markov o *graphical lasso* sobre la matriz de eventos para quitar las asociaciones indirectas; (b) benchmark con comunidades simuladas que tengan interacciones conocidas, para medir precisión y recall del cribado.

### 7. Freilich et al. (2018). Species co-occurrence networks: Can they reveal trophic and non-trophic interactions in ecological communities? *Ecology*. https://doi.org/10.1002/ecy.2142
- Método: compara redes de co-ocurrencia con una red de interacciones conocidas de la zona intermareal rocosa (Chile).
- Aporta: mide cuántas interacciones reales recupera la co-ocurrencia: pocas.
- Ideas: (a) replicar su diseño con GloBI más literatura marina mediterránea como verdad de referencia y reportar precisión y recall con IC; (b) separar interacciones tróficas y no tróficas (epibiosis, simbiosis, limpieza), donde “misma foto” debería funcionar mejor.

### 8. Johnston et al. (2021). Analytical guidelines to increase the value of community science data: An example using eBird data to estimate species distributions. *Diversity and Distributions*. https://doi.org/10.1111/ddi.13271
- Método: filtrado de listas, submuestreo espacial y temporal equilibrado, covariables de esfuerzo (duración, distancia, experiencia del observador).
- Aporta: comparación cuantitativa de cada paso de control de sesgo.
- Ideas: (a) submuestreo espacial en malla (1 evento por celda × día) para quitar los hotspots; (b) covariable de experiencia del observador; (c) tabla de sensibilidad: cuántos pares sobreviven a cada filtro.

### 9. Isaac et al. (2014). Statistics for citizen science: extracting signals of change from noisy ecological data. *Methods in Ecology and Evolution*. https://doi.org/10.1111/2041-210X.12254
- Método: simulación de sesgos (esfuerzo, detectabilidad, longitud de lista) y comparación de métodos; recomienda la ocupación y la longitud de lista como covariable.
- Ideas: usar la **longitud de lista** (nº de especies por evento) como covariable de esfuerzo en el modelo nulo de pares.

### 10. Barve et al. (2020). Methods for broad-scale plant phenology assessments using citizen scientists' photographs. *Applications in Plant Sciences*. https://doi.org/10.1002/aps3.11315
- Método: anotación de fenología sobre fotos de iNaturalist; controla el esfuerzo con la estacionalidad de las observaciones totales.
- Ideas: estacionalidad relativa (fracción de la especie entre todas las observaciones del mes) para la parte de estacionalidad compartida, en lugar de conteos brutos.

## Las 5 mejoras más claras para nuestro paper
1. **Modelo nulo serio:** `cooccur` real (Veech) y una JSDM/HMSC con esfuerzo, observador y longitud de lista como covariables; reportar pares positivos **y negativos**.
2. **Quitar las asociaciones indirectas:** red de Markov o *graphical lasso* sobre los eventos; la red residual sustituye a los 51.401 pares “significativos”.
3. **Validación cuantitativa:** precisión y recall frente a GloBI más literatura (diseño Freilich), separando tróficas y no tróficas, y benchmark con comunidades simuladas (Harris, Blanchet).
4. **Análisis multiescala y de sensibilidad:** foto, evento de 3 h, celda × mes, y tabla de cuántos pares sobreviven a cada filtro (submuestreo espacial, Johnston).
5. **Figuras estándar:** observado frente a esperado, heatmap de pares, partición de varianza y red residual coloreada por tipo de interacción.

## Parte B — Benchmarks breves para otros papers (los ficheros de cada paper no se han tocado)

### BioFauna (método de identificación)
- Van Horn et al. (2018). The iNaturalist Species Classification and Detection Dataset. CVPR. https://doi.org/10.1109/CVPR.2018.00914. Long-tail y métricas por frecuencia de clase. **Idea:** reportar el acierto por cuartiles de tamaño de galería y la curva acierto–nº de fotos.
- Mac Aodha et al. (2019). Presence-Only Geographical Priors for Fine-Grained Image Classification. ICCV. https://doi.org/10.1109/ICCV.2019.00969. Prior espacio-temporal que multiplica la salida visual; da varios puntos de mejora. **Idea:** prior de zona y mes con BioQuest; es exactamente la tarea de “zona/mes BQ”, y este paper es la cita base.
- Wäldchen & Mäder (2018). Machine learning for image based species identification. *Methods Ecol Evol*. https://doi.org/10.1111/2041-210X.13075. Revisión con checklist de buenas prácticas. **Idea:** seguir su checklist (split por observador, OOS, top-k).
- Villon et al. (2018). A Deep learning method for accurate and fast identification of coral reef fishes in underwater images. *Ecological Informatics*. https://doi.org/10.1016/j.ecoinf.2018.09.007. Comparación con humanos expertos. **Idea:** comparar BioFauna con 2–3 expertos humanos sobre 300 fotos marinas difíciles.

### Invasoras (Cataluña)
- Zenetos et al. (2022). Established non-indigenous species increased by 40% in 11 years in the Mediterranean Sea. *Mediterranean Marine Science*. https://doi.org/10.12681/mms.29106. Inventario de referencia. **Idea:** cruzar nuestra lista con la suya y marcar las especies sin registro previo en Cataluña.
- Azzurro et al. (2019). Climate change, biological invasions, and the shifting distribution of Mediterranean fishes. *Global Change Biology*. https://doi.org/10.1111/gcb.14670. Conocimiento ecológico local. **Idea:** contrastar nuestras fechas de primera observación con las de su encuesta.
- Giovos et al. (2019). Citizen-science for monitoring marine invasions… eastern Mediterranean. *Biological Invasions*. https://doi.org/10.1007/s10530-019-02083-w. **Idea:** cuantificar el adelanto de la detección ciudadana frente a la primera cita formal.
- Larson et al. (2020). From eDNA to citizen science: emerging tools for the early detection of invasive species. *Front Ecol Environ*. https://doi.org/10.1002/fee.2162. **Idea:** sección de “sistema de alerta temprana” con BioFauna más revisión humana.
- Seebens et al. (2017). No saturation in the accumulation of alien species worldwide. *Nature Communications*. https://doi.org/10.1038/ncomms14435. **Idea:** curva de acumulación de primeras observaciones en Cataluña corregida por esfuerzo.

### Declives (Pinna nobilis)
- van Strien et al. (2013). Opportunistic citizen science data… reliable estimates of distribution trends if analysed with occupancy models. *J Appl Ecol*. https://doi.org/10.1111/1365-2664.12158. **Idea:** sustituir el ratio sobre esfuerzo por un modelo de ocupación con longitud de lista.
- Outhwaite et al. (2019). Annual estimates of occupancy… UK, 1970–2015. *Scientific Data*. https://doi.org/10.1038/s41597-019-0269-1. **Idea:** publicar series anuales de ocupación con IC como dataset.
- Vázquez-Luis et al. (2017). S.O.S. Pinna nobilis: A Mass Mortality Event in Western Mediterranean Sea. *Front Mar Sci*. https://doi.org/10.3389/fmars.2017.00220. **Idea:** fecha de referencia para validar la ruptura detectada (~2019) con la cronología documentada.
- Garrabou et al. (2022). Marine heatwaves drive recurrent mass mortalities in the Mediterranean Sea. *Global Change Biology*. https://doi.org/10.1111/gcb.16301. **Idea:** cruzar las rupturas de *Paramuricea* y *Corallium* con los años de ola de calor (2003, 2022…).
- Catanese et al. (2018) ya está citado (https://doi.org/10.1016/j.jip.2018.07.006). La segunda cita del borrador (“Özalp & Kersting-type literature”) es un marcador provisional: hay que comprobarla o sustituirla por Vázquez-Luis 2017.
