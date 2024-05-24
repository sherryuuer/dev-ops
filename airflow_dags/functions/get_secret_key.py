from google.cloud import secretmanager

PROJECT_ID = "bandainamco-lake-bsp-dev"
SECRET_ID = "gbase-access-key"

def _get_connection_info(project_id=PROJECT_ID, secret_id=SECRET_ID):
    """
    Secret ManagerからFTP接続情報を取得する

    Args:
        project_id (str): 処理を実行するGCPプロジェクトID
        secret_id (str): Secret managerのSecret ID

    Returns:
        object: シークレット情報
    """

    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_path(project_id, secret_id)

    res = client.get_secret(request={"name": name})
    print(res.keys())