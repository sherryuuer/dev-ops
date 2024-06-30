from google.cloud import bigquery

def table_exists(project_id, dataset_id, table_id):
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    try:
        client.get_table(table_ref)
        return True
    except Exception as e:
        return False

# example
project_id = 'your_project_id'
dataset_id = 'analytics_xxx'
table_id = 'events_20230623'

if table_exists(project_id, dataset_id, table_id):
    print(f"Table {table_id} exists.")
else:
    print(f"Table {table_id} does not exist.")
