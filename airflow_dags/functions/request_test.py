import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def test_google_connection():
    url = "https://www.google.com"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Connection to Google homepage successful!")
        else:
            print(f"Failed to connect to Google homepage. Status code: {response.status_code}")
    except requests.ConnectionError as e:
        print(f"Failed to connect to Google homepage: {e}")


default_args = {
    'owner': 'airflow',
    'catchup': False,
}

with DAG(
    'request_test',
    default_args=default_args,
    start_date=datetime(2022, 9, 26),
    schedule_interval=None  # "00 12 * * *"
) as dag:

    task1 = PythonOperator(
        task_id='task1',
        python_callable=test_google_connection
    )
