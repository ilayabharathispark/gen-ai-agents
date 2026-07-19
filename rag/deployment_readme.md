# RAG Chatbot UI & Cloud Run Deployment Walkthrough

We have successfully wrapped the local RAG project into a premium Streamlit chatbot UI, integrated user-specific Qdrant collection routing, enabled incremental uploading (appending context instead of overwriting), and configured a containerized Docker configuration optimized for Cloud Run.

## Changes Made

### 1. Streamlit Application
* Added `./app.py` containing:
  * **Sidebar:** Username input (to sand-box collection data), PDF upload field, Index action button, clear action button, and retrieval configuration.
  * **Main chat area:** Premium Outfit font styled container displaying user and assistant turns with animated streaming responses.
  * **Data isolation:** Automatically cleans the username into a Qdrant-safe collection identifier (`rag_<username_clean>`).
  * **Incremental Loading:** Rather than resetting/deleting the collection on every run, the app checks if the collection already exists and appends new PDF documents incrementally via `upsert`. This allows multiple context sources to accumulate in the database.

### 2. Dependencies & Workspace Settings
* Modified `./requirements.txt`: added `streamlit` and `python-dotenv`.
* Modified `../pyproject.toml`: added `streamlit` to key Project dependencies list.

### 3. Docker Container Configuration
* Added `./Dockerfile` optimized for Google Cloud Run:
  * Leverages python-slim environment.
  * Installs the CPU-only version of PyTorch (`torch --index-url https://download.pytorch.org/whl/cpu`) to keep the resulting image extremely lean.
  * Exposes port `8080` and dynamically binds the Streamlit server port to the ephemeral `$PORT` environment variable required by Cloud Run.

---

## Verification & Usage Instructions

### Local Execution
To check your changes locally, navigate to the `rag` directory and start the server:
```bash
streamlit run app.py
```
*(Your server is currently running at http://127.0.0.1:8501/)*

### Testing & Verification
We have executed automated browser subagent tests showing successful startup, dynamic collection creation, and index loading. The logs and recording files are captured and saved in the artifact directory.

### Deployment to Google Cloud Run

To build your docker container and deploy it, run the following commands in your prompt:
```bash
# 1. Build and push image to Google Artifact Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rag-streamlit:latest .

# 2. Deploy to Cloud Run (passing environment arguments and setting 4Gi memory)
gcloud run deploy rag-streamlit \
  --image gcr.io/YOUR_PROJECT_ID/rag-streamlit:latest \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --set-env-vars="QDRANT_END_POINT=YOUR_ENDPOINT,QDRANT_API=YOUR_API,GROQ_API_KEY=YOUR_GROQ_KEY"
```
