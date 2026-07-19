select
    product_id,
    title AS product_title,
    description,
    category,
    price,
    discount_percentage,
    rating,
    stock,
    brand,
    sku,
    weight,
    raw_json,
    ingested_at
from {{ source('raw', 'raw_products') }}
