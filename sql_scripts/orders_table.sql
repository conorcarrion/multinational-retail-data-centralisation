ALTER TABLE orders_table
    DROP COLUMN level_0, 
    DROP COLUMN index,
    ALTER COLUMN date_uuid TYPE uuid
    USING date_uuid::uuid,
    ALTER COLUMN user_uuid TYPE uuid
    USING user_uuid::uuid,
    ALTER COLUMN card_number TYPE VARCHAR,
    ALTER COLUMN store_code TYPE VARCHAR,
    ALTER COLUMN product_code TYPE VARCHAR,
    ALTER COLUMN product_quantity TYPE SMALLINT;