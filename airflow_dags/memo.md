## memo sheet

- .airflowignore can be set to ignore file in /dags to stop the dag
- over write parameters
scheduler
parsing_processes
6
dag_dir_list_interval
30
core
max_active_tasks_per_dag
20
parallelism
36
min_serialized_dag_update_interval
30
non_pooled_task_slot_count
36
dag_file_processor_timeout
150
default_timezone
Asia/Tokyo
max_active_runs_per_dag
100
webserver
default_ui_timezone
Asia/Tokyo
这些参数是 Airflow 的配置参数，用于配置 Airflow 的各种行为和性能。下面是对每个参数的解释：
1. **scheduler**：指定要使用的调度器，用于安排任务的执行。例如，可以选择使用 `CeleryScheduler` 或 `SequentialScheduler`。
2. **parsing_processes**：用于指定解析 DAG 文件的进程数量。增加此参数可以加快 DAG 文件的解析速度。
3. **dag_dir_list_interval**：指定监视 DAG 文件目录的间隔时间，以秒为单位。在这个时间间隔内，Airflow 将定期检查 DAG 文件目录以查找新的或更新的 DAG 文件。
4. **core.max_active_tasks_per_dag**：每个 DAG 可以同时运行的最大活动任务数。
5. **parallelism**：指定 Airflow 进程的最大并行度。这决定了 Airflow 可以同时执行的任务数量。
6. **min_serialized_dag_update_interval**：指定更新序列化 DAG 对象的最小间隔时间，以秒为单位。
7. **non_pooled_task_slot_count**：非池化任务的槽位数，用于控制非池化任务的并行度。
8. **dag_file_processor_timeout**：用于设置 DAG 文件处理器的超时时间，以秒为单位。如果 DAG 文件处理时间超过此时间，则会超时。
9. **default_timezone**：默认的时区设置，用于解析时间戳和日期。
10. **max_active_runs_per_dag**：每个 DAG 可以同时运行的最大活动运行数。
11. **webserver.default_ui_timezone**：Web 服务器的默认 UI 时区设置，用于显示用户界面的时间戳和日期。
这些参数是在 Airflow 的配置文件中进行设置的，通过设置这些参数，可以对 Airflow 的行为和性能进行调优和配置。

- site:
dags:
https://cloud.google.com/composer/docs/composer-2/write-dags?hl=zh-cn
blocked config override:
https://cloud.google.com/composer/docs/concepts/airflow-configurations?hl=zh-cn


