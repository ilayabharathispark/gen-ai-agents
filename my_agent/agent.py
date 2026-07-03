import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

# Load environment variables from .env file
load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
