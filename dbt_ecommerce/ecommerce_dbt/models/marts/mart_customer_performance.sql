SELECT
    user_id,
    full_name,
    email,
    address_city,
    address_country,
    number_of_carts,
    total_quantity,
    gross_revenue,
    discounted_revenu,
    average_cart_value
FROM {{ref('int_user_cart_summary')}}