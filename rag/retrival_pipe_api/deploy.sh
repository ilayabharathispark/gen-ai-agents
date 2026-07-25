#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================================="
echo "🚀 Deployment: submitting build to Cloud Build..."
echo "=========================================================="
gcloud builds submit --tag asia-south1-docker.pkg.dev/ilaya-bharathi-murugan/agent/rag-retrieval-api:v1

echo "=========================================================="
echo "☸️ Deployment: deploying to Cloud Run (rag-retrieval-api)..."
echo "=========================================================="
gcloud run deploy rag-retrieval-api \
  --image asia-south1-docker.pkg.dev/ilaya-bharathi-murugan/agent/rag-retrieval-api:v1 \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --set-env-vars QDRANT_END_POINT="<get it from .env local>",\
QDRANT_API="<get it from .env local>"

echo "=========================================================="
echo "✅ Deployment completed successfully!"
echo "=========================================================="
