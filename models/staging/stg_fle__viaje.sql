
SELECT
    TRY_CAST(NULLIF(TRIM("IdViaje"), '') AS INTEGER) AS id_viaje,

    TRY_CAST(NULLIF(TRIM("ClaPlanta"), '') AS INTEGER) AS cla_planta,

    TRY_CAST(NULLIF(TRIM("FechaCompromiso"), '') AS TIMESTAMP)
        AS fecha_compromiso,

    TRY_CAST(NULLIF(TRIM("FechaRealEmbarque"), '') AS TIMESTAMP)
        AS fecha_real_embarque,

    TRY_CAST(NULLIF(TRIM("FechaEmbarqueFinal"), '') AS TIMESTAMP)
        AS fecha_embarque_final,

    UPPER(NULLIF(TRIM("Estatus"), '')) AS estatus,

    TRY_CAST(NULLIF(TRIM("CostoFlete"), '') AS DECIMAL(18, 2))
        AS costo_flete,

    "_ab_cdc_lsn" AS cdc_lsn,

    TRY_CAST(NULLIF(TRIM("_ab_cdc_updated_at"), '') AS TIMESTAMP)
        AS cdc_updated_at,

    TRY_CAST(NULLIF(TRIM("_ab_cdc_deleted_at"), '') AS TIMESTAMP)
        AS cdc_deleted_at,

    TRY_CAST(NULLIF(TRIM("_airbyte_extracted_at"), '') AS TIMESTAMP)
        AS airbyte_extracted_at

FROM {{ source('fle', 'fle_viaje') }}
