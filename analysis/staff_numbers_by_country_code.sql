SELECT
  SUM(staff_numbers) AS total_staff_numbers,
  CASE WHEN country_code IS NULL THEN 'Web' ELSE country_code END AS country_code
FROM dim_store_details
GROUP BY country_code
ORDER BY total_staff_numbers DESC