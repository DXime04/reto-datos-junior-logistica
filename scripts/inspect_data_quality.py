
from pathlib import Path
import duckdb

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "deacero.duckdb"

conn = duckdb.connect(str(DB_PATH), read_only=True)

try:
    print("\n=== CLIENTES ELIMINADOS ===\n")

    eliminados = conn.execute("""
        SELECT
            cla_cliente,
            nom_cliente,
            segmento,
            cdc_lsn,
            cdc_updated_at,
            cdc_deleted_at
        FROM main.stg_vta__cliente
        WHERE cdc_deleted_at IS NOT NULL
        ORDER BY TRY_CAST(cdc_lsn AS BIGINT)
    """).fetchall()

    for fila in eliminados:
        print(fila)

    print("\n=== LSN REPETIDOS EN VIAJES ===\n")

    viajes = conn.execute("""
        SELECT
            cdc_lsn,
            COUNT(*) AS registros,
            COUNT(DISTINCT (
                id_viaje, estatus, fecha_compromiso,
                fecha_real_embarque, fecha_embarque_final,
                costo_flete
            )) AS versiones_distintas
        FROM main.stg_fle__viaje
        GROUP BY cdc_lsn
        HAVING COUNT(*) > 1
        ORDER BY registros DESC
        LIMIT 10
    """).fetchall()

    for fila in viajes:
        print(fila)

    print("\n=== LSN REPETIDOS EN DETALLES ===\n")

    detalles = conn.execute("""
        SELECT
            cdc_lsn,
            COUNT(*) AS registros,
            COUNT(DISTINCT (
                id_viaje, id_partida, cla_cliente,
                cla_articulo, peso_kg
            )) AS versiones_distintas
        FROM main.stg_fle__viaje_det
        GROUP BY cdc_lsn
        HAVING COUNT(*) > 1
        ORDER BY registros DESC
        LIMIT 10
    """).fetchall()

    for fila in detalles:
        print(fila)

    print("\n=== LSN CON INFORMACION DIFERENTE: VIAJES ===\n")

    conflictos_viajes = conn.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT cdc_lsn
            FROM main.stg_fle__viaje
            GROUP BY cdc_lsn
            HAVING COUNT(DISTINCT (
                id_viaje, estatus, fecha_compromiso,
                fecha_real_embarque, fecha_embarque_final,
                costo_flete
            )) > 1
        ) AS conflictos
    """).fetchone()

    print("LSN conflictivos:", conflictos_viajes[0])

    print("\n=== LSN CON INFORMACION DIFERENTE: DETALLES ===\n")

    conflictos_detalles = conn.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT cdc_lsn
            FROM main.stg_fle__viaje_det
            GROUP BY cdc_lsn
            HAVING COUNT(DISTINCT (
                id_viaje, id_partida, cla_cliente,
                cla_articulo, peso_kg
            )) > 1
        ) AS conflictos
    """).fetchone()

    print("LSN conflictivos:", conflictos_detalles[0])

finally:
    conn.close()
