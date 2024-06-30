from __future__ import annotations
import os
import json
import time

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.pubsub import PubSubPullOperator
from airflow.models.xcom_arg import XComArg

PROJECT = os.getenv('project')
TOPIC_ID = "zdh-test-topic"
SUBSCRIPTION = "zdh-test-subscription"


def handle_messages(pulled_messages, context):
    file_names = list()
    for idx, m in enumerate(pulled_messages):
        data = json.loads(m.message.data.decode("utf-8"))
        print(f"message {idx} data is {data}")
        file_names.append({"file_name": data["name"]})
    return file_names


def _prep_file1(file_path):
    print(f"Prepping {file_path} with prep_file1")
    time.sleep(1)
    print("Done with prep_file1!")


def _prep_file2(file_path):
    print(f"Prepping {file_path} with prep_file2")
    time.sleep(1)
    print("Done with prep_file2!")


def _prep_file3(file_path):
    print(f"Prepping {file_path} with prep_file3")
    time.sleep(1)
    print("Done with prep_file3!")


def cleansing_data(file_path):

    prep_funcs = {
        'filename1': _prep_file1,
        'filename2': _prep_file2,
        'filename3': _prep_file3,
    }

    # get the table name 
    base_file_name = os.path.splitext(file_path.split('/')[-1])[0]

    prep_func = prep_funcs.get(base_file_name, None)

    if prep_func:
        return prep_func(file_path)
    else:
        print(f"No matching prep function for file: {base_file_name}")


with DAG(
    "pull_and_process",
    start_date=days_ago(1),
    schedule_interval=None,
    max_active_runs=1,
    catchup=False,
) as trigger_dag:

    pull_messages_task = PubSubPullOperator(
        task_id="pull_messages_operator",
        project_id=PROJECT,
        ack_messages=True,
        messages_callback=handle_messages,
        subscription=SUBSCRIPTION,
        max_messages=50,
    )

    process_task = (
        PythonOperator.partial(
            task_id="cleansing_data",
            python_callable=cleansing_data
        )
        .expand(op_kwargs=XComArg(pull_messages_task))
    )

    pull_messages_task >> process_task
