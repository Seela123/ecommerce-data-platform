from datetime import datetime, timezone
from .db_connection import get_db_connect


def write_ingestion_log(
    source_name,
    target_table,
    status,
    rows_loaded,
    started_at,
    error_message=None
):
    connection = None

    try:
        connection = get_db_connect()
        cursor = connection.cursor()

        cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw.raw_api_ingestion_log (
                log_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                source_name TEXT NOT NULL,
                target_table TEXT NOT NULL,
                status VARCHAR(10) NOT NULL CHECK (status IN ('SUCCESS', 'FAILED')),
                rows_loaded INT NOT NULL DEFAULT 0,
                started_at TIMESTAMP WITH TIME ZONE NOT NULL,
                finished_at TIMESTAMP WITH TIME ZONE NOT NULL,
                error_message TEXT
            );
        """)

        insert_query = """
            INSERT INTO raw.raw_api_ingestion_log (
                source_name,
                target_table,
                status,
                rows_loaded,
                started_at,
                finished_at,
                error_message
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """

        cursor.execute(
            insert_query,
            (
                source_name,
                target_table,
                status,
                rows_loaded,
                started_at,
                datetime.now(timezone.utc),
                error_message
            )
        )

        connection.commit()
        cursor.close()

    except Exception as e:
        print(f"Failed to write ingestion log: {e}")

    finally:
        if connection:
            connection.close()