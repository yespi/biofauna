# Nudibranquios del Mediterráneo: asociaciones con presas y sustrato a partir de fotografías de ciencia ciudadana, y acierto de un identificador automático

**17-oct-2026.** Estado: introducción, métodos y resultados de identificación completos; resultados de asociaciones **pendientes del análisis del escaneo** (ver §3.3); discusión esquemática. Autoría y agradecimientos: por completar. Revista objetivo: *Journal of Molluscan Studies* (peso en asociaciones) o *Ecological Informatics* (peso en el identificador).

> Reglas de redacción: no citar rutas internas ni notas entre agentes; toda cifra con su n; toda cita con fuente verificada (las no verificadas se marcan **[VERIFICAR]**).

## Resumen (borrador)
Los nudibranquios son depredadores especialistas cuya dieta se conoce, sobre todo, por observación directa y estudios puntuales. Las plataformas de ciencia ciudadana acumulan cientos de miles de fotografías que podrían documentar esas relaciones a gran escala, pero dos obstáculos lo impiden: identificar con fiabilidad al nudibranquio y a su presa, y distinguir convivencia de interacción. Evaluamos un identificador (BioCLIP-2.5 con recuperación k-NN y calibración jerárquica) sobre **6.927 fotografías de evaluación de 342 especies de Nudibranchia *s. l.*** (acierto de especie **86,5 %**, IC 95 % Wilson 85,7–87,3; género 92,5 %; familia 94,7 %), y mostramos que el resultado depende fuertemente del tamaño de la referencia y de la fuga entre galería y evaluación (**83,6 %** al excluir las filas con similitud ≥ 0,95 con la galería de su especie). Proponemos un criterio estricto de asociación —ambas especies visibles en la misma fotografía, con exclusión de la misma observación/observador/día— y lo aplicamos a 25 nudibranquios y 61 presas/sustratos candidatos. [RESULTADOS DEL ESCANEO: pendientes.]

## 1. Introducción
1. Nudibranquios: especialización trófica, dieta ligada a esponjas, hidrozoos, briozoos, ascidias, algas (revisiones de dieta: McDonald & Nybakken, serie *A worldwide review of the food of nudibranch mollusks*, *The Veliger* — **[VERIFICAR]** parte, año y páginas de Doridacea y Aeolidacea; solo se han confirmado las partes I, Arminacea 1997, y Dendronotacea 1999).
2. Casos de referencia mediterráneos: *Peltodoris atromaculata* sobre *Petrosia ficiformis* (Avila 1996, *J. Molluscan Stud.* 62:151–157, doi:10.1093/mollus/62.2.151); *Cratena peregrina* sobre *Eudendrium racemosum* con kleptopredación (Martin et al. 2003, *Mar. Biol.* 143:533–541, doi:10.1007/s00227-003-1078-8 sobre nematocistos; Willis et al. 2017 **[VERIFICAR]**).
3. Ciencia ciudadana (Minka SDG, iNaturalist, GBIF): volumen y sesgos (esfuerzo estival, observadores costeros, fotografía macro centrada en el animal).
4. Problema: identificar presas por foto (esponjas, hidrozoos, briozoos) es poco fiable incluso para expertos. **Hipótesis H1:** la co-aparición en la misma fotografía, con presas a nivel de género/familia, recupera las asociaciones conocidas con una precisión estimable frente a una tabla de referencia. **H2:** el acierto del identificador en nudibranquios es comparable al del resto de heterobranquios y cae con n de referencia pequeño y en pares crípticos. **H3:** la fuga galería↔evaluación infla el acierto en una magnitud medible.
5. Objetivos: (a) acierto del identificador con IC por especie y control de fuga; (b) tabla de referencia de dietas; (c) cribado de asociaciones por misma foto con exclusión de no independencia.

## 2. Métodos
### 2.1 Fuentes y ámbito
Galería ≈ 1,29 M vectores / 3.066 especies (Minka SDG, iNaturalist, GBIF, Wikimedia Commons, DORIS, SeaSlugForum, WoRMS). Nudibranchia *s. l.* = órdenes *Nudibranchia* + *Doridida* del linaje de Minka (342 especies del catálogo, **globales**). **Pendiente:** filtrar al Mediterráneo con WoRMS (ámbito del título); las métricas actuales no están restringidas.
### 2.2 Identificador
Embeddings BioCLIP-2.5 ViT-H/14, k-NN sobre FAISS, calibración jerárquica; salida: especie/género/familia con umbral de abstención. Evaluación: conjunto congelado de 64.343 filas (3.082 especies; hash en el registro del proyecto), fotos retenidas fuera de la galería.
### 2.3 Métricas
Acierto por especie con IC 95 % de Wilson; acierto de género y familia; matriz de confusión intra-*Nudibranchia*; estratificación por n de la especie en la evaluación (<10, 10–29, ≥30) y por pertenencia a pares crípticos (`cryptic_pairs`); acierto de nudibranquios frente al resto de heterobranquios.
### 2.4 Control de fuga
Fila con fuga = similitud coseno ≥ 0,95 entre su embedding y algún vector de la galería de su especie. Además, auditoría previa del conjunto: 0 rutas, 0 hashes y 0 observaciones compartidas evaluación↔galería. Se reporta el acierto con y sin fuga.
### 2.5 Tabla de referencia (*gold*) de dietas
25 nudibranquios de la lista corta; para cada uno, presa/sustrato, nivel taxonómico, tipo de relación (predación, kleptopredación, sustrato) y **fuente primaria verificada**; sin fuente verificada = «sin verificar» y no entra en el cálculo de precisión. `datos/nudi_dietas_gold.csv`.
### 2.6 Cribado de asociaciones por misma fotografía
1) Lista corta de 150 parejas (cribado por eventos observador × ~1 km × día × 3 h; solo propone). 2) Por especie, hasta 60 fotos de la galería, 5 vistas (entera y cuatro cuadrantes), embedding y búsqueda de 300 vecinos. 3) Candidata si la otra especie aparece con similitud ≥ 0,82 (≥ 0,86 como primera). 4) **Exclusión de no independencia:** se descarta la candidata si la otra especie tiene en la galería una foto de la misma observación o del mismo observador y día. 5) Presa evaluada a **género/familia**, no a especie, salvo confirmación experta. 6) Revisión visual ciega por ≥ 2 personas, κ de Cohen; muestra aleatoria de candidatas para falsos positivos. 7) Niveles: 0 co-ocurrencia; 1 misma foto en ≥ 3 observaciones independientes; 2 contacto visible (sobre, alimentándose). **Interpretación de ausencias:** la ausencia de la presa en la foto no es informativa (macro, presa recortada); solo se reportan presencias.
### 2.7 Licencias y figuras previstas
Solo CC0, CC BY, CC BY-SA para publicación; las CC BY-NC (†) deben sustituirse o contar con permiso. Figuras: F1 flujo metodológico; F2 acierto por especie con IC frente a n; F3 matriz de confusión intra-*Nudibranchia* (familias principales); F4 acierto con/sin fuga; F5 red de asociaciones confirmadas (nivel ≥ 1); F6–F8 láminas de las asociaciones nivel 2 (con autor, licencia, fecha, lugar y enlace por foto).

## 3. Resultados
### 3.1 Identificación (evaluación congelada, 6.927 filas de 342 especies)
| Medida | n | Acierto | IC 95 % Wilson |
|---|---:|---:|---|
| Especie, Nudibranchia *s. l.* | 6.927 | 86,5 % | 85,7–87,3 |
| Género | 6.927 | 92,5 % | — |
| Familia | 6.927 | 94,7 % | — |
| Resto de heterobranquios | 4.836 | 82,1 % | 81,0–83,2 |
| Todo el conjunto | 64.343 | 84,4 % | — |

Estratificación por n en evaluación: **n < 10** (59 especies, 313 filas) 63,3 % (57,8–68,4); **10–29** (172 spp, 3.284) 82,7 % (81,4–84,0); **≥ 30** (111 spp, 3.330) 92,5 % (91,5–93,3). 91 de 342 especies tienen el límite inferior del IC < 50 %: el n pequeño impide afirmar su acierto individual. **Lista corta (25 nudibranquios):** 584 filas, 90,8 % (88,1–92,8). Pares crípticos: 85,6 % (n = 2.770) frente a 87,1 % (n = 4.157) en no crípticos; la diferencia es pequeña (**[VERIFICAR]** con prueba de diferencia de proporciones antes de interpretarla).
Tabla completa por especie: `datos/nudi_acierto_por_especie.csv`.

### 3.2 Confusiones y fuga
Errores: 933. **786 (84 %) caen dentro de Nudibranchia *s. l.*; 416 (45 %) en el mismo género y 564 (60 %) en la misma familia.** Confusiones más frecuentes: *Amphorina andra*↔*A. farrani* (12), *Trinchesia caerulea*↔*T. cuanensis* (11), pares de *Doto* (*D. eireana, D. coronata, D. maculata, D. millbayana…*), *Aeolidia papillosa*↔*A. filomenae* (6), *Rubramoena amoena*↔*R. rubescens* (4). Los 147 errores fuera del grupo se reparten sobre todo entre briozoos/hidrozoos con aspecto similar y otros heterobranquios. Tabla: `datos/nudi_confusion_intra.csv`.
**Fuga:** 1.348 de 6.927 filas (19,5 %) tienen similitud ≥ 0,95 con la galería de su especie; su acierto es 98,8 % (98,1–99,3), frente a **83,6 % (82,6–84,5)** de las 5.579 filas sin fuga. Esta es la cifra honesta para fotos nuevas. (Auditoría de conjunto: 0 rutas/hashes/observaciones compartidas; máximo coseno con un vector de galería 0,996 en nudibranquios.) `datos/nudi_fuga.json`.

### 3.3 Asociaciones
Escaneo de segunda especie sobre 86 especies (25 nudibranquios + 61 presas/sustratos; 60 fotos × 5 vistas por especie; 17-oct-2026). Se evaluaron 150 pares candidatos; **48** produjeron al menos una candidata bruta (341 candidatas) y **47** conservaron alguna tras excluir no independencia (302 candidatas: 0 misma observación, 33 mismo observador y día, 6 sin trazabilidad a observación). **19** pares reúnen ≥ 3 observaciones independientes. Restringiendo a la vista completa con similitud ≥ 0,95 (207 candidatas, criterio más conservador), **11 de 17** pares con candidatas conservan ≥ 3 observaciones. Las vistas por recorte (esquinas; 95 candidatas, similitud típica 0,84–0,89) son más ambiguas y no deben contarse como evidencia.

Pares con más observaciones independientes (`datos/copresencia_nudi_pares_20261017.csv`): *Peltodoris atromaculata*–*Petrosia ficiformis* (39), *Idaliadoris neapolitana*–*Schizobrachiella sanguinea* (39), *P. atromaculata*–*Lithophyllum stictiforme* (38), *P. atromaculata*–*Axinella damicornis* (21), *Tylodina perversa*–*Aplysina aerophoba* (20), *P. atromaculata*–*Crambe crambe* (20), *Felimare picta*–*Amphiroa beauvoisii* (17), *Cratena peregrina*–*Crambe crambe* (10). Recall frente a la tabla *gold*: la pareja con cita verificada (*Peltodoris*→*Petrosia*, Avila 1996) se recupera; el resto de la tabla está «sin verificar», por lo que **no se calcula recall global** (pendiente de completar fuentes).

**Revisión visual (preliminar, no exhaustiva):** muestra aleatoria de 12 candidatas independientes (semilla 1) examinadas en montaje. Las 8 de vista completa muestran de forma plausible ambos taxones en la escena; 2 de las 4 de recorte (oscuras, similitud 0,84–0,86) no permiten confirmar la presa. No se estima aún una tasa de falsos positivos con IC: requiere una muestra mayor y revisión por un especialista (**[VERIFICAR]**). Aviso: pares como *Peltodoris*–*Lithophyllum* o *Idaliadoris*–*Schizobrachiella* indican **co-presencia/sustrato**, no depredación. Limitación: el índice FAISS no conserva el vínculo vector→observación; la exclusión se aplica solo sobre las candidatas.

## 4. Discusión (esquema)
- Identificación: ≈ 84 % sin fuga; los errores son mayoritariamente intragénero/intrafamilia, esperables por la taxonomía críptica; las especies con n pequeño no admiten conclusiones individuales.
- Asociaciones: solo presencia; niveles de evidencia; no se afirma depredación sin nivel 2 y fuente.
- Limitaciones: sesgo de esfuerzo estival/costero; presa a género/familia; ámbito no restringido aún al Mediterráneo; galería con fotos CC BY-NC; la fuga residual en el escaneo (vectores sin trazabilidad a observación en el índice) se controla solo a nivel de candidata.
- Datos y código: repositorio público `yespi/biofauna`; DOI de la versión congelada: **pendiente (Zenodo)**.

## Bibliografía (solo ítems verificados o marcados)
- Avila, C. (1996). The growth of *Peltodoris atromaculata* Bergh, 1880 (Gastropoda: Nudibranchia) in the laboratory. *J. Molluscan Stud.* 62:151–157. doi:10.1093/mollus/62.2.151 — verificado (Crossref).
- Martin et al. (2003). Management of nematocysts in the alimentary tract and in cnidosacs of the aeolid nudibranch gastropod *Cratena peregrina*. *Mar. Biol.* 143:533–541. doi:10.1007/s00227-003-1078-8 — existencia verificada (Crossref); **[VERIFICAR]** lista completa de autores.
- McDonald, G. R., & Nybakken, J. W. A worldwide review of the food of nudibranch mollusks. *The Veliger* — **[VERIFICAR]** partes y años.
- Willis et al. 2017 (SZN) — **[VERIFICAR]** título, revista y DOI (el PDF no se pudo abrir).
