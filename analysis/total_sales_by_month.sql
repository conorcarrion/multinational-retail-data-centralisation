SELECT d.month, SUM(p.product_price * o.product_quantity)
FROM orders_table o
INNER JOIN dim_date_times d
ON d.date_uuid = o.date_uuid
INNER JOIN dim_products_table p
ON p.product_code = o.product_code
GROUP BY d.month