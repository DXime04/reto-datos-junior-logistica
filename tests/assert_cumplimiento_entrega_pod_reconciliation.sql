
WITH mart AS (
    SELECT
        SUM(toneladas_entregadas) AS entregadas,
        SUM(toneladas_a_tiempo) AS a_tiempo
    FROM {{ ref('cumplimiento_entrega') }}
),

esperado AS (
    SELECT
        SUM(peso_kg) / 1000.0 AS entregadas,
        SUM(
            CASE
                WHEN entrega_a_tiempo = TRUE
                THEN peso_kg
                ELSE 0
            END
        ) / 1000.0 AS a_tiempo
    FROM {{ ref('int_embarque__partida') }}
    WHERE fecha_entrega IS NOT NULL
      AND entrega_a_tiempo IS NOT NULL
)

SELECT
    mart.entregadas AS entregadas_mart,
    esperado.entregadas AS entregadas_esperadas,
    mart.a_tiempo AS a_tiempo_mart,
    esperado.a_tiempo AS a_tiempo_esperado
FROM mart
CROSS JOIN esperado
WHERE ABS(mart.entregadas - esperado.entregadas) > 0.001
   OR ABS(mart.a_tiempo - esperado.a_tiempo) > 0.001
