SELECT
    product_id,
    product_title,
    description,
    category,
    brand,
    sku,
    price,
    discount_percentage,
    rating,
    stock,
    weight,
    ingested_at
FROM {{ref('stg_products')}}