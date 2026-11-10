SELECT
    anio_mes,
    segmento_cliente,
    COUNT(*) AS cantidad
FROM {{ ref('cumplimiento_entrega') }}
GROUP BY anio_mes, segmento_cliente
HAVING COUNT(*) > 1