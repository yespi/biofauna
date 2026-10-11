# Nativas en expansión (termófilas / «nativas invasoras»)

**Generado:** 2026-10-11 ~11:58 CEST (Cursor papers4). **Sin GPU.**  
**Método compartido con el paper de declives:** `scripts/tendencias_esfuerzo_nativas_declives_20261011.py`.  
**CSV:** [`nativas_expansion_tendencias_20261011.csv`](material/nativas_expansion_tendencias_20261011.csv) · meta [`meta_nativas_20261011.json`](meta_nativas_20261011.json).

## 1. Pregunta

¿Hay especies **nativas** (o antiguas en el Mediterráneo) cuya tasa de detección en Cataluña, **corregida por esfuerzo**, sube más que un panel de controles de la misma caja? Es el espejo del análisis de declives: mismas ventanas (2015–2019 vs 2020–2024), misma caja y mismas series de esfuerzo.

## 2. Método (corregido por esfuerzo + controles)

1. Esfuerzo anual = filas de `public_observations` en caja CAT (lat 40,45–42,95; lon 0,10–3,40): **1.220** (2013) → **102.301** (2024).
2. Tasa especie-año: `obs_especie_año / esfuerzo_año × 1000`.
3. `ratio_5y` = media tasa 2020–2024 / media 2015–2019.
4. Panel de controles (peces/invertebrados comunes de la misma caja): media `ratio_5y` = **2,398**.
5. `ratio_vs_controls` = `ratio_5y` / 2,398.  
   - ≥ 1,15 → **expansión relativa**  
   - ≤ 0,35 → declive relativo (temporal / semipermanente / permanente según residual)  
   - ~0,9–1,15 → coherente con el aumento general de cobertura ciudadana

**Limitación:** el esfuerzo crece ~84× (2013→2024). Un `ratio_5y` > 1 **sin** comparar con controles refleja sobre todo más ojos y apps, no necesariamente más individuos. Por eso la columna operativa es `category_vs_controls`.

## 3. Resultados (caja Cataluña)

| Especie | n CAT | ratio_5y | vs controles | Categoría relativa | Nota |
|---|---:|---:|---:|---|---|
| *Thalassoma pavo* | 6.125 | 2,88 | **1,20** | **expansión relativa** | Termófilo; coherente con ClimateFish ([DOI](https://doi.org/10.3389/fmars.2022.910887)) |
| *Sparisoma cretense* | 27 | — | — | dato escaso / primeras citas | Solo desde 2021 en BQ; **hipótesis** de llegada termófila |
| *Epinephelus costae* | 127 | 1,88 | 0,78 | por debajo de controles | Sube en bruto, no supera el panel |
| *Arbacia lixula* | 2.914 | 2,10 | 0,87 | por debajo de controles | Aumento bruto; no expansión relativa |
| *Paracentrotus lividus* | 5.280 | 1,41 | 0,59 | declive leve relativo | Contraste erizos: *Arbacia* crece más que *Paracentrotus* en bruto |
| *Caulerpa cylindracea* | 402 | 1,97 | 0,82 | por debajo de controles | **Invasora** (contraste); ver ORIGEN/vías |
| *Rhizostoma pulmo* | 1.468 | 1,17 | 0,49 | declive leve relativo | Sin señal de «bloom» relativo |
| *Cotylorhiza tuberculata* | 1.216 | 1,19 | 0,50 | declive leve relativo | Idem |
| *Pelagia noctiluca* | 444 | 0,56 | 0,23 | declive temporal relativo | No expansionista en este proxy |
| *Sphyraena viridensis* | 1.192 | 0,76 | 0,32 | declive temporal relativo | Contrasta con narrativa termófila simple |

Figuras: `material/figuras/nativa_trend_*.png`, `material/figuras/nativa_presabs_*.png`.

## 4. Lectura crítica

1. **Solo *Thalassoma pavo* supera claramente el panel de controles** entre las nativas/termófilas con n suficiente. Eso es compatible con el seguimiento ClimateFish de peces termófilos ([Coronado-Franco / ClimateFish 2022](https://doi.org/10.3389/fmars.2022.910887)).
2. *Sparisoma cretense* aparece tarde y con n=27: útil como **alerta temprana candidata**, no como tendencia robusta.
3. Las medusas del listado **no** muestran expansión relativa en ciencia ciudadana corregida; afirmar blooms regionales exigiría series independientes (redes de monitoreo) — aquí queda como **hipótesis no respaldada** por este proxy.
4. *Caulerpa cylindracea* (invasora) tampoco supera el umbral relativo 1,15: la expansión espacial documentada en literatura ([García et al. 2015](https://doi.org/10.1007/698_2015_411); mapas 5 años del paper) puede coexistir con un ratio temporal moderado una vez densificada.

## 5. Bibliografía (DOI verificados Crossref 11-oct-2026)

- ClimateFish (2022). https://doi.org/10.3389/fmars.2022.910887  
- García, M., Weitzmann, B., et al. (2015). https://doi.org/10.1007/698_2015_411  
- Katsanevakis et al. (2013) pathways. https://doi.org/10.1016/j.ocecoaman.2013.02.024  
- Serrano et al. (2013) *Oculina*. https://doi.org/10.1371/journal.pone.0052739  
