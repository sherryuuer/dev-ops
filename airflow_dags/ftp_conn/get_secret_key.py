from google.cloud import secretmanager
import ftplib
import json

PROJECT_ID = 'bandainamco-lake-bsp-dev'
SECRET_ID = 'gbase-access-key'
VERSION = '1'

def _get_connection_info():

    # client = secretmanager.SecretManagerServiceClient()
    # name = f"projects/{project_id}/secrets/gbase-access-key/versions/1"

    # # Get the secret version.
    # response = client.get_secret_version(request={"name": name})

    # # Print information about the secret version.
    # state = response.state.name
    # print(f"Got secret version {response.name} with state {state}")

    client = secretmanager.SecretManagerServiceClient()
    path = client.secret_version_path(PROJECT_ID, SECRET_ID, VERSION)

    response = client.access_secret_version(name=path)
    secret_value = response.payload.data.decode('UTF-8')
    
    # try to get key
    secret_dict = json.loads(secret_value)
    # return list(secret_dict.keys())
    return secret_dict


def _connect_ftp_server():
    """
    FTPサーバーへFTPSプロトコルで接続する

    Args:
        connection_info (object): Secret Managerから取得した接続情報

    Returns:
        FTP_TLS: FTPサーバーへの接続
    """
    connection_info = _get_connection_info()
    print(connection_info["host"])
    # ftps = ftplib.FTP_TLS(
    #     host=connection_info["host"],
    #     user=connection_info["user"],
    #     passwd=connection_info["password"],
    #     timeout=60,
    # )
    # ftps.prot_p()
    
    # return ftps
    ftp = ftplib.FTP(
        host=connection_info["host"],
        user=connection_info["user"],
        passwd=connection_info["password"]
    )
    ftp.login()
    ftp.retrlines('LIST')
    ftp.quit()