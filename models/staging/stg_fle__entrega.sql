
SELECT
    TRY_CAST(NULLIF(TRIM("IdViaje"), '') AS INTEGER)
        AS id_viaje,

    TRY_CAST(NULLIF(TRIM("FechaEntrega"), '') AS TIMESTAMP)
        AS fecha_entrega,

    "_ab_cdc_lsn" AS cdc_lsn,

    TRY_CAST(NULLIF(TRIM("_ab_cdc_updated_at"), '') AS TIMESTAMP)
        AS cdc_updated_at,

    TRY_CAST(NULLIF(TRIM("_ab_cdc_deleted_at"), '') AS TIMESTAMP)
        AS cdc_deleted_at,

    TRY_CAST(NULLIF(TRIM("_airbyte_extracted_at"), '') AS TIMESTAMP)
        AS airbyte_extracted_at

FROM {{ source('fle', 'fle_entrega') }}
