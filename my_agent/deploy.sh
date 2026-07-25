#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================================="
echo "🚀 Deployment: submitting build to Cloud Build..."
echo "=========================================================="
gcloud builds submit --tag asia-south1-docker.pkg.dev/ilaya-bharathi-murugan/agent/my-agent:v1

echo "=========================================================="
echo "☸️ Deployment: deploying to Cloud Run (my-agent)..."
echo "=========================================================="
gcloud run deploy my-agent \
  --image asia-south1-docker.pkg.dev/ilaya-bharathi-murugan/agent/my-agent:v1 \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="<get it from .env local>",\
LANGSMITH_API_KEY="<get it from .env local>",\
LANGSMITH_PROJECT="my-agent",\
LANGSMITH_TRACING=true,\
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

echo "=========================================================="
echo "✅ Deployment completed successfully!"
echo "=========================================================="
