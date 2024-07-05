## 通过CloudRun部署数据处理的简单测试

官方链接为Cloud Run中，使用Eventarc驱动Run的端点的部分，当GCS中更新了文件，则驱动Run部署容器，进行处理。

数据处理逻辑是将收到的event中的file path中的数据文件进行Bigquery数据库load的简单处理。

## 非常好的地方

- CloudRun集成了通过Github进行自动CICD部署的选项，不需要自己进行复杂的CICD部署，当设置的Github的路径中更新了Dockerfile等内容，则会自动进行build和deply镜像，在[图中](deploy_by_cloudrun.png)可以看到是Run的部署，在Github中也可以显示
- 通过Run主动选择连接到Github仓库，然后选择安全认证，可以自动进行认证，比一般的无需认证的方式相比，更加安全
- 之前Run支持的region还很少，但是现在也支持更多的region，比如自己所在的东京
