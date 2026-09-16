import logging
import os

from dotenv import load_dotenv

load_dotenv()

# Explicitly import vertexai and its types submodule so vertexai.types is populated
import vertexai
try:
    import vertexai.types
except ImportError:
    pass

from langsmith.integrations.google_adk import configure_google_adk

configure_google_adk(project_name=os.getenv("LANGSMITH_PROJECT"))

from google.adk.agents import Agent
from google.adk.tools.load_memory_tool import LoadMemoryTool

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# After the agent replies -> Save to Memory Bank
# ─────────────────────────────────────────────
async def after_agent_callback(callback_context):
    """
    Runs after the agent produces its response.
    Persists the session interaction to Vertex AI Memory Bank.
    """
    session_id = str(callback_context.session.id)
    events = callback_context.session.events

    if not events:
        return

    try:
        logger.info("Persisting session %s to Vertex AI Memory Bank...", session_id)
        if hasattr(callback_context, "add_session_to_memory"):
            await callback_context.add_session_to_memory()
        else:
            await callback_context.add_events_to_memory(events=events)
        logger.info("Successfully persisted session %s to Memory Bank.", session_id)
    except Exception as e:
        logger.exception("Vertex AI Memory Bank ingestion failed for session %s: %s", session_id, e)


# ─────────────────────────────────────────────
# Tool — Employee lookup
# ─────────────────────────────────────────────
def employee_details(employee_id: str) -> dict:
    """
    Retrieve employee details using the employee ID.

    Args:
        employee_id: Unique identifier of the employee. Example: "EMP001"

    Returns:
        A dictionary with employee info, or an error message if not found.
    """
    employees = {
        "EMP001": {
            "name": "John Doe",
            "department": "Data Engineering",
            "designation": "Senior Data Engineer",
            "location": "Chennai",
            "experience": 6,
            "skills": ["Python", "PySpark", "GCP", "SQL"],
        },
        "EMP002": {
            "name": "Jane Smith",
            "department": "Data Science",
            "designation": "Data Scientist",
            "location": "Bangalore",
            "experience": 4,
            "skills": ["Python", "Pandas", "Machine Learning", "BigQuery"],
        },
    }

    return employees.get(employee_id, {"error": "Employee not found"})


# ─────────────────────────────────────────────
# Root Agent
# ─────────────────────────────────────────────
root_agent = Agent(
    name="memory_demo_agent_1",
    model="gemini-2.5-flash",
    instruction="""
    You are a helpful assistant.

    Always check and use information from memory when it is relevant to the user's conversation.
    If the user asks about employee details, use the employee_details() tool.
    If the user asks a general question, answer from your knowledge.
    Never invent memories.
    """,
    tools=[LoadMemoryTool(), employee_details],
    after_agent_callback=after_agent_callback,
)