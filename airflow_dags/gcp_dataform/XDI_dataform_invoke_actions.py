import json
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.google.cloud.operators.dataform import (
    DataformCreateWorkflowInvocationOperator
)


MANIFEST_PATH = '/home/airflow/gcs/dags/DI/manifest.json'
REPOSITORY_ID = 'repo_name'


with DAG(
    dag_id='dataform_invoke_actions',
    start_date=datetime(2023, 10, 22),
    schedule_interval=None,
    default_args={
        'owner': 'airflow',
        'catchup': False,
        'execution_timeout': timedelta(seconds=3600),
        'retries': 3,
    },
) as dag:

    # manifestでinvokeタスクを定義する
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)
    actions = manifest['actions']

    tasks = {}

    for action in actions:
        # if tag in action['tags']:
        target = action['target']
        included_target = target.split('.')
        included_target = {
            'database': included_target[0],
            'schema': included_target[1],
            'name': included_target[2],
        }

        tasks[target] = DataformCreateWorkflowInvocationOperator(
            task_id=f'invoke_{target}_task',
            project_id='project_name',
            region='asia-northeast1',
            repository_id=REPOSITORY_ID,
            workflow_invocation={
                'compilation_result': manifest['compile_response_name'],
                'invocation_config': {
                    'included_targets': [included_target],
                }
            },
        )

    for action in actions:
        # if tag in action['tags']:
        target = action['target']
        for d_target in action.get('dependency_targets', []):
            upstream = tasks.get(d_target, None)
            if upstream:
                upstream >> tasks[target]

    # 最終まとめタスク
    end_op = EmptyOperator(
        task_id='end_task',
        trigger_rule='none_failed_or_skipped',
        depends_on_past=True
    )

    # define some other task
    # other_task

    # 依存関係
    tasks.pop('project_name.dataset.mart_name') >> other_task >> end_op
    list(tasks.values()) >> end_op
    end_op >> other_task
