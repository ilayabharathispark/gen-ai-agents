from . import observability
from google.adk.agents import Agent
from dotenv import load_dotenv

load_dotenv()

def get_current_time() -> dict:
    """Returns the current time."""
    from datetime import datetime

    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def add_numbers(a: int, b: int) -> dict:
    """Adds two numbers."""
    return {
        "result": a + b
    }


root_agent = Agent(
    name="demo_agent",
    model="groq/llama-3.3-70b-versatile", #gemini-2.5-flash",
    description="Simple ADK demo agent",
    instruction="""
You are a helpful assistant.

Use:
- get_current_time() whenever the user asks for the current time.
- add_numbers(a, b) whenever the user asks to add two numbers.
""",
    tools=[
        get_current_time,
        add_numbers,
    ],
)