# Discusión — Invasoras en Cataluña

## Qué muestran los datos

De **114** especies de la lista interna, **35** tienen al menos una observación en Cataluña y **52** en España (máximo entre fuentes; `presencia_cat_es.csv`). La mayoría (**79**) aparecen como **ausentes** en la caja combinada — coherente con lista UE amplia y cobertura desigual: muchas invasoras dulceacuícolas o terrestres no están en el foco del buceo costero.

El único taxon marino de la lista UE con presencia clara en CAT en este cruce es ***Rugulopteryx okamurae*** (101 obs iNat en la tabla top-15). El resto de invasoras «visibles» en costa son sobre todo **terrestres** (*Ailanthus*, *Vespa velutina*…) o **agua dulce** (*Procambarus clarkii*, *Gambusia holbrooki*).

## Esfuerzo y series temporales

La curva de observaciones en BioQuest dentro de la caja CAT (**820** obs en 2013 → **102.301** en 2024; SQL §1) explica picos aparentes en especies muy observadas (*Ailanthus*, *Myocastor*). Las tasas normalizadas (§5) atenúan pero no eliminan el sesgo taxonómico (plantas y aves mejor muestreadas que peces invasores).

## Exóticas marinas fuera de la lista UE

El bloque Weitzmann (§11 de `RESULTADOS_v1.md`) muestra un patrón distinto: especies **no nativas** ya documentadas en iNat (p. ej. *Oculina patagonica* primera iNat CAT **2011-08-15**, n=126) mientras la primera foto enlazada en galería BF en CAT es **2017-08-15** (n=793 en enrich) — retraso esperable entre primer registro ciudadano y entrada en cosecha/índice BioFauna.

*Caulerpa cylindracea* alinea mejor iNat (**2014-11-11**) y BF (**2014-08-05**); BioQuest Minka registra actividad desde **2014-08** (384 obs en caja). *Zebrasoma flavescens* y *Balistoides conspicillum* tienen primeras iNat en CAT pero **0** fotos enlazadas BF en la caja: exóticas de acuario, útiles como alerta pero fuera del índice actual.

## Limitaciones

1. BioQuest Academy no descarga la lista UE entera (**3** de 114 con filas directas en `public_observations` para taxones UE).
2. Caja Minka ≠ límites administrativos.
3. Categorías operativas ≠ estatus legal / EASIN.
4. Origen y vector solo cuando existen en `academy_invasive` (**4** especies).
5. Primera foto BF = proxy por metadatos enrich; no sustituye revisión taxonómica de primer registro oficial.

## Próximos pasos

- Completar origen/vector vía EASIN y literatura primaria por especie.
- Integrar mapas con límites administrativos y capas de hábitat.
- Ampliar bloque marino con las **142** especies doridoideas del catálogo vivo ausentes del calendario corto de 133 nudibranquios (tarea paralela nº 5 del plan de papers).
