
SELECT
    TRY_CAST(NULLIF(TRIM("ClaPlanta"), '') AS INTEGER)
        AS cla_planta,

    NULLIF(TRIM("NomPlanta"), '')
        AS nom_planta,

    TRY_CAST(NULLIF(TRIM("ClaPais"), '') AS INTEGER)
        AS cla_pais,

    "_ab_cdc_lsn" AS cdc_lsn,

    TRY_CAST(NULLIF(TRIM("_ab_cdc_updated_at"), '') AS TIMESTAMP)
        AS cdc_updated_at,

    TRY_CAST(NULLIF(TRIM("_ab_cdc_deleted_at"), '') AS TIMESTAMP)
        AS cdc_deleted_at,

    TRY_CAST(NULLIF(TRIM("_airbyte_extracted_at"), '') AS TIMESTAMP)
        AS airbyte_extracted_at

FROM {{ source('opc', 'opc_planta') }}
