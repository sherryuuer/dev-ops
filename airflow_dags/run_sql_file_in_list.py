from datetime import timedelta, datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from dm_table_list import DM_LIST


def run_query_file(tablename):
    """
    BQへSQLを実行する関数

    Parameters
    ----------
    tablename ： string
        BQのテーブル名(且つ、SQLファイル名)
    """

    import google.auth
    from google.cloud import bigquery

    # GSSをソースにしているテーブルが存在するためスコープの指定が必要
    credentials, project = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/cloud-platform",
        ]
    )

    client = bigquery.Client(credentials=credentials, project=project)

    # SQL文取得
    with open(f'/home/airflow/gcs/dags/{tablename}.sql', 'r') as f:
        create_query = f.read()

    client.query(create_query).result()
    print(f'{tablename}.sql query completed.')


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
    'run_sql_file_in_list',
    default_args=default_args,
    schedule_interval=None
) as dag:

    dm_create_dict = {}

    end_op = EmptyOperator(
        task_id='end_task',
        trigger_rule='none_failed_or_skipped',
        depends_on_past=True
    )

    for i, v in enumerate(DM_LIST):
        dm_dict[v['tablename']] = PythonOperator(
            task_id='run_{0}_file'.format(v['tablename']),
            python_callable=run_query_file,
            op_kwargs={'tablename': v['tablename']},
            depends_on_past=True
        )

    # マート間での依存関係有
    dm_dict.pop('table_1') >> dm_dict.pop('table_2') >> end_op

    # マート間での依存関係無
    list(dm_dict.values()) >> end_op
