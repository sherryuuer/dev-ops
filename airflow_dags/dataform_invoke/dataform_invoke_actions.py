import os
import json
from datetime import datetime, timedelta

from airflow import DAG
# from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.dataform import (
    DataformCreateWorkflowInvocationOperator,
)
from airflow.sensors.python import PythonSensor
from airflow.utils.task_group import TaskGroup
from dataform_invoke.funcs.bigquery import check_dataset_updated

# from temp.common.utility_funcs import notify_job_error, notify_job_success
from dataform_invoke.conf.manifest_conf import MANIFEST_PATH, REPOSITORY_ID

AF_MANIFEST_PATH = f'/home/airflow/gcs/{MANIFEST_PATH}'


with DAG(
    dag_id='dataform_invoke_actions',
    start_date=datetime(2023, 10, 22),
    schedule_interval=None,
    default_args={
        'owner': 'airflow',
        'catchup': False,
        'execution_timeout': timedelta(seconds=3600),
        'retries': 0,
    },
) as dag:

    with TaskGroup('dm_taskgroup', tooltip='update dm task group') as dm_update_tg:
        # manifestでinvokeタスクを定義する
        with open(AF_MANIFEST_PATH, 'r') as f:
            manifest = json.load(f)

        # 日次実行のアクションのみを取得
        actions = manifest['schedule']['sche_daily']

        dataset_sensor_tasks = {}
        for schema in actions['all_schema_tags']:
            # 管理テーブルの成功数をセンサーする
            dataset_sensor_tasks[schema] = PythonSensor(
                task_id=f'bigquery_{schema}_updated_sensor',
                python_callable=check_dataset_updated,
                op_kwargs={'dataset_name': schema},
                mode='reschedule',
                poke_interval=60,  # 300
                timeout=3600,
            )

        action_tasks = {}
        for target, action in actions['actions'].items():
            included_target = target.split('.')
            included_target = {
                'database': included_target[0],
                'schema': included_target[1],
                'name': included_target[2],
            }

            action_tasks[target] = DataformCreateWorkflowInvocationOperator(
                task_id=f'invoke_{target}_task',
                project_id=os.getenv('project'),
                region='asia-northeast1',
                repository_id=REPOSITORY_ID,
                workflow_invocation={
                    'compilation_result': manifest['compile_response_name'],
                    'invocation_config': {
                        'included_targets': [included_target],
                    }
                },
            )

        # task group内の依存関係
        for target, action in actions['actions'].items():
            for d_target in action.get('dependency_targets', []):
                action_tasks[d_target] >> action_tasks[target]
                # upstream = action_tasks.get(d_target, None)
                # if upstream:
                #    upstream >> action_tasks[target]
            for schema in action.get('schema_tags', []):
                dataset_sensor_tasks[schema] >> action_tasks[target]
                # upstream = dataset_sensor_tasks.get(schema, None)
                # if upstream:
                #    upstream >> action_tasks[target]

    # スラックに成功通知
    # slk_success_op = PythonOperator(
    #     task_id='create_dm_success',
    #     provide_context=True,
    #     python_callable=notify_job_success,
    #     op_kwargs={'job_name': dag.dag_id},
    #     trigger_rule='none_failed_or_skipped'
    # )

    # スラックに失敗通知
    # slk_fail_op = PythonOperator(
    #     task_id='create_dm_failed',
    #     provide_context=True,
    #     python_callable=notify_job_error,
    #     op_kwargs={'job_name': dag.dag_id},
    #     trigger_rule='one_failed'
    # )

    # dm_update_tg >> [slk_success_op, slk_fail_op]
    dm_update_tg
