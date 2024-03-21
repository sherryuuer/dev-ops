from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from DI.archive import create_and_save_manifest


# modify the project_name and repo_name
PARENT = 'projects/project_name/locations/asia-northeast1/repositories/repo_name'
DAG_BUCKET = 'dag_bucket_name'
MANIFEST_PATH = 'dags/manifest.json'


with DAG(
    dag_id='XDI_dataform_create_manifest',
    start_date=datetime(2024, 1, 24),
    schedule_interval=None,  # '00 23 * * *',
    default_args={
        'owner': 'airflow',
        'catchup': False,
        'execution_timeout': timedelta(seconds=3600),
        'retries': 3,
    },
) as dag:

    # manifestファイルを作成と保存する
    create_manifest = PythonOperator(
        task_id='create_save_manifest_task',
        python_callable=create_and_save_manifest,
        op_kwargs={
            'parent': PARENT,
            'dag_bucket': DAG_BUCKET,
            'manifest_path': MANIFEST_PATH,
        },
        depends_on_past=True
    )

    create_manifest
