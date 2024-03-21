import json
from datetime import timedelta, datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
# inport other operators


def create_dag(dag_name, exec_schedule, start_date_year, start_date_month, start_date_day, start_date_hour, start_date_minite, other_args):
    """
    dag作成用の関数

    Args:
        dag_name : str
            dag名
        exec_schedule : str
            dag実行スケジュールのcron式
        start_date_year : int
            dagのstart_dateの年
        start_date_month : int
            dagのstart_dateの月
        start_date_day : int
            dagのstart_dateの日
        start_date_hour : int
            dagのstart_dateの時
        start_date_minite : int
            dagのstart_dateの分
        some_other_args : list(dict)
            ...

    Returns:
        dag : dag
            作成したdagインスタンス

    """

    default_args = {
        'owner': 'airflow',
        'start_date': datetime(start_date_year, start_date_month, start_date_day, start_date_hour, start_date_minite),
        'execution_timeout': timedelta(seconds=3600),
        'retries': 3,
        'retry_delay': timedelta(minutes=10),
        'soft_fail': False
    }

    with DAG(
        f'prefix_dag_name_{dag_name}',
        default_args=default_args,
        schedule_interval=exec_schedule,
        catchup=False
    ) as dag:

        # tasks
        empty_task = EmptyOperator(
            task_id='empty_task',
            trigger_rule='none_failed_or_skipped',
            depends_on_past=True
        )

        python_task = PythonOperator(
            task_id='python_task',
            provide_context=True,
            python_callable=some_function,
        )

        empty_task >> python_task

    return dag
