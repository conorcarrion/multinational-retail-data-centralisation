SELECT
  SUM(p.product_price * o.product_quantity) AS total_sales,
  d.year,
  d.month
FROM orders_table o
INNER JOIN dim_date_times d ON d.date_uuid = o.date_uuid
INNER JOIN dim_products_table p ON p.product_code = o.product_code
INNER JOIN dim_store_details s ON s.store_code = o.store_code
GROUP BY d.year, d.month
ORDER BY total_sales DESC