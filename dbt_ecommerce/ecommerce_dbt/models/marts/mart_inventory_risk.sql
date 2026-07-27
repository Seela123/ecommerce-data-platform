SELECT
    product_id,
    product_title,
    category,
    brand,
    current_stock,
    total_quantity_sold,
    gross_revenue,
    rating,
CASE
	WHEN current_stock < total_quantity_sold THEN 'high_risk'
	WHEN current_stock < AVG(total_quantity_sold) OVER() THEN 'medium_risk'
	ELSE 'low_risk'
END AS inventory_risk_level
FROM {{ref('mart_product_performance')}}