def run_query_file(tablename):
    """
    BQへSQLを実行する関数

    Parameters
    ----------
    tablename ： string
        BQのテーブル名(且つ、SQLファイル名)
    """

    import google.auth
    from google.cloud import bigquery

    # GSSをソースにしているテーブルが存在するためスコープの指定が必要
    credentials, project = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/cloud-platform",
        ]
    )

    client = bigquery.Client(credentials=credentials, project=project)

    # SQL文取得
    with open(f'/home/airflow/gcs/dags/{tablename}.sql', 'r') as f:
        create_query = f.read()

    client.query(create_query).result()
    print(f'{tablename}.sql query completed.')
