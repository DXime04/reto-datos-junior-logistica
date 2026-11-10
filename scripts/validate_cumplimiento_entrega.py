
from pathlib import Path
import duckdb

project_dir = Path(__file__).resolve().parents[1]
db_path = project_dir / "deacero.duckdb"

con = duckdb.connect(str(db_path), read_only=True)

print("\n=== VALIDACIÓN: CUMPLIMIENTO ENTREGA ===")

# 1. Resumen general
resumen = con.execute("""
    SELECT
        COUNT(*) AS registros,
        ROUND(SUM(toneladas_entregadas), 3),
        ROUND(SUM(toneladas_a_tiempo), 3),
        ROUND(
            100.0 * SUM(toneladas_a_tiempo) /
            NULLIF(SUM(toneladas_entregadas), 0),
            2
        )
    FROM mart_logistica.cumplimiento_entrega
""").fetchone()

print("\nResumen general:")
print(f"Registros: {resumen[0]}")
print(f"Toneladas entregadas: {resumen[1]}")
print(f"Toneladas a tiempo: {resumen[2]}")
print(f"Cumplimiento global: {resumen[3]}%")

# 2. Distribución por segmento
print("\nResultados por segmento:")
segmentos = con.execute("""
    SELECT
        segmento_cliente,
        SUM(toneladas_entregadas),
        SUM(toneladas_a_tiempo),
        ROUND(
            100.0 * SUM(toneladas_a_tiempo) /
            NULLIF(SUM(toneladas_entregadas), 0),
            2
        )
    FROM mart_logistica.cumplimiento_entrega
    GROUP BY segmento_cliente
    ORDER BY segmento_cliente
""").fetchall()

for fila in segmentos:
    print(fila)

# 3. Revisar duplicados en la granularidad
duplicados = con.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT anio_mes, segmento_cliente
        FROM mart_logistica.cumplimiento_entrega
        GROUP BY anio_mes, segmento_cliente
        HAVING COUNT(*) > 1
    )
""").fetchone()[0]

print(f"\nCombinaciones mes-segmento duplicadas: {duplicados}")

# 4. Revisar porcentajes fuera de rango
porcentajes_invalidos = con.execute("""
    SELECT COUNT(*)
    FROM mart_logistica.cumplimiento_entrega
    WHERE pct_a_tiempo < 0
       OR pct_a_tiempo > 100
       OR pct_a_tiempo IS NULL
""").fetchone()[0]

print(f"Porcentajes inválidos: {porcentajes_invalidos}")

# 5. Revisar toneladas a tiempo mayores que las entregadas
toneladas_invalidas = con.execute("""
    SELECT COUNT(*)
    FROM mart_logistica.cumplimiento_entrega
    WHERE toneladas_a_tiempo > toneladas_entregadas
       OR toneladas_a_tiempo < 0
       OR toneladas_entregadas <= 0
""").fetchone()[0]

print(f"Registros con toneladas inválidas: {toneladas_invalidas}")

# 6. Revisar categorías
print("\nSegmentos incluidos:")
print(con.execute("""
    SELECT DISTINCT segmento_cliente
    FROM mart_logistica.cumplimiento_entrega
    ORDER BY segmento_cliente
""").fetchall())

con.close()
