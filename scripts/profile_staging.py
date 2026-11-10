
from pathlib import Path
import duckdb

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "deacero.duckdb"

conn = duckdb.connect(str(DB_PATH), read_only=True)

try:
    print("\n=== PERFILAMIENTO: VIAJES ===\n")

    # 1. Resumen general
    resumen = conn.execute("""
        SELECT
            COUNT(*) AS total_registros,
            COUNT(DISTINCT id_viaje) AS viajes_unicos,
            COUNT(*) - COUNT(DISTINCT id_viaje) AS diferencia_registros,
            COUNT(DISTINCT cdc_lsn) AS lsn_unicos,
            COUNT(*) FILTER (
                WHERE id_viaje IS NULL
            ) AS viajes_sin_identificador,
            COUNT(*) FILTER (
                WHERE cdc_deleted_at IS NOT NULL
            ) AS registros_eliminados
        FROM main.stg_fle__viaje
    """).fetchone()

    print("Resumen general:")
    print(resumen)

    # 2. Distribución de estatus
    print("\nDistribución de estatus:")

    estatus = conn.execute("""
        SELECT
            estatus,
            COUNT(*) AS registros
        FROM main.stg_fle__viaje
        GROUP BY estatus
        ORDER BY registros DESC
    """).fetchall()

    for fila in estatus:
        print(fila)

    # 3. Fechas de embarque
    print("\nFechas reales de embarque:")

    fechas = conn.execute("""
        SELECT
            COUNT(*) FILTER (
                WHERE fecha_real_embarque IS NULL
            ) AS fechas_nulas,

            COUNT(*) FILTER (
                WHERE CAST(fecha_real_embarque AS DATE)
                    = DATE '1900-01-01'
            ) AS fechas_1900,

            COUNT(*) FILTER (
                WHERE fecha_real_embarque IS NOT NULL
                  AND CAST(fecha_real_embarque AS DATE)
                    <> DATE '1900-01-01'
            ) AS fechas_validas
        FROM main.stg_fle__viaje
    """).fetchone()

    print(fechas)

    # 4. Calidad de fechas por estatus y disponibilidad de fecha alternativa
    print("\nFechas y alternativas por estatus:")

    fechas_estatus = conn.execute("""
        SELECT
            estatus,
            COUNT(*) AS registros,

            COUNT(*) FILTER (
                WHERE fecha_real_embarque IS NULL
                   OR CAST(fecha_real_embarque AS DATE) = DATE '1900-01-01'
            ) AS fecha_real_no_disponible,

            COUNT(*) FILTER (
                WHERE fecha_embarque_final IS NOT NULL
                  AND CAST(fecha_embarque_final AS DATE) <> DATE '1900-01-01'
            ) AS fecha_final_valida,

            COUNT(*) FILTER (
                WHERE (
                    fecha_real_embarque IS NULL
                    OR CAST(fecha_real_embarque AS DATE) = DATE '1900-01-01'
                )
                AND (
                    fecha_embarque_final IS NULL
                    OR CAST(fecha_embarque_final AS DATE) = DATE '1900-01-01'
                )
            ) AS sin_ninguna_fecha_valida

        FROM main.stg_fle__viaje
        GROUP BY estatus
        ORDER BY estatus
    """).fetchall()

    for fila in fechas_estatus:
        print(fila)

    # 5. Disponibilidad de costos
    print("\nDisponibilidad de costos por estatus:")

    costos = conn.execute("""
        SELECT
            estatus,
            COUNT(*) AS registros,
            COUNT(*) FILTER (WHERE costo_flete IS NULL) AS costos_nulos,
            COUNT(*) FILTER (WHERE costo_flete = 0) AS costos_cero,
            MIN(costo_flete) AS costo_minimo,
            MAX(costo_flete) AS costo_maximo
        FROM main.stg_fle__viaje
        GROUP BY estatus
        ORDER BY estatus
    """).fetchall()

    for fila in costos:
        print(fila)

    # 6. Metadatos CDC
    print("\nResumen de metadatos CDC:")

    cdc = conn.execute("""
        SELECT
            COUNT(*) FILTER (WHERE cdc_lsn IS NULL) AS lsn_nulos,
            COUNT(*) FILTER (WHERE cdc_updated_at IS NULL) AS updated_at_nulos,
            COUNT(DISTINCT cdc_lsn) AS lsn_distintos,
            MIN(cdc_updated_at) AS primera_actualizacion,
            MAX(cdc_updated_at) AS ultima_actualizacion
        FROM main.stg_fle__viaje
    """).fetchone()

    print(cdc)

    print("\nEjemplos de valores LSN:")

    lsn = conn.execute("""
        SELECT DISTINCT cdc_lsn
        FROM main.stg_fle__viaje
        WHERE cdc_lsn IS NOT NULL
        ORDER BY cdc_lsn
        LIMIT 10
    """).fetchall()

    for fila in lsn:
        print(fila)

finally:
    conn.close()
