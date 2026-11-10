
from pathlib import Path
import duckdb

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "deacero.duckdb"

conn = duckdb.connect(str(DB_PATH), read_only=True)

try:
    # PERFILAMIENTO DE DETALLES
    print("\n=== PERFILAMIENTO: DETALLES DE VIAJE ===\n")

    detalle = conn.execute("""
        SELECT
            COUNT(*) AS total_registros,
            COUNT(DISTINCT id_viaje) AS viajes_unicos,
            COUNT(DISTINCT (id_viaje, id_partida)) AS claves_compuestas_unicas,
            COUNT(*) FILTER (
                WHERE id_viaje IS NULL OR id_partida IS NULL
            ) AS claves_nulas,
            COUNT(*) FILTER (
                WHERE peso_kg IS NULL
            ) AS pesos_nulos,
            COUNT(*) FILTER (
                WHERE peso_kg <= 0
            ) AS pesos_no_positivos,
            COUNT(DISTINCT cdc_lsn) AS lsn_unicos,
            COUNT(*) FILTER (
                WHERE cdc_deleted_at IS NOT NULL
            ) AS registros_eliminados
        FROM main.stg_fle__viaje_det
    """).fetchone()

    print("Resumen general:")
    print(detalle)

    print("\nDistribución de partidas:")
    partidas = conn.execute("""
        SELECT id_partida, COUNT(*) AS registros
        FROM main.stg_fle__viaje_det
        GROUP BY id_partida
        ORDER BY id_partida
    """).fetchall()

    for fila in partidas:
        print(fila)

    # PERFILAMIENTO DE ENTREGAS
    print("\n=== PERFILAMIENTO: ENTREGAS ===\n")

    entrega = conn.execute("""
        SELECT
            COUNT(*) AS total_registros,
            COUNT(DISTINCT id_viaje) AS viajes_unicos,
            COUNT(*) FILTER (
                WHERE id_viaje IS NULL
            ) AS viajes_sin_identificador,
            COUNT(*) FILTER (
                WHERE fecha_entrega IS NULL
            ) AS fechas_entrega_nulas,
            COUNT(DISTINCT cdc_lsn) AS lsn_unicos,
            COUNT(*) FILTER (
                WHERE cdc_deleted_at IS NOT NULL
            ) AS registros_eliminados
        FROM main.stg_fle__entrega
    """).fetchone()

    print("Resumen general:")
    print(entrega)

finally:
    conn.close()
