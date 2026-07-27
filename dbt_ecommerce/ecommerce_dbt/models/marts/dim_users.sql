SELECT
    user_id,
    first_name,
    full_name,
    age,
    gender,
    email,
    phone,
    username,
    birth_date,
    address_city,
    address_state,
    address_country,
    company_name,
    ingested_at
FROM {{ref('stg_users')}}