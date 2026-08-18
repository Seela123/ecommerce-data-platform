import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime
from airflow.operators.empty import EmptyOperator


with DAG(
    dag_id="ecommerce_daily_pipeline",
    start_date=datetime(2026, 8, 10),
    schedule='0 0 1 * *',
    catchup=False
) as dag:

    start_task = EmptyOperator(
        task_id='start',
    )

    extract_products= BashOperator(
        task_id="run_products_pipeline",
        bash_command="python3 /usr/local/airflow/scripts/extract_products.py",
        doc_md="### This will run scripts in in file scripts/extract_products and will upload"

)

    extract_carts= BashOperator(
        task_id="run_carts_pipeline",
        bash_command="python3 /usr/local/airflow/scripts/extract_carts.py",
        doc_md="### this will run scripts from scripts/extract_carts.py"
    )

    extract_users= BashOperator(
        task_id="extract_users",
        bash_command="python3 /usr/local/airflow/scripts/extract_users.py",
        doc_md="### this will run scripts from scripts/extract_users.py "
        )

    load_users = BashOperator(
        task_id="load_users",
        bash_command="python3 /usr/local/airflow/scripts/load_users.py",
        doc_md="### this will run scripts from scripts/loud_users.py "
    )

    dbt_run = BashOperator(
        task_id="run_dbt",
        bash_command="cd /usr/local/airflow/dbt_ecommerce/ecommerce_dbt && dbt run --profiles-dir ..",

    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /usr/local/airflow/dbt_ecommerce/ecommerce_dbt && dbt test --profiles-dir ..",
        doc_md="this will run dbt_ecoomerce/ecommerce_dbt dbt test and will do all testes from dbt"
    )

    end_task = EmptyOperator(
        task_id='end',
    )

    start_task >> extract_products >> extract_carts >> extract_users >> load_users >> dbt_run >> dbt_test >> end_task