WITH partidas AS (
    SELECT
        d.id_viaje,
        d.id_partida,
        d.cla_cliente,
        d.peso_kg,

        v.cla_planta,
        v.nom_planta,
        v.fecha_embarque

    FROM {{ ref('int_viaje_det__vigente') }} AS d

    INNER JOIN {{ ref('int_embarque__viaje') }} AS v
        ON d.id_viaje = v.id_viaje
),

partidas_con_segmento AS (
    SELECT
        p.*,
        c.segmento AS segmento_cliente,

        ROW_NUMBER() OVER (
            PARTITION BY p.id_viaje, p.id_partida
            ORDER BY
                c.cdc_updated_at DESC NULLS LAST,
                TRY_CAST(c.cdc_lsn AS BIGINT) DESC NULLS LAST
        ) AS numero_version_cliente

    FROM partidas AS p

    LEFT JOIN {{ ref('int_cliente__historial') }} AS c
        ON p.cla_cliente = c.cla_cliente
       AND c.cdc_updated_at <= p.fecha_embarque
),

partidas_clasificadas AS (
    SELECT
        id_viaje,
        id_partida,
        cla_cliente,
        peso_kg,
        cla_planta,
        nom_planta,
        fecha_embarque,

        CASE
            WHEN segmento_cliente IN (
                'DISTRIBUIDOR',
                'CONSTRUCTORA',
                'INDUSTRIAL'
            )
            THEN segmento_cliente
            ELSE 'NO_IDENTIFICADO'
        END AS segmento_cliente

    FROM partidas_con_segmento
    WHERE numero_version_cliente = 1
)

SELECT
    p.*,
    e.fecha_entrega,
    e.entrega_a_tiempo

FROM partidas_clasificadas AS p

LEFT JOIN {{ ref('int_entrega__puntualidad') }} AS e
    ON p.id_viaje = e.id_viaje