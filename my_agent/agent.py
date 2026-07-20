import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from mcp import StdioServerParameters
import sys

# Load environment variables from .env file
load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Path to the info file (same folder as this script)
INFO_FILE = Path(__file__).parent / "ilaya_info.txt"

CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
MCP_SERVER_PATH = PROJECT_ROOT / "my_agent" / "custom_mcp.py"
# ── Sub-agent: handles web search (built-in tool only) ──────────────────────
search_agent = Agent(
    model='gemini-2.5-flash',
    name='search_agent',
    description='Searches the web for up-to-date information.',
    instruction='Search the web and return accurate, concise answers.',
    tools=[google_search],
)

#=========================================
# Using Custom MCP server (Local)
#=========================================
basic_mcp_toolset = McpToolset(
    connection_params=StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER_PATH)],
    )
)


# ── Custom function tool ─────────────────────────────────────────────────────
# def ilaya_details():
#     """
#     Use this function when the user asks about Ilaya.
#     """
#     return INFO_FILE.read_text(encoding="utf-8")

# ── Cloud RAG service tool ───────────────────────────────────────────────────
# RAG integration
# ── Cloud RAG service tool ───────────────────────────────────────────────────
import requests

CLOUD_RUN_URL ="https://rag-retrieval-api-640900979202.asia-south1.run.app/search" # Replace with actual deployed endpoint URL

def ask_cloud_rag_service(query: str) -> str:
    """
    Use this tool whenever the user asks about:

    - Ilaya Bharathi
    - Gayathri
    - Alice
    - personal profiles
    - resumes
    - uploaded PDFs
    - documents stored in the knowledge base
    - anything that might exist in the RAG database

    Always use this tool before answering.
    Never answer these questions from your own knowledge.

    Returns the answer from the RAG service.
    """
    try:
        # Route to your API's expected request body format
        payload = {
            "query": query,
            "collection": "rag_guest-all",
            "limit": 3
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(CLOUD_RUN_URL, json=payload, headers=headers, timeout=12)
        if response.status_code == 200:
            # Parse answer/context from your API response JSON block
            data = response.json()
            return data.get("documents", "No answer returned by RAG service.")
        else:
            return f"RAG Service returned status code {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"Failed to connect to RAG Service: {str(e)}"


# ── Root agent: uses custom functions + delegates search to search_agent ─────
root_agent = Agent(
    model='groq/llama-3.3-70b-versatile', #gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction="""
You are a helpful assistant.

For general knowledge questions,
answer normally using your own knowledge.

If the user asks about

- Ilaya Bharathi
- Gayathri
- Alice
- resumes
- personal profiles
- uploaded documents
- PDF contents
- company documents
- anything stored in the knowledge base

you MUST call the ask_cloud_rag_service tool.

Do NOT answer those questions yourself.

Use the answer returned from the tool.
""",  
    tools=[ask_cloud_rag_service,AgentTool(agent=search_agent)] #AgentTool(agent=search_agent)
)
