WITH registros_unicos AS (
    SELECT DISTINCT *
    FROM {{ ref('stg_fle__entrega') }}
),

versiones_ordenadas AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY id_viaje
            ORDER BY
                TRY_CAST(cdc_lsn AS BIGINT) DESC,
                cdc_updated_at DESC,
                airbyte_extracted_at DESC
        ) AS numero_version
    FROM registros_unicos
    WHERE id_viaje IS NOT NULL
)

SELECT
    id_viaje,
    fecha_entrega,
    cdc_lsn,
    cdc_updated_at,
    cdc_deleted_at,
    airbyte_extracted_at
FROM versiones_ordenadas
WHERE numero_version = 1
  AND cdc_deleted_at IS NULL