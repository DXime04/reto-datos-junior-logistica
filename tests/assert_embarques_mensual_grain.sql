SELECT
    anio_mes,
    cla_planta,
    COUNT(*) AS cantidad
FROM {{ ref('embarques_mensual') }}
GROUP BY anio_mes, cla_planta
HAVING COUNT(*) > 1