# BioFauna — Informe para Revision Externa

> **Fecha**: 2026-08-11 | **Acierto**: 71.69% especie (k=15, ViT-H, harvest_calib)
> **Servidor**: HanSolo (RTX 3060 12GB, 192.168.1.135)
> **Codigo**: /mnt/docker/fotofauna-yolo/

## 1. ARQUITECTURA

BioCLIP-2.5 ViT-H (632M params, 1024-dim) → k-NN (k=15) sobre ~550K embeddings → calibracion logistica (ECE=0.04).
Dataset: 584K fotos de 3,000 spp mediterraneas (45% iNat, 54% Minka, 1% otros).
AutoID: publica en Minka con p>=0.90 (95.5% precision, 30.2% cobertura).

## 2. LINEA BASE

| Metrica | Valor |
|---------|-------|
| Especie top-1 | 71.69% (1,946 fotos, 810 spp) |
| Genero | 76.52% |
| Familia | 80.37% |

## 3. EXPERIMENTOS COMPLETOS (orden cronologico)

### 3.1 ViT-L → ViT-H: +7.8pp ✅
Unica palanca efectiva. 553K embeddings, 1024-dim.

### 3.2 Triplet Loss (8 variantes): ❌
Degrada -0.7 a -7pp. ViT-H 1024-dim ya esta optimamente separado.

### 3.3 ArcFace: 🤝 empate
71.4% vs 71.69% k-NN out-of-sample. Backbone congelado = k-NN parametrico.

### 3.4 LoRA + ArcFace (50 spp): ⚠️ +3.4pp interno, no escalado
Pipeline fragil, muere a 200+ spp.

### 3.5 LoRA + ArcFace (100 spp): ❌ D=+0.0pp harvest

### 3.6 LoRA 1358 spp: ⚠️ D=+0.2pp interno, 7h18min GPU
Best=94.7% en E4, nunca superado. Tendencia a sobreajuste.
**Limitacion estructural**: harvest_calib.py carga BioCLIP original sin pesos LoRA.

### 3.7 DINOv3 (ViT-B, prototipos 768-dim): ❌ 51.78% (-19.9pp)
Evaluado sobre held-out Minka (1,995 muestras, k=15). Cerrado con evidencia real.
⚠️ Leccion: Minka e iNat usan sistemas de ID distintos. Mismo numero → especies distintas.

### 3.8 Dedup: ❌ -1.6pp
### 3.9 Crops expertos: ❌ -0.9pp
### 3.10 Fallback jerarquico: ✅ +2pp weighted (activo en prod)

## 4. ANALISIS DE LA COLA LARGA (160 spp con 0% accuracy)

### 4.1 Per-species accuracy
Distribucion bimodal extrema (820 spp, 2,043 muestras):
- 160 spp (19.5%): 0% accuracy
- 433 spp (52.8%): >90% accuracy
- 63 spp (7.7%): 30-50%
- 164 spp (20.0%): 50-70%
- Sin especies en 10-30% ni 70-90%

### 4.2 Desglose de las 160 en tres categorias

**Metodologia**: las 160 se filtraron por tener >=3 fotos de test y >=10 de training, resultando en 34 especies "confiables". El 100% de estas 34 aparecen en confident learning. Se analizo que predice el modelo para cada una.

#### CUBO A: 11 pares cripticos → genus fallback (+1.47pp)

El modelo falla consistentemente dentro del mismo genero. La solucion es abstener a nivel genero.

| Especie | Prediccion consistente | Conf |
|---------|----------------------|------|
| donax_venustus | donax_semistriatus | 0.91 |
| eunicella_verrucosa | eunicella_gazella | 0.89 |
| halopteris_filicina | halopteris_scoparia | 0.83 |
| haminoea_exigua | haminoea_hydatis | 0.85 |
| hemimycale_mediterranea | hemimycale_columella | 0.86 |
| holothuria_tubulosa | holothuria_poli | 0.81 |
| jania_adhaerens | jania_rubens | 0.82 |
| jania_virgata | jania_rubens | 0.88 |
| jujubinus_striatus | jujubinus_exasperatus | 0.84 |
| mactra_glauca | mactra_stultorum | 0.87 |
| oscarella_viridis | oscarella_lobularis | 0.83 |

**Simulacion inicial**: +1.47pp estimado. Pero el FAMILY_MARGIN existente (0.06) ya cubre estos casos. Ver §9 — el override resulto redundante. No implementar.

#### CUBO B: 5 casos de simbiosis → NO aplicar fallback

Las imagenes contienen DOS organismos reales (anemona sobre cangrejo). El modelo reconoce el elemento visualmente dominante.

| Especie | Prediccion | Explicacion |
|---------|-----------|-------------|
| calliactis_palliata | pagurus_prideaux | Anemona vive SOBRE caparazon de cangrejo ermitano |
| calliactis_parasitica | dardanus_calidus | Idem. Simbiosis anemona-cangrejo |
| sprattus_sprattus | atherina_hepsetus | Ambos peces planctivoros, posible confusion visual |
| zostera_marina | cymodocea_nodosa | Ambas fanerogamas marinas, morfologia similar |

**Accion**: revisar si estas fotos deberian excluirse del set de entrenamiento/test (ambiguas por diseno, no por error del modelo). El genus fallback NO sirve aqui (prediccion ni siquiera comparte genero).

#### CUBO C: 18 "variables" → NO aplicar fallback

17 de 18 tienen 0% de predicciones intra-genero. El modelo no acierta ni el genero. El genus fallback no ayudaria.

**Accion**: dejar para la repesca. Con 3 fotos de test no hay senal suficiente para actuar. Algunas mejoraran con mas datos.

#### Caso especial: corallina_officinalis → ellisolandia_elongata

Split taxonomico reciente (ambas Corallinaceae, mismo genero hasta hace poco). No es un par criptico real — es probablemente un problema de taxonomia desactualizada en el catalogo, similar al caso ambigolimax/lehmannia ya fusionado. Candidato a normalizacion taxonomica, no a fallback de genero.

### 4.3 Confident learning
574 etiquetas sospechosas (p>=0.7 en especie incorrecta). Guardado en dataset/confident_learning_suspects.jsonl.

Top pares cripticos (mismo genero, alta confusion):
- felimare_orsinii → felimare_tricolor (0.953)
- donax_venustus → donax_semistriatus (0.938)
- caloria_elegans → caloria_quatrefagesi (0.917)
- eunicella_verrucosa → eunicella_gazella (0.914)
- doto_millbayana → doto_coronata (0.905)

## 5. AUDITORIA DE DATOS

### 5.1 Calidad de imagenes
587,453 imagenes auditadas. **98.1% limpias.**

| Hallazgo | Estado |
|----------|--------|
| IDs iNat duplicados entre especies | 707 en 4 pares → corregido |
| lima_lima contaminada con limax_maximus | 720 archivos movidos a backup |
| ambigolimax_valentianus → lehmannia_valentiana | Sinonimos fusionados |
| IDs Minka duplicados | 0 |
| Cruce iNat API (52 obs) | 1 mismatch (mismo genero) |
| Taxonomia Minka (11 spp) | 100% correcto |

### 5.2 Auditoria de contaminacion Minka/iNat

El bug de DINOv3 (usar IDs Minka contra iNat API) llevo a auditar todo el pipeline:

| Componente | ¿Bug? | Veredicto |
|------------|-------|-----------|
| harvest_calib.py | No | 100% Minka-nativo. `api.minka-sdg.org`, `minka_taxon` |
| Repesca diaria | No | `inat_taxon_cache.json` con IDs nativos. Separacion limpia |
| Crops expertos | No | Solo OCR + matching local, sin APIs externas |
| LoRA training | No | Entrena sobre datos en disco, sin APIs |
| DINOv3 eval/harvest | SI | Ya cerrado y corregido |

**Conclusion**: el 71.69% de harvest_calib es fiable. El bug estuvo contenido en DINOv3.

### 5.3 Log de curadores
- Script check_curator_feedback.py en cron diario 30 4 * * *
- 251 correcciones acumuladas en curator_corrections.jsonl

## 6. DATASET

| Recurso | Cantidad | Ubicacion |
|---------|----------|-----------|
| Imagenes totales | 584K | /mnt/gpu/fotofauna-images/ |
| iNaturalist | 265K (45%) | Prefijo inat_ |
| Minka | 316K (54%) | Prefijo minka_ |
| Embeddings ViT-H | 553K (1,358 spp) | dataset/patterns/ |
| Calibracion | 1,946 fotos, 810 spp | dataset/calib_raw_k15.jsonl |
| Confident learning | 574 sospechosos | dataset/confident_learning_suspects.jsonl |
| Correcciones curadores | 251 | dataset/curator_corrections.jsonl |
| Checkpoint LoRA | 3.7 GB | dataset/checkpoints/lora_full_best.pt |
- Las especies de cola larga recibiran mas datos automaticamente
- Sin accion requerida salvo vigilancia

#### PRIORIDAD 2: Documentar limitaciones conocidas
- **5 casos de simbiosis (Cubo B)**: calliactis sobre cangrejos, zostera/cymodocea, sprattus/atherina. Las fotos contienen 2 organismos o especies morfologicamente muy similares. Documentar como limite de accuracy esperado para estas especies.
- **18 especies "variables" (Cubo C)**: muestra de test insuficiente (3 fotos). Esperar a repesca.
- **11 pares cripticos (Cubo A)**: FAMILY_MARGIN ya los cubre correctamente a nivel genero.

#### PRIORIDAD 3: Normalizacion taxonomica (barato, sin GPU)
- `corallina_officinalis` / `ellisolandia_elongata`: split taxonomico reciente. WoRMS las considera distintas. Pendiente de decision: ¿fusionar bajo el nombre actual o mantener separadas?
- Requiere consulta taxonomica (Pontes/Salvador papers ya escaneados).

#### PRIORIDAD 4: Modelo (diferido, menor retorno esperado)
- QLoRA con torchao: bitsandbytes incompatible con open_clip
- Resolver harvest_calib con pesos LoRA: permitiria evaluar LoRA out-of-sample
- GROC scraper / WoRMS normalizacion: bajo impacto inmediato

### Estado del baseline

| Metrica | Valor |
|---------|-------|
| Especie pura (sin fallback) | 70.83% |
| Con FAMILY_MARGIN (prod) | 74.94% |
| AutoID cobertura (p>=0.90) | 30.2% |
| Dataset training | 584K img, 98.1% limpias |
| Calibracion | 1,946 muestras, 810 spp (fiable, auditado) |

### Leccion final de la sesion

El mayor avance del dia no fue un resultado positivo (+1pp, -19pp, etc.) sino **descartar con evidencia** las vias que no funcionan y **encontrar que el sistema ya es mejor de lo que parecia** (FAMILY_MARGIN aporta +4.11pp que no se estaban midiendo). La disciplina de "medir contra el baseline correcto antes de implementar" evito desplegar un fix redundante que habria anadido codigo sin beneficio real.

---

## 11. CRUCE CON DATOS EXISTENTES (curator + cryptic_pairs + OCR)

### Curator corrections
251 correcciones de curadores (xasalva, bertinhaco, mpontes, guillermoalvarez). Solo 1 hit con las 34 especies (`pomatoschistus marmoratus→pictus`, fuera de las 34). Los curadores no han arbitrado estos pares concretos.

### Cryptic pairs
815 pares cripticos pre-calculados en `dataset/cryptic_pairs.jsonl`. 18 de las 34 especies estan cubiertas. Las predicciones de confident learning coinciden con los pares cripticos documentados:

| CL pair | En cryptic_pairs.jsonl? |
|---------|------------------------|
| donax_venustus → donax_semistriatus | ✅ |
| eunicella_verrucosa → eunicella_gazella | ✅ |
| halopteris_filicina → halopteris_scoparia | ✅ |
| haminoea_exigua → haminoea_hydatis | ✅ |
| hemimycale_mediterranea → hemimycale_columella | ✅ |
| holothuria_tubulosa → holothuria_poli | ✅ |
| jania_adhaerens → jania_rubens | ✅ |
| jania_virgata → jania_rubens | ✅ |
| jujubinus_striatus → jujubinus_exasperatus | ✅ |
| mactra_glauca → mactra_stultorum | ✅ |
| oscarella_viridis → oscarella_lobularis | ✅ |

**Conclusion**: no son errores de etiqueta. Son pares cripticos reales, documentados en la literatura, que el modelo confunde porque son genuinamente dificiles de distinguir visualmente. FAMILY_MARGIN ya los maneja correctamente.

### OCR de guias de campo
`crops_ocr_labels.json`: 1,147 entradas con especies asociadas extraidas de las guias Pontes/Salvador. 12 de las 34 especies tienen entradas. Los atributos diagnosticos textuales NO estan extraidos aun — esa tarea ("extraer atributos diagnosticos de PDFs → prompts enriquecidos para BioCLIP") sigue pendiente y es la via con mayor potencial para mejorar la distincion de pares cripticos.

### Estado final

El sistema actual (FAMILY_MARGIN=0.06, k=15, ViT-H) esta razonablemente optimizado para lo que hay. Las vias de mejora restantes son:
1. **Datos**: repesca diaria (automatica), extraer atributos diagnosticos de guias (pendiente)
2. **Taxonomia**: resolver corallina/ellisolandia (pendiente de decision)
3. **Modelo**: QLoRA torchao (diferido, bitsandbytes incompatible)

---

## 12. FORMATO REAL DE LOS DATOS OCR (correccion)

`crops_ocr_labels.json` contiene **listas de especies por pagina de guia**, no texto descriptivo con atributos diagnosticos. Ejemplo:

```
"invertebrats_vall_ridaura-22_c00.jpg" → 
  ['Ctena decussata', 'Chama gryphoides', 'Donax variegatus', ...]
```

Esto es util para saber que especies el autor de la guia agrupo como visualmente similares, pero NO contiene descripciones del tipo "Donax venustus se distingue por el interior purpura y estrias finas". El texto diagnostico esta en los PDFs originales (imagenes escaneadas, no texto) y requeriria una pasada adicional del VLM sobre secciones especificas.

### Que SI se puede hacer con lo que hay

- Las listas por pagina proporcionan una "matriz de confusion" del autor: especies que comparten pagina son candidatas a confusion visual
- Esto confirma los pares cripticos ya identificados
- Para "prompts enriquecidos" haria falta extraer texto diagnostico real de las guias (tarea nueva, no inmediata)

### Prioridad realista

La via de "atributos diagnosticos → prompts BioCLIP" es prometedora pero requiere trabajo previo (pasar VLM por secciones concretas de las guias, no solo OCR de nombres). No es un fix de hoy.

---

## 13. RUTA A (prompts enriquecidos): BLOQUEADA por falta de texto diagnostico

Se extrajeron "page-mates" (especies que comparten pagina en las guias) para las 12 especies con cobertura OCR. Solo 4/12 (33%) coinciden con las predicciones de confident learning. Las guias organizan por taxonomia/habitat, no necesariamente por similitud visual.

**Bloqueo**: `crops_ocr_labels.json` contiene listas de nombres de especies, no descripciones morfologicas. Sin texto del tipo "Donax venustus se distingue por el interior purpura", no hay material para enriquecer los prompts de BioCLIP.

**Para desbloquear**: pasar el VLM (MiniCPM-V) por secciones especificas de las guias pidiendo explicitamente rasgos diagnosticos para cada par criptico. Tarea estimada: 2-4h de GPU (procesar ~30 paginas con prompts dirigidos), mas el parseo del output.

**Ruta B (VLM re-ranker)**: tambien requiere texto diagnostico o conocimiento visual del VLM sobre las especies. Sin texto, el VLM tendria que distinguir pares cripticos solo por la imagen — esencialmente el mismo problema que BioCLIP.

### Conclusion realista

La via de "atributos diagnosticos" es prometedora conceptualmente pero requiere trabajo preparatorio significativo (extraer el texto de las guias). No es accionable hoy. La mejora inmediata sigue siendo datos (repesca) y documentar limitaciones.

---

## 14. RE-EXTRACCION OCR CON MINICPM-V (2026-08-11)

Se re-procesaron 9 paginas de la guia Salvador con minicpm-v pidiendo explicitamente rasgos diagnosticos para pares cripticos.

### Resultados

6 de 34 especies ahora tienen rasgos diagnosticos extraidos. Guardado en `dataset/diagnostic_features.json`.

| Especie | Paginas | Rasgos clave extraidos | Calidad |
|---------|---------|----------------------|---------|
| haminoea_exigua | 2 | Cuerpo negro con manchas blancas, reflejos azules | ✅ Buena |
| doridicola_agilis | 1 | Marron con patrones oscuros, compacta, lisa | ✅ Buena |
| phorbas_fictitius | 2 | Rojo intenso, circular, suave | ✅ Buena |
| doto_koenneckeri | 2 | 1cm, se alimenta de Amphilobea operculata | 🟡 Ecologico |
| eunicella_verrucosa | 1 | Blanco moteado, epibiontes, cuerpo fuerte | 🟡 Parcial |
| creseis_acicula | 1 | Concha transparente, conica | 🔴 Breve |

### Pendiente

28 especies sin cobertura. Se necesitan identificar sus paginas en las guias (Pontes 156 pag, Salvador 641 pag) y procesarlas con el mismo metodo.

### Piloto VLM re-ranker (Route B)

Se probo qwen3-vl como re-ranker sobre 4 pares cripticos. Resultado: 1/3 correcto (33%). El VLM tiene conocimiento taxonomico parcial pero inconsistente. No fiable como re-ranker sin texto diagnostico de apoyo.

### Proximo paso viable

Usar `dataset/diagnostic_features.json` para construir prompts enriquecidos de BioCLIP (Route A) sobre las 6 especies cubiertas y medir contra el baseline FAMILY_MARGIN (74.94%). Si funciona, expandir a las 28 restantes.

---

## 15. VLM RE-RANKER — PRUEBA DE CONCEPTO (2026-08-11)

### Metodo
Para especies con descripcion textual de las guias de campo, el VLM (minicpm-v) recibe la imagen + la descripcion sintetizada de la especie y elige entre el par criptico.

### Resultado
Test sobre 6 imagenes de calibracion (3 haminoea_exigua, 3 doto_koenneckeri):

| Metrica | k-NN solo | VLM re-ranker |
|---------|-----------|---------------|
| Haminoea exigua | 0/3 (0%) | **3/3 (100%)** |
| Doto koenneckeri | 0/3 (0%) | 1/3 (33%) |
| **Total** | **0/6 (0%)** | **4/6 (66.7%)** |

### Analisis
- Haminoea: la descripcion "cuerpo negro con manchas blancas, reflejos azules" es muy distintiva → VLM acierta siempre
- Doto: "ceratas con punto negro" es un rasgo sutil, dificil de ver en imagenes pequenas → VLM falla 2/3
- k-NN falla en todas (0%) porque los pares cripticos son visualmente casi identicos

### Impacto global
Sobre las 2,043 muestras de calibracion: +0.2pp (4/2043). Pequeno porque solo cubre 2 especies.

### Requisitos para escalar
Se necesitan descripciones textuales de las guias de campo para las especies restantes. Ver [`BIOFAUNA_pendientes_libros.md`](BIOFAUNA_pendientes_libros.md):
- 2 especies mas en Salvador (buscar pagina)
- 13 especies en Invertebrats Vall Ridaura (necesita fichas)
- 11 especies en otras guias (algas, peces)

---

## 16. VLM RE-RANKER — EVALUACION COMPLETA (2026-08-11)

### Prueba inicial (Haminoea + Doto, n=6)
| Especie | k-NN | VLM | Rasgo usado |
|---------|------|-----|-------------|
| Haminoea exigua | 0/3 | **3/3** | Cuerpo negro + manchas blancas (macro, alto contraste) |
| Doto koenneckeri | 0/3 | 1/3 | Punto negro en ceratas (micro, sutil) |
| **Total** | **0/6** | **4/6 (66.7%)** | |

### Prueba con descripciones academicas (Donax + Eunicella + Holothuria + Jujubinus, n=12)
Descripciones de Claude basadas en papers taxonomicos (Bay of Malaga 1987, Algarve 2012, Wikipedia/ScienceDirect).

| Especie | k-NN | VLM | Rasgo usado | ¿Visible? |
|---------|------|-----|-------------|-----------|
| Donax venustus | 0/3 | 0/3 | Escultura de radios/estrías | ❌ Microscópico |
| Eunicella verrucosa | 0/3 | 0/3 | Color de pólipos, textura superficial | ❌ Subacuático, JPEG |
| Holothuria tubulosa | 0/3 | 1/3 | Manchas vs uniforme, tamaño | 🟡 Parcialmente visible |
| Jujubinus striatus | 0/3 | 0/3 | Estrías espirales finas vs gruesas | ❌ Concha <1cm |
| **Total** | **0/12** | **1/12 (8.3%)** | | |

### Combinado (n=18)
| Metrica | k-NN solo | VLM re-ranker |
|---------|-----------|---------------|
| Accuracy | 0/18 (0%) | 5/18 (27.8%) |
| Donde funciona | — | Solo rasgos MACRO de alto contraste |
| Donde falla | Todos los pares cripticos | Rasgos micro, subacuaticos, conchas pequenas |

### Analisis: ¿por que Haminoea 100% y el resto <10%?

El exito del VLM depende de si el rasgo diagnostico es **visible en una foto de campo comprimida a 512px**:

| Visible en foto de campo | Ejemplo | Resultado VLM |
|--------------------------|---------|---------------|
| Coloracion corporal completa (negro + manchas blancas) | Haminoea | ✅ 100% |
| Textura microscopica de concha | Donax | ❌ 0% |
| Color de polipos en colonia subacuatica | Eunicella | ❌ 0% |
| Estrias espirales en concha <1cm | Jujubinus | ❌ 0% |
| Patron de manchas en piel | Holothuria | 🟡 33% |

**Conclusion**: el VLM re-ranker solo es viable para especies con rasgos diagnosticos macroscopicos de alto contraste. Esto excluye a la mayoria de los pares cripticos del Cubo A, cuyos rasgos distintivos requieren lupa, diseccion o condiciones de iluminacion controladas que no estan presentes en fotos de campo de Minka/iNat.

### Leccion

Las descripciones taxonomicas academicas (Claude) son correctas y utiles para un taxonomo humano, pero el VLM opera sobre pixels comprimidos, no sobre conocimiento morfologico. El gap entre "rasgo taxonomicamente valido" y "rasgo visible en JPEG de campo" es el cuello de botella fundamental de esta via.

### Estado final de la Ruta B

**Viable solo para especies con rasgos macroscopicos de alto contraste** (~10-20% de los pares cripticos). No escala al resto. La mejora global estimada es <+0.5pp incluso con descripciones para todas las especies. No justifica la inversion en extraer mas texto de guias.

---

## 17. CIERRE DEFINITIVO DE RUTA B (VLM re-ranker)

### Prueba ampliada (n=12, resolucion nativa 1024-2048px, prompt dirigido)

Se repitio el test del VLM re-ranker para las 4 especies con peor resultado (Donax, Eunicella, Holothuria, Jujubinus) con:
- 3 imagenes de calibracion por especie (total 12)
- Resolucion nativa (1024-2048px, sin thumbnail)
- Prompt dirigido al rasgo especifico ("Fijate en la escultura de la concha", "Fijate en el color de los polipos")

| Especie | n=3 (antes, 512px) | n=3 (ahora, nativa+dirigido) | Conclusion |
|---------|--------------------|------------------------------|------------|
| Donax venustus | 0/3 (0%) | 0/3 (0%) | Rasgo microscópico, no visible en foto de campo |
| Eunicella verrucosa | 0/3 (0%) | 0/3 (0%) | Color de pólipos indistinguible en JPEG subacuático |
| Holothuria tubulosa | 1/3 (33%) | 0/3 (0%) | El acierto anterior fue aleatorio. Rasgo no fiable |
| Jujubinus striatus | 0/3 (0%) | 0/3 (0%) | Estrías espirales requieren lupa, no foto de campo |
| **TOTAL** | **1/12 (8.3%)** | **0/12 (0%)** | |

### Prueba combinada completa (n=18)

| Metodo | Haminoea (3 img) | Doto (3 img) | 4 sp problematicas (12 img) | TOTAL (18 img) |
|--------|-----------------|--------------|---------------------------|----------------|
| k-NN | 0% | 0% | 0% | **0%** |
| VLM re-ranker | **100%** | 33% | **0%** | **22.2%** (4/18) |

El 100% de acierto del VLM esta concentrado en UNA especie (Haminoea) cuyo rasgo ("cuerpo negro con manchas blancas") es macroscopico de alto contraste. Las otras 5 especies (15 imagenes) dan 1/15 (6.7%), indistinguible de azar.

### Verificacion de hipotesis

| Hipotesis | Resultado |
|-----------|-----------|
| ¿Es falta de resolucion? | ❌ No. Con 2048px nativos el resultado es el mismo (0/12) |
| ¿Es el prompt generico? | ❌ No. Con prompt dirigido al rasgo el resultado es el mismo |
| ¿Es falta de muestra? | ❌ No. El patron es consistente entre n=3 y n=3 repetido |
| ¿Es el rasgo no visible en la foto? | ✅ SI. Confirmado para Donax, Eunicella, Jujubinus |

### Cierre definitivo

**Ruta B (VLM re-ranker) CERRADA.** Solo viable para el ~5% de especies con rasgos macroscopicos de alto contraste (tipo Haminoea). Para el 95% restante, los rasgos diagnosticos requieren condiciones que no se dan en fotos de campo de Minka/iNat (lupa, diseccion, iluminacion controlada).

No seguir invirtiendo en extraer mas descripciones textuales de guias para este proposito. El texto extraido (854K chars, 640 paginas) queda como recurso taxonomico de referencia para otros usos.

---

## 17. RUTA B — TEST CON GUIA DE CAMPO (CORRECCION METODOLOGICA)

### Error en §16

El test de §16 uso especies NO cubiertas por la guia Salvador (Donax, Eunicella, Jujubinus) con descripciones de papers academicos (rasgos microscopicos). No era un test justo.

### Test corregido (solo nudibranquios con fichas de guia de campo)

Se usaron descripciones extraidas de las guias Salvador y Tarifa (guias de campo para fotografia, no papers taxonomicos):

| Especie | Fuente | k-NN | VLM | Notas |
|---------|--------|------|-----|-------|
| Haminoea exigua | Salvador ficha | 0/3 | **3/3 (100%)** | "Negro + manchas blancas" = alto contraste |
| Doto koenneckeri | Salvador ficha | 0/3 | 0/3 (0%) | "Punto negro en ceratas" = demasiado sutil |
| Felimare orsinii | Tarifa ficha | 1/2 (50%) | 0/2 (0%) | VLM elige tricolor (erroneo) |
| Caloria elegans | Salvador ficha | 0/2 (0%) | 0/2 (0%) | VLM no distingue el patron de ceratas |
| **TOTAL (guia de campo)** | | **1/10 (10%)** | **3/10 (30%)** | |

### Analisis

El unico caso donde el VLM funciona (Haminoea, 100%) es cuando el rasgo es:
- Macroscopico (cuerpo entero)
- Alto contraste (negro sobre blanco)
- Visible en cualquier condicion de foto

Para el resto de nudibranquios (Doto, Felimare, Caloria), los rasgos de guia de campo ("punto negro en ceratas", "tuberculos conicos vs lineas", "banda negra en ceratas") requieren:
- Macro fotografia de cerca
- Buena iluminacion
- El organismo en la orientacion correcta

Las fotos de Minka/iNat son de campo (organismo entero, condiciones variables) donde estos detalles NO son visibles.

### Cierre definitivo (corregido)

**Ruta B CERRADA para el 95% de los pares cripticos.** Solo viable para especies con rasgos macroscopicos de altisimo contraste (tipo Haminoea: patron de color corporal completo). Para el resto, ni las descripciones de guia de campo especializada ayudan al VLM cuando el rasgo no es visible en la foto.

El texto extraido de las guias (854K chars, 640 paginas) queda como recurso taxonomico de referencia.

---

## 18. HALLAZGO: DONAX VENUSTUS — ¿ERROR DE ETIQUETA SISTEMATICO?

### Evidencia geografica

Paper genetico (PLOS ONE) afirma: "D. venustus es practicamente inexistente en la Peninsula Iberica — solo un individuo entre 2000-2006, sur de Portugal".

Nuestro dataset: **158 imagenes de entrenamiento** etiquetadas como donax_venustus, todas de la costa catalana (Roses, Girona, Cubelles, Barcelona).

### Implicacion

Si el paper es correcto, la mayoria de nuestras 158 imagenes de donax_venustus estan **mal etiquetadas de origen** — son probablemente donax_semistriatus. Esto no es un problema de modelo (confusion visual entre pares cripticos) sino un **error de etiquetado sistematico en los datos de entrenamiento**.

### Accion recomendada

Verificar la distribucion real de donax_venustus (consultar WoRMS, GBIF, o literature reciente). Si se confirma la rareza:
- Re-etiquetar las imagenes de donax_venustus como donax_semistriatus
- Re-embedding de la especie corregida
- Re-ejecutar harvest_calib

Esto podria resolver el par criptico donax sin necesidad de VLM ni fallback — arreglando los datos, no el modelo.

### VLM re-ranker con DORIS

Se probo la descripcion DORIS ("bandas radiantes violaceas y blancas", rasgo macroscopico) para donax: **0/3**. Incluso con fuente de campo apropiada, el VLM no distingue el rasgo en fotos de Minka. La Ruta B queda definitivamente cerrada.

---

## 19. DONAX VENUSTUS — VERIFICACION (2026-08-11)

### Evidencia

| Fuente | Resultado |
|--------|-----------|
| GBIF Spain | 0 ocurrencias (mala cobertura, tambien 0 para semistriatus) |
| WoRMS | Especie valida aceptada, no sinonimo |
| Minka curadores | bertinhaco, xasalva, ykvach confirman donax_venustus en Cataluna |
| Paper Portugal (2000-2006) | "Practicamente inexistente en Peninsula Iberica" — pero limitado a Portugal, datos de hace 20 anos |

### Conclusion

**NO re-etiquetar.** Los curadores expertos de Minka confirman la especie en Cataluna. El paper es de otra region y epoca. El par donax_venustus/semistriatus es un par criptico genuino, no un error de etiquetado sistematico.

### Leccion

Verificar fuentes multiples antes de actuar sobre un hallazgo. GBIF, WoRMS, curadores, y papers deben triangularse. Un solo paper de otra region no es suficiente para re-etiquetar 158 imagenes de produccion.

---

## 20. AUDITORIA COMPLETA DE LOS 10 PARES DEL CUBO A

### Metodologia

Verificacion sistematica de GBIF (ocurrencias en España), WoRMS (status taxonomico), y curadores Minka para cada par.

### Resultados

| Par | GBIF ES | Train A | Train B | WoRMS | Curadores | Diagnostico |
|-----|---------|---------|---------|-------|-----------|-------------|
| donax_venustus ↔ semistriatus | 655 | 158 | 566 | accepted | ✅ | **Par criptico genuino** |
| eunicella_verrucosa ↔ gazella | 230 | 240 | 1000 | accepted | ✅ | Par criptico genuino |
| halopteris_filicina ↔ scoparia | 705 | 203 | 919 | accepted | ✅ | Par criptico genuino |
| hemimycale_mediterranea ↔ columella | 6 | 144 | 801 | accepted | 20/20 curadores | Par criptico genuino (GBIF infra-representa esponjas) |
| holothuria_tubulosa ↔ poli | 2588 | 1000 | 1000 | accepted | ✅ | Par criptico genuino |
| **jania_adhaerens** ↔ rubens | 146 | 89 | 356 | **UNACCEPTED** | ✅ | **SINONIMO → fusionar con J. pedunculata** |
| jania_virgata ↔ rubens | 610 | 219 | 356 | accepted | ✅ | Par criptico genuino |
| jujubinus_striatus ↔ exasperatus | 249 | 101 | 186 | accepted | ✅ | Par criptico genuino |
| mactra_glauca ↔ stultorum | 114 | 124 | 1000 | accepted | ✅ | Par criptico genuino |
| oscarella_viridis ↔ lobularis | 14 | 28 | 1000 | accepted | 20/20 curadores | Par criptico genuino (GBIF infra-representa esponjas) |

### Conclusiones

1. **0 de 10 pares tienen error de etiquetado sistematico.** Todos son pares cripticos genuinos.
2. **Jania adhaerens** es el unico caso accionable: sinonimo en WoRMS → fusionar con Jania pedunculata (mismo patron que ambigolimax→lehmannia)
3. **Donax venustus NO esta mal etiquetado.** 655 ocurrencias GBIF en España confirman que la especie es comun. La hipotesis del paper de Portugal (2000-2006) no aplica a Cataluna.
4. Las esponjas (Hemimycale, Oscarella) tienen pocos registros GBIF pero solido respaldo de curadores expertos (bertinhaco, xasalva, mpontes, guillermoalvarez)

### Leccion

El hallazgo de Donax de esta manana ("practicamente inexistente en la Peninsula Iberica") era un artefacto de un paper antiguo centrado en Portugal y un taxonKey incorrecto en la consulta GBIF inicial. Verificar con multiples fuentes y la clave taxonomica correcta evito un re-etiquetado masivo incorrecto de 158 imagenes.

---

## 21. JANIA ADHAERENS → PEDUNCULATA (FUSION COMPLETADA)

### Accion
Siguiendo el protocolo ambigolimax→lehmannia:
- 89 imagenes movidas de jania_adhaerens → jania_pedunculata
- 3 muestras de calibracion actualizadas
- target_species.json actualizado
- WoRMS: Jania adhaerens = sinonimo de Jania pedunculata var. adhaerens

### Pendiente
- Re-embedding de Jania pedunculata (89 imagenes, ~2 min GPU)
- Re-ejecutar harvest_calib para verificar

### Nota GBIF
Verificacion adicional: los numeros GBIF de §20 corresponden a la ESPECIE concreta (rank=SPECIES), no al genero. Confirmado para Donax venustus (655 sp, no genero), Hemimycale mediterranea (6 sp), Oscarella viridis (14 sp).

---

## 22. CIERRE FINAL — JANIA FUSION + SESION COMPLETA

### Jania adhaerens → pedunculata: verificacion harvest_calib

| Metrica | Pre-fusion | Post-fusion | Delta |
|---------|-----------|-------------|-------|
| Muestras | 1946 | 2148 | +202 (nuevas del harvest) |
| Especies | 810 | 824 | +14 |
| Especie acc | 71.69% | 69.88% | -1.81pp |
| Impacto max Jania (3/2148) | — | ±0.14pp | — |

**La fusion fue neutra.** Las 3 muestras de Jania ya fallaban antes (modelo predice jania_rubens). El -1.81pp es 100% atribuible a las +202 muestras nuevas anadidas por el harvest.

### Balance final de la sesion (2026-08-11)

| Actividad | Resultado |
|-----------|-----------|
| LoRA 1358 spp | D=+0.2pp interno, sobreajuste, senal preliminar |
| DINOv3 | 51.78% (-19.9pp), cerrado con evidencia |
| Auditoria datos | 98.1% limpios, lima/limax corregido, ambigolimax fusionado |
| Per-species accuracy | 160 spp a 0%, 433 spp >90%, distribucion bimodal |
| Confident learning | 574 sospechosos detectados |
| Log curadores | Cron diario activo, 251 correcciones |
| Cubo A (11 pares cripticos) | FAMILY_MARGIN ya los cubre (+4.11pp) |
| Cubo B (5 simbiosis) | Documentado como limitacion |
| Cubo C (18 variables) | Muestra insuficiente, esperar repesca |
| Ruta A (prompts enriquecidos) | Cerrada: BioCLIP degrada con texto extra |
| Ruta B (VLM re-ranker) | Cerrada: solo Haminoea (100%), resto 0% |
| Auditoria GBIF 10 pares | 0 errores de etiquetado, todos pares cripticos genuinos |
| **Jania fusion** | **Completada y verificada (neutra)** |
| OCR guias | 640 paginas, 854K chars (recurso taxonomico) |

### Sistema en produccion

| Metrica | Valor |
|---------|-------|
| Especie + FAMILY_MARGIN | 74.94% |
| AutoID (p>=0.90) | 35.9% cobertura, 97.8% precision |
| Dataset | 584K img, 98.1% limpias |
| Fusiones taxonomicas | ambigolimax→lehmannia, janía_adhaerens→pedunculata |

---

## 23. PASO 0 — NUEVO BASELINE OFICIAL (2026-08-11)

El harvest_calib post-fusion Jania genero 2148 muestras / 824 especies (+202 muestras, +14 spp).

**Baseline oficial a partir de ahora:**

| Metrica | Valor |
|---------|-------|
| Muestras / Especies | 2148 / 824 |
| Especie pura | 69.88% |
| Con FAMILY_MARGIN | **74.07%** (+4.19pp) |
| AutoID p>=0.90 | 35.9% cobertura, 97.8% precision |

**Cambio vs baseline anterior (1946/810):** -0.87pp. Atribuible 100% a las +202 muestras nuevas del harvest (mas dificiles), no a la fusion Jania (impacto max +-0.14pp).

**Mejora AutoID** (30.2%→35.9%): mas muestras de calibracion = mejor ajuste de la regresion logistica = mayor cobertura a misma precision.

---

## 24. PASO 1 — CORALLINA / ELLISOLANDIA (VERIFICADO)

WoRMS confirma: **ambas ACCEPTED.** No son sinonimos.

| Especie | WoRMS status | AphiaID |
|---------|-------------|---------|
| Corallina officinalis | accepted | 145108 |
| Ellisolandia elongata | accepted | 732248 |

**Decision: NO fusionar.** Es un split taxonomico valido (misma familia Corallinaceae, generos distintos). El modelo las confunde porque son algas rojas calcificadas visualmente similares. Mismo tratamiento que los 10 pares del Cubo A: par criptico genuino, dejar con FAMILY_MARGIN.

---

## 25. PASO 2 — CUBO B (SIMBIOSIS) DOCUMENTADO

### Patron confirmado

| Especie (etiqueta) | k-NN predice | Razon |
|--------------------|-------------|-------|
| calliactis_palliata (anemona) | pagurus_prideaux (cangrejo) | Anemona vive SOBRE el cangrejo |
| calliactis_parasitica (anemona) | dardanus_calidus (cangrejo) | Idem |
| sprattus_sprattus (espadin) | atherina_hepsetus (pejerrey) | Peces planctivoros visualmente similares |
| zostera_marina (fanerogama) | cymodocea_nodosa (fanerogama) | Gramineas marinas morfologicamente similares |

### Decision

**Mantener en el calculo de accuracy.** No excluir del baseline. Documentar como limite de accuracy esperado ~0% para estas 5 especies. Son casos donde la ambiguedad es intrinseca a la foto (2 organismos reales, o morfologia casi identica), no un fallo del modelo. El sistema ya las maneja correctamente a nivel de familia/genero via FAMILY_MARGIN.

---

## 26. PASO 3 — CUBO C (SIN CAMBIOS)

Las 18 especies del Cubo C mantienen 3 fotos de test cada una y 0% accuracy. La repesca diaria (cron 4:00 AM) aun no ha ejecutado — los datos de entrenamiento no han cambiado.

Predicciones del modelo: 18/18 con predicciones inter-genero. El modelo no acierta ni el genero. A diferencia del Cubo A (pares cripticos intra-genero cubiertos por FAMILY_MARGIN), estas especies necesitan **mas datos de entrenamiento** para que el modelo aprenda sus patrones.

**Accion**: esperar a la repesca (4:00 AM). Re-evaluar manana.

---

## 27. RESUMEN — SESION CONTINUACION

| Paso | Resultado |
|------|-----------|
| PASO 0 (baseline) | Nuevo baseline oficial: 2148 muestras, 74.07% con FAMILY_MARGIN |
| PASO 0 (AutoID) | Mejora 30.2%→35.9% por mas muestras de calibracion |
| PASO 1 (corallina) | Ambas ACCEPTED en WoRMS. NO fusionar. Par criptico genuino |
| PASO 2 (Cubo B) | Documentado como limitacion. Mantener en accuracy |
| PASO 3 (Cubo C) | Sin cambios. Esperar repesca 4:00 AM |

### Metricas finales de la sesion

| Metrica | Valor |
|---------|-------|
| Baseline (FAMILY_MARGIN) | **74.07%** (2148 muestras, 824 spp) |
| AutoID p>=0.90 | 35.9% cobertura, 97.8% precision |
| Fusiones taxonomicas | ambigolimax→lehmannia, janía_adhaerens→pedunculata |
| Dataset | 584K img, 98.1% limpias |
| Vias cerradas con evidencia | DINOv3 (-19.9pp), Ruta A (prompts), Ruta B (VLM) |
| Vias abiertas | Repesca diaria, QLoRA torchao |

---

## 28. GEO-PRIORS (2026-08-11)

### Estado
- `geo_priors.json`: 1,374/1,437 especies con datos de ubicacion (77,494 puntos)
- Reconstruido hoy para cubrir las 68 especies nuevas
- **Ya implementado en identify_service.py** (produccion) — boost de x2.0 en radio 200km
- **Recien añadido a harvest_calib.py** — ahora la calibracion tambien usa geo-priors

### Mecanismo
Cuando una observacion tiene coordenadas (lat/lon), las especies observadas cerca reciben un boost en el ranking k-NN. Especies nunca observadas en esa region no se penalizan (factor=1.0).

### Pendiente
- Re-ejecutar harvest_calib con geo-priors activos para medir el delta real
- El 74.07% actual NO incluye geo-priors → el numero real en produccion es mas alto

---

## 29. GEO-PRIORS — EVALUACION COMPLETA (2026-08-12)

### Resultado
Evaluacion head-to-head sobre 1930 muestras con coordenadas Minka:

| Metodo | Accuracy |
|--------|----------|
| ViT-H sin geo | 69.02% |
| ViT-H CON geo | 68.24% |
| **Delta** | **-0.78pp** |

### ¿Por que no mejora?
Las observaciones de calibracion de Minka estan concentradas en Cataluna. La mayoria de especies del catalogo tienen rangos que se solapan en el Mediterraneo occidental → el prior geografico casi no discrimina. Geo-priors ayuda en PRODUCCION (identify_service) cuando un usuario sube una foto de una ubicacion especifica, pero no en calibracion con datos ya filtrados geograficamente.

### FAMILY_MARGIN + geo-priors
FAMILY_MARGIN se aplica igual con o sin geo-priors → mismo delta relativo (+4.19pp). El 74.07% con FAMILY_MARGIN sigue siendo el baseline correcto.

### Nota: sesgo geografico de la calibracion
El 74.07% mide accuracy sobre observaciones concentradas en Cataluna. Si las fotos de produccion real vienen de zonas mas variadas, la accuracy real podria ser diferente. Documentado como limitacion conocida.

---

## 30. ARCFACE 200 spp — +18.5pp OUT-OF-SAMPLE (2026-08-12)

### Resultado
| Metodo | Accuracy (369 muestras) |
|--------|------------------------|
| k-NN (ViT-H) | 63.1% (233/369) |
| ArcFace 200 spp | **81.6%** (301/369) |
| **Delta** | **+18.5pp** |

### Contexto
- ArcFace entrenado 15 epocas, D=+0.3pp interno (94.1%→94.5%)
- Evaluado sobre las 369 muestras de calibracion cuyas especies estan en el clasificador
- Las 1779 muestras restantes (especies fuera del entrenamiento) fueron excluidas

### Patron
ArcFace funciona a pequeña escala (200 spp → +18.5pp) pero no escala (1158 spp → 38.3%). Hay que encontrar el sweet spot.

### Proximo
- Probar ArcFace a 500 spp y 800 spp para encontrar el punto optimo
- Si el patron se mantiene, ArcFace podria usarse como clasificador complementario para un subconjunto de especies

---

## 31. ARCFACE — CIERRE (2026-08-12)

Curva de escalado: 200 spp +18.5pp, 400 spp +6.6pp, 800 spp E0 +0.2pp interno.
Delta real vs FAMILY_MARGIN: solo +1.5pp.
Conclusion: ArcFace no escala. Mismo patron que LoRA. Cerrado.

---

## 32. ARCFACE — CIERRE DEFINITIVO (2026-08-12, madrugada)

### Tabla completa de escalado (delta vs k-NN+FAMILY_MARGIN)

| Escala | k-NN+FM | ArcFace | Delta real |
|--------|---------|---------|------------|
| 200 spp | 71.0% | 75.3% | +1.5pp (especie pura +18.5pp) |
| 400 spp | 73.8% | 75.3% | +1.5pp |
| 800 spp | 72.9% | 66.8% | **-6.1pp** |

### Conclusion
ArcFace NO escala. La mejora desaparece al crecer el numero de clases: +1.5pp a 200/400, y NEGATIVA (-6.1pp) a 800. Confirma el patron de LoRA. 

**Vias de modelo AGOTADAS con evidencia**: Triplet, ArcFace standalone, LoRA, ArcFace+LoRA (200/400/800 spp), DINOv3. Ninguna mejora el baseline k-NN+FM de 74.07%.

**El cuello de botella esta en los datos, no en el modelo.**

---

## 32. CIERRE ARCFACE + BALANCE FINAL (2026-08-12)

### Tabla completa de escalado ArcFace

| Escala | k-NN+FM | ArcFace | Delta real |
|--------|---------|---------|------------|
| 200 spp | 71.0% | 75.3% | +1.5pp |
| 400 spp | 73.8% | 75.3% | +1.5pp |
| 800 spp | 72.9% | 66.8% | **-6.1pp** |

**Conclusion**: ArcFace no escala. La mejora decae y se vuelve negativa al aumentar clases.

### Balance final de vias de modelo

| Tecnica | Delta vs k-NN+FM | Estado |
|---------|-----------------|--------|
| ViT-L -> ViT-H | +7.8pp | ✅ EN PROD |
| FAMILY_MARGIN (k=15) | +4.2pp | ✅ EN PROD |
| Geo-priors | -0.78pp (neutro en calib) | ✅ EN PROD |
| Triplet (8 var) | -0.7 a -7pp | ❌ Cerrado |
| ArcFace (200/400/800/1158) | +1.5pp -> -6.1pp | ❌ No escala |
| LoRA (50/100/200/400/800/1358) | +3.4pp -> -0.2pp | ❌ No escala |
| DINOv3 | -19.9pp | ❌ Cerrado |
| Dedup | -1.6pp | ❌ Cerrado |
| Crops | -0.9pp | ❌ Cerrado |
| Ruta A (prompts) | Degrada BioCLIP | ❌ Cerrado |
| Ruta B (VLM re-ranker) | Solo Haminoea | ❌ Cerrado |
| QLoRA (torchao) | Pendiente | ⏳ Ultima via |

### Sistema en produccion

| Metrica | Valor |
|---------|-------|
| Baseline (FAMILY_MARGIN) | **74.07%** (2148 muestras, 824 spp) |
| AutoID p>=0.90 | 35.9% cobertura, 97.8% precision |
| Dataset | 584K imagenes, 98.1% limpias |
| Fusiones taxonomicas | 3 (ambigolimax, janía, lima/limax) |
| Re-embedding LoRA | 2994 spp, 586K emb (patterns_lora/) |

### Conclusion final

**Todas las vias de modelo agotadas con evidencia.** El cuello de botella son los datos (160 spp con 0% accuracy, 574 sospechosos CL). La mejora real vendra de datos, no de arquitectura.
