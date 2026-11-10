
WITH entregas AS (
    SELECT
        STRFTIME(fecha_embarque, '%Y-%m') AS anio_mes,
        segmento_cliente,
        peso_kg,
        entrega_a_tiempo
    FROM {{ ref('int_embarque__partida') }}
    WHERE fecha_entrega IS NOT NULL
      AND entrega_a_tiempo IS NOT NULL
),

metricas AS (
    SELECT
        anio_mes,
        segmento_cliente,

        SUM(peso_kg) / 1000.0 AS toneladas_entregadas,

        SUM(
            CASE
                WHEN entrega_a_tiempo = TRUE
                THEN peso_kg
                ELSE 0
            END
        ) / 1000.0 AS toneladas_a_tiempo

    FROM entregas
    GROUP BY
        anio_mes,
        segmento_cliente
)

SELECT
    anio_mes,
    segmento_cliente,

    CAST(
        ROUND(toneladas_entregadas, 3)
        AS DECIMAL(18, 3)
    ) AS toneladas_entregadas,

    CAST(
        ROUND(toneladas_a_tiempo, 3)
        AS DECIMAL(18, 3)
    ) AS toneladas_a_tiempo,

    CAST(
        ROUND(
            100.0 * toneladas_a_tiempo /
            NULLIF(toneladas_entregadas, 0),
            2
        )
        AS DECIMAL(18, 2)
    ) AS pct_a_tiempo

FROM metricas
