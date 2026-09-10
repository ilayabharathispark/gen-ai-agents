# Google ADK Agent with Memory Bank Integration

This project demonstrates how to build and deploy an AI Agent using the **Google Agent Development Kit (ADK)** integrated with persistent **Memory Bank** capabilities and custom tool calling.

---

## 📌 Features

- **Agent Engine & Memory Bank Integration**: Persists user interactions and context across agent sessions using Google ADK's `PreloadMemoryTool` and `after_agent_callback`.
- **Custom Tool Integration**: Includes a custom `employee_details` Python function tool to query employee metadata.
- **Gemini 2.5 Model**: Powered by Google's `gemini-2.5-flash`.
- **Local & Cloud Execution**: Test locally using Google ADK CLI or provision a Vertex AI Agent Engine Memory Bank on GCP.

---

## 📁 Project Structure

```text
adk_agent_memorybank/
│
├── agent.py                 # Core ADK Agent definition with memory callbacks and tools
├── create_memeory_bank.py   # Python script to provision a Vertex AI Agent Engine Memory Bank
├── .adk/                    # Local session database (SQLite) created automatically by ADK
└── README.md                # Project documentation & instructions
```

---

## ⚙️ Prerequisites & Setup

### 1. Environment Requirements
- **Python**: 3.10 or higher
- **Google Cloud SDK**: Installed and authenticated

### 2. Install Required Dependencies

```bash
pip install google-adk google-genai google-cloud-aiplatform vertexai
```

### 3. Google Cloud Authentication

Authenticate with your Google Cloud account and set your active project:

```bash
# Login to Google Cloud
gcloud auth application-default login

# Set your active GCP project ID
gcloud config set project YOUR_PROJECT_ID
```

---

## 🚀 Step-by-Step Guide

### Step 1: Provision Vertex AI Memory Bank (Optional for Cloud Memory)

Edit `create_memeory_bank.py` and replace `YOUR_PROJECT_ID` with your Google Cloud project ID:

```python
PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
```

Run the script to create the Agent Engine Memory Bank resource on GCP:

```bash
python create_memeory_bank.py
```

*Output:*
```text
Memory Bank created
projects/<PROJECT_NUMBER>/locations/us-central1/reasoningEngines/<ENGINE_ID>
```

---

### Step 2: Code Walkthrough (`agent.py`)

`agent.py` configures the root agent with tools and automatic event persistence:

1. **Memory Callback (`after_agent_callback`)**: Automatically saves conversation events to memory after every agent interaction:
   ```python
   async def after_agent_callback(callback_context):
       events = callback_context.session.events
       if events:
           await callback_context.add_events_to_memory(events=events)
   ```

2. **Custom Tool (`employee_details`)**: Fetches structured metadata for employee IDs (`EMP001`, `EMP002`):
   ```python
   def employee_details(employee_id: str) -> dict:
       ...
   ```

3. **Agent Registration (`root_agent`)**:
   ```python
   root_agent = Agent(
       name="memory_demo_agent_1",
       model="gemini-2.5-flash",
       instruction="...",
       tools=[PreloadMemoryTool(), employee_details],
       after_agent_callback=after_agent_callback,
   )
   ```

---

### Step 3: Run the Agent Locally

#### Web UI Mode:
```bash
adk web --memory_service_uri=agentengine://<engine_id>
```
*This launches a local web browser interface to chat with the agent and view session state.*

---

## 🧪 Testing Prompts

Try the following interactions to test both tool execution and persistent memory:

1. **Tool Invocation Test:**
   - *Prompt:* `"Can you give me details for employee EMP001?"`
   - *Expected Result:* Calls `employee_details("EMP001")` and returns details for John Doe (Senior Data Engineer).

2. **Memory Persistence Test:**
   - *Prompt:* `"Remember that my favorite programming language is Python."`
   - *Next Session Prompt:* `"What is my favorite programming language?"`
   - *Expected Result:* Uses memory to recall `"Python"`.

---

## 🛠️ Summary of Commands

| Action | Command |
| :--- | :--- |
| **Authenticate GCP** | `gcloud auth application-default login` |
| **Install Dependencies** | `pip install google-adk vertexai google-genai` |
| **Create Memory Bank** | `python create_memeory_bank.py` |
| **Run Agent via Web UI** | `adk web --memory_service_uri=agentengine://<engine_id>` |
