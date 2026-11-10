# Reto de Ingeniería de Datos Junior – Logística DEACERO

## Descripción del proyecto

Este proyecto implementa un flujo de ingeniería de datos para transformar información operativa de logística en dos modelos analíticos (*marts*) utilizando **dbt y DuckDB**.

El objetivo es integrar, depurar y transformar información de viajes, partidas, entregas, clientes y plantas para generar indicadores que permitan analizar los embarques mensuales y el cumplimiento de entregas.

Se priorizaron la trazabilidad de las transformaciones, la calidad de los datos, la aplicación de reglas de negocio y la reproducibilidad de los resultados.

## Tecnologías utilizadas

- **Python 3.12:** carga de archivos CSV y análisis exploratorio.
- **DuckDB:** almacenamiento y procesamiento local de datos.
- **dbt Core:** transformación, organización y pruebas de datos.
- **SQL:** limpieza, integración, cálculos y agregaciones.
- **Git y GitHub:** control de versiones y publicación del proyecto.

## Arquitectura del proyecto

El flujo se organiza en tres capas principales:

| Capa | Descripción |
|---|---|
| Landing | Datos originales cargados desde los archivos CSV, conservando las columnas como texto. |
| Staging | Estandarización de nombres, limpieza de valores y conversión de tipos de datos. |
| Intermediate | Depuración de versiones CDC, integración de fuentes y aplicación de reglas de negocio. |
| Marts | Modelos analíticos agregados para consumo y análisis. |

### Flujo de datos

```
Archivos CSV
     |
     v
Landing (DuckDB)
     |
     v
Staging (dbt)
     |
     v
Intermediate (dbt)
     |
     +----------------------+
     |                      |
     v                      v
embarques_mensual    cumplimiento_entrega
     |                      |
     +----------+-----------+
                |
                v
       Pruebas automatizadas
```

## Modelos analíticos

Los dos modelos finales se generan en el esquema `mart_logistica`.

### 1. `embarques_mensual`

**Granularidad:** un registro por combinación de año-mes y planta.

| Campo | Descripción |
|---|---|
| `anio_mes` | Mes del embarque en formato YYYY-MM. |
| `cla_planta` | Identificador de la planta. |
| `nom_planta` | Nombre de la planta. |
| `num_viajes` | Cantidad de viajes embarcados. |
| `toneladas_embarcadas` | Toneladas totales embarcadas. |
| `costo_flete_mxn` | Costo total de flete en MXN. |
| `costo_flete_por_ton` | Costo de flete por tonelada. |

El costo por tonelada se calcula dividiendo el costo total del flete entre las toneladas embarcadas de cada combinación de mes y planta.

### 2. `cumplimiento_entrega`

**Granularidad:** un registro por combinación de año-mes y segmento de cliente.

| Campo | Descripción |
|---|---|
| `anio_mes` | Mes del embarque en formato YYYY-MM. |
| `segmento_cliente` | Segmento del cliente. |
| `toneladas_entregadas` | Toneladas correspondientes a entregas con POD. |
| `toneladas_a_tiempo` | Toneladas entregadas dentro de la fecha compromiso. |
| `pct_a_tiempo` | Porcentaje de toneladas entregadas a tiempo. |

Los segmentos considerados son `DISTRIBUIDOR`, `CONSTRUCTORA`, `INDUSTRIAL` y `NO_IDENTIFICADO`.

El porcentaje de cumplimiento se calcula de forma ponderada, utilizando las toneladas entregadas y no el número de viajes.

## Estructura del repositorio

```
DEACERO-Data-Challenge/
│
├── data/
│   └── replica/
│       └── carga_1/
│           ├── fle_entrega.csv
│           ├── fle_viaje.csv
│           ├── fle_viaje_det.csv
│           ├── opc_planta.csv
│           └── vta_cliente.csv
│
├── docs/
│   ├── contrato-marts.md
│   ├── convenciones.md
│   ├── diccionario-landing.md
│   └── requerimiento-negocio.md
│
├── macros/
│   └── generate_schema_name.sql
│
├── models/
│   ├── staging/
│   ├── intermediate/
│   └── marts/
│
├── scripts/
│   ├── load_landing.py
│   └── ...
│
├── tests/
│
├── HALLAZGOS.md
├── dbt_project.yml
├── .gitignore
└── README.md
```

Los scripts adicionales de perfilamiento y validación se encuentran en la carpeta `scripts/`.

## Requisitos previos

- Python 3.12.
- Git.
- Acceso a los archivos CSV incluidos en `data/replica/carga_1/`.

No se requiere una instancia externa de base de datos ni servicios en la nube.

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/DXime04/reto-datos-junior-logistica.git
cd reto-datos-junior-logistica
```

### 2. Crear y activar el entorno virtual

En Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar el perfil de dbt

Crear el archivo `profiles.yml` en:

```
%USERPROFILE%\.dbt\profiles.yml
```

Agregar la siguiente configuración, sustituyendo la ruta por la ubicación local del proyecto:

```yaml
deacero_logistica:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: 'RUTA_LOCAL_DEL_PROYECTO/deacero.duckdb'
      schema: main
      threads: 4
```

Verificar la conexión:

```powershell
dbt debug
```

### 5. Cargar los datos Landing

Desde la raíz del proyecto, ejecutar:

```powershell
python scripts/load_landing.py
```

El script crea los esquemas necesarios y carga los cinco archivos CSV en DuckDB.

Las tablas se generan mediante `CREATE OR REPLACE TABLE`, por lo que volver a ejecutar el script reemplaza los datos anteriores y evita duplicaciones.

### 6. Ejecutar transformaciones y pruebas

Ejecutar:

```powershell
dbt build
```

Este comando construye los modelos y ejecuta las pruebas de datos definidas en el proyecto.

Para ejecutar las pruebas por separado:

```powershell
dbt test
```

La ejecución puede repetirse sin acumular registros, ya que los modelos se reconstruyen a partir de las fuentes Landing.

## Decisiones de transformación y reglas de negocio

Entre las principales decisiones implementadas se encuentran:

- **Versiones CDC:** se conserva la versión más reciente de cada registro utilizando `_ab_cdc_lsn` como criterio principal y las fechas de actualización y extracción como desempate.
- **Eliminaciones CDC:** se excluyen los registros cuya última versión está marcada como eliminada.
- **Estatus de viaje:** únicamente se consideran viajes `TRA` y `ENT` para los indicadores de embarques.
- **Fecha de embarque:** se utiliza `FechaRealEmbarque`; cuando no está disponible o contiene el valor centinela `1900-01-01`, se recurre a `FechaEmbarqueFinal`.
- **Toneladas:** se calcula la conversión de kilogramos a toneladas a partir del peso de las partidas.
- **Costo de flete:** se contabiliza una sola vez por viaje para evitar duplicaciones al integrar partidas.
- **Puntualidad:** se compara la fecha de entrega registrada en el POD contra la fecha compromiso.
- **Ausencia de POD:** los viajes sin evidencia de entrega no se consideran dentro del cálculo del cumplimiento.
- **Segmentación histórica:** se utiliza la versión del segmento del cliente vigente a la fecha del embarque.
- **Clientes no identificados:** se conservan bajo el segmento `NO_IDENTIFICADO`.

El detalle de los hallazgos, su impacto y el tratamiento aplicado se encuentra en `HALLAZGOS.md`.

## Pruebas automatizadas

Se implementaron cinco pruebas de datos mediante dbt:

| Prueba | Objetivo |
|---|---|
| `assert_embarques_mensual_grain` | Verificar la granularidad del mart de embarques. |
| `assert_embarques_mensual_reconciliation` | Conciliar viajes, toneladas y costos contra el modelo intermedio. |
| `assert_cumplimiento_entrega_grain` | Verificar la granularidad del mart de cumplimiento. |
| `assert_cumplimiento_entrega_pod_reconciliation` | Conciliar toneladas entregadas y a tiempo contra los registros con POD. |
| `assert_cumplimiento_entrega_business_rules` | Validar porcentajes y límites de toneladas conforme a las reglas de negocio. |

**Último resultado de ejecución:**

```text
PASS=5
WARN=0
ERROR=0
SKIP=0
```

## Resultados obtenidos

### Embarques mensuales

- 24 registros agregados.
- 1,689 viajes.
- 47,091.622 toneladas embarcadas.
- $28,421,589.81 MXN en costo total de flete.

### Cumplimiento de entrega

- 24 registros agregados.
- 45,395.554 toneladas entregadas con POD.
- 24,473.001 toneladas entregadas a tiempo.
- 53.91% de cumplimiento ponderado.

Los viajes sin POD se excluyeron del indicador de cumplimiento, de acuerdo con la regla de negocio establecida.

## Valor agregado

Además de los modelos solicitados, se incorporaron actividades y componentes para fortalecer la calidad y trazabilidad del proyecto:

- Scripts de perfilamiento exploratorio de las fuentes.
- Validaciones de llaves, duplicados, valores nulos y metadatos CDC.
- Modelos intermedios para separar la lógica de negocio de las agregaciones finales.
- Pruebas automatizadas de granularidad, conciliación y reglas de negocio.
- Documentación de hallazgos y decisiones de transformación.

## Fuera de alcance

- Desarrollo de dashboards o interfaces de visualización.
- Implementación de infraestructura productiva o despliegue en la nube.
- Automatización de cargas mediante orquestadores.
- Integración con fuentes externas distintas a los archivos proporcionados.
- Implementación de mecanismos de actualización incremental o procesamiento CDC en tiempo real.

## Consideraciones finales

El proyecto busca demostrar un flujo reproducible de ingeniería de datos, desde la ingesta y perfilamiento hasta la transformación y validación de información logística.

La base de datos `deacero.duckdb` se genera localmente durante la ejecución y no se incluye en el repositorio. Los datos pueden reconstruirse siguiendo los pasos de instalación y ejecución descritos anteriormente.