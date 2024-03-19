def run_query():
    from google.cloud import bigquery

    client = bigquery.Client()
    query = """
        select 1
    """
    print(f'Query start!')
    result = client.query(query).result()
    print(f'Query completed!')
    result = [row for row in result][0]

    return result
