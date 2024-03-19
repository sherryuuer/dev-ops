from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryExecuteQueryOperator,
)

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
    'run_bq_query_by_operator',
    default_args=default_args,
    template_searchpath=['/home/airflow/gcs/dags/DI'],
    # タスクで実行するSQLのテーブル名を動的に設定するためmacroを利用している
    user_defined_macros={'exec_date': exec_date},
    schedule_interval=None  # '30 7 * * *'
) as dag:

    # BQクエリ実行
    task_name = BigQueryExecuteQueryOperator(
        task_id='task_name',
        location='asia-northeast1',
        sql='sql/test.sql',
        use_legacy_sql=False,
        depends_on_past=True
    )

    task_name
