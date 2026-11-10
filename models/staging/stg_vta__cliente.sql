
SELECT
    TRY_CAST(NULLIF(TRIM("ClaCliente"), '') AS INTEGER)
        AS cla_cliente,

    NULLIF(TRIM("NomCliente"), '')
        AS nom_cliente,

    UPPER(NULLIF(TRIM("Segmento"), ''))
        AS segmento,

    TRY_CAST(NULLIF(TRIM("ClaEstado"), '') AS INTEGER)
        AS cla_estado,

    "_ab_cdc_lsn" AS cdc_lsn,

    TRY_CAST(NULLIF(TRIM("_ab_cdc_updated_at"), '') AS TIMESTAMP)
        AS cdc_updated_at,

    TRY_CAST(NULLIF(TRIM("_ab_cdc_deleted_at"), '') AS TIMESTAMP)
        AS cdc_deleted_at,

    TRY_CAST(NULLIF(TRIM("_airbyte_extracted_at"), '') AS TIMESTAMP)
        AS airbyte_extracted_at

FROM {{ source('vta', 'vta_cliente') }}
