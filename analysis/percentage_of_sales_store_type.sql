SELECT
  s.store_type,
  SUM(p.product_price * o.product_quantity) AS total_sales,
  SUM(p.product_price * o.product_quantity) / SUM(SUM(p.product_price * o.product_quantity)) OVER () * 100 AS "percentage_total(%)"
FROM orders_table o
INNER JOIN dim_date_times d ON d.date_uuid = o.date_uuid
INNER JOIN dim_products_table p ON p.product_code = o.product_code
INNER JOIN dim_store_details s ON s.store_code = o.store_code
GROUP BY s.store_type