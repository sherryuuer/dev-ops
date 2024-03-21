import json
from google.cloud import dataform_v1beta1, storage


def _get_compilation_result(client, parent):
    """
    dataform定義のコンパイル結果情報を取得する

    Args:
        client (object): dataformクライアント
        parent (str): 対象のdataformのrootリポジトリ

    Returns:
        object: コンパイル結果情報
    """

    compilation_result = dataform_v1beta1.CompilationResult(
        git_commitish='main'
    )
    request = dataform_v1beta1.CreateCompilationResultRequest(
        parent=parent,
        compilation_result=compilation_result,
    )
    compile_result = client.create_compilation_result(request)

    return compile_result


def _get_compilation_result_actions(client, compile_result_name):
    """
    dataformのアクション詳細情報を取得する

    Args:
        client (object): dataformクライアント
        compile_result_name (str): コンパイル結果情報名

    Returns:
        object: アクション詳細情報のページャー
    """

    query_request = dataform_v1beta1.QueryCompilationResultActionsRequest(
        name=compile_result_name
    )
    page_result = client.query_compilation_result_actions(request=query_request)

    return page_result


def _save_manifest(
        compilation_result_actions_pages, 
        compile_result_name, 
        dag_bucket, 
        manifest_path,
    ):
    """
    dataformのマニフェストファイル（DM間の依存関係設定ファイル）を加工・保存する

    Args:
        compilation_result_actions_pages (object): アクション詳細情報のページャー
        compile_result_name (str): コンパイル結果情報名
        dag_bucket (str): ファイル保存先のバケット
        manifest_path (str): ファイル保存詳細パス
    """

    results = []
    for action in compilation_result_actions_pages:

        result = {}

        relation = getattr(action, 'relation', None)
        operations = getattr(action, 'operations', None)

        if not relation and not operations:
            continue

        if relation:
            result['action_type'] = 'relation'
            result['dependency_targets'] = [
                f'{target.database}.{target.schema}.{target.name}'
                for target in relation.dependency_targets
            ]
            result['tags'] = list(relation.tags)
        elif operations:
            result['action_type'] = 'operations'
            result['dependency_targets'] = [
                f'{target.database}.{target.schema}.{target.name}'
                for target in operations.dependency_targets
            ]
            result['tags'] = list(operations.tags)

        result['target'] = f'{action.target.database}.{action.target.schema}.{action.target.name}'
        results.append(result)

    manifest = {
        'compile_response_name': compile_result_name,
        'actions': results,
    }

    print(f'manifest: {manifest}')
    storage_client = storage.Client()
    bucket = storage_client.bucket(dag_bucket)
    blob = bucket.blob(manifest_path)
    blob.upload_from_string(json.dumps(manifest, indent=4))


def create_and_save_manifest(parent, dag_bucket, manifest_path):
    """
    dataform APIで必要なデータを取得してマニフェストファイルを作成する

    Args:
        parent (str): 対象のdataformのrootリポジトリ
        dag_bucket (str): ファイル保存先のバケット
        manifest_path (str): ファイル保存詳細パス    
    """

    client = dataform_v1beta1.DataformClient()

    compile_result = _get_compilation_result(client, parent)
    compile_result_name = compile_result.name
    page_result = _get_compilation_result_actions(client, compile_result_name)
    _save_manifest(page_result, compile_result_name, dag_bucket, manifest_path)
