import os
import json
from dotenv import load_dotenv
import requests
from datetime import datetime, timezone
from utils.db_connection import get_db_connect
from utils.ingestion_logger import write_ingestion_log

load_dotenv()

BASE_DIR = r"C:\Users\Selman\Desktop\ecommerce-data-platform"
STORAGE_DIR = os.path.join(BASE_DIR, "data", "staging")
FILE_PATH = os.path.join(STORAGE_DIR, "carts.json")
ITEMS_FILE_PATH = os.path.join(STORAGE_DIR, "cart_items.json")


os.makedirs(STORAGE_DIR, exist_ok=True)

connection = None

started_at = datetime.now(timezone.utc)

try:
    connection = get_db_connect()

    print("Successfully connected to database")

    cursor = connection.cursor()

    cursor.execute("CREATE SCHEMA IF NOT EXISTS staging;")

    create_table = """
    CREATE TABLE IF NOT EXISTS staging.raw_carts (
        cart_id INT PRIMARY KEY,
        user_id INT,
        total NUMERIC(12,2),
        discounted_total NUMERIC(12,2),
        total_products INT,
        total_quantity INT,
        raw_json TEXT NOT NULL,
        ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """

    cursor.execute(create_table)
    print("Table staging.raw_carts created or already exists")

    create_table_items = """ 
        CREATE TABLE IF NOT EXISTS staging.raw_cart_items (
    cart_id INT NOT NULL,
    line_number INT NOT NULL,
    product_id INT NOT NULL,
    title TEXT,
    price NUMERIC(12,2),
    quantity INT,
    total NUMERIC(12,2),
    discount_percentage NUMERIC(5,2),
    discounted_total NUMERIC(12,2),
    thumbnail TEXT,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cart_id, line_number)
);
    """

    cursor.execute(create_table_items)
    connection.commit()

    print("Table staging.raw_carts_items created or already exists")

    url = "https://dummyjson.com/carts"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    limit = 100
    skip = 0
    all_carts = []
    all_cart_items = []

    insert_query = """
    INSERT INTO staging.raw_carts (
        cart_id,
        user_id,
        total,
        discounted_total,
        total_products,
        total_quantity,
        raw_json,
        ingested_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (cart_id) DO UPDATE SET
        user_id = EXCLUDED.user_id,
        total = EXCLUDED.total,
        discounted_total = EXCLUDED.discounted_total,
        total_products = EXCLUDED.total_products,
        total_quantity = EXCLUDED.total_quantity,
        raw_json = EXCLUDED.raw_json,
        ingested_at = EXCLUDED.ingested_at;
    """

    insert_item_query = """
        INSERT INTO staging.raw_cart_items (
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
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (cart_id, line_number)
        DO UPDATE SET
            product_id = EXCLUDED.product_id,
            title = EXCLUDED.title,
            price = EXCLUDED.price,
            quantity = EXCLUDED.quantity,
            total = EXCLUDED.total,
            discount_percentage = EXCLUDED.discount_percentage,
            discounted_total = EXCLUDED.discounted_total,
            thumbnail = EXCLUDED.thumbnail,
            ingested_at = EXCLUDED.ingested_at;
    """


    while True:
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

        carts = payload.get("carts", [])
        total_available = payload.get("total", 0)

        if not carts:
            print("No more carts found.")
            break

        print(f"Fetched {len(carts)} carts. Skip: {skip}")

        all_carts.extend(carts)

        for cart in carts:
            clean_table = {
                "cart_id": cart.get("id"),
                "user_id": cart.get("userId"),
                "total": cart.get("total"),
                "discounted_total": cart.get("discountedTotal"),
                "total_products": cart.get("totalProducts"),
                "total_quantity": cart.get("totalQuantity"),
                "raw_json": json.dumps(cart, ensure_ascii=False),
                "ingested_at": datetime.now()
            }

            cursor.execute(insert_query, (
                clean_table["cart_id"],
                clean_table["user_id"],
                clean_table["total"],
                clean_table["discounted_total"],
                clean_table["total_products"],
                clean_table["total_quantity"],
                clean_table["raw_json"],
                clean_table["ingested_at"]
            ))

            for line_number, product in enumerate(cart.get("products", []), start=1):
                db_ingested_at = datetime.now()

                clean_item = {
                    "cart_id": cart.get("id"),
                    "line_number": line_number,
                    "product_id": product.get("id"),
                    "title": product.get("title"),
                    "price": product.get("price"),
                    "quantity": product.get("quantity"),
                    "total": product.get("total"),
                    "discount_percentage": product.get("discountPercentage"),
                    "discounted_total": product.get("discountedTotal"),
                    "thumbnail": product.get("thumbnail"),
                    "ingested_at": db_ingested_at.isoformat()  # string for JSON
                }

                cursor.execute(
                    insert_item_query,
                    (
                        clean_item["cart_id"],
                        clean_item["line_number"],
                        clean_item["product_id"],
                        clean_item["title"],
                        clean_item["price"],
                        clean_item["quantity"],
                        clean_item["total"],
                        clean_item["discount_percentage"],
                        clean_item["discounted_total"],
                        clean_item["thumbnail"],
                        db_ingested_at
                    )
                )

                all_cart_items.append(clean_item)

                connection.commit()

        skip += limit

        if skip >= total_available:
            print("All carts successfully processed!")
            break

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(all_carts, f, indent=4, ensure_ascii=False)

    with open(ITEMS_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(all_cart_items, f, indent=4, ensure_ascii=False)

    write_ingestion_log(
        source_name="dummyjson_carts_api",
        target_table="staging.raw_carts",
        status="SUCCESS",
        rows_loaded=len(all_carts),
        started_at=started_at
    )

    write_ingestion_log(
        source_name="dummyjson_carts_api",
        target_table="staging.raw_cart_items",
        status="SUCCESS",
        rows_loaded=len(all_cart_items),
        started_at=started_at
    )



    print(f"Saved all staging carts to: {FILE_PATH}")
    print(f"Inserted/updated {len(all_carts)} carts into staging.raw_carts")

    print(f"Saved all staging cart items to: {ITEMS_FILE_PATH}")
    print(f"Inserted/updated {len(all_cart_items)} carts into staging.raw_cart_items")

except Exception as e:
    print(f"Error: {e}")

    write_ingestion_log(
        source_name="dummyjson_carts_api",
        target_table="staging.raw_carts",
        status="FAILED",
        rows_loaded=len(all_carts),
        started_at=started_at
    )

    write_ingestion_log(
        source_name="dummyjson_carts_api",
        target_table="staging.raw_cart_items",
        status="FAILED",
        rows_loaded=len(all_cart_items),
        started_at=started_at
    )

    if connection:
        connection.rollback()

finally:
    if connection:
        connection.close()
        print("Database connection closed.")