import json
import requests
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from google.cloud import pubsub_v1


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'monitor_pubsub_logging',
    default_args=default_args,
    description='A DAG to monitor GCP Pub/Sub and notify on failures',
    schedule_interval='@hourly',
    start_date=days_ago(1),
    tags=['gcp', 'pubsub', 'logging'],
)

PROJECT_ID = ''
TOPIC_NAME = 'gcs-file-sensor'
SUBSCRIPTION_NAME = 'subscription-name'
TEAMS_WEBHOOK_URL = 'webhook-url'

def check_pubsub_messages():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)
    
    response = subscriber.pull(subscription=subscription_path, max_messages=10)
    
    failure_count = 0
    for msg in response.received_messages:
        message_data = json.loads(msg.message.data)
        if message_data.get('status') == 'FAILURE':
            failure_count += 1
    
    if failure_count > 1:
        notify(failure_count)
    
    # ack
    ack_ids = [msg.ack_id for msg in response.received_messages]
    subscriber.acknowledge(subscription=subscription_path, ack_ids=ack_ids)

def notify(failure_count):
    """notify Microsoft Teams"""
    message = f'There are {failure_count} failure messages in the Pub/Sub topic {TOPIC_NAME}.'
    payload = {
        'text': message
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(TEAMS_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f'Notification to Teams failed: {response.status_code}, {response.text}')

# task
monitor_pubsub_task = PythonOperator(
    task_id='monitor_pubsub_messages',
    python_callable=check_pubsub_messages,
    dag=dag,
)

