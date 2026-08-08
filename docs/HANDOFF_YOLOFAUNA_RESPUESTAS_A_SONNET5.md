# Respuesta a Sonnet 5 — Análisis del Handoff YOLOFauna

> 2026-08-08. Respuesta de Yespi/Gustavo al análisis de Sonnet 5 sobre HANDOFF_YOLOFAUNA_COMPLETO.md

## 1. Versión del documento analizado

Sonnet 5 leyó el handoff del **6 de agosto**, que refleja el estado PRE-ViT-H (baseline 63.8% con BioCLIP-2 ViT-L). Desde entonces hemos avanzado significativamente. El handoff actualizado (2026-08-08) está en el mismo directorio.

## 2. Puntos con los que CONCUERDO y aplico

### 2.1 Deduplicación de fotos casi-idénticas
**Estado**: NO probado.  
**Plan**: Detectar ráfagas (misma especie, misma observación iNat/Minka, similitud coseno >0.99) y colapsarlas antes del k-NN. En 550K fotos hay ráfagas seguro.  
**Prioridad**: Alta.

### 2.2 Fallback jerárquico (especie → género → familia)
**Estado**: Parcial. Actualmente si p<0.90 se abstiene o cae en iNat.  
**Plan**: Si especie no llega al umbral pero género sí (umbral más bajo, ej. p≥0.70), devolver género. Si familia llega, devolver familia. Esto aumentaría la cobertura útil del 30% actual sin bajar la precisión de especie.  
**Prioridad**: Alta.

### 2.3 Macro-F1 y accuracy por especie
**Estado**: Solo reportamos top-1 global.  
**Plan**: Añadir al informe de calibración accuracy desglosada por especie, macro-F1, y métricas por "tier" (número de fotos en training). Esto revelará dónde falla el modelo realmente.  
**Prioridad**: Alta.

### 2.4 k adaptativo
**Estado**: k=25 fijo. El weighted k-NN se probó y falló.  
**Plan**: Revisar POR QUÉ falló weighted k-NN (probablemente mala implementación). Probar k variable según densidad: k=10 para especies con >1000 fotos, k=50 para especies con <50 fotos.  
**Prioridad**: Media.

### 2.5 Limpieza de etiquetas (confident learning)
**Estado**: NO probado. Asumimos que Minka/iNat son ground truth perfecto.  
**Plan**: Aplicar confident learning sobre los 550K embeddings: detectar muestras cuyo k-NN mayoritario contradice la etiqueta original. Revisar y corregir. Esto puede subir accuracy sin tocar el modelo.  
**Prioridad**: Media.

## 3. Puntos con los que DISCREPO o matizo

### 3.1 "Dejar de tocar el modelo y centrarse 100% en datos"
**Discrepo parcialmente**. El cambio de BioCLIP-2 ViT-L a ViT-H nos dio **+6.8pp** (63.8% → 70.6%). El encoder SÍ importa. Pero estoy de acuerdo en que a partir de ~70% el retorno de invertir en datos es mayor que en arquitectura. La evidencia de 9 experimentos fallidos es sólida para ViT-L, pero hay que re-evaluar en ViT-H.

### 3.2 "El nombre YOLOFauna es engañoso"
Es el nombre histórico del proyecto. No hay YOLO en el stack actual, pero es la marca que usamos internamente. No voy a cambiarlo. Añadiré una nota aclaratoria en el README.

### 3.3 "k=25 fijo es subóptimo y el weighted k-NN merece revisión"
Estoy de acuerdo en que merece revisión. Pero "weighted k-NN falló" está documentado como experimento #8 de 9 fallidos. Antes de repetirlo, quiero entender por qué falló exactamente (¿inversión de pesos? ¿normalización incorrecta?).

## 4. Puntos que POSPONGO

### 4.1 Tracking de experimentos (W&B/MLflow)
Útil, pero no prioritario ahora. Tenemos 13 experimentos documentados en markdown. Con 1-2 experimentos por semana, el coste de migrar a W&B no se justifica todavía.

### 4.2 Licencias CC de iNat/Minka
No planeamos publicar el dataset a corto plazo. Si algún día lo hacemos, será un problema real. Pero ahora mismo es prematuro.

### 4.3 Mecanismo de auditoría AutoID
Sabemos que el 5% de AutoID son errores. No hay mecanismo automático de auditoría. Pero los expertos de Minka corrigen identificaciones, y ese feedback ya se recoge (la repesca diaria incluye correcciones de curadores). No es un sistema formal pero existe.

## 5. Puntos que YA están corregidos o superados

### 5.1 "63.4% accuracy"
Era el baseline con ViT-L. Ahora estamos en **70.6%** con ViT-H. El handoff del 6 de agosto está desactualizado.

### 5.2 Inconsistencia "429 vs 2,261 crops"
Error de redacción del documento viejo. Ya corregido en el handoff de hoy. Los 429 crops etiquetados son de fuentes diversas (no solo OCR). Los 2,261 son el total extraído de todas las guías.

### 5.3 Sección 10.6 "NO APLICA"
Corregido. La redacción era confusa. El embedding service (:8090) está en red Docker interna. La API pública (:3005) tiene Google OAuth. Sí aplica, y está mitigado.

## 6. Resumen: qué entra en el plan AHORA

| Prioridad | Tarea | Tipo |
|-----------|-------|------|
| 🔴 AHORA | Terminar re-embedding ViT-H | Infra |
| 🔴 AHORA | Triplet loss ViT-H + recalibrar | Modelo |
| 🟡 PRONTO | Deduplicación dataset | Datos |
| 🟡 PRONTO | Fallback jerárquico (especie→género→familia) | Producto |
| 🟡 PRONTO | Macro-F1 por especie | Métrica |
| 🟢 DESPUÉS | k adaptativo | Modelo |
| 🟢 DESPUÉS | Confident learning (limpieza etiquetas) | Datos |
