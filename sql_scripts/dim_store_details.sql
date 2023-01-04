ALTER TABLE dim_store_details
    DROP COLUMN index,
    ALTER COLUMN longitude TYPE DECIMAL(9,6) USING longitude::numeric(9,6),
    ALTER COLUMN locality TYPE VARCHAR(255),
    ALTER COLUMN store_code TYPE VARCHAR(12),
    ALTER COLUMN staff_numbers TYPE SMALLINT,
    ALTER COLUMN opening_date TYPE DATE USING opening_date::date,
    ALTER COLUMN store_type TYPE VARCHAR(255),
    ALTER COLUMN store_type DROP NOT NULL,
    ALTER COLUMN latitude TYPE DECIMAL(9,6) USING latitude::numeric(9,6),
    ALTER COLUMN country_code TYPE CHAR(2),
    ALTER COLUMN continent TYPE VARCHAR(255);