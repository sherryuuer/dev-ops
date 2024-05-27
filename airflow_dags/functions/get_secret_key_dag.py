from airflow import DAG
from airflow.operators.python import PythonOperator
from temp.get_secret_key import _get_connection_info, _connect_ftp_server
# from airflow.providers.ftp.sensors.ftp import FTPSSensor
from airflow.providers.ftp.sensors.ftp import FTPSensor
from datetime import datetime


default_args = {
    'owner': 'airflow',
    'catchup': False,
}

with DAG(
    'check_ftp_connection',
    default_args=default_args,
    start_date=datetime(2022, 9, 26),
    schedule_interval=None  # "00 12 * * *"
) as dag:

    # task1 = PythonOperator(
    #     task_id='task1',
    #     python_callable=_get_connection_info
    # )

    task2 = PythonOperator(
        task_id='task2',
        python_callable=_connect_ftp_server
    )

    # FTPサーバーのデータファイル有無を確認
    task3 = FTPSensor(
        task_id=f'check_ftp_task',
        path=f"test.txt",
        ftp_conn_id='gbase-access-key',
        mode='reschedule',
        soft_fail=False,
        poke_interval=300,
        timeout=3600,
    )

    