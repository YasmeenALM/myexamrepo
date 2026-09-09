#!/usr/bin/env bash
set -euo pipefail

if [ -z "${PROJECT:-}" ]; then
  echo "Usage: PROJECT=your-gcp-project [TAG=ver] ./scripts/build_and_push.sh"
  exit 1
fi

TAG=${TAG:-latest}

echo "Building and pushing backend image..."
gcloud builds submit --tag gcr.io/${PROJECT}/backend:${TAG} ./backend

echo "Building and pushing frontend image..."
gcloud builds submit --tag gcr.io/${PROJECT}/frontend:${TAG} ./frontend

echo "Images pushed: gcr.io/${PROJECT}/backend:${TAG} and gcr.io/${PROJECT}/frontend:${TAG}"
