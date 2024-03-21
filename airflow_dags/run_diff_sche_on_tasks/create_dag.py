# airflow DAG
from DI.create_dag_function import create_dag
from DI.sche_class_list import (
    DagSche8AM1stOfEveryMonth,
    DagSche1030AM1stEveryMonth,
    DagSche0730AM2ndOfEveryMonth,
    DagSche8AM20stOfEveryMonth,
    DagSche8AM25thOfEveryMonth,
    DagSche8AMEveryMonday,
    DagSche8AMEvery2Monday,
    DagSche1030AMEveryMonday,
    DagSche0730AMEveryTuesday,
    DagSche8AMEveryWednesday
)

create_dag_list = [
    DagSche8AM1stOfEveryMonth,
    DagSche1030AM1stEveryMonth,
    DagSche0730AM2ndOfEveryMonth,
    DagSche8AM20stOfEveryMonth,
    DagSche8AM25thOfEveryMonth,
    DagSche8AMEveryMonday,
    DagSche8AMEvery2Monday,
    DagSche1030AMEveryMonday,
    DagSche0730AMEveryTuesday,
    DagSche8AMEveryWednesday
]

for cls in create_dag_list:
    dag = create_dag(
        cls.DAG_NAME,
        cls.EXEC_SCHEDULE,
        cls.START_DATE_YEAR,
        cls.START_DATE_MONTH,
        cls.START_DATE_DAY,
        cls.START_DATE_HOUR,
        cls.START_DATE_MINITE,
        cls.SOME_LIST
    )
    globals()[f'dag_{dag.dag_id}'] = dag
