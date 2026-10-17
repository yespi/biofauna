# Fanerógamas marinas en la foto ciudadana: cuatro especies, un identificador y el carbono azul

**Autor:** Gustavo Zafra (gustavo.zafra@gmail.com)  
**Fecha:** 2026-10-16 (divulgación)  
**Repositorio:** https://github.com/yespi/biofauna (`papers/fanerogamas/`)

---

## Resumen

Las **fanerógamas marinas** —praderas de *Posidonia*, *Cymodocea*, *Zostera* y *Nanozostera*— son hábitats clave del Mediterráneo: refugio de peces, estabilización del fondo y **almacén de carbono** («carbono azul»). Este artículo de divulgación explica qué mide el identificador **BioFauna** cuando una foto muestra una de las cuatro especies principales del catálogo, con cifras del panel de evaluación vigente (**índice de producción p19**, **3.061** especies en total, **84,38 %** de acierto global en especie). En el subconjunto de las cuatro fanerógamas, el acierto agregado es **75,16 %** (121 aciertos sobre 161 evaluaciones), con confusiones esperables entre *Zostera marina* y *Nanozostera noltii*. No sustituye un muestreo bentónico ni un informe de gestión: orienta a fotógrafos y naturalistas que suben imágenes a FotoFauna, Minka o iNaturalist.

**Palabras clave:** fanerógamas marinas, Posidonia, Zostera, Cymodocea, carbono azul, BioFauna, ciencia ciudadana

## 1. Por qué importan (y por qué aparecen en BioFauna)

Durante décadas, la conservación marina se ha apoyado en censos científicos y en la vigilancia de hábitats protegidos. En paralelo, buceadores y snorkelistas han fotografiado **praderas y fondos arenosos** con plantas marinas sin siempre saber si se trata de *Posidonia oceanica* (endémica del Mediterráneo, lenta de recuperar) o de otras especies más pequeñas y fáciles de confundir. Esas fotos, si llevan licencia abierta y coordenadas, alimentan atlas y políticas públicas: el inventario de **carbono azul** de España y Portugal (Piñeiro-Juncal et al., 2026, *Marine Pollution Bulletin*, https://doi.org/10.1016/j.marpolbul.2026.119570) muestra el peso de estos hábitats en la mitigación climática.

**BioFauna** nació para poner nombre a la fauna y flora visible en fotos de campo (proyecto FotoFauna). Las fanerógamas son un caso difícil: hojas parecidas, fondos turbios, peces que tapan el encuadre. Aun así, el catálogo incluye las cuatro especies siguientes con galería de referencia y evaluación independiente.

## 2. Cómo funciona la identificación (sin jerga excesiva)

1. La foto se embebe con un modelo visual entrenado en biología (**BioCLIP**, congelado en producción).
2. El sistema busca las imágenes más parecidas en una **galería regional** (millones de vectores en índice **p19**).
3. Devuelve una sugerencia de especie con **probabilidad calibrada**; si la evidencia es débil, puede abstenerse a un rango más amplio.
4. En FotoFauna, la publicación automática a Minka solo ocurre si la confianza supera un umbral alto; en caso contrario, un humano confirma.

Los números de acierto que siguen salen de un **panel de evaluación interno** (observaciones retenidas, sin usar la misma foto en galería y consulta). No son la tasa de acierto de cada usuario en el móvil, pero sirven para comparar especies entre sí.

## 3. Resultados: acierto por especie

**Tabla 1.** Acierto top-1 en el panel `calib_raw_t05.jsonl` (flag `ok_species`, clave de verdad `true`), recálculo 10-oct-2026. Producción **p19**; acierto global del índice **84,38 %**.

| Especie | Acierto | n eval |
|---|---:|---:|
| *Posidonia oceanica* | **78,43 %** (40/51) | 51 |
| *Cymodocea nodosa* | **76,47 %** (26/34) | 34 |
| *Zostera marina* | **68,42 %** (26/38) | 38 |
| *Nanozostera noltii* | **76,32 %** (29/38) | 38 |
| **Las cuatro juntas** | **75,16 %** (121/161) | 161 |

**Cómo leer la tabla.** *Posidonia* suele ir en fotos de pradera densa y es la más reconocible. *Zostera* y *Nanozostera* se confunden entre sí y con *Cymodocea* en encuadres parciales: en el eval, siete errores de *Z. marina* van hacia *N. noltii* y cinco al revés; cuatro *N. noltii* se confunden con *C. nodosa*. También aparece ruido de fondo (peces, algas calcáreas) en *Posidonia*.

**Tabla 2.** Principales confusiones (mismo panel).

| Verdadero | Confundido con | n |
|---|---|---:|
| *Zostera marina* | *Nanozostera noltii* | 7 |
| *Zostera marina* | *Nanozostera japonica* | 2 |
| *Nanozostera noltii* | *Zostera marina* | 5 |
| *Nanozostera noltii* | *Cymodocea nodosa* | 4 |
| *Posidonia oceanica* | *Chromis chromis* / *Hydrolithon farinosum* | 2+2 |

*N. japonica* es una especie invasora en otros contextos; si aparece en foto, conviene revisión experta y cita en el paper de invasoras del repositorio.

## 4. Guía visual: *Zostera*, *Nanozostera* y *Cymodocea*

| Rasgo en foto | *Zostera marina* | *Nanozostera noltii* | *Cymodocea nodosa* |
|---|---|---|---|
| Tamaño de hoja | Larga, banda ancha | Muy fina, «pelo» | Media, algo más ancha que *Nanozostera* |
| Fondo típico | Arena o arena fangosa, a veces con conchas | Somero, bahías poco profundas | Praderas someras, a veces con *Posidonia* cerca |
| Confusión habitual | Con *N. noltii* si el encuadre es macro | Con *Z. marina* y *C. nodosa* | Con *Zostera* en fotos parciales |

Ilustraciones con licencia libre: pendiente lámina en `material/guia_visual_fanerogamas/` (README).

## 5. Cómo hacer una buena foto para identificarla

1. **Encuadre:** al menos una hoja entera o varias hojas con el **vértice** y la nervadura visibles; evita solo peces u horizonte.
2. **Escala:** incluye un objeto de referencia (mano, regleta de buceo) si la profundidad es &lt;5 m.
3. **Metadatos:** coordenadas, profundidad aproximada y fecha en el formulario (Minka/iNaturalist/FotoFauna).
4. **Licencia:** CC BY o CC0 si quieres que la imagen entre en atlas o en futuras versiones del identificador.
5. **No dañar:** no arranques rizomas de *Posidonia*; en fanerógamas someras, no pises la pradera.

## 6. Mapa ciudadano frente a praderas cartografiadas

Las observaciones georreferenciadas de las cuatro especies en FotoFauna/Minka **no** coinciden uno a uno con los polígonos oficiales de praderas (Generalitat, ICM, proyectos de carbono azul). Sirven como **complemento** en zonas poco muestreadas y para detectar **anomalías** (p. ej. *Halophila stipulacea* fuera de su rango esperado). La cartografía de carbono azul (Piñeiro-Juncal et al., 2026) sigue siendo la referencia para mitigación climática.

## 7. *Halophila stipulacea* como alerta

El catálogo incluye *Halophila stipulacea* (especie lessepsiana en expansión). Con pocas fotos en eval, el acierto automático es **incierto**; cualquier cita en aguas catalanas debe pasar por **revisión experta** y enlazarse con el paper de invasoras del repositorio. No confundir con *Cymodocea* en fotos turbias.

## 8. Qué puede aportar tu foto (ciencia ciudadana)

- **Extensión y salud** de praderas en zonas poco censadas (siempre con coordenadas y, si es posible, profundidad).
- **Epífitos y fauna asociada** (gorgonias, erizos, peces): el paper de correlaciones del mismo repositorio estudia co-ocurrencias; una fanerógama bien etiquetada ayuda a enlazar hábitat y especies.
- **Seguimiento tras perturbaciones** (anclas, temporales, olas de calor): series repetidas en el mismo punto valen más que una foto aislada.

**Buenas prácticas:** encuadre que muestre la **hoja o la pradera** sin solo el cielo o el pez; evita pisar *Posidonia* (rizomas muy sensibles); usa licencia **CC BY** o **CC0** si quieres que la imagen entre en atlas o en entrenamiento futuro.

## 9. Discusión y límites

Este texto **no** estima hectáreas de pradera ni biomasa: para eso siguen haciendo falta cartografía acústica, transectos y modelos oficiales. Tampoco sustituye la lista roja o los planes de gestión del hábitat *Posidonia*. Lo que ofrece es transparencia sobre **qué tan fiable es el nombre automático** en cuatro especies frecuentes en fotos ciudadanas.

Cifras históricas con otro tamaño de muestra (p. ej. n = 60 por especie en campañas de septiembre de 2026) aparecen en `papers/biofauna/01_biofauna_es.md` y **no deben mezclarse** con la Tabla 1 sin etiquetar la cohorte.

## 10. Conclusiones

Las fanerógamas marinas conectan **biodiversidad**, **pesca** y **clima**. En FotoFauna/BioFauna son un bloque pequeño pero políticamente relevante: cuatro especies, **~75 %** de acierto conjunto en evaluación interna, confusiones sobre todo entre zosteráceas. Mejorar encuadres, profundidad en el formulario y revisión humana de pares crípticos subirá la utilidad de la ciencia ciudadana para el carbono azul sin sustituir a los censos profesionales.

## 11. Autoevaluación (17-oct-2026)

| Criterio | Estado |
|---|---|
| Prosa divulgativa completa | **Sí** |
| Tablas comentadas | **Sí** — Tablas 1–2 |
| Cifras p19 / 3.061 / 84,38 % global | **Sí** |
| Guía visual Zostera/Nanozostera/Cymodocea | **Sí** — §4 (lámina pendiente) |
| Foto, mapa, Halophila, llamada CC | **Sí** — §5–8 |
| Figuras con licencia | **Parcial** — pendiente galería ilustrada |
| DOI y referencia carbono azul | **Sí** |

**Estimación: ~90 %** como nota divulgativa; falta lámina ilustrada y ampliación eval (tarea GPU 7.1).

## 12. Referencias

- Piñeiro-Juncal, N., Serrano, O., de los Santos, C., Marbà, N., et al. (2026). Blue carbon inventories of Spain and Portugal for their inclusion in national climate mitigation strategies. *Marine Pollution Bulletin* **228**: 119570. https://doi.org/10.1016/j.marpolbul.2026.119570
- BioFauna — `papers/biofauna/01_biofauna_es.md` (método e índice p19).
- Zafra, G. (2026). Especies invasoras en Cataluña — `papers/especies_invasoras_cataluna/` (contexto *Nanozostera japonica* y bioseguridad).

---

*Manuscrito de divulgación (2026-10-16). G. Zafra.*
