SELECT
    STRFTIME(fecha_embarque, '%Y-%m') AS anio_mes,
    cla_planta,
    nom_planta,

    COUNT(DISTINCT id_viaje) AS num_viajes,

    CAST(
        ROUND(SUM(toneladas_embarcadas), 3)
        AS DECIMAL(18, 3)
    ) AS toneladas_embarcadas,

    CAST(
        ROUND(SUM(costo_flete), 2)
        AS DECIMAL(18, 2)
    ) AS costo_flete_mxn,

    CAST(
        ROUND(
            SUM(costo_flete) /
            NULLIF(SUM(toneladas_embarcadas), 0),
            2
        )
        AS DECIMAL(18, 2)
    ) AS costo_flete_por_ton

FROM {{ ref('int_embarque__viaje_metricas') }}

GROUP BY
    STRFTIME(fecha_embarque, '%Y-%m'),
    cla_planta,
    nom_planta