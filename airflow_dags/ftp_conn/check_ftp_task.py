from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.ftp.sensors.ftp import FTPSSensor
# from airflow.providers.ftp.sensors.ftp import FTPSensor
from datetime import datetime


PROJECT_ID = ''
SECRET_ID = ''
VERSION = '1'

def _get_connection_info():

    from google.cloud import secretmanager
    import json

    client = secretmanager.SecretManagerServiceClient()
    path = client.secret_version_path(PROJECT_ID, SECRET_ID, VERSION)

    response = client.access_secret_version(name=path)
    secret_value = response.payload.data.decode('UTF-8')
    
    # try to get key
    secret_dict = json.loads(secret_value)
    # return list(secret_dict.keys())
    return secret_dict


def _connect_ftp_server():

    import ftplib
    connection_info = _get_connection_info()
    print(connection_info["host"])
    ftps = ftplib.FTP_TLS(
        host=connection_info["host"],
        user=connection_info["user"],
        passwd=connection_info["password"],
        timeout=60,
    )
    ftps.prot_p()
    # ftp = ftplib.FTP(
    #     host=connection_info["host"],
    #     user=connection_info["user"],
    #     passwd=connection_info["password"]
    # )
    # ftp.login()
    # ftp.retrlines('LIST')
    # ftp.quit()


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

    task1 = PythonOperator(
        task_id='ftplib_ftp_task',
        python_callable=_connect_ftp_server
    )

    # FTPサーバーのデータファイル有無を確認
    task2 = FTPSSensor(
        task_id=f'airflow_connection_ftp_task',
        path=f"test.txt",
        ftp_conn_id='con-id', # set at airflow
        mode='reschedule',
        soft_fail=False,
        poke_interval=300,
        timeout=3600,
    )

    