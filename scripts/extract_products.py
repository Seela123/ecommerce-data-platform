from datetime import datetime, timezone
import os
import json
from dotenv import load_dotenv
import requests
from utils.db_connection import get_db_connect
from utils.ingestion_logger import write_ingestion_log


load_dotenv()

BASE_DIR = r"C:\Users\Selman\Desktop\ecommerce-data-platform"
STORAGE_DIR = os.path.join(BASE_DIR, "data", "raw")
FILE_PATH = os.path.join(STORAGE_DIR, "products.json")

os.makedirs(STORAGE_DIR, exist_ok=True)

connection = None
started_at = datetime.now(timezone.utc)


try:
    connection = get_db_connect()
    cursor = connection.cursor()

    create_table = """
    CREATE TABLE IF NOT EXISTS raw.raw_products (
        product_id INT PRIMARY KEY,
        title VARCHAR(255),
        description TEXT,
        category VARCHAR(255),
        price NUMERIC(10,2),
        discount_percentage NUMERIC(5,2),
        rating NUMERIC(3,2),
        stock INT,
        brand VARCHAR(255),
        sku VARCHAR(255),
        weight INT,
        raw_json TEXT NOT NULL,
        ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """

    cursor.execute(create_table)
    connection.commit()
    cursor.close()

    print("Table raw_products is ready!")

except Exception as e:
    print(f"Failed to create table: {e}")
    connection.rollback()


url = "https://dummyjson.com/products"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

limit = 100
skip = 0
all_products = []

while True:
    try:
        response = requests.get(
            url,
            headers=headers,
            params={
                "limit": limit,
                "skip": skip
            },
            timeout=30
        )

        response.raise_for_status()
        payload = response.json()

        products = payload.get("products", [])
        total = payload.get("total", 0)

        if not products:
            print("No more products found.")
            break

        print(f"Fetched {len(products)} products. Skip: {skip}")

        all_products.extend(products)

        cursor = connection.cursor()

        insert_query = """
        INSERT INTO raw.raw_products (
            product_id,
            title,
            description,
            category,
            price,
            discount_percentage,
            rating,
            stock,
            brand,
            sku,
            weight,
            raw_json
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            category = EXCLUDED.category,
            price = EXCLUDED.price,
            discount_percentage = EXCLUDED.discount_percentage,
            rating = EXCLUDED.rating,
            stock = EXCLUDED.stock,
            brand = EXCLUDED.brand,
            sku = EXCLUDED.sku,
            weight = EXCLUDED.weight,
            raw_json = EXCLUDED.raw_json;
        """

        for prod in products:
            clean_table = {
                "product_id": prod.get("id"),
                "title": prod.get("title"),
                "description": prod.get("description"),
                "category": prod.get("category"),
                "price": prod.get("price"),
                "discount_percentage": prod.get("discountPercentage"),
                "rating": prod.get("rating"),
                "stock": prod.get("stock"),
                "brand": prod.get("brand"),
                "sku": prod.get("sku"),
                "weight": prod.get("weight"),
                "raw_json": json.dumps(prod, ensure_ascii=False)
            }

            cursor.execute(insert_query, (
                clean_table["product_id"],
                clean_table["title"],
                clean_table["description"],
                clean_table["category"],
                clean_table["price"],
                clean_table["discount_percentage"],
                clean_table["rating"],
                clean_table["stock"],
                clean_table["brand"],
                clean_table["sku"],
                clean_table["weight"],
                clean_table["raw_json"]
            ))

        connection.commit()
        cursor.close()

        print(f"Inserted {len(products)} products into raw_products")

        skip += limit

        if skip >= total:
            print("All products successfully processed!")




    except Exception as e:
        print(f"Error during extraction/loading: {e}")
        connection.rollback()

        write_ingestion_log(
            source_name="dummyjson_products_api",
            target_table="raw.raw_products",
            status="FAILED",
            rows_loaded=len(all_products),
            started_at=started_at
        )



with open(FILE_PATH, "w", encoding="utf-8") as f:
    json.dump(all_products, f, indent=4, ensure_ascii=False)

print(f"Saved all raw products to: {FILE_PATH}")

write_ingestion_log(
        source_name="dummyjson_products_api",
        target_table="raw.raw_products",
        status="SUCCESS",
        rows_loaded=len(all_products),
        started_at=started_at
        )


if connection:
    connection.close()
    print("Database connection closed.")