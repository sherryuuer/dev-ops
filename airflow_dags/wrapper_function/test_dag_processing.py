from datetime import datetime, timedelta
from pytz import timezone
from pprint import pprint

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.models.baseoperator import chain

from temp.test_dag_factory import wrapper_dag
from temp.tablelist import table_list


# 別ファイルからインポートする予定
def print_context(**kwargs):
    pprint(kwargs)
    pprint(f"timeout: {kwargs['task'].execution_timeout}")


# start_dateを昨日に動的に設定するため：airflowの仕様により実行時間が(実行時間の前日 + 1day)
yesterday = datetime.now(tz=timezone('Asia/Tokyo')) - timedelta(days=1)


with DAG(
    dag_id='ZDI_test_func_ver1',
    # start_dateはdefault_argsではなくて、DAGのパラメータで渡さないとなぜかエラーになるので注意
    start_date=yesterday,
    schedule_interval='30 17 * * *',
    default_args={
        'owner': 'airflow',
        'execution_timeout': timedelta(seconds=3695),
        'retries': 3,
        'retry_delay': timedelta(minutes=10),
        'soft_fail': False,
    },
    catchup=False,
) as dag:

    # pre_tasks = []
    post_tasks_1 = []
    post_tasks_2 = []

    # for table in table_list:
    #     pre_tasks.append(PythonOperator(task_id=f'pre_task_{table}', python_callable=print_context))

    with TaskGroup('pre_taskgroup', tooltip='Load data taskgroup') as pre_taskgroup:

        dummy_task = EmptyOperator(task_id='end_task')
        dummy_task

    with TaskGroup('post_taskgroup', tooltip='Load data taskgroup') as post_taskgroup:

        for table in table_list:
            post_tasks_1.append(EmptyOperator(task_id=f'post_task_1_{table}'))
            post_tasks_2.append(EmptyOperator(task_id=f'post_task_2_{table}'))
        
        # list >> list 
        chain(post_tasks_1, post_tasks_2) 

    dag = wrapper_dag(
        dag=dag,
        # pre_tasks=[pre_tasks], 
        pre_tasks=[[pre_taskgroup]],
        post_tasks=[[post_taskgroup]],
    )