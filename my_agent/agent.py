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
# search_agent = Agent(
#     model='gemini-2.5-flash',
#     name='search_agent',
#     description='Searches the web for up-to-date information.',
#     instruction='Search the web and return accurate, concise answers.',
#     tools=[google_search],
# )

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
def ilaya_details():
    """
    Use this function when the user asks about Ilaya.
    """
    return INFO_FILE.read_text(encoding="utf-8")


# ── Root agent: uses custom functions + delegates search to search_agent ─────
root_agent = Agent(
    model='groq/meta-llama/llama-4-scout-17b-16e-instruct', #gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=(
        "You are a helpful assistant. "
        "Use your own training knowledge to answer general questions about people, places, events, science, sports, etc. "
        "ONLY call the 'ilaya_details' tool when the user specifically asks about a person named Ilaya."
        "you have custome MCP server access, when user asks choose wisely to use the tools"
    ),  
    tools=[ilaya_details,basic_mcp_toolset] #AgentTool(agent=search_agent)
)
