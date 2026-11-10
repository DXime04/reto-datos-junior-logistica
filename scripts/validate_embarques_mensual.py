
from pathlib import Path
import duckdb

# Conectar a la base de datos del proyecto
project_dir = Path(__file__).resolve().parents[1]
db_path = project_dir / "deacero.duckdb"

con = duckdb.connect(str(db_path), read_only=True)

print("\n=== VALIDACIÓN: EMBARQUES MENSUAL ===")

# 1. Revisar registros y totales
resumen = con.execute("""
    SELECT
        COUNT(*) AS registros,
        SUM(num_viajes) AS total_viajes,
        ROUND(SUM(toneladas_embarcadas), 3) AS total_toneladas,
        ROUND(SUM(costo_flete_mxn), 2) AS costo_total_mxn
    FROM mart_logistica.embarques_mensual
""").fetchone()

print("\nResumen general:")
print(f"Registros: {resumen[0]}")
print(f"Viajes: {resumen[1]}")
print(f"Toneladas: {resumen[2]}")
print(f"Costo de flete: ${resumen[3]:,.2f} MXN")

# 2. Revisar duplicados en la granularidad mensual por planta
duplicados = con.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT anio_mes, cla_planta
        FROM mart_logistica.embarques_mensual
        GROUP BY anio_mes, cla_planta
        HAVING COUNT(*) > 1
    )
""").fetchone()[0]

print(f"\nCombinaciones mes-planta duplicadas: {duplicados}")

# 3. Revisar valores nulos o inválidos
invalidos = con.execute("""
    SELECT COUNT(*)
    FROM mart_logistica.embarques_mensual
    WHERE num_viajes <= 0
       OR toneladas_embarcadas < 0
       OR costo_flete_mxn < 0
       OR costo_flete_por_ton < 0
       OR anio_mes IS NULL
       OR cla_planta IS NULL
""").fetchone()[0]

print(f"Registros con valores inválidos: {invalidos}")

# 4. Mostrar el detalle mensual
print("\nDetalle por mes y planta:")
detalle = con.execute("""
    SELECT *
    FROM mart_logistica.embarques_mensual
    ORDER BY anio_mes, cla_planta
""").fetchall()

for fila in detalle:
    print(fila)

con.close()
