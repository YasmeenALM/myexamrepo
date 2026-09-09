This document outlines quick steps to deploy the project to Google Kubernetes Engine (GKE).

Prerequisites
- Install and configure the Google Cloud SDK (`gcloud`) and `kubectl`.
- Enable the Container API: `gcloud services enable container.googleapis.com`
- Authenticate and set project/zone: `gcloud auth login` then `gcloud config set project YOUR_PROJECT`

Build & push images (Cloud Build)

```bash
PROJECT=your-gcp-project TAG=latest ./scripts/build_and_push.sh
```

Create cluster

```bash
gcloud container clusters create exam-cluster --zone=us-central1-c --num-nodes=2 --machine-type=e2-medium
gcloud container clusters get-credentials exam-cluster --zone=us-central1-c --project $PROJECT
```

Create secrets (replace values)

```bash
kubectl create namespace exam-app
kubectl create secret generic backend-secrets -n exam-app \
  --from-literal=DATABASE_URL="mysql+pymysql://<DB_USER>:<DB_PASS>@127.0.0.1:3306/<DB_NAME>" \
  --from-literal=SECRET_KEY="change-me"

Using the Cloud SQL Auth Proxy sidecar (recommended)

1) Create a service account with the Cloud SQL Client role and download the JSON key.
2) Create a Kubernetes secret containing the JSON key:

```bash
kubectl create secret generic cloudsql-instance-credentials \
  --from-file=credentials.json=/path/to/key.json -n exam-app
```

3) Create `backend-secrets` with a DATABASE_URL that points to the proxy localhost port (proxy exposes the instance on 127.0.0.1:3306 inside the pod):

```bash
kubectl create secret generic backend-secrets -n exam-app \
  --from-literal=DATABASE_URL="mysql+pymysql://<DB_USER>:<DB_PASS>@127.0.0.1:3306/<DB_NAME>" \
  --from-literal=SECRET_KEY="very-secret-value"
```

Example using your Cloud SQL public IP (quick, less secure — not recommended):

```bash
kubectl create secret generic backend-secrets -n exam-app \
  --from-literal=DATABASE_URL="mysql+pymysql://admin:YourPassword@136.65.135.23:3306/examdb" \
  --from-literal=SECRET_KEY="very-secret-value"
```
```

Deploy manifests

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend-deployment.yaml -n exam-app
kubectl apply -f k8s/frontend-deployment.yaml -n exam-app
kubectl apply -f k8s/ingress.yaml -n exam-app
```

Verify

```bash
kubectl get pods -n exam-app
kubectl get svc -n exam-app
kubectl get ingress -n exam-app
```

Notes
- Replace `your-gcp-project` with your GCP project ID.
- If you prefer Artifact Registry, adjust the image paths accordingly.
- Configure DNS to point to the ingress IP if you want a custom domain.
