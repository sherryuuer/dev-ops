import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from pubsub_functions import publish_message


PROJECT = os.getenv('project')

default_args = {
    'owner': 'airflow',
    'catchup': False,
}

with DAG(
    'publish_test_dag',
    default_args=default_args,
    start_date=datetime(2022, 9, 26),
    schedule_interval=None  # "00 12 * * *"
) as dag:

    publish_message = PythonOperator(
        task_id='publish_task',
        python_callable=publish_message,
        op_args = {
            'project_id' : PROJECT
        },
    )
