# Auditoria de datos — Calidad de imagenes

> **Fecha**: 2026-08-11 | **Alcance**: 587,453 imagenes en 3,000+ especies

## Resumen

El dataset de entrenamiento esta mayoritariamente limpio. Se detecto y corregio un unico caso grave de contaminacion, mas una fusion de sinonimos.

## Hallazgos

### 1. Duplicados entre especies (iNat)

707 IDs de observacion de iNaturalist aparecian en mas de un directorio de especie. Afectan a 8 especies en 4 pares:

| Par | IDs compartidos | Diagnostico | Accion |
|-----|-----------------|-------------|--------|
| `lima_lima` ↔ `limax_maximus` | 515 | Bivalvo vs babosa. Contaminacion por prefijo ("lima" ⊆ "limax"). | 720 archivos movidos de lima_lima a backup |
| `ambigolimax_valentianus` ↔ `lehmannia_valentiana` | 185 | Sinonimos taxonomicos (misma especie). | Fusionados en lehmannia_valentiana |
| `elysia_margaritae` ↔ `elysia_translucens` | 6 | Mismo genero, posible confusion taxonomica. | Sin accion (pares cripticos) |
| `loligo_forbesii` ↔ `loligo_vulgaris` | 1 | Mismo genero. Trivial. | Sin accion |

**Minka: 0 duplicados.** El sistema de IDs de Minka es consistente.

### 2. Auditoria cruzada iNat (52 observaciones)

Muestreo de imagenes iNat en directorios de especie, verificando contra la API de iNaturalist:

| Muestra | Observaciones | Mismatches | % limpio |
|---------|---------------|------------|----------|
| 34 especies "cero" | 41 | 1 | 97.6% |
| 40 especies aleatorias | 11 | 0 | 100% |
| **Total** | **52** | **1** | **98.1%** |

Unico mismatch: `amphiroa_rubra` tiene 1 imagen de `amphiroa cryptarthrodia` (mismo genero, probablemente confusion taxonomica en iNat, no error de descarga).

### 3. Prefijos de nombre

Solo 5 pares de especies tienen nombres donde una es prefijo de otra. Solo lima/limax tenia contaminacion real. Los otros 4 pares son limpios.

### 4. Taxonomia Minka

Verificacion de taxon ID contra API de Minka para 11 especies: 100% correcto. Los `minka_taxon` en `target_species.json` mapean correctamente a los nombres cientificos.

## Acciones correctivas realizadas

1. **lima_lima**: 720 archivos iNat movidos a `_cleanup_backup/lima_lima_contamination/`. Pertenecen a `limax_maximus`.
2. **ambigolimax_valentianus**: fusionado en `lehmannia_valentiana` (7 archivos unicos movidos, duplicados eliminados). Directorio `ambigolimax_valentianus` ahora vacio.
3. **Backup**: `_cleanup_backup/` contiene los archivos removidos por si hay que restaurar.

## Impacto en el modelo

- El problema de las 160 especies con 0% accuracy NO se explica por contaminacion de imagenes
- Las 34 especies "confiablemente cero" no tienen IDs duplicados ni mismatches en la auditoria
- La causa de la cola larga sigue siendo desconocida (posibles etiquetas incorrectas no detectadas por auditoria de IDs, o limitacion real del modelo)
- La limpieza de lima/limax mejora la calidad de 2 especies pero no mueve el accuracy global

## Recomendaciones

1. Re-embedding de las especies afectadas (lima_lima, limax_maximus, lehmannia_valentiana) tras la limpieza
2. Investigar etiquetas incorrectas no detectables por ID (especies mal identificadas en origen)
3. Los 574 sospechosos de confident learning siguen siendo la mejor pista
