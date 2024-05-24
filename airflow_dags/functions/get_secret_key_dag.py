from airflow import DAG
from airflow.operators.python import PythonOperator
from temp.get_secret_key import _get_connection_info
from datetime import datetime


default_args = {
    'owner': 'airflow',
    'catchup': False,
}

with DAG(
    'check_secret_manager_data_type',
    default_args=default_args,
    start_date=datetime(2022, 9, 26),
    schedule_interval=None  # "00 12 * * *"
) as dag:

    task = PythonOperator(
        task_id='task1',
        python_callable=_get_connection_info
    )

    task