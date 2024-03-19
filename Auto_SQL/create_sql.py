from SQL_format import (
    DDL_SQL_FORMAT,
    MERGE_SQL_FORMAT,
    ADD_SQL_FORMAT,
    PHP_FORMAT
)

# tables = [{"tablename": tablename,
#           "columns":[
#               {"name": column, "type": type},
#               {"name": column, "type": type},
#               ......
#           ]
#           }]


def _format_php(tablename, columns):

    # 'columns': [{'name': 'id', 'type': 'int(10)'}, ]
    formatted_columns = []
    for column in columns:
        column_name = column["name"]
        formatted_columns.append(f"'{column_name}'")

    php_format = PHP_FORMAT.format(
        tablename=tablename,
        columns=','.join(formatted_columns)
    )
    return php_format


def _create_ddl(tablename, columns, project, dataset):

    # 'columns': [{'name': 'id', 'type': 'int(10)'}, ]
    formatted_columns = []
    for column in columns:
        column_name = column["name"]
        data_type = column["type"]

        if 'int' in data_type.lower():
            data_type = 'INT64'
        elif 'var' in data_type.lower():
            data_type = 'STRING'
        elif 'datetime' in data_type.lower():
            data_type = 'DATETIME'
        elif 'text' in data_type.lower():
            data_type = 'STRING'
        else:
            data_type = data_type
        formatted_columns.append(f"{column_name} {data_type}")
    formatted_columns.append("send_date DATE")

    ddl_sql = DDL_SQL_FORMAT.format(
        project=project,
        dataset=dataset,
        tablename=tablename,
        columns=',\n'.join(formatted_columns)
    )
    return ddl_sql


def _create_add_col(tablename, columns, project, dataset):

    # 'columns': [{'name': 'id', 'type': 'int(10)'}, ]
    formatted_columns = []
    formatted_columns.append("* except(created, modified, send_date)")
    for column in columns:
        column_name = column["name"]
        data_type = column["type"]

        if 'int' in data_type.lower():
            data_type = 'integer'
        elif 'var' in data_type.lower():
            data_type = 'string'
        elif 'datetime' in data_type.lower():
            data_type = 'datetime'
        elif 'text' in data_type.lower():
            data_type = 'STRING'
        else:
            data_type = data_type
        formatted_columns.append(f"cast(null as {data_type}) {column_name}")
    formatted_columns.append("created")
    formatted_columns.append("modified")
    formatted_columns.append("send_date")

    ddl_sql = ADD_SQL_FORMAT.format(
        project=project,
        dataset=dataset,
        tablename=tablename,
        columns='\n,'.join(formatted_columns)
    )
    return ddl_sql


def _create_merge_ddl(tablename, columns, project, dataset):

    update_cols = []
    insert_cols = []
    for column in columns:
        column_name = column["name"]
        update_cols.append(f"t.`{column_name}` = tmp.`{column_name}`") 
        insert_cols.append(f"`{column_name}`")
    update_cols.append("t.`send_date` = tmp.`send_date`")
    insert_cols.append("`send_date`")

    merge_sql = MERGE_SQL_FORMAT.format(
        project=project,
        dataset=dataset,
        tablename=tablename,
        update_cols='\n    ,'.join(update_cols),
        insert_cols='\n        ,'.join(insert_cols)
    )
    return merge_sql


def create_php_file(tables, dataset):
    for table in tables:
        tablename = table["tablename"]
        columns = table["columns"]
        php_format = _format_php(tablename=tablename, columns=columns)
        with open(f"{dataset}_list.php", "a") as file:
            file.write(php_format)


def create_ddl_sql_file(tables, project, dataset):
    for table in tables:
        tablename = table["tablename"]
        columns = table["columns"]
        ddl_sql = _create_ddl(tablename=tablename, columns=columns, project=project, dataset=dataset)
        with open(f"{dataset}_ddl.sql", "a") as sql_file:
            sql_file.write(ddl_sql)


def create_add_ddl_sql_file(tables, project, dataset):
    for table in tables:
        tablename = table["tablename"]
        columns = table["columns"]
        ddl_sql = _create_add_col(tablename=tablename, columns=columns, project=project, dataset=dataset)
        with open(f"{dataset}_add_ddl.sql", "a") as sql_file:
            sql_file.write(ddl_sql)


def create_merge_sql_files(tables, project, dataset):
    for table in tables:
        tablename = table["tablename"]
        columns = table["columns"]
        merge_sql = _create_merge_ddl(tablename=tablename, columns=columns, project=project, dataset=dataset)
        with open(f"{tablename}_exec.sql", "w") as sql_file:
            sql_file.write(merge_sql)
