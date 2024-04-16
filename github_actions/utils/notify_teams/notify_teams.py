import requests
import sys

from mention_members import MENTION_MEMBERS


def _prep_job_message(info, repository, commit_message, author, timestamp):
    """
    JOBが失敗した場合の通知メッセージを作成する
    失敗した場合は運用メンバーへメンションする
    format sample here:
    https://learn.microsoft.com/ja-jp/microsoftteams/platform/task-modules-and-cards/cards/cards-format?tabs=adaptive-md%2Cdesktop%2Cconnector-html

    Returns:
        dict: 通知メッセージ
    """

    entries = []
    mentions_text = f'デプロイ成功しました！\n\n'
    if info == 'failure':

        for m in MENTION_MEMBERS:
            entries.append(
                {
                    'type': 'mention',
                    'text': f'<at>{m}</at>',
                    'mentioned': {
                        'id': m,
                        'name': m.split('@')[0]
                    },
                }
            )
        mentions = ''.join([f'<at>{m}</at> ' for m in MENTION_MEMBERS])
        mentions_text = f'{mentions}\n\nデプロイ失敗しました！\n\n'

    text = (f'{mentions_text}リポジトリ：{repository}\n\n'
            f'コミットメッセージ：{commit_message}\n\n'
            f'作成者：{author}\n\n'
            f'タイムスタンプ：{timestamp}')

    message = {
        'type': 'message',
        'attachments': [{
            'contentType': 'application/vnd.microsoft.card.adaptive',
            'content': {
                'type': 'AdaptiveCard',
                'body': [{
                    'type': 'TextBlock',
                    'text': text,
                    'wrap': True
                }],
                '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                'version': '1.0',
                'msteams': {
                    'entities': entries,
                    'width': 'Full',
                },
            },
        }],
    }

    return message


def notify_message(webhook_url, info, repository, commit_message, author, timestamp):
    """
    メッセージをteamsへ通知する

    Args:
        message (string): 通知するメッセージ
        webhook_url (string): teamsへの通知に利用するwebhookのURL
    """
    response = requests.post(
        webhook_url,
        json=_prep_job_message(
            info, repository, commit_message, author, timestamp),
    )
    print(f'response: {response}')


if __name__ == "__main__":

    # パラメータ解析
    webhook_url = sys.argv[1]
    info = sys.argv[2]
    repository = sys.argv[3]
    commit_message = sys.argv[4]
    author = sys.argv[5]
    timestamp = sys.argv[6]

    # 関数実行
    notify_message(webhook_url, info, repository,
                   commit_message, author, timestamp)
