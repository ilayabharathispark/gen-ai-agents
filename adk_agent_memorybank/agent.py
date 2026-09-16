import os
import logging

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================================================
# LANGSMITH
# =========================================================

from langsmith.integrations.google_adk import configure_google_adk

logger.info("Calling configure_google_adk()")

configure_google_adk(
    project_name=os.getenv("LANGSMITH_PROJECT")
)

logger.info("configure_google_adk() completed")


# =========================================================
# ADK
# =========================================================

from google.adk.agents import Agent
from google.adk.tools.load_memory_tool import LoadMemoryTool


# =========================================================
# MEMORY BANK CALLBACK
# =========================================================

async def after_agent_callback(callback_context):

    logger.info("========== AFTER AGENT ==========")

    try:

        events = callback_context.session.events

        logger.info(
            "Events available for Memory Bank: %d",
            len(events) if events else 0
        )

        if not events:
            return

        await callback_context.add_events_to_memory(
            events=events
        )

        logger.info(
            "Memory Bank add_events_to_memory() completed"
        )

    except Exception as exc:

        logger.exception(
            "Memory Bank callback failed: %s",
            exc
        )


# =========================================================
# EMPLOYEE TOOL
# =========================================================

def employee_details(employee_id: str) -> dict:

    employees = {

        "EMP001": {
            "name": "John Doe",
            "department": "Data Engineering",
            "designation": "Senior Data Engineer",
            "location": "Chennai",
            "experience": 6,
            "skills": [
                "Python",
                "PySpark",
                "GCP",
                "SQL"
            ],
        },

        "EMP002": {
            "name": "Jane Smith",
            "department": "Data Science",
            "designation": "Data Scientist",
            "location": "Bangalore",
            "experience": 4,
            "skills": [
                "Python",
                "Pandas",
                "Machine Learning",
                "BigQuery"
            ],
        },
    }

    return employees.get(
        employee_id,
        {"error": "Employee not found"}
    )


# =========================================================
# ROOT AGENT
# =========================================================

root_agent = Agent(

    name="memory_demo_agent_1",

    model="gemini-2.5-flash",

    instruction="""
You are a helpful assistant.

If the user asks about employee details,
use the employee_details tool.

Use information from memory when relevant.

If the user asks a general question,
answer from your knowledge.

Never invent memories.
""",

    tools=[
        LoadMemoryTool(),
        employee_details,
    ],

    after_agent_callback=after_agent_callback,
)