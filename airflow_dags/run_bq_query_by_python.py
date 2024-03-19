from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def run_query():
    from google.cloud import bigquery

    client = bigquery.Client()
    query = """
        select 1
    """
    print(f'Query start!')
    result = client.query(query).result()
    print(f'Query completed!')
    result = [row for row in result][0]

    return result


default_args = {
    'owner': 'airflow',
    'catchup': False,
}

with DAG(
    'run_bq_query_by_python',
    default_args=default_args,
    start_date=datetime(2022, 9, 26),
    schedule_interval=None  # "00 12 * * *"
) as dag:

    task_name = PythonOperator(
        task_id='task_name',
        python_callable=run_query
    )

    task_name
