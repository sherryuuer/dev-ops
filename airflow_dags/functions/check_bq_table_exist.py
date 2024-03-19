from google.cloud import bigquery
from google.cloud.exceptions import NotFound


def check_ga_table_exists(exec_date):
    client = bigquery.Client()

    table_id = f"project.dataset.tabel_name_{exec_date}"

    try:
        client.get_table(table_id)
        print(f"Table {table_id} already exists.")
        return True
    except NotFound:
        print(f"Table {table_id} is not found.")
        return False
