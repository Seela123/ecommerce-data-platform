SELECT
    u.user_id,
    u.full_name,
	u.email,
    u.address_city,
    u.address_country,
    COUNT(c.cart_id) as number_of_carts,
	c.total_quantity,
    SUM(c.total) AS gross_revenue,
    SUM(c.discounted_total) AS discounted_revenu,
    ROUND(SUM(c.discounted_total) / NULLIF(COUNT(c.cart_id), 0), 2) AS average_cart_value,
	u.ingested_at
FROM {{ref ('stg_users')}} u
LEFT JOIN {{ref ('stg_carts')}} c
    ON u.user_id = c.user_id
GROUP BY
    u.user_id,
    u.full_name,
    u.address_city,
    u.address_country,
	u.ingested_at,
	u.email,
	c.total_quantity