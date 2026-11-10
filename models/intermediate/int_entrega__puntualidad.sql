SELECT
    v.id_viaje,
    v.fecha_compromiso,
    e.fecha_entrega,

    CASE
        WHEN e.id_viaje IS NOT NULL
         AND e.fecha_entrega <= v.fecha_compromiso
        THEN TRUE
        WHEN e.id_viaje IS NOT NULL
        THEN FALSE
        ELSE NULL
    END AS entrega_a_tiempo

FROM {{ ref('int_viaje__vigente') }} AS v

LEFT JOIN {{ ref('int_entrega__vigente') }} AS e
    ON v.id_viaje = e.id_viaje

WHERE v.estatus IN ('TRA', 'ENT')