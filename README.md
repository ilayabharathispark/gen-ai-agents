# 🤖 My AI Agents — Google ADK Setup Guide

A step-by-step guide to set up, configure, and run an AI agent using **Google Agent Development Kit (ADK)** with the Groq model, Google Search tool, and a custom web UI.

---

## 📋 Prerequisites

Before you begin, make sure you have the following installed:

| Requirement | Version | Check Command |
|---|---|---|
| Python | ≥ 3.12 | `python --version` |
| pip | Latest | `pip --version` |
| Git | Any | `git --version` |

You will also need a **Groq API Key** from [Groq Console](https://console.groq.com/keys).

---

## 🚀 Step 1 — Clone or Create the Project

```bash
# Create a new project folder
mkdir my-ai-agents
cd my-ai-agents

# OR clone an existing repo
git clone <your-repo-url>
cd my-ai-agents
```

---

## 🐍 Step 2 — Create a Virtual Environment

A virtual environment keeps your dependencies isolated from other Python projects.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate it (Windows CMD)
.venv\Scripts\activate.bat

# Activate it (macOS / Linux)
source .venv/bin/activate
```

> ✅ Your terminal prompt should now show `(.venv)` indicating the environment is active.

---

## 📦 Step 3 — Install Dependencies

Install the Google ADK package and `python-dotenv` for environment variable management.

```bash
pip install google-adk python-dotenv
```

Verify the installation:

```bash
adk --version
```

---

## 🔑 Step 4 — Configure Your Groq API Key

Create a `.env` file in the project root to store your API key securely.

```bash
# In the project root (my-ai-agents/)
touch .env       # macOS / Linux
# OR on Windows, just create the file manually
```

Add the following to `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ **Never commit your `.env` file to Git.** Make sure `.env` is listed in your `.gitignore`.

```gitignore
# .gitignore
.env
.venv/
__pycache__/
```

---

## 🗂️ Step 5 — Project Structure

After setup, your project should look like this:

```
my-ai-agents/
├── .env                  ← Your API keys (never commit this)
├── .gitignore
├── .python-version       ← Python version pin
├── .venv/                ← Virtual environment
├── main.py               ← Entry point (optional)
├── pyproject.toml        ← Project metadata
└── my_agent/
    ├── __init__.py       ← Makes it a Python package (if needed)
    ├── ilaya_info.txt    ← Custom knowledge file
    └── agent.py          ← Your agent definition
```

---

## 🧠 Step 6 — Create the Agent

Create `my_agent/agent.py` with the following content:

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Path to the info file (same folder as this script)
INFO_FILE = Path(__file__).parent / "ilaya_info.txt"


# ── Sub-agent: handles web search (built-in tool only) ──────────────────────
search_agent = Agent(
    model='groq/llama-3.3-70b-versatile',
    name='search_agent',
    description='Searches the web for up-to-date information.',
    instruction='Search the web and return accurate, concise answers.',
    tools=[google_search],
)


# ── Custom function tool ─────────────────────────────────────────────────────
def ilaya_details():
    """
    Use this function when the user asks about Ilaya.
    """
    return INFO_FILE.read_text(encoding="utf-8")


# ── Root agent: uses custom functions + delegates search to search_agent ─────
root_agent = Agent(
    model='groq/llama-3.3-70b-versatile',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=(
        "You are a helpful assistant. "
        "Use your own training knowledge to answer general questions about people, places, events, science, sports, etc. "
        "ONLY call the 'ilaya_details' tool when the user specifically asks about a person named Ilaya."
    ),
    tools=[ilaya_details] #AgentTool(agent=search_agent)
)
```

### 🔧 Key Components Explained

| Component | Purpose |
|---|---|
| `load_dotenv()` | Loads `GROQ_API_KEY` from your `.env` file |
| `ilaya_details()` | Custom tool — reads and returns information from `ilaya_info.txt` |
| `Agent(model=...)` | Defines the LLM model to use (`groq/llama-3.3-70b-versatile`) |
| `tools=[...]` | Registers tools the agent can use |

---

## 🌐 Step 7 — Run the ADK Web UI

ADK provides a built-in web interface to interact with your agent.

```bash
# Make sure you are in the project root (my-ai-agents/)
adk web my_agent
```

You should see output like:

```
INFO: Uvicorn running on http://localhost:8000
```

Open your browser and go to: **[http://localhost:8000](http://localhost:8000)**

> ⚠️ **Windows Note:** The `--reload` flag is not supported on Windows due to event loop limitations. Simply run `adk web my_agent` without it.

---

## 💬 Step 8 — Test Your Agent

Once the web UI is open, try asking:

| Prompt | Expected Behaviour |
|---|---|
| `"Who is Ilaya?"` | Calls `ilaya_details()` custom tool |
| `"What is the latest news on AI?"` | Uses `google_search` to fetch live results |
| `"What is 2 + 2?"` | Answers directly from the model |

---

## 🛠️ Adding More Tools

To add a new custom tool, define a Python function with a clear docstring and add it to the `tools` list:

```python
def my_custom_tool():
    """
    Describe when the agent should use this tool.
    """
    return "result from tool"

root_agent = Agent(
    ...
    tools=[ilaya_details, my_custom_tool],
)
```

> 📝 The **docstring** is critical — the agent uses it to decide when to call the tool.

---

## 🔄 Restarting the Server

After any changes to `agent.py`, restart the ADK web server:

```bash
# Stop the server
Ctrl + C

# Start it again
adk web my_agent
```

---

## 📚 Useful Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Groq Console (Get API Key)](https://console.groq.com/keys)
- [Groq Supported Models Docs](https://console.groq.com/docs/models)
- [python-dotenv Docs](https://pypi.org/project/python-dotenv/)

---

## 🧹 Deactivating the Virtual Environment

When you're done working:

```bash
deactivate
```
