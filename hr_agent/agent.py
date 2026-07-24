import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.adk.tools.mcp_tool import McpToolset
from mcp import StdioServerParameters

# Load environment variables from .env file
load_dotenv()

# Determine paths dynamically relative to this file
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
BQ_SERVER_PATH = PROJECT_ROOT / "my_mcp" / "bq_mcp_server.py"

#Configure McpToolset pointing to the custom BigQuery FastMCP server
#Under the hood, this launches bq_mcp_server.py using the active python interpreter

#=========================================
# Using Custom MCP server (Local)
#=========================================
# bq_toolset = McpToolset(
#     connection_params=StdioServerParameters(
#         command=sys.executable,
#         args=[str(BQ_SERVER_PATH)],
#     )
# )

#=========================================
# Using Google's MCP server (Google Cloud Console)
#=========================================
bigquery_toolset = McpToolset(
    connection_params=StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@toolbox-sdk/server",
            "--prebuilt",
            "bigquery",
            "--stdio",
        ],
        env={
            "BIGQUERY_PROJECT": "ilaya-bharathi-murugan",
            "GOOGLE_APPLICATION_CREDENTIALS": r"C:\\Users\\ILAYA BHARATHI M\\Downloads\\ilaya-bharathi-murugan-e7fa05858bec.json",
        },
    )
)

# Root agent configuration
root_agent = Agent(
    model="gemini-2.5-flash", #gemini-2.5-flash is recoommended for GCP tool calls
    name='salary_agent',
    description='An agent specialized in querying employee salary information and statistics from Google BigQuery.',
    instruction=(
        "You are a salary agent. "
        "Use the tools provided in your toolset (from the BigQuery server) "
        "to query employee details, department statistics, and salary ranges. "
        "Always format monetary values nicely (e.g., $50,000.00)."
    ),
    tools=[bigquery_toolset]  # bq_toolset
)
