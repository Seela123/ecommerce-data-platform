SELECT
    category,
    SUM(quantity) AS total_quantity_sold,
    SUM(item_total) AS gross_revenue,
    SUM(discounted_total) AS discounted_revenue,
    ROUND(AVG(discount_percentage),2) AS average_discount_percentage,
    COUNT(product_id) AS number_of_product,
    COUNT(line_number) AS number_of_cart_lines
FROM {{ref('fct_sales')}}
GROUP BY category