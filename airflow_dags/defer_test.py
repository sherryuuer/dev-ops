from datetime import timedelta, timezone, datetime

from airflow import DAG
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.operators.python import PythonOperator


def run_query():
    from google.cloud import bigquery

    client = bigquery.Client()
    query = """
        select 1
    """
    print(f'Query start!')
    client.query(query).result()
    print(f'Query completed!')


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2020, 11, 29),
    'catchup': False,
    'execution_timeout': timedelta(seconds=3600),
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'soft_fail': False
}

with DAG(
    'defer_test',
    default_args=default_args,
    schedule_interval=None
) as dag:

    gcs_sensor = GCSObjectExistenceSensor(
        task_id='gcs_sensor_task',
        bucket='bandainamco-lake-bsp-dev__zdh_dev__samples',
        object='chaonan_wang/test.txt',
        deferrable=True,
        poke_interval=300,
        # timeout=60  # seconds
    )

    query_task = PythonOperator(
        task_id='query_task',
        python_callable=run_query
    )

    gcs_sensor >> query_task
