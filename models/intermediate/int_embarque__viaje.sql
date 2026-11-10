WITH viajes AS (
    SELECT
        id_viaje,
        cla_planta,
        estatus,
        costo_flete,

        COALESCE(
            NULLIF(fecha_real_embarque, TIMESTAMP '1900-01-01 00:00:00'),
            NULLIF(fecha_embarque_final, TIMESTAMP '1900-01-01 00:00:00')
        ) AS fecha_embarque

    FROM {{ ref('int_viaje__vigente') }}

    WHERE estatus IN ('TRA', 'ENT')
),

viajes_con_planta AS (
    SELECT
        v.id_viaje,
        v.cla_planta,
        p.nom_planta,
        v.estatus,
        v.fecha_embarque,
        v.costo_flete

    FROM viajes AS v

    LEFT JOIN {{ ref('stg_opc__planta') }} AS p
        ON v.cla_planta = p.cla_planta
)

SELECT *
FROM viajes_con_planta
WHERE fecha_embarque IS NOT NULL