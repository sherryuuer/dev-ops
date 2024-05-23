from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from dataform_invoke.funcs.manifest_generator import create_and_save_manifest
from dataform_invoke.conf.manifest_conf import DAG_BUCKET, MANIFEST_PATH, PARENT

with DAG(
    dag_id='dataform_create_manifest',
    start_date=datetime(2024, 1, 24),
    schedule_interval=None,
    default_args={
        'owner': 'airflow',
        'catchup': False,
        'execution_timeout': timedelta(seconds=3600),
        'retries': 0,
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
    )

    create_manifest
