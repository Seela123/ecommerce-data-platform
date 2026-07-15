import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connect():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )

        print("Successfully connected to database")
        return connection

    except Exception as e:
        print(f"Connection error: {e}")
        raise