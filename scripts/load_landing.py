
from pathlib import Path
import duckdb


# Rutas del proyecto
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "replica" / "carga_1"
DB_PATH = ROOT_DIR / "deacero.duckdb"


# Archivos CSV y esquemas de destino
FILES = {
    "fle_viaje": "landing_fle",
    "fle_viaje_det": "landing_fle",
    "fle_entrega": "landing_fle",
    "vta_cliente": "landing_vta",
    "opc_planta": "landing_opc",
}


def load_landing():
    conn = duckdb.connect(str(DB_PATH))

    try:
        # Crear esquemas
        schemas = set(FILES.values())

        for schema in schemas:
            conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        print("Iniciando carga de datos Landing...\n")

        for table, schema in FILES.items():
            csv_path = DATA_DIR / f"{table}.csv"

            if not csv_path.exists():
                raise FileNotFoundError(
                    f"No se encontró el archivo: {csv_path}"
                )

            # Conservar todas las columnas como texto.
            # El valor centinela evita interpretar campos vacíos
            # como NULL durante la carga.
            csv_sql_path = csv_path.as_posix().replace("'", "''")

            conn.execute(f"""
                CREATE OR REPLACE TABLE {schema}.{table} AS
                SELECT *
                FROM read_csv(
                    '{csv_sql_path}',
                    header = true,
                    all_varchar = true,
                    nullstr = '__DBT_NULL_SENTINEL__'
                )
            """)

            count = conn.execute(
                f"SELECT COUNT(*) FROM {schema}.{table}"
            ).fetchone()[0]

            print(f"{schema}.{table}: {count:,} registros cargados")

        print("\n¡Carga Landing completada correctamente!")

    finally:
        conn.close()


if __name__ == "__main__":
    load_landing()
