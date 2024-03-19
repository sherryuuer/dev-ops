from google.cloud import bigquery
from airflow.models import Variable


def _get_ti_metadata(task_instance):
    """
    TASK情報を取得するための内部利用関数

    parameter:
    ---------------------
    kwargs : dict[any]
        DAG実行時のコンテキスト

    return:
    ---------------------
    ti_dict : dict[any]
        配信に必要なメタデータ

    """

    ti_dict = {}

    ti_dict['dag_id'] = task_instance.dag_id
    ti_dict['task_id'] = task_instance.task_id
    ti_dict['start_date'] = task_instance.start_date
    ti_dict['state'] = task_instance.state

    return ti_dict


def _insert_ti_metadata_to_bq(dag_id, table_name, start_end, execution_date, state):
    """
    TASK実行状況をBQの管理テーブルへ挿入する為の内部利用関数

    parameter:
    ---------------------
    dag_id : str
        DAG実行ID
    table_name : str
        連携対象テーブル名
    start_end : str
        処理開始・完了のステータス
        「start、end」のどちらかを指定
    execution_date : str
        処理実行開始・完了時間
    state : str
        処理の成功・失敗ステータス

    """

    query = f"""
        INSERT INTO `project.dataset.moniter_table`
        (
            dag_id
            ,table_name
            ,start_end
            ,execution_date
            ,stutas
        ) VALUES(
            '{dag_id}'
            ,'{table_name}'
            ,'{start_end}'
            ,CAST(TIMESTAMP_ADD('{execution_date}', INTERVAL 9 HOUR) as datetime)
            ,'{state}'
        )
    """

    bigquery_client = bigquery.Client()

    print(f'{table_name} {start_end} data insert begin!')
    bigquery_client.query(query).result()
    print(f'{table_name} {start_end} data insert completed!')


def python_start_write(**kwargs):
    """
    MYSQL連携バッチのTASK開始をBQの管理テーブルへ挿入する為の関数

    parameter:
    ---------------------
    kwargs : dict[any]
        DAG実行時のコンテキスト

    """

    ti_meta = _get_ti_metadata(kwargs['task_instance'])
    _insert_ti_metadata_to_bq(
        ti_meta['dag_id'],
        ti_meta['task_id'][10:],
        'start',
        ti_meta['start_date'],
        ti_meta['state'],
    )


def python_end_write_success(**kwargs):
    """
    TASK成功をBQの管理テーブルへ挿入する為の関数

    parameter:
    ---------------------
    kwargs : dict[any]
        DAG実行時のコンテキスト

    """

    ti_meta = _get_ti_metadata(kwargs['task_instance'])
    _insert_ti_metadata_to_bq(
        ti_meta['dag_id'],
        ti_meta['task_id'][15:],
        'end',
        ti_meta['start_date'],
        'success',
    )


def python_end_write_failed(**kwargs):
    """
    MYSQL連携バッチのTASK失敗をBQの管理テーブルへ挿入する為の関数

    parameter:
    ---------------------
    kwargs : dict[any]
        DAG実行時のコンテキスト

    """

    ti_meta = _get_ti_metadata(kwargs['task_instance'])
    _insert_ti_metadata_to_bq(
        ti_meta['dag_id'],
        ti_meta['task_id'][14:],
        'end',
        ti_meta['start_date'],
        'failed',
    )


def insert_task_result_to_bq(mode, **kwargs):
    """
    連携バッチのTASK開始・実行結果をBQの管理テーブルへ挿入する為の関数
    将来的に既存の関数から移行用の関数

    parameter:
    ---------------------
    mode : str
        関数の処理モード
        「write_start、write_end_success、write_end_failed」のどれかを指定
    kwargs : dict[any]
        DAG実行時のコンテキスト

    """

    # mode引数チェック
    if mode in ('write_start', 'write_end_success', 'write_end_failed'):
        raise ValueError(
            f'invalid literal. mode is "write_start", "write_end_success" or "write_end_failed" available: {mode}')

    task_instance = kwargs['task_instance']
    dag_id = task_instance.dag_id
    task_id = task_instance.task_id[10:]
    start_end = 'start'
    start_date = task_instance.start_date
    state = task_instance.state

    if mode in ('write_end_success', 'write_end_failed'):
        start_end = 'end'

        if mode == 'write_end_success':
            task_id = task_instance.task_id[15:]
            state = 'success'
        else:
            task_id = task_instance.task_id[14:]
            state = 'failed'

    # BQへデータ投入
    _insert_ti_metadata_to_bq(
        dag_id,
        task_id,
        start_end,
        start_date,
        state
    )


def _notify_slack_dag_exec_state(dag_id, task_id, state='success'):
    """
    TASK実行結果をSLACKへ通知するための内部利用関数

    parameter:
    ---------------------
    dag_id : str
        実行DAGのID
    task_id : str
        実行TASKのID
    state : str
        成功・失敗の通知ステータス
        「success、failed」のどちらかを指定

    """

    import requests

    SUCCESS_TEXT = '処理が成功しました。'
    FAILED_TEXT = '処理が失敗しました。'

    slack_channel_id = 'xxxxxxxxxxx'
    slack_api_endpoint = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Authorization': f'Bearer {Variable.get("bot-user_oauth_token")}',
    }
    # states引数チェック
    if state not in ('success', 'failed'):
        raise ValueError(
            f'invalid literal. state is "success" or "failed" available: {state}')
    mention = '' if state == 'success' else '<!channel>\n'
    text = SUCCESS_TEXT
    if state == 'failed':
        text = FAILED_TEXT

    payload = {
        'channel': slack_channel_id,
        'text': (
            f'{mention}'
            f'{dag_id}{task_id}{text}'
        ),
    }

    response = requests.post(slack_api_endpoint, headers=headers, json=payload)
    print(response.text)


def notify_success(**kwargs):
    """
    TASK成功をSLACKへ通知するための関数

    parameter:
    ---------------------
    kwargs : dict[any]
        DAG実行のコンテキスト

    """

    _notify_slack_dag_exec_state(kwargs['dag'], kwargs['task'], 'success')


def notify_error(**kwargs):
    """
    TASKエラー・失敗をSLACKへ通知するための関数

    parameter:
    ---------------------
    kwargs : dict[any]
        DAG実行のコンテキスト

    """

    _notify_slack_dag_exec_state(kwargs['dag'], kwargs['task'], 'failed')
