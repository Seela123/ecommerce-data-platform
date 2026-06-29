import json
import os
from pathlib import Path
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
USERS_FILE_PATH = PROJECT_ROOT / "data" / "raw" / "users.json"

load_dotenv(PROJECT_ROOT / ".env")


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw.raw_users (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    maiden_name VARCHAR(255),
    age INT,
    gender VARCHAR(50),
    email TEXT,
    phone TEXT,
    username VARCHAR(255),
    birth_date DATE,
    image_url TEXT,
    address_line TEXT,
    address_city VARCHAR(255),
    address_state VARCHAR(255),
    address_country VARCHAR(255),
    company_name TEXT,
    raw_json JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL
);
"""


UPSERT_USER_SQL = """
INSERT INTO raw.raw_users (
    user_id,
    first_name,
    last_name,
    maiden_name,
    age,
    gender,
    email,
    phone,
    username,
    birth_date,
    image_url,
    address_line,
    address_city,
    address_state,
    address_country,
    company_name,
    raw_json,
    ingested_at
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (user_id)
DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    maiden_name = EXCLUDED.maiden_name,
    age = EXCLUDED.age,
    gender = EXCLUDED.gender,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    username = EXCLUDED.username,
    birth_date = EXCLUDED.birth_date,
    image_url = EXCLUDED.image_url,
    address_line = EXCLUDED.address_line,
    address_city = EXCLUDED.address_city,
    address_state = EXCLUDED.address_state,
    address_country = EXCLUDED.address_country,
    company_name = EXCLUDED.company_name,
    raw_json = EXCLUDED.raw_json,
    ingested_at = EXCLUDED.ingested_at;
"""


def read_users() -> list[dict]:
    with open(USERS_FILE_PATH, "r", encoding="utf-8") as file:
        payload = json.load(file)

    users = payload.get("users", [])

    if not users:
        raise ValueError("No users found in users.json")

    if payload.get("total_users") != len(users):
        raise ValueError(
            f"User count mismatch. "
            f"Metadata: {payload.get('total_users')}, actual: {len(users)}"
        )

    return users


def create_raw_users_table(connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)

    connection.commit()
    print("Table raw.raw_users created or already exists")


def remove_sensitive_fields(user: dict) -> dict:
    clean_user = user.copy()

    # Keep the original JSON structure but do not store passwords in PostgreSQL.
    clean_user.pop("password", None)

    return clean_user


def load_users(connection, users: list[dict]) -> None:
    ingested_at = datetime.now(timezone.utc)

    with connection.cursor() as cursor:
        for user in users:
            address = user.get("address") or {}
            company = user.get("company") or {}

            cursor.execute(
                UPSERT_USER_SQL,
                (
                    user.get("id"),
                    user.get("firstName"),
                    user.get("lastName"),
                    user.get("maidenName"),
                    user.get("age"),
                    user.get("gender"),
                    user.get("email"),
                    user.get("phone"),
                    user.get("username"),
                    user.get("birthDate"),
                    user.get("image"),
                    address.get("address"),
                    address.get("city"),
                    address.get("state"),
                    address.get("country"),
                    company.get("name"),
                    Json(remove_sensitive_fields(user)),
                    ingested_at
                )
            )

    connection.commit()
    print(f"Inserted/updated {len(users)} users into raw.raw_users")


def main():
    connection = None

    try:
        users = read_users()

        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )

        print("Successfully connected to database")

        create_raw_users_table(connection)
        load_users(connection, users)

    except Exception as error:
        if connection:
            connection.rollback()

        print(f"Users load failed: {error}")
        raise

    finally:
        if connection:
            connection.close()
            print("Database connection closed")


if __name__ == "__main__":
    main()