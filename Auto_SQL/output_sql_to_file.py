from create_sql import (
    create_php_file,
    create_ddl_sql_file,
    create_add_ddl_sql_file,
    create_merge_sql_files
)


def get_tables_list(lines):
    # tables = [{"tablename": tablename,
    #           "columns":[
    #               {"name": column, "type": type},
    #               {"name": column, "type": type},
    #               ......
    #           ]
    #           }]
    tables = []

    # loop the data
    for line in lines:
        parts = line.strip().split('\t')
        # ensure there are three parts in the data
        if len(parts) == 3:
            tablename, column_name, data_type = parts
            # init the tables dict
            table = {
                "tablename": tablename,
                "columns": []
            }
            # init the columns dict
            column = {
                "name": column_name,
                "type": data_type
            }
            # add column to table
            table["columns"].append(column)
            # check if the table exist if not add
            found = False
            for existing_table in tables:
                if existing_table["tablename"] == tablename:
                    existing_table["columns"].append(column)
                    found = True
                    break
            # add table
            if not found:
                tables.append(table)

    # print out
    # for table in tables:
    #     print(table)
    #     print("----------------------")
    return tables


# steps
# read file
with open('ToolBox/Auto_SQL/data.txt', 'r') as file:
# with open('Auto_SQL/data.txt', 'r') as file:
    lines = file.readlines()

# must give it 3 parameters : tablename columns type

# notice that hashed data will become string.

# 1,application new table data into data.txt
tables = get_tables_list(lines)
# create_php_file(tables, dataset='application_furusatotax')
create_ddl_sql_file(tables, project='tbk-dap-prod', dataset='application_furusatotax')
# create_merge_sql_files(tables, project='tbk-dap-prod', dataset='application_furusatotax')

# 2,contents new table data into data.txt
# tables = get_tables_list(lines)
# create_php_file(tables, dataset='content_furusatotax')
# create_ddl_sql_file(tables, project='tbk-dap-prod', dataset='content_furusatotax')
# create_merge_sql_files(tables, project='tbk-dap-prod', dataset='content_furusatotax')

# 3,application column add
# tables = get_tables_list(lines)
# create_add_ddl_sql_file(tables, project='tbk-dap-prod', dataset='application_furusatotax')

# 4,content column add
# tables = get_tables_list(lines)
# create_add_ddl_sql_file(tables, project='tbk-dap-prod', dataset='content_furusatotax')

# other tasks:
# php list add columns
# php security add levels
# merge sql files add column
