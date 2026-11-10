SELECT *
FROM {{ ref('cumplimiento_entrega') }}
WHERE pct_a_tiempo < 0
   OR pct_a_tiempo > 100
   OR pct_a_tiempo IS NULL
   OR toneladas_a_tiempo < 0
   OR toneladas_a_tiempo > toneladas_entregadas
   OR toneladas_entregadas <= 0