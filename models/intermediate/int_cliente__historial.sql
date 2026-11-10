WITH registros_unicos AS (
    SELECT DISTINCT *
    FROM {{ ref('stg_vta__cliente') }}
)

SELECT
    cla_cliente,
    nom_cliente,
    segmento,
    cla_estado,
    cdc_lsn,
    cdc_updated_at,
    cdc_deleted_at,
    airbyte_extracted_at
FROM registros_unicos
WHERE cla_cliente IS NOT NULL
  AND cdc_deleted_at IS NULL
  AND cdc_updated_at IS NOT NULL