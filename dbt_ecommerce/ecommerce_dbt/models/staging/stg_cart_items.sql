SELECT
    cart_id,
    line_number,
    product_id,
    title,
    price,
    quantity,
    total,
    discount_percentage,
    discounted_total,
    thumbnail,
    ingested_at
FROM {{ source('raw', 'raw_cart_items') }}