SELECT
    product_id,
    product_title,
    category,
    brand,
    price,
    sku,
    rating,
    current_stock,
    discounted_total_sold AS total_quantity_sold,
    gross_revenue,
    discounted_revenue,
    average_discounted_percentage
FROM {{ref('int_product_sales_summary')}}