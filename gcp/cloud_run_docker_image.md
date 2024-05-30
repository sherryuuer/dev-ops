## Host docker on Cloud Run

- Enable artifact registry api

`gcloud services enable artifactregistry.googleapis.com`

- Log in

`gcloud auth login`

- Update gcloud

`gcloud components update`

- Create a repository

```bash
gcloud artifacts repositories create video-processing-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker repository for video processing service"
```

- Build Image

`docker build -t us-central1-docker.pkg.dev/<PROJECT_ID>/video-processing-repo/video-processing-service .`

- Configure Docker to use gcloud as the credential helper

`gcloud auth configure-docker us-central1-docker.pkg.dev`

- Push image to gcloud registry

`docker push us-central1-docker.pkg.dev/<PROJECT_ID>/video-processing-repo/video-processing-service`

- Deploy to CouldRun

```bash
# Enable cloud run
gcloud services enable run.googleapis.com

# Deploy container to cloud run
gcloud run deploy video-processing-service --image us-central1-docker.pkg.dev/PROJECT_ID/video-processing-repo/video-processing-service \
  --region=us-central1 \
  --platform managed \
  --timeout=3600 \
  --memory=2Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --ingress=internal
```

by set the ingress as internal so the Pub/Sub service can invoke it.
