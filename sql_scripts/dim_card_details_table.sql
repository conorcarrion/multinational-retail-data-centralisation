ALTER TABLE dim_card_details
    DROP COLUMN index,
    ALTER COLUMN expiry_date TYPE CHAR(5),
	ALTER COLUMN card_number TYPE VARCHAR(20),
	ALTER COLUMN date_payment_confirmed TYPE DATE USING date_payment_confirmed::date;