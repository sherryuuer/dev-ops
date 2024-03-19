from datetime import timedelta, datetime

from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


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
    'trigger_other_dag',
    default_args=default_args,
    schedule_interval=None
) as dag:

    # DAGを起動する
    trigger_dag_task = TriggerDagRunOperator(
        task_id='trigger_dag_task',
        trigger_dag_id='other_dag_name',
        depends_on_past=True
    )

    trigger_dag_task
