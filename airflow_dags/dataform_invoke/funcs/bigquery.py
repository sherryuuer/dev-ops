import os
from google.cloud import bigquery

project = os.getenv('project')


def check_dataset_updated(dataset_name):
    """
    datasetに含まれるローデータテーブルの更新が完了しているか確認する

    Args:
        dataset_name (str): 対象のデータセット名

    Returns:
        boolean: True: 更新済、False: 未更新
    """

    table_name = f'{project}.zdh__source__operate.rawdata_update_statuses'
    check_sql = f"""
        select
            count(*) >= 1 as is_updated
        from
            (
                select
                    dataset
                from
                    {table_name}
                where
                    update_datetime = current_date('Asia/Tokyo')
                    and dataset = '{dataset_name}'
            )
    """

    client = bigquery.Client()
    rows = client.query(check_sql).result()
    result = [row for row in rows][0]

    return result['is_updated']
