from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.ftp.sensors.ftp import FTPSSensor
from airflow.utils.decorators import apply_defaults
import ftplib
from datetime import datetime


PROJECT_ID = 'bandainamco-lake-bsp-dev'
SECRET_ID = 'gbase-access-key'
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

    connection_info = _get_connection_info()
    print(connection_info["host"])
    ftps = ftplib.FTP_TLS(
        host=connection_info["host"],
        user=connection_info["user"],
        passwd=connection_info["password"],
        timeout=60,
    )
    ftps.prot_p()


class CustomFTPSSensor(FTPSSensor):
    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def poke(self, context):
        # create FTP hook to try to connect
        hook = self._create_hook()
        connection = hook.get_connection(self.ftp_conn_id)
        self.log.info('Attempting to connect to FTPS server: %s', connection.host)

        try:
            with hook.get_conn() as ftp_conn:
                self.log.info('Successfully connected to FTPS server: %s', connection.host)
                
                self.log.info('Poking for %s', self.path)
                # try:
                #     ftp_conn.voidcmd(f"MDTM {self.path}")
                # except ftplib.error_perm as e:
                #     self.log.info('Ftp error encountered: %s', str(e))
                #     error_code = self._get_error_code(e)
                #     if ((error_code != 550) and
                #             (self.fail_on_transient_errors or
                #                 (error_code not in self.transient_errors))):
                #         raise e
                #     return False

                return True
        except Exception as e:
            self.log.error('Failed to connect to FTPS server: %s', e)
            return False


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
    # task2 = FTPSSensor(
    #     task_id=f'airflow_connection_ftp_task',
    #     path=f"test.txt",
    #     ftp_conn_id='gbase-access-key',
    #     mode='reschedule',
    #     soft_fail=False,
    #     poke_interval=300,
    #     timeout=3600,
    # )
    task2 = CustomFTPSSensor(
        task_id='airflow_connection_ftp_task',
        path='test.txt',
        ftp_conn_id='gbase-access-key',
        mode='reschedule',
        soft_fail=False,
        poke_interval=300,
        timeout=3600,
    )


    