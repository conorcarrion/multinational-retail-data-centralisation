ALTER TABLE dim_products_table
    DROP COLUMN index,
    ADD COLUMN weight_class VARCHAR(255);

UPDATE dim_products_table
SET weight_class =
    CASE
        WHEN product_weight BETWEEN 0 AND 3 THEN 'Light'
        WHEN product_weight BETWEEN 3 AND 41 THEN 'Mid_Sized'
        WHEN product_weight BETWEEN 41 AND 141 THEN 'Heavy'
        WHEN product_weight BETWEEN 141 AND 200 THEN 'Truck_Required'
        ELSE 'Other'
    END;

ALTER TABLE dim_products_table
    RENAME COLUMN removed TO still_available;

ALTER TABLE dim_products_table
	ALTER COLUMN product_price TYPE FLOAT,
	ALTER COLUMN "EAN" TYPE VARCHAR(18),
	ALTER COLUMN product_code TYPE VARCHAR(12),
	ALTER COLUMN date_added TYPE DATE USING date_added::date,
	ALTER COLUMN uuid TYPE UUID USING uuid::uuid,
	ALTER COLUMN weight_class TYPE VARCHAR(15)
    ALTER COLUMN unit_weight TYPE SMALLINT;
    ALTER COLUMN units_in_product TYPE SMALLINT;

UPDATE dim_products_table
SET still_available =
    CASE still_available
        WHEN 'Available' THEN TRUE
        WHEN 'Removed' THEN FALSE
        ELSE NULL
    END;

ALTER TABLE dim_products_table
    ALTER COLUMN still_available TYPE bool;