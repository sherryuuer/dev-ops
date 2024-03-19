def load_gcs_data_to_bq(kubunname, dataset, tablename):
    """
    GCSのデータをBQにロード

    Parameters
    ----------
    kubunname : string
        区分名
    dataset : string
        データセット名
    tablename : string
        テーブル名
    """

    import gzip
    import io

    from google.api_core.exceptions import BadRequest
    from google.cloud import storage

    date_today = datetime.now(
        timezone(timedelta(hours=9), 'JST')).strftime('%Y%m%d')
    project_name = 'project_name'
    bucket_name = 'tbk-dap-prod-interface-bucket'
    client = bigquery.Client()

    # スキーマ定義抽出用
    schema_dataset_ref = client.dataset(dataset, project=project_name)
    schema_table_ref = schema_dataset_ref.table(f'{tablename}')
    schema_table = client.get_table(schema_table_ref)

    # テーブルへデータロード
    uri = f'gs://{bucket_name}/{kubunname}/{tablename}/{
        date_today}/{tablename}_{date_today}*.tsv.gz'
    table_id = f'{project_name}.{dataset}.{tablename}_tmp'
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=0,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        allow_quoted_newlines=True,
        field_delimiter='\t',
        max_bad_records=0,
        schema=schema_table.schema,
        quote_character='"'
    )
    job = client.load_table_from_uri(uri, table_id, job_config=job_config)

    try:
        job.result()
    except BadRequest as e:
        print(f'error：{e}')

        # BQへロード出来ないデータを削除
        blob_prefix = f'{
            kubunname}/{tablename}/{date_today}/{tablename}_{date_today}'
        delimiter = '/'
        merge_content = []

        gcs_client = storage.Client()
        blobs = gcs_client.list_blobs(
            bucket_name, prefix=blob_prefix, delimiter=delimiter)
        for blob in blobs:
            content = blob.download_as_string()
            with io.BytesIO(content) as s:
                with gzip.open(s, mode='rb') as g:
                    merge_content.append(g.read().replace(
                        b'\x00', b'').replace(b'0000-00-00 00:00:00', b''))

        with io.BytesIO(b''.join(merge_content)) as s:
            job = client.load_table_from_file(
                s, table_id, job_config=job_config)
            job.result()
