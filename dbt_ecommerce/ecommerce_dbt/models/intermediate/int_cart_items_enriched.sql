SELECT
    ci.cart_id,
    ci.line_number,
    u.user_id,
    ci.product_id,
    ci.title AS product_title,
    p.brand,
    ci.price,
    ci.quantity,
    ci.total AS item_total,
    ci.discount_percentage,
    ci.discounted_total,
    u.address_city AS user_city,
    p.category,
    u.address_city,
    u.address_country,
    ci.ingested_at
FROM {{ref('stg_cart_items')}} ci
LEFT JOIN {{ref('stg_products')}} p
ON ci.product_id = p.product_id
LEFT JOIN {{ref('stg_carts') }} c
ON ci.cart_id = c.cart_id
LEFT JOIN {{ref('stg_users')}} u
ON ci.line_number = u.user_id