from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022, 10, 19),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'backup-composer-env',
    schedule_interval='00 20 * * *',
    catchup=False,
    default_args=default_args
) as dag:

    save_ss_path = 'gs://bucket_name/composer-snapshot'

    # backup task
    bkup_task = BashOperator(
        task_id='bkup_task',
        bash_command=f"""
            gcloud beta composer environments snapshots save tbk-dap-prod-composer-01 \
                --location asia-northeast1 \
                --snapshot-location "{save_ss_path}"
        """,
        depends_on_past=True
    )

    bkup_task
