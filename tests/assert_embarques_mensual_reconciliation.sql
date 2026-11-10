
WITH mart AS (
    SELECT
        SUM(num_viajes) AS viajes,
        SUM(toneladas_embarcadas) AS toneladas,
        SUM(costo_flete_mxn) AS costo
    FROM {{ ref('embarques_mensual') }}
),

esperado AS (
    SELECT
        COUNT(*) AS viajes,
        SUM(toneladas_embarcadas) AS toneladas,
        SUM(costo_flete) AS costo
    FROM {{ ref('int_embarque__viaje_metricas') }}
)

SELECT
    mart.viajes AS viajes_mart,
    esperado.viajes AS viajes_esperados,
    mart.toneladas AS toneladas_mart,
    esperado.toneladas AS toneladas_esperadas,
    mart.costo AS costo_mart,
    esperado.costo AS costo_esperado
FROM mart
CROSS JOIN esperado
WHERE mart.viajes != esperado.viajes
   OR ABS(mart.toneladas - esperado.toneladas) > 0.001
   OR ABS(mart.costo - esperado.costo) > 0.01
