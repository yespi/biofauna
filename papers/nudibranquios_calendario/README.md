# Calendario de observación de los nudibranquios y su sustrato

**Estado: BORRADOR AUTOMÁTICO (8-oct-2026).** Primera versión del calendario por especie; **aún sin sustrato, sin datos de BioQuest y sin revisión a ojo**.

## Qué hay
- [`CALENDARIO_BORRADOR_20261008.md`](CALENDARIO_BORRADOR_20261008.md): tabla por especie con el periodo del año en que se observa («17 diciembre – 9 julio», «Todo el año», …) **y el pico de observaciones entre paréntesis** («Todo el año (pico: Julio–Agosto)») y **las 3 ubicaciones donde más se ve** (p. ej. *Cratena peregrina*: Todo el año · Tarragona, Illes Medes / L'Estartit, Reserva del Toro).
- [`calendario_nudibranquios_20261008.csv`](calendario_nudibranquios_20261008.csv): los mismos datos en tabla.
- Código: [`../../scripts/nudi_calendario_20261008.py`](../../scripts/nudi_calendario_20261008.py).

## Cómo se calcula (regla ajustable)
Observaciones con fecha de iNaturalist, Minka SDG y GBIF dentro de una caja mediterránea (lon −5,6…36,3; lat 30…46,6), sin duplicados (observador + fecha + coordenadas redondeadas). Histograma del día del año, suavizado circularmente (ventana de 15 días); un día es «observable» si supera el 15 % del máximo; los huecos de hasta 21 días se unen y se descartan tramos de menos de 10 días; el año se trata como circular (un periodo puede cruzar el fin de año). Con menos de 20 observaciones: «sin dato suficiente». **Regla «Todo el año» (orden de Gustavo, 8-oct):** si hay observaciones en 11 o más de los 12 meses (con al menos 30 observaciones) o el periodo cubre 300 días o más, se asume que puede verse siempre (36 de las 54 especies con datos). **Pico:** el mes (o los dos meses seguidos) con más observaciones únicas; se muestran dos si el segundo alcanza el 85 % del primero. **Ubicaciones:** las 3 zonas con más observaciones; en la costa de Cataluña se asignan a una lista de zonas de buceo (Tossa de Mar, Illes Medes, Blanes, Cap de Creus…, radio ≈6 km) y, fuera de ella, a la localidad más frecuente del texto de lugar de las observaciones (celdas de 0,1°); el nombre de lugar de las plataformas es irregular, así que es orientativo.

## Cobertura y limitaciones
- **54 de las 133 especies de Nudibranchia del catálogo** tienen datos suficientes; el resto figura como «sin dato suficiente».
- Es un calendario de **cuándo se fotografía**, no de cuándo está presente el animal: la ciencia ciudadana tiene sesgo estival y de esfuerzo de buceo, y la regla produce periodos muy amplios en especies abundantes.
- Pendiente: sustrato (esponja, planta, alga, hidrozoo…, en lista si hay varios), datos de BioQuest, revisión a ojo con curadores y rango por zona (Cataluña frente al resto).

## Datos y atribución
Las fotografías que se incluyan llevarán autor, licencia, fecha y hora, lugar y coordenadas, como en los demás documentos de este repositorio. Ver también [`../proyecto_correlacion/`](../proyecto_correlacion/).
