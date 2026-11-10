WITH toneladas_por_viaje AS (
    SELECT
        id_viaje,
        SUM(peso_kg) / 1000.0 AS toneladas_embarcadas
    FROM {{ ref('int_embarque__partida') }}
    GROUP BY id_viaje
)

SELECT
    v.id_viaje,
    v.cla_planta,
    v.nom_planta,
    v.fecha_embarque,
    v.costo_flete,
    COALESCE(t.toneladas_embarcadas, 0) AS toneladas_embarcadas

FROM {{ ref('int_embarque__viaje') }} AS v

LEFT JOIN toneladas_por_viaje AS t
    ON v.id_viaje = t.id_viaje