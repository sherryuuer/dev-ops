DDL_SQL_FORMAT = """
CREATE OR REPLACE TABLE `{project}.{dataset}.{tablename}_c`
(
{columns}
)
PARTITION BY DATETIME_TRUNC(created, DAY);

"""

MERGE_SQL_FORMAT = """merge `{project}.{dataset}.{tablename}_{{ab_side}}` t
using `{project}.{dataset}.{tablename}_tmp` tmp
on
    t.`id` = tmp.`id`
when matched then
update set
    {update_cols}
when not matched then
insert values
    (
        {insert_cols}
    )
;
"""

ADD_SQL_FORMAT = """
create or replace table `{project}.{dataset}.{tablename}_c` partition by DATETIME_TRUNC(created, DAY)
as select 
{columns}
from `tbk-dap-prod.{dataset}.{tablename}_a`;

"""

PHP_FORMAT = """
            '{tablename}'
                => [
                    'type' => SYNC_TYPE_TRANSACTION,
                    'columns' => [
                        {columns}
                    ],
                    'masks' => [
                    ]
                ],
"""
