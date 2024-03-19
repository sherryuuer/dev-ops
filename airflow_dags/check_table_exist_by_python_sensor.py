from datetime import datetime, timedelta, timezone
from airflow.sensors.python import PythonSensor
from airflow import DAG
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


def check_ga_table_exists(exec_date):
    client = bigquery.Client()

    table_id = f"project.dataset.tabel_name_{exec_date}"

    try:
        client.get_table(table_id)
        print(f"Table {table_id} already exists.")
        return True
    except NotFound:
        print(f"Table {table_id} is not found.")
        return False


exec_date = (datetime.now(timezone(timedelta(hours=9), 'JST')) -
             timedelta(days=2)).strftime('%Y%m%d')


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 29),
    'catchup': False,
    'execution_timeout': timedelta(seconds=3600),
    'retries': 3,
    'retry_delay': timedelta(minutes=10),
    'soft_fail': False,
}

with DAG(
    'check_table_exist_by_python_sensor',
    default_args=default_args,
    template_searchpath=['/home/airflow/gcs/dags/DI'],
    # ga_modifyタスクで実行するSQLのテーブル名を動的に設定するためmacroを利用している
    user_defined_macros={'exec_date': exec_date},
    schedule_interval='30 7 * * *'
) as dag:

    # GAテーブル存在するかをセンサーする
    sensor_task = PythonSensor(
        task_id='sensor_task',
        python_callable=check_ga_table_exists,
        op_kwargs={"exec_date": exec_date},
        mode='reschedule',
        poke_interval=300,
        timeout=3600,
        depends_on_past=True
    )

    sensor_task
