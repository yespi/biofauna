# BioFauna — Especies pendientes de escanear de las guias

> **Fecha**: 2026-08-11 | **Contexto**: VLM re-ranker probado con exito (66.7% vs 0% k-NN)
> **Metodo**: Minicpm-v recibe imagen + descripcion sintetizada de la guia → elige entre par criptico

## Prioridad 1 — Salvador (nudibranquios y babosas de mar)

Guia: `salvador_guia_escaneada.pdf` (73 MB) o `salvador_2022_csic.pdf` (5 MB)
Ya procesadas: 311 paginas, 161 especies indexadas.

**Falta la ficha de estas especies** (probablemente estan en la guia pero no en el indice que encontramos):

| Especie | Grupo | Pagina estimada |
|---------|-------|-----------------|
| doridicola_agilis | ¿copepodo/nudibranquio? | Buscar en Salvador |
| creseis_acicula | pteropodo | Buscar en Salvador |

(Nota: phorbas_fictitius NO esta en Salvador — es una esponja, no un nudibranquio)

## Prioridad 2 — Invertebrats Vall de Ridaura

Guia: `invertebrats_vall_ridaura.pdf` (13 MB) — guia general de invertebrados marinos
Ya procesadas: paginas de indice/checklist (solo nombres, sin descripciones)

**Falta la ficha descriptiva de estas especies:**

| Especie | Grupo | Notas |
|---------|-------|-------|
| calliactis_palliata | anemona | Simbiosis con cangrejo ermitano |
| calliactis_parasitica | anemona | Simbiosis con cangrejo ermitano |
| eunicella_verrucosa | gorgonia | Par criptico con E. gazella |
| donax_venustus | bivalvo | Par criptico con D. semistriatus |
| phorbas_fictitius | esponja | Par criptico con H. columella |
| hemimycale_mediterranea | esponja | Par criptico con H. columella |
| holothuria_tubulosa | holoturia | Par criptico con H. poli |
| oscarella_viridis | esponja | Par criptico con O. lobularis |
| aplidium_asperum | ascidia | |
| fasciospongia_cavernosa | esponja | |
| golfingia_vulgaris | sipunculido | |
| neotima_lucullana | hidrozoo | |
| synarachnactis_lloydii | cnidario | Par criptico con P. solitarius |

## Prioridad 3 — Otras guias (algas, peces, fanerogamas)

Estas especies NO estan en las guias de invertebrados. Necesitan sus propias guias:

| Especie | Grupo | Guia necesaria |
|---------|-------|----------------|
| amphiroa_rubra | alga roja | Algues Ridaura / Flora |
| chrysonephos_lewisii | alga | Algues Ridaura / Flora |
| corallina_officinalis | alga roja | Algues Ridaura / Flora |
| gongolaria_elegans | alga parda | Algues Ridaura / Flora |
| halopteris_filicina | alga parda | Algues Ridaura / Flora |
| hypnea_musciformis | alga roja | Algues Ridaura / Flora |
| jania_adhaerens | alga roja | Algues Ridaura / Flora |
| jania_virgata | alga roja | Algues Ridaura / Flora |
| mugil_cephalus | pez | FAO Fish Guide |
| sprattus_sprattus | pez | FAO Fish Guide |
| zostera_marina | fanerogama | Flora / Algues |

## Resumen

| Prioridad | Especies | Guia | Estado |
|-----------|----------|------|--------|
| YA LISTAS | 2 (haminoea, doto) | Salvador | VLM test 66.7% ✅ |
| P1 - Salvador | 2 (doridicola, creseis) | Salvador | Buscar pagina |
| P2 - Invertebrats | 13 | Vall Ridaura | Necesita fichas |
| P3 - Otras guias | 11 | Algas/Peces | Guias separadas |
