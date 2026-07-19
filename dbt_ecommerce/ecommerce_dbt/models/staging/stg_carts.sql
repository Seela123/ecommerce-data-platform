SELECT
    cart_id,
    user_id,
    total,
    discounted_total,
    total_products,
    total_quantity,
    raw_json,
    ingested_at
FROM {{ source ('raw', 'raw_carts') }}