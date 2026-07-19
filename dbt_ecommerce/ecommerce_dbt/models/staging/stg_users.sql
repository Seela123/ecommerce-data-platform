SELECT
    user_id,
    first_name,
    CONCAT(first_name, ' ', last_name) AS full_name,
    maiden_name,
    age,
    gender,
    email,
    phone,
    username,
    birth_date,
    image_url,
    address_city,
    address_state,
    address_country,
    company_name,
    raw_json
    ingested_at
FROM {{ source('raw' , 'raw_users') }}