SELECT
	p.product_id,
	p.product_title,
	p.category,
	p.brand,
	p.sku,
	p.rating,
	p.stock AS current_stock,
	SUM(ci.quantity) AS discounted_total_sold,
	SUM(ci.total) AS gross_revenue,
	SUM(ci.discounted_total) AS discounted_revenue,
	ROUND(AVG(ci.discount_percentage),2) AS average_discounted_percentage,
	ci.ingested_at::DATE AS ingested_at
FROM {{ref ('stg_products')}} p
LEFT JOIN {{ref('stg_cart_items')}} ci
ON p.product_id = ci.product_id
GROUP BY
	p.product_id,
	p.product_title,
	p.category,
	p.brand,
	p.sku,
	p.rating,
	p.stock,
	ci.ingested_at::DATE