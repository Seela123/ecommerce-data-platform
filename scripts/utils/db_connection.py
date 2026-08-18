import os
import psycopg2

def get_db_connect():
    if os.getenv("AIRFLOW_HOME"):
        host = "host.docker.internal"
        port = "5433"
    else:
        # 2. Fallback to your local machine values if running standalone
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5433")

    return psycopg2.connect(
        host=host,
        port=port,
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
