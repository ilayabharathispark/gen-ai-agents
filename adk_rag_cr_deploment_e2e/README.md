# my_agent — Google ADK Agent with Web UI & Cloud Run Setup

This folder contains the `my_agent` application, a serverless agent deployment powered by **Google Agent Development Kit (ADK)** and the **Groq Llama 3.3 model**. It includes a Web UI wrapper built with FastAPI.

---

## 📂 File Structure

*   `agent.py`: Defines the root agent (`root_agent`) delegating search queries to `search_agent` utilizing Groq’s Llama-3.3-70b-versatile model.
*   `main.py`: The entrypoint starting the FastAPI application with ADK's web interface enabled.
*   `ilaya_info.txt`: Text database containing knowledge for the custom function tool.
*   `requirements.txt`: Python package requirements.
*   `Dockerfile`: Directs GCP on compiling and runtime service parameters.

---

## 🚀 Running Locally

1.  **Activate virtual environment & set API Key**:
    ```bash
    # Set your key in your environment or .env file
    GROQ_API_KEY=your_groq_api_key
    ```
2.  **Start the FastAPI App manually**:
    ```bash
    python main.py
    ```
    OR run via Uvicorn directly:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8080
    ```
3.  **Access the Web Interface**:
    Open the server index at `http://localhost:8080` in your web browser.

---

## ☁️ Google Cloud Run Deployment

To deploy this agent package directly to Cloud Run:

### 1. Build and Submit Container Image
Run the Google Cloud Build submit trigger:
```bash
gcloud builds submit \
--tag asia-south1-docker.pkg.dev/<PROJECT_ID>/<REPOS_NAME>/cloudrun-test:v1
```

### 2. Deploy to Cloud Run
Run the deploy command with external/public availability:
```bash
gcloud run deploy cloudrun-test \
    --image asia-south1-docker.pkg.dev/<PROJECT_ID>/<REPOS_NAME>/cloudrun-test:v1 \
    --platform managed \
    --region asia-south1 \
    --allow-unauthenticated \
    --set-env-vars GROQ_API_KEY=<YOUR_GROQ_API_KEY>
```
