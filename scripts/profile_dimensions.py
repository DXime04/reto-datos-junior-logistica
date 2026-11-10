
from pathlib import Path
import duckdb

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "deacero.duckdb"

conn = duckdb.connect(str(DB_PATH), read_only=True)

try:
    # CLIENTES
    print("\n=== PERFILAMIENTO: CLIENTES ===\n")

    resumen_clientes = conn.execute("""
        SELECT
            COUNT(*) AS total_registros,
            COUNT(DISTINCT cla_cliente) AS clientes_unicos,
            COUNT(DISTINCT cdc_lsn) AS lsn_unicos,
            COUNT(*) FILTER (
                WHERE cdc_deleted_at IS NOT NULL
            ) AS registros_eliminados,
            COUNT(*) FILTER (
                WHERE segmento IS NULL
            ) AS segmentos_nulos,
            COUNT(DISTINCT segmento) AS segmentos_distintos
        FROM main.stg_vta__cliente
    """).fetchone()

    print("Resumen general:")
    print(resumen_clientes)

    print("\nDistribución de segmentos:")
    segmentos = conn.execute("""
        SELECT segmento, COUNT(*) AS registros
        FROM main.stg_vta__cliente
        GROUP BY segmento
        ORDER BY registros DESC
    """).fetchall()

    for fila in segmentos:
        print(fila)

    print("\nHistorial de clientes con más de un registro:")
    historial = conn.execute("""
        SELECT
            cla_cliente,
            COUNT(*) AS versiones,
            COUNT(DISTINCT segmento) AS segmentos_distintos,
            MIN(cdc_updated_at) AS primera_actualizacion,
            MAX(cdc_updated_at) AS ultima_actualizacion
        FROM main.stg_vta__cliente
        GROUP BY cla_cliente
        HAVING COUNT(*) > 1
        ORDER BY versiones DESC
        LIMIT 15
    """).fetchall()

    for fila in historial:
        print(fila)

    # PLANTAS
    print("\n=== PERFILAMIENTO: PLANTAS ===\n")

    plantas = conn.execute("""
        SELECT
            COUNT(*) AS total_registros,
            COUNT(DISTINCT cla_planta) AS plantas_unicas,
            COUNT(*) FILTER (
                WHERE cla_planta IS NULL
            ) AS claves_nulas,
            COUNT(*) FILTER (
                WHERE nom_planta IS NULL
            ) AS nombres_nulos,
            COUNT(*) FILTER (
                WHERE cdc_deleted_at IS NOT NULL
            ) AS registros_eliminados
        FROM main.stg_opc__planta
    """).fetchone()

    print("Resumen general:")
    print(plantas)

    print("\nCatálogo de plantas:")
    catalogo = conn.execute("""
        SELECT cla_planta, nom_planta, cla_pais
        FROM main.stg_opc__planta
        ORDER BY cla_planta
    """).fetchall()

    for fila in catalogo:
        print(fila)

    # DUPLICADOS DE DETALLE
    print("\n=== REVISION: PARTIDAS REPETIDAS ===\n")

    duplicados_detalle = conn.execute("""
        SELECT
            id_viaje,
            id_partida,
            COUNT(*) AS versiones,
            COUNT(DISTINCT cdc_lsn) AS lsn_distintos
        FROM main.stg_fle__viaje_det
        GROUP BY id_viaje, id_partida
        HAVING COUNT(*) > 1
        ORDER BY versiones DESC
        LIMIT 10
    """).fetchall()

    for fila in duplicados_detalle:
        print(fila)

    # DUPLICADOS DE ENTREGA
    print("\n=== REVISION: VIAJES CON VARIAS ENTREGAS ===\n")

    duplicados_entrega = conn.execute("""
        SELECT
            id_viaje,
            COUNT(*) AS registros,
            MIN(fecha_entrega) AS primera_fecha,
            MAX(fecha_entrega) AS ultima_fecha
        FROM main.stg_fle__entrega
        GROUP BY id_viaje
        HAVING COUNT(*) > 1
        ORDER BY registros DESC
        LIMIT 15
    """).fetchall()

    for fila in duplicados_entrega:
        print(fila)

finally:
    conn.close()
