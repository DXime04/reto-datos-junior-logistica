# Hallazgos del análisis de datos

## 1. Historial de cambios y estatus de viajes (`fle_viaje`)

**Qué se observó:**

- Se identificaron 5,584 registros correspondientes a 1,827 viajes.
- La fuente contiene múltiples versiones de un mismo viaje debido a los registros CDC.
- Se identificaron 19 viajes cuya última versión estaba marcada como eliminada.
- Después de seleccionar la última versión vigente, se obtuvieron 1,808 viajes.
- La distribución de estatus vigente fue: 1,652 ENT, 37 TRA, 25 PRO y 94 CAN.
- Se encontraron fechas de embarque nulas y valores centinela `1900-01-01`.

**Cómo se detectó:**

Mediante consultas de perfilamiento para comparar el número de registros contra los identificadores únicos, revisar los metadatos CDC y analizar la distribución de estatus y fechas.

**Impacto:**

Utilizar todas las versiones podría duplicar viajes y alterar los indicadores de embarques, toneladas y costos. Además, incluir viajes PRO o CAN podría contabilizar operaciones que no representan embarques realizados.

**Tratamiento:**

- Se conservaron las versiones más recientes utilizando `_ab_cdc_lsn`, con desempate mediante fechas de actualización y extracción.
- Se excluyeron los registros cuya última versión estaba eliminada.
- Se consideraron únicamente los estatus TRA y ENT para los indicadores de embarques.
- Se utilizó `FechaRealEmbarque` y, cuando no estuvo disponible o contenía el valor centinela, se recurrió a `FechaEmbarqueFinal`.
- Se excluyeron los registros sin una fecha válida de embarque.

## 2. Duplicados y versiones de partidas (`fle_viaje_det`)

**Qué se observó:**

- Se encontraron 3,965 registros en la fuente.
- Se identificaron 3,757 combinaciones únicas de `IdViaje` e `IdPartida`.
- Se observaron registros duplicados y versiones posteriores de algunas partidas.
- Se encontraron pesos nulos o no positivos: ninguno.
- Se identificaron 0 registros marcados como eliminados.

**Cómo se detectó:**

Mediante el análisis de llaves compuestas, comparación de registros repetidos y revisión de los metadatos CDC.

**Impacto:**

La duplicación de partidas podría incrementar artificialmente las toneladas embarcadas y afectar los indicadores de cumplimiento por segmento de cliente.

**Tratamiento:**

- Se eliminaron duplicados exactos.
- Se conservó la versión más reciente por combinación de `id_viaje` e `id_partida`, utilizando los metadatos CDC.
- Se conservaron únicamente las versiones vigentes.
- Se utilizó `PesoKg` para calcular toneladas mediante la conversión de kilogramos a toneladas.

El resultado fue de 3,757 partidas vigentes, con un peso acumulado de 51,001,344 kg.

## 3. Correcciones y registros faltantes de entrega (`fle_entrega`)

**Qué se observó:**

- Se encontraron 1,708 registros correspondientes a 1,628 viajes únicos.
- Se identificaron 80 registros adicionales asociados a viajes con más de una versión de entrega.
- Se detectaron viajes embarcados sin registro de prueba de entrega (POD).
- Se identificaron 61 viajes sin POD, equivalentes a 113 partidas y 1,696.068 toneladas.

**Cómo se detectó:**

Mediante la comparación de registros contra identificadores únicos de viaje, revisión de versiones CDC y cruce con los viajes embarcados.

**Impacto:**

Considerar todas las versiones podría duplicar entregas. Por otra parte, asumir que los viajes sin POD fueron entregados a tiempo o fuera de tiempo distorsionaría el indicador de cumplimiento.

**Tratamiento:**

- Se conservó la última versión de entrega por viaje, utilizando el LSN como criterio principal.
- Se evaluó la puntualidad únicamente para viajes con POD.
- Se excluyeron del denominador de cumplimiento los viajes sin evidencia de entrega.

## 4. Historial de segmentos de clientes (`vta_cliente`)

**Qué se observó:**

- Se encontraron 110 registros correspondientes a 82 clientes únicos.
- Se identificaron diferentes versiones de clientes y cambios en sus segmentos.
- Se detectaron dos clientes eliminados: 1901 y 1902, identificados como registros de prueba.
- Se observó que el cliente 1055 cambió de INDUSTRIAL a CONSTRUCTORA el 5 de febrero de 2026.
- Se identificaron partidas cuyos clientes no pudieron asociarse con un segmento válido.

**Cómo se detectó:**

Mediante el análisis de clientes únicos, versiones CDC, segmentos registrados y fechas de actualización.

**Impacto:**

Utilizar únicamente el segmento más reciente podría clasificar incorrectamente embarques históricos. Asimismo, excluir clientes desconocidos podría ocasionar pérdida de toneladas en los indicadores.

**Tratamiento:**

- Se conservó el historial de versiones vigentes de los clientes.
- Se utilizó `cdc_updated_at` como referencia temporal para asociar el segmento válido a la fecha del embarque.
- Se excluyeron las versiones eliminadas.
- Los clientes sin segmento identificable se clasificaron como `NO_IDENTIFICADO`.

En el mart de cumplimiento se conservaron 79 partidas correspondientes a 983.190 toneladas bajo el segmento `NO_IDENTIFICADO`.

## 5. Catálogo de plantas (`opc_planta`)

**Qué se observó:**

Se identificaron cuatro plantas: Monterrey, Celaya, Saltillo y Houston.

**Cómo se detectó:**

Mediante la revisión de identificadores únicos y la validación de las relaciones entre viajes y el catálogo de plantas.

**Impacto:**

Una asociación incorrecta o inexistente podría generar embarques sin identificación de planta y afectar los indicadores de operación.

**Tratamiento:**

Se utilizó `ClaPlanta` como llave de asociación entre viajes y catálogo. Los cuatro identificadores utilizados en los embarques pudieron relacionarse con su nombre de planta correspondiente.

## 6. Ajustes durante la validación de pruebas automatizadas

**Qué se observó:**

Durante la primera ejecución de `dbt test`, tres pruebas finalizaron correctamente y dos presentaron errores de tipo `Binder Error`, debido a referencias ambiguas a columnas compartidas entre las CTE `mart` y `esperado`.

**Cómo se detectó:**

Al ejecutar las pruebas de conciliación, DuckDB reportó ambigüedad en las columnas `viajes` y `entregadas`.

**Impacto:**

Las dos pruebas de conciliación no pudieron ejecutarse correctamente. El problema se encontraba en las consultas de validación y no en los modelos ni en los resultados de los marts.

**Tratamiento:**

Se corrigieron las consultas calificando explícitamente las columnas mediante sus respectivos alias (`mart` y `esperado`).

**Resultado:**

Se ejecutó nuevamente `dbt test` y las cinco pruebas automatizadas finalizaron exitosamente:

- 5 PASS
- 0 WARN
- 0 ERROR
- 0 SKIP

## 7. Resultados generales de los marts

### `embarques_mensual`

- 24 registros agregados.
- 1,689 viajes.
- 47,091.622 toneladas embarcadas.
- $28,421,589.81 MXN en costo de flete.
- Sin duplicados en la granularidad `anio_mes × cla_planta`.

El costo de flete por tonelada se calculó como la división del costo total entre las toneladas totales de cada combinación de mes y planta.

### `cumplimiento_entrega`

- 24 registros agregados.
- 45,395.554 toneladas entregadas con POD.
- 24,473.001 toneladas entregadas a tiempo.
- 53.91% de cumplimiento ponderado.
- Sin duplicados en la granularidad `anio_mes × segmento_cliente`.

Los viajes sin POD se excluyeron del cálculo del cumplimiento, de acuerdo con las reglas de negocio establecidas.

---

## Consideraciones finales

Los principales retos identificados estuvieron relacionados con el historial de cambios CDC, la duplicación de registros, la ausencia de evidencia de entrega y los cambios históricos en la segmentación de clientes.

El tratamiento aplicado busca conservar la información vigente, evitar duplicaciones y mantener la trazabilidad de las decisiones de transformación.

Los resultados fueron contrastados mediante consultas de validación y pruebas automatizadas de granularidad, reglas de negocio y conciliación.