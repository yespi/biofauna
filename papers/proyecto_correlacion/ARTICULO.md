# Asociaciones entre especies marinas reveladas por un identificador automático de fauna y 1,2 millones de fotografías de ciencia ciudadana

**Borrador v1 — 28-sep-2026** · Proyecto Correlación (BioFauna)

---

## Resumen

La ciencia ciudadana marina ha generado volúmenes de observaciones con fotografía que rara vez se explotan más
allá de la distribución de especies. Aquí presentamos un análisis de **1.222.170 fotografías** y **759.207
observaciones geolocalizadas y fechadas** (Minka SDG, iNaturalist y otras fuentes públicas), identificadas de
forma automática por **BioFauna** —un recuperador k-NN sobre *embeddings* de BioCLIP-2.5 ViT-H/14 con
calibración jerárquica— para descubrir **asociaciones entre especies**. Definimos un *evento* de muestreo
(observador × celda ~1 km × día × franja de 3 h) y evaluamos la co-ocurrencia de pares con soporte,
repetibilidad espacial y temporal, hallando **70.971 pares significativos**. El método **recupera asociaciones
ya documentadas** con alta robustez —por ejemplo *Peltodoris atromaculata* sobre la esponja *Petrosia
ficiformis* (79 eventos, lift 11,1, 44 localidades, 74 días)— y revela **candidatas no descritas** con lectura
biológica plausible, como medusas con anfípodos hiperídeos comensales, gambas limpiadoras con anémonas y
parejas de fauna infaunal. El trabajo subraya el papel de las personas curadoras en la verificación de las
especies crípticas y esboza su aplicación a la conservación y a la divulgación.

**Palabras clave:** ciencia ciudadana, asociaciones interespecíficas, *habitat use*, aprendizaje profundo,
Mediterráneo, fotografía submarina.

## 1. Introducción

La fotografía submarina *amateur* se ha convertido en una fuente masiva de datos de biodiversidad. Las
plataformas de ciencia ciudadana (**Minka SDG**, impulsada desde el ecosistema **FECDAS**; **iNaturalist**;
**GBIF**) acumulan millones de observaciones verificadas, y los identificadores automáticos permiten
consolidar ese archivo a escala de catálogo. Sin embargo, la mayoría de los análisis se limitan a inventarios
y mapas de distribución. Las fotografías contienen además **contexto ecológico**: qué especies aparecen
juntas, sobre qué sustrato y en qué condiciones. Este trabajo explora esa información latente.

*(Precedente: el uso de co-ocurrencia en datos participativos para inferir asociaciones, con sus conocidos
sesgos de esfuerzo y observador —ver §Límites.)*

## 2. Material y métodos

Resumen (detalle en [`METODOS.md`](METODOS.md) y en el material suplementario):

- **Datos**: 1.222.170 fotografías; 759.207 observaciones con coordenadas, fecha y (92 %) hora; catálogo curado
  de 2.985 taxones mediterráneos.
- **Identificación**: BioFauna (BioCLIP-2.5 ViT-H/14 + FAISS k-NN, k=15, agregador T=0,05 con tope de 3 votos
  por especie, calibración jerárquica), con guardas de publicación y auditoría de fugas.
- **Unidad de análisis**: *evento* = (observador × celda ~1,1 km × día × franja de 3 h); grupo de especies
  vistas juntas.
- **Filtros**: solo catálogo; soporte ≥8 eventos; repetibilidad en **≥3 localidades y ≥3 días**.
- **Métricas**: co-ocurrencia observada `n`, esperada por marginales y **lift**; p de Poisson para cribado.
- **Validación interna**: búsqueda ciega de asociaciones documentadas (§3.1).

## 3. Resultados

### 3.1 Validación del método (asociaciones documentadas recuperadas)

| asociación | n | lift | localidades | días | fuente |
|---|---:|---:|---:|---:|---|
| *Peltodoris atromaculata* — *Petrosia ficiformis* | 79 | 11,1 | 44 | 74 | bibliografía clásica |
| *Felimare picta* — *Ircinia oros* | 29 | 4,1 | 20 | 28 | esponja hospedadora |
| *Cratena peregrina* — *Eudendrium racemosum* | 5 | 10,5 | — | — | hidrozoo presa |
| *Doto paulinae* — *Sertularella mediterranea* | 5 | 48,3 | — | — | hidrozoo hospedador |

### 3.2 Grupos taxonómicos

Los pares se concentran en las familias mejor representadas fotográficamente (esparidos, blénidos, góbidos,
lábridos, algas coralinas, ascidias, holoturias, actinias, troquidos, dictyotáceas, facelínidos, serpúlidos,
sabelidos e ircínidos). El **98 % de los pares son inter-familia**, esperable en asociaciones de hábitat o
tróficas.

### 3.3 Candidatas nuevas (pendientes de revisión experta)

| grupo funcional | A — B | n | lift | localidades | días |
|---|---|---:|---:|---:|---:|
| comensalismo en medusas | *Blackfordia virginica* — *Phronima sedentaria* | 19 | 653 | 6 | 15 |
| simbiosis de limpieza | *Lysmata grabhami* — *Telmatactis cricoides* | 9 | 547 | 7 | 8 |
| infauna (mismo sedimento) | *Fustiaria rubescens* — *Loripinus fragilis* | 16 | 892 | 7 | 15 |
| infauna | *Abra alba* — *Abra longicallus* | 9 | 534 | 7 | 9 |
| microhábitat de sustrato duro | *Macrorhynchia philippina* — *Telmatactis cricoides* | 8 | 765 | 5 | 6 |
| plancton gelatinoso | *Callianira bialata* — *Vanadis formosa* | 9 | 645 | 7 | 9 |
| nudibranquios co-habitantes | *Doris fontainii* — *Tyrinna delicata* | 14 | 1.277 | 9 | 12 |

*(Tabla completa: material suplementario; figura principal: red top-12.)*

## 4. Discusión

Las candidatas se agrupan en tres clases de interpretación: **comensalismo/foresia** (medusa—anfípodo),
**simbiosis de limpieza** (gamba—anémona) y **co-habitación de sustrato** (fauna infaunal, fondo duro, algas coralinas). El reto metodológico central es distinguir **interacción** de
**coincidencia** por hábitat, estación o esfuerzo de observación; de ahí la exigencia de repetibilidad
espacial y temporal y el nulo estratificado en curso.

## 5. Limitaciones

1. Co-ocurrencia ≠ interacción; se mitiga con filtros y nulo, pero la confirmación última es la observación
   dirigida.
2. Sesgo de esfuerzo y de observador (eventos tipo *bioblitz*).
3. Cobertura desigual entre grupos taxonómicos.

## 6. Conclusiones y aplicaciones

Las fotografías de ciencia ciudadana contienen asociaciones ecológicas recuperables a escala de catálogo. Los
resultados permiten (a) **priorizar** la búsqueda de especies raras allí donde aparece su asociada,
(b) **enriquecer BioQuest** con sugerencias «si ves X, busca Y» y redes de asociación por zona, y (c) plantear
**hipótesis testables** para la investigación marina, con el valor añadido de cubrir aguas someras y costeras
donde los satélites rinden peor.

## Agradecimientos

A la comunidad observadora y, muy especialmente, a las **personas curadoras**: **Miquel Pontes** (`mpontes`),
**Xavier Salvador** (`xasalva`) y los curadores **`bertinhaco`**, **`uriborrajo`**, **`martanp`**, **`badosa`**
y **`guillermoalvarez`**, cuyo trabajo diario hace fiables las identificaciones de las especies **crípticas**.
Mención especial a la **FECDAS** y a su **Projecte Aneris** por impulsar la ciencia ciudadana marina y la
formación de observadores; a **Minka SDG** e **iNaturalist** por las plataformas y los datos; y a **GBIF**,
**Wikimedia Commons**, **DORIS/FFESSM**, **SeaSlugForum**, **WoRMS** y **FishBase** por las imágenes y los
datos taxonómicos. Este análisis ha sido posible gracias al **identificador BioFauna** (BioCLIP-2.5 ViT-H/14 +
FAISS) desarrollado en el proyecto.

## Material suplementario

- Tablas de asociaciones (top 40 y conjunto completo).
- Figura de red de asociaciones.
- **Láminas fotográficas** por caso (en preparación): para cada asociación, 2-4 fotografías de archivo con la
  **atribución y licencia** de su autor original. **Criterio de inclusión: solo imágenes con licencia
  reutilizable (CC BY, CC BY-SA, CC0) o permiso explícito del autor.**
