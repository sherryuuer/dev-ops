from datetime import timedelta


class DagSche8AM1stOfEveryMonth:
    """
    毎月1日8時実行のtech_mart用
    """

    EXEC_SCHEDULE = '00 8 1 * *'
    START_DATE_YEAR = 2023
    START_DATE_MONTH = 2
    START_DATE_DAY = 1
    START_DATE_HOUR = 0
    START_DATE_MINITE = 0
    DAG_NAME = '8AM1stOfEveryMonth'

    SOME_LIST = [
        {'key': 'value'},
    ]


class DagSche1030AM1stEveryMonth:
    """
    毎月1日10時30分実行のtech_mart用
    """

    EXEC_SCHEDULE = '30 10 1 * *'
    START_DATE_YEAR = 2024
    START_DATE_MONTH = 1
    START_DATE_DAY = 1
    START_DATE_HOUR = 0
    START_DATE_MINITE = 0
    DAG_NAME = '1030AM1stOfEveryMonth'

    SOME_LIST = [
        {'key': 'value'},
    ]


class DagSche0730AM2ndOfEveryMonth:
    """
    毎月2日の07時30分実行のtech_mart用
    """

    EXEC_SCHEDULE = '30 7 2 * *'
    START_DATE_YEAR = 2023
    START_DATE_MONTH = 1
    START_DATE_DAY = 2
    START_DATE_HOUR = 0
    START_DATE_MINITE = 0
    DAG_NAME = '0730AM2ndOfEveryMonth'

    SOME_LIST = [
        {'key': 'value'},
    ]


class DagSche8AM20stOfEveryMonth:
    """
    毎月20日8時実行のtech_mart用
    """

    EXEC_SCHEDULE = '00 8 20 * *'
    START_DATE_YEAR = 2023
    START_DATE_MONTH = 10
    START_DATE_DAY = 20
    START_DATE_HOUR = 0
    START_DATE_MINITE = 0
    DAG_NAME = '8AM20stOfEveryMonth'

    SOME_LIST = [
        {'key': 'value'},
    ]


class DagSche8AM25thOfEveryMonth:
    """
    毎月25日8時実行のtech_mart用
    """

    EXEC_SCHEDULE = '00 8 25 * *'
    START_DATE_YEAR = 2023
    START_DATE_MONTH = 11
    START_DATE_DAY = 25
    START_DATE_HOUR = 0
    START_DATE_MINITE = 0
    DAG_NAME = '8AM25thOfEveryMonth'

    SOME_LIST = [
        {'key': 'value'},
    ]


class DagSche8AMEveryMonday:
    """
    毎週月曜日8時実行のtech_mart用
    """

    EXEC_SCHEDULE = '00 8 * * 1'
    START_DATE_YEAR = 2023
    START_DATE_MONTH = 1
    START_DATE_DAY = 30
    START_DATE_HOUR = 0
    START_DATE_MINITE = 0
    DAG_NAME = '8AMEveryMonday'

    SOME_LIST = [
        {'key': 'value'},
    ]


class DagSche8AMEvery2Monday:
    """
    隔週月曜日8時実行のtech_mart用
    """

    EXEC_SCHEDULE = timedelta(weeks=2)
    START_DATE_YEAR = 2023
    START_DATE_MONTH = 11
    START_DATE_DAY = 20
    START_DATE_HOUR = 8
    START_DATE_MINITE = 0
    DAG_NAME = '8AMEvery2Monday'

    SOME_LIST = [
        {'key': 'value'},
    ]


class DagSche1030AMEveryMonday:
    """
    毎週月曜日10時30分実行のtech_mart用
    """

    EXEC_SCHEDULE = '30 10 * * 1'
    START_DATE_YEAR = 2024
    START_DATE_MONTH = 1
    START_DATE_DAY = 15
    START_DATE_HOUR = 0
    START_DATE_MINITE = 0
    DAG_NAME = '1030AMEveryMonday'

    SOME_LIST = [
        {'key': 'value'},
    ]


class DagSche0730AMEveryTuesday:
    """
    毎週火曜日7時30分実行のtech_mart用
    """

    EXEC_SCHEDULE = '30 8 * * 2'
    START_DATE_YEAR = 2023
    START_DATE_MONTH = 1
    START_DATE_DAY = 31
    START_DATE_HOUR = 0
    START_DATE_MINITE = 0
    DAG_NAME = '0730AMEveryTuesday'

    SOME_LIST = [
        {'key': 'value'},
    ]


class DagSche8AMEveryWednesday:
    """
    毎週水曜日8時実行のtech_mart用
    """

    EXEC_SCHEDULE = '00 8 * * 3'
    START_DATE_YEAR = 2022
    START_DATE_MONTH = 2
    START_DATE_DAY = 1
    START_DATE_HOUR = 0
    START_DATE_MINITE = 0
    DAG_NAME = '8AMEveryWednesday'

    SOME_LIST = [
        {'key': 'value'},
    ]
