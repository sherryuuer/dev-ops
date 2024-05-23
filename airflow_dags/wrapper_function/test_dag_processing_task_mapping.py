from datetime import datetime, timedelta
from pytz import timezone
from pprint import pprint

from airflow import DAG
# EmptyOperatorはmapreduceできない、task_idはmapできないため、そもそもいらぬと思います
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.decorators import task
# from airflow import XComArg

from temp.test_dag_factory import wrapper_dag
from temp.tablelist import table_list


yesterday = datetime.now(tz=timezone('Asia/Tokyo')) - timedelta(days=1)


# 別ファイルからインポートする予定、decorateするためにもう一回def書く必要がある
@task
def print_table_1(tablename):
    # xcom iterator
    return f'{tablename}_task1'

@task
def print_table_2(tablename):
    # xcom iterator
    return f'{tablename}_task2'

@task
def get_tables(table_list=table_list):
    print(table_list)
    return [table for table in table_list]

with DAG(
    dag_id='ZDI_test_mapreduce_task',
    # start_dateはdefault_argsではなくて、DAGのパラメータで渡さないとなぜかエラーになるので注意
    start_date=yesterday,
    schedule_interval=None, # '30 2 * * *',
    default_args={
        'owner': 'airflow',
        'execution_timeout': timedelta(seconds=3695),
        'retries': 1, # test
        'retry_delay': timedelta(minutes=10),
        # 'soft_fail': False,
    },
    catchup=False,
) as dag:

    # keep this without task map reduce
    pre_tasks = []

    for table in table_list:
        # modify id
        pre_tasks.append(EmptyOperator(task_id=f'post_task_1_{table}'))

    # この場合はtaskgroupいる？
    with TaskGroup('test_taskgroup', tooltip='Load data taskgroup') as post_taskgroup:


        # with decorator:The @task decorator is recommended over the classic PythonOperator to execute Python callables.
        # but we have to isolate the func to other file so maybe not use this
        lst = get_tables(table_list)

        # soft fail で失敗log1
        # print_table_1.expand(tablename=lst)
        # print_table_2.expand(tablename=lst)
        task1 = print_table_1.expand(tablename=lst)
        task2 = print_table_2.expand(tablename=lst)
        # '_TaskDecorator' object has no attribute 'output'
        # print_table_2.expand(tablename=print_table_1.output)
        # task1 = print_table_1.expand(tablename=lst)
        # airflow.exceptions.SerializationError: Failed to serialize DAG 'ZDI_test_mapreduce_task': 'PlainXComArg' object has no attribute 'task_id'
        # task2 = print_table_2.expand(tablename=XComArg(task1))
        # pass value by output :
        # print_table_2.expand(tablename=print_table_1.output)
        # TypeError: unsupported operand type(s) for >>: '_TaskDecorator' and '_TaskDecorator'
        # print_table_1 >> print_table_2
        task1 >> task2

    dag = wrapper_dag(
        dag=dag,
        pre_tasks=[pre_tasks], 
        post_tasks=[[post_taskgroup]],
    )


# Mapreduceのリソース影響との観点はこれはとても気に入るのですが
# シンプルさ感じられる

# とてもいいですが、メンバーの学習コストも高いかも
# インポートした関数を再度defで加工する必要がある、関数が多いとちょっと、
# 超シンプルなPython関数以外、複雑なロジックには汎用性が少ない、統一するのはできるかの懸念点がある
# 何時間もdebugして気持ち悪くなる、他のオペレーターと組み合わせすると複雑点がおおい、私は理解不足かも
# テーブルのリスト化するのはファンクションが必要、タスクとして表示する。これで１対多関係になる
# task_idがcustomできない、表示するときはどのテーブルの処理なのか画面で検索確認できない、わかりずらい、どうでもよいタスクならいいが
# argsの影響はなに？例えばsoft failとか、それ以外の動作が影響にでる？
# taskがdecoratorされたらタスクになるはずが_TaskDecoratorになるのはちょっと理解足りないかも。
# タスクつなぐ時は>>で使うか、XComArgですが、これのxcomの書き方は今後も工夫する必要がある、これに関するテストはうまくいってなかった。