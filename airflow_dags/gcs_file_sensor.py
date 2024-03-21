from datetime import timedelta, timezone, datetime

from airflow import DAG
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2020, 11, 29),
    'catchup': False,
    'execution_timeout': timedelta(seconds=3600),
    'retries': 3,
    'retry_delay': timedelta(minutes=10),
    'soft_fail': False
}

with DAG(
    'gcs_file_sensor',
    default_args=default_args,
    schedule_interval=None
) as dag:

    gcs_sensor = GCSObjectExistenceSensor(
        task_id='gcs_sensor_task',
        bucket='interface-bucket',
        object='folder/file.tsv.gz',
        mode='reschedule',
        timeout=600  # seconds
    )

    gcs_sensor
