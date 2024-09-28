## k8s app pj history

- build image: `docker build -t image_name .`, and you wait
- list up images: `docker images`
- tag the image: `docker tag image_name sherryuuer/testrepo`
- login to my docker hub: `docker login -u sherryuuer -p my-password`
- docker push: `docker push sherryuuer/testrepo`, and you wait

- Verify the Cluster: `kubectl get nodes`

- create the pods.yaml file

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kubernetes-pod
  labels:
    project: kubernetes-project
spec:
  containers:
    - name: kubernetes-pod
      image: sherryuuer/testrepo:latest  # Use the image name from Docker Hub 而不是本地创建的名字
      ports:
        - containerPort: 31111
```

- `kubectl apply -f pods.yaml` this will make pod/kubernetes-pod created
- `kubectl get pods` will get the pods we created list up
  ```
  root@ed8602849:/usercode# kubectl get pods
  NAME             READY   STATUS    RESTARTS   AGE
  kubernetes-pod   1/1     Running   1          11m
  ```
- Create a Deployment : deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubernetes-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      project: kubernetes-project
  template:
    metadata:
      labels:
        project: kubernetes-project
    spec:
      containers:
      - name: kubernetes-pod
        imagePullPolicy: Always
        ports:
        - containerPort: 31111
        image: sherryuuer/testrepo:latest
```

- create a Deployment, and then verify it:
  - `kubectl apply -f deployment.yaml`
  - `kubectl get deployments`
    ```
    root@ed8602849:/usercode# kubectl get deployments
    NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
    kubernetes-deployment   2/2     2            2           21s
    ```

- create a Service. We can do that in the service.yaml file
```yaml
apiVersion: v1
kind: Service
metadata:
  name: kubernetes-svc
spec:
  type: NodePort
  ports:
  - port: 31111
    protocol: TCP
    targetPort: 3000
    nodePort: 31111
  selector:
    project: kubernetes-project
```

- create a service:
  - `kubectl apply -f service.yaml`
  - `kubectl get service`
    ```
    root@ed8602849:/usercode# kubectl get service
    NAME             TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)           AGE
    kubernetes       ClusterIP   10.96.0.1      <none>        443/TCP           46m
    kubernetes-svc   NodePort    10.96.134.58   <none>        31111:31111/TCP   33s
    ```

- port-forward the service: `kubectl port-forward svc/kubernetes-svc 31111:31111 --address 0.0.0.0`
  ```
  root@ed8602849:/usercode# kubectl port-forward svc/kubernetes-svc 31111:31111 --address 0.0.0.0
  Forwarding from 0.0.0.0:31111 -> 3000
  Handling connection for 31111
  ```

## include

发布应用到 Kubernetes 的流程可以分为几个主要步骤。下面是整个流程的梳理，包括所需工具、代码示例、注意事项和扩展方式。

### 1. 准备工作

#### 工具
- **Docker**: 用于构建和管理容器镜像。
- **Kubernetes**: 用于管理容器化应用的开源平台。
- **kubectl**: Kubernetes 的命令行工具，用于与 Kubernetes API 交互。
- **Docker Hub 或其他容器注册中心**: 存储和分发容器镜像的地方。

### 2. 构建 Docker 镜像

#### 代码示例
- **Dockerfile**:
```dockerfile
# 使用官方的基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY . .

# 安装依赖
RUN pip install -r requirements.txt

# 启动应用
CMD ["python", "app.py"]
```

#### 构建镜像
```bash
docker build -t your-username/your-image-name:tag .
```

### 3. 推送镜像到容器注册中心

#### 登录 Docker Hub
```bash
docker login -u your-username -p your-password
```

#### 推送镜像
```bash
docker push your-username/your-image-name:tag
```

### 4. 创建 Kubernetes 配置文件

#### Pod 示例
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: your-pod-name
  labels:
    app: your-app-name
spec:
  containers:
    - name: your-container-name
      image: your-username/your-image-name:tag
      ports:
        - containerPort: 80
```

#### Deployment 示例
使用 Deployment 以便于管理 Pod 的副本和更新。
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: your-deployment-name
spec:
  replicas: 3
  selector:
    matchLabels:
      app: your-app-name
  template:
    metadata:
      labels:
        app: your-app-name
    spec:
      containers:
        - name: your-container-name
          image: your-username/your-image-name:tag
          ports:
            - containerPort: 80
```

### 5. 部署应用到 Kubernetes

#### 应用配置
```bash
kubectl apply -f deployment.yaml
```

#### 验证部署
```bash
kubectl get pods
kubectl get deployments
```

### 6. 暴露应用

#### 创建服务
为了让外部可以访问到应用，需要创建一个 Service：
```yaml
apiVersion: v1
kind: Service
metadata:
  name: your-service-name
spec:
  type: LoadBalancer  # 或 ClusterIP, NodePort 根据需求选择
  selector:
    app: your-app-name
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

#### 部署服务
```bash
kubectl apply -f service.yaml
```

### 7. 注意事项

- **命名空间**: 在 Kubernetes 中使用命名空间来隔离资源。
- **资源限制**: 为容器设置 CPU 和内存的请求和限制，确保资源的合理使用。
- **健康检查**: 配置 liveness 和 readiness 探针以监控应用的健康状态。
- **日志管理**: 考虑使用集中化的日志管理工具（如 ELK Stack）来收集和分析日志。

### 8. 扩展方式

- **水平扩展**: 使用 `kubectl scale deployment your-deployment-name --replicas=n` 来水平扩展 Pod 的副本数量。
- **滚动更新**: 通过更新 Deployment 配置文件并应用来实现无缝更新。
- **监控和告警**: 集成 Prometheus 和 Grafana 来监控集群和应用的性能。
- **自动化**: 使用 CI/CD 工具（如 Jenkins, GitHub Actions）实现自动构建和部署。
