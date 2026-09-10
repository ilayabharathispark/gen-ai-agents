import os

from dotenv import load_dotenv

load_dotenv()

from langsmith.integrations.google_adk import configure_google_adk

print("Calling configure_google_adk()")

configure_google_adk(
    project_name=os.getenv("LANGSMITH_PROJECT")
)

print("configure_google_adk() completed")

from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.load_memory_tool import LoadMemoryTool


async def after_agent_callback(callback_context):

    print("========== AFTER AGENT ==========")

    events = callback_context.session.events

    if events:
        await callback_context.add_events_to_memory(
            events=events
        )


def employee_details(employee_id: str) -> dict:
    """
    Retrieve employee details using the employee ID.

    This tool returns basic employee information such as name,
    department, designation, location, years of experience,
    and technical skills.

    Args:
        employee_id: Unique identifier of the employee.
            Example: "EMP001"

    Returns:
        A dictionary containing the employee's details if the
        employee ID exists. If the employee is not found, returns
        a dictionary containing an error message.

    Examples:
        employee_details("EMP001")

        Returns:
            {
                "name": "John Doe",
                "department": "Data Engineering",
                "designation": "Senior Data Engineer",
                "location": "Chennai",
                "experience": 6,
                "skills": ["Python", "PySpark", "GCP", "SQL"]
            }
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

    return employees.get(
        employee_id,
        {"error": "Employee not found"}
    )



root_agent = Agent(
    name="memory_demo_agent_1",

    model="gemini-2.5-flash",

    instruction="""
    You are a helpful assistant.

    if user asked about employyee details use employee_details() tools to fetch answer

    Use information from memory when it is relevant.

    if user asked about general question answer from your knowledge
    Never invent memories.
    """,

    tools=[
        LoadMemoryTool(),employee_details
    ],

    after_agent_callback=after_agent_callback, 

)