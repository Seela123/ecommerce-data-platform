SELECT
    cart_id,
    line_number,
    user_id,
    product_id,
    product_title,
    category,
    brand,
    price,
    quantity,
    item_total,
    discount_percentage,
    discounted_total,
    address_city AS user_city,
    address_country AS user_country,
    ingested_at
FROM {{ref('int_cart_items_enriched')}}