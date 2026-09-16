import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

# Explicitly import vertexai and its types submodule so vertexai.types is populated
import vertexai
try:
    import vertexai.types
except ImportError:
    pass


import json

from langsmith.integrations.google_adk import configure_google_adk

configure_google_adk(project_name=os.getenv("LANGSMITH_PROJECT"))

from google.adk.agents import Agent
from google.adk.tools.load_memory_tool import LoadMemoryTool

from .memory import RedisMemoryManager

# ─────────────────────────────────────────────
# Initialise short-term memory (Redis Cloud)
# ─────────────────────────────────────────────
redis_memory = RedisMemoryManager()


# ─────────────────────────────────────────────
# STEP A — Before the agent replies
# ─────────────────────────────────────────────
async def before_agent_callback(callback_context):
    """
    Runs before the agent processes each user message.

    Reads the last 10 turns from Redis and injects them into the agent's
    instruction via {short_term_context}.

    FIX: We only store short_term_context in ADK state (needed for template
    substitution). We do NOT store session_id in state — ADK's internal
    protobuf session serialization can turn UUID strings into bytes when
    passing through its state system, which causes LangSmith's json.dumps
    to crash. Instead, we read session_id directly from session.id everywhere.
    """
    session_id = callback_context.session.id

    # Read recent history from Redis and format it as readable text
    context = redis_memory.build_context_string(session_id)

    # Store ONLY short_term_context in state (required for {short_term_context}
    # template substitution in the instruction).
    # Explicitly cast to str to prevent any accidental bytes leaking into state.
    callback_context.state["short_term_context"] = str(context)


# ─────────────────────────────────────────────
# STEP B — After the agent replies
# ─────────────────────────────────────────────
async def after_agent_callback(callback_context):
    """
    Runs after the agent produces its response.

    FIX: Read session_id directly from callback_context.session.id instead
    of from state. This avoids any protobuf bytes round-trip through ADK state.
    """
    # Get session_id directly — never via state
    session_id = callback_context.session.id
    events = callback_context.session.events

    if not events:
        return

    # ── Short-term: save each turn to Redis ──
    for event in events:
        if not hasattr(event, "content") or not event.content:
            continue

        # Extract text parts only (ignore function_call / function_response parts)
        text_parts = [
            str(part.text)                          # explicit str() — no bytes
            for part in event.content.parts
            if hasattr(part, "text") and part.text
        ]

        if not text_parts:
            continue

        role = "user" if event.author == "user" else "agent"
        text = " ".join(text_parts).strip()

        redis_memory.add_turn(session_id, role, text)

    # ── Long-term: push events to InMemory / Vertex AI MemoryBank ──
    try:
        # Pass required keyword argument events=events
        await callback_context.add_events_to_memory(events=events)

        # ADK's VertexMemoryBankService spawns a background `ingest_events` task.
        # Wait for background ingestion tasks to complete before this callback exits
        # so ADK's runner doesn't close the underlying HTTP client prematurely.
        current_task = asyncio.current_task()
        pending_tasks = [
            t for t in asyncio.all_tasks()
            if t != current_task and not t.done()
        ]
        if pending_tasks:
            await asyncio.gather(*pending_tasks, return_exceptions=True)
    except Exception as e:
        import logging
        logging.warning(f"Memory Bank event ingestion warning: {e}")



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

    {short_term_context}

    If the user asks about employee details, use the employee_details() tool.
    Use information from memory when it is relevant.
    If the user asks a general question, answer from your knowledge.
    Never invent memories.
    """,

    tools=[LoadMemoryTool(), employee_details],

    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)