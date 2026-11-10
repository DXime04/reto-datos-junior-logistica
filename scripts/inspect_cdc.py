
from pathlib import Path
import duckdb

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "deacero.duckdb"

conn = duckdb.connect(str(DB_PATH), read_only=True)

try:
    # 1. VERSIONES DE UNA PARTIDA
    print("\n=== VERSIONES DE PARTIDAS ===\n")

    partidas = conn.execute("""
        SELECT
            id_viaje,
            id_partida,
            peso_kg,
            cdc_lsn,
            cdc_updated_at,
            cdc_deleted_at,
            airbyte_extracted_at
        FROM main.stg_fle__viaje_det
        WHERE id_viaje = 250987
          AND id_partida = 1
        ORDER BY TRY_CAST(cdc_lsn AS BIGINT)
    """).fetchall()

    for fila in partidas:
        print(fila)

    # 2. VERSIONES DE UNA ENTREGA
    print("\n=== VERSIONES DE ENTREGA ===\n")

    entregas = conn.execute("""
        SELECT
            id_viaje,
            fecha_entrega,
            cdc_lsn,
            cdc_updated_at,
            cdc_deleted_at,
            airbyte_extracted_at
        FROM main.stg_fle__entrega
        WHERE id_viaje = 250221
        ORDER BY TRY_CAST(cdc_lsn AS BIGINT)
    """).fetchall()

    for fila in entregas:
        print(fila)

    # 3. VIAJE RELACIONADO CON ESAS ENTREGAS
    print("\n=== VIAJE 250221 ===\n")

    viaje = conn.execute("""
        SELECT
            id_viaje,
            estatus,
            fecha_compromiso,
            fecha_real_embarque,
            fecha_embarque_final,
            costo_flete,
            cdc_lsn,
            cdc_updated_at,
            cdc_deleted_at
        FROM main.stg_fle__viaje
        WHERE id_viaje = 250221
        ORDER BY TRY_CAST(cdc_lsn AS BIGINT)
    """).fetchall()

    for fila in viaje:
        print(fila)

    # 4. HISTORIAL DE UN CLIENTE
    print("\n=== HISTORIAL DEL CLIENTE 1055 ===\n")

    cliente = conn.execute("""
        SELECT
            cla_cliente,
            nom_cliente,
            segmento,
            cdc_lsn,
            cdc_updated_at,
            cdc_deleted_at,
            airbyte_extracted_at
        FROM main.stg_vta__cliente
        WHERE cla_cliente = 1055
        ORDER BY TRY_CAST(cdc_lsn AS BIGINT)
    """).fetchall()

    for fila in cliente:
        print(fila)

finally:
    conn.close()
