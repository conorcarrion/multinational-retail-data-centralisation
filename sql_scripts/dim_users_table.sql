ALTER TABLE dim_users
    DROP COLUMN level_0, 
    DROP COLUMN index,
    ALTER COLUMN first_name TYPE VARCHAR(255),
    ALTER COLUMN last_name TYPE VARCHAR(255),
    ALTER COLUMN date_of_birth TYPE DATE USING date_of_birth::date,
    ALTER COLUMN country_code TYPE CHAR(2);
    ALTER COLUMN user_uuid TYPE UUID USING user_uuid::uuid,
    ALTER COLUMN join_date TYPE DATE USING join_date::date;