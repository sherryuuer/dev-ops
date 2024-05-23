from airflow.models.baseoperator import chain
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from pprint import pprint


# 別ファイルからインポートする予定
def print_context(**kwargs):
    pprint(kwargs)
    pprint(f"timeout: {kwargs['task'].execution_timeout}")


def wrapper_dag(
    dag,
    pre_tasks=None,
    post_tasks=None,
):
    
    pre_tasks = pre_tasks or []
    post_tasks = post_tasks or []

    with dag:
        start_task = PythonOperator(task_id=f'start_task', python_callable=print_context)
        end_task = EmptyOperator(task_id='end_task')
    
    chain(*pre_tasks, start_task, *post_tasks, end_task)

    return dag