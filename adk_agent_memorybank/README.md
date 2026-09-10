# Google ADK Agent with Memory Bank Integration

This project demonstrates how to build, test, and deploy an AI Agent using the **Google Agent Development Kit (ADK)** integrated with persistent **Memory Bank** capabilities, custom tool calling, and automated CI/CD deployment to **Google Cloud Run**.

---

## 📌 Features

- **Agent Engine & Memory Bank Integration**: Persists user interactions and context across agent sessions using Google ADK's `LoadMemoryTool` and `after_agent_callback`.
- **Custom Tool Integration**: Includes a custom `employee_details` Python function tool to query employee metadata.
- **Gemini 2.5 Model**: Powered by Google's `gemini-2.5-flash`.
- **Local & Cloud Execution**: Test locally using Google ADK CLI or connect to Vertex AI Agent Engine Memory Bank on GCP.
- **Automated CI/CD**: Deploy directly to Google Cloud Run via GitHub Actions with optional Memory Bank runtime URI configuration.

---

## 📁 Project Structure

```text
adk_agent_memorybank/
│
├── agent.py                 # Core ADK Agent definition with memory callbacks and tools
├── create_memory_bank.py    # Python script to provision a Vertex AI Agent Engine Memory Bank
├── Dockerfile               # Production container image configuration for Cloud Run
├── requirements.txt         # Python package dependencies
├── .adk/                    # Local session database (SQLite) created automatically by ADK
└── README.md                # Project documentation & setup instructions
```

---

## ⚙️ Prerequisites & Environment Setup

### 1. Environment Requirements
- **Python**: 3.11 or higher
- **Google Cloud SDK**: Installed and authenticated

### 2. Install Required Dependencies

```bash
pip install google-adk google-genai google-cloud-aiplatform vertexai python-dotenv langsmith
```

### 3. Google Cloud Authentication

Authenticate with your Google Cloud account and set your active project:

```bash
# Login to Google Cloud
gcloud auth application-default login

# Set active GCP project ID
gcloud config set project YOUR_PROJECT_ID
```

---

## 🧠 Creating & Provisioning Agent Memory in Vertex AI Agent Runtime

To persist user memories in Vertex AI Cloud Reasoning Engines, create an Agent Engine Memory Bank resource:

### Step 1: Execute `create_memory_bank.py`

Verify environment variables `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` in your `.env` file, then run:

```bash
python create_memory_bank.py
```

### Step 2: Extract the Memory Service URI

The script returns the created resource name:
```text
Memory Bank created successfully!
Resource name:
projects/1234567890/locations/asia-south1/reasoningEngines/9876543210
```

Prefix the resource name with `agentengine://` to form the full **Memory Service URI**:
```text
agentengine://projects/1234567890/locations/asia-south1/reasoningEngines/9876543210
```

---

## 💻 Running the Agent Locally

### Local Mode (Container / SQLite Memory):
```bash
adk web
```

### Connected to Vertex AI Agent Engine Memory Bank Runtime:
```bash
adk web --memory_service_uri="agentengine://projects/<PROJECT_NUMBER>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>"
```

---

## 🚀 CI/CD Deployment to Google Cloud Run

Deployments are automated via GitHub Actions using the `.github/workflows/deploy-cloud-run.yml` workflow.

### 1. Required GitHub Secrets

Configure the following secrets in your GitHub repository (**Settings > Secrets and variables > Actions**):

| Secret Name | Description |
| :--- | :--- |
| `GCP_SA_KEY` | Service Account JSON Key with Cloud Run Admin & Artifact Registry permissions |
| `GCP_PROJECT_ID` | Your Google Cloud Project ID |
| `GEMINI_API_KEY` | Google Gemini API Key |
| `LANGSMITH_API_KEY` | LangSmith API Key (optional for observability) |

### 2. Required GCP Service Account Permissions

Ensure the Cloud Run default runtime service account has the **Vertex AI User** role (`roles/aiplatform.user`) to communicate with Agent Engine Memory Bank:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

### 3. Triggering CI/CD Workflow

1. Go to your GitHub repository -> **Actions** tab.
2. Select **Deploy ADK Agent to Google Cloud Run**.
3. Click **Run workflow**.
4. Configure dispatch parameters:
   - **Cloud Run Service Name**: `adk-agent-memorybank`
   - **Working Directory**: `adk_agent_memorybank`
   - **Google Cloud Region**: `asia-south1` (or your preferred region)
   - **Memory Service URI**:`agentengine://<ENGINE_ID>` deploy with memory bank
5. Click **Run workflow** to initiate build, image push to Artifact Registry, and Cloud Run deployment.

> 💡 **Note**: If `memory_service_uri` is left blank, the container automatically falls back to local container session storage.

---

## 🧪 Testing Prompts

1. **Tool Invocation Test:**
   - *Prompt:* `"Can you give me details for employee EMP001?"`
   - *Expected Result:* Calls `employee_details("EMP001")` and returns details for John Doe.

2. **Memory Persistence Test:**
   - *Prompt:* `"Remember that my favorite programming language is Python."`
   - *Next Session Prompt:* `"What is my favorite programming language?"`
   - *Expected Result:* Recalls `"Python"` from Memory Bank.

---

## 🛠️ Summary of Commands

| Action | Command |
| :--- | :--- |
| **Authenticate GCP** | `gcloud auth application-default login` |
| **Create Memory Bank** | `python create_memory_bank.py` |
| **Run Local Agent** | `adk web` |
| **Run Agent with Memory Bank** | `adk web --memory_service_uri=agentengine://...` |
