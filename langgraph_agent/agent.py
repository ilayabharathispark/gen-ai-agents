import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Load environmental variables (GOOGLE_API_KEY, etc.)
load_dotenv()

# 1. Define the Agent State
# We use TypedDict to define the structure of our agent's state.
# The 'messages' key holds a sequence of LangChain message objects.
# The 'add_messages' annotation tells LangGraph how to update this state:
# it will append new messages to the list instead of overwriting.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# 2. Define the Tools
# Any standard Python function decorated with LangChain's @tool
# can be passed to our LLM. LangGraph will inspect the docstrings and
# types to generate schemas for the model.
@tool
def get_weather(city: str) -> str:
    """Get the current weather details for a given city."""
    city_lower = city.strip().lower()
    if "tokyo" in city_lower:
        return "It is currently sunny and 26°C (79°F) in Tokyo, wind NE at 12 km/h, 60% humidity."
    elif "london" in city_lower:
        return "It is currently rainy and 15°C (59°F) in London, wind SW at 22 km/h, 92% humidity."
    elif "new york" in city_lower:
        return "It is currently cloudy and 22°C (72°F) in New York, wind W at 8 km/h, 75% humidity."
    else:
        return f"The weather in '{city}' is currently 20°C (68°F) with dynamic clouds."

# 3. Define the LLM and Bind Tools
# We retrieve the Gemini model and bind our tools to it.
# Binding tools tells the model about their existence and schema so that
# it can formulate a tool call when needed.
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)
tools = [get_weather]
model_with_tools = model.bind_tools(tools)

# 4. Define Nodes
# Nodes are standard python functions that get the State as input and return updates to it.

def call_model(state: AgentState):
    """Invokes the model with the current messages in the state."""
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    # We return an update dictionary targeting the 'messages' list.
    # Because of `add_messages` reducer, this response is appended.
    return {"messages": [response]}

# The ToolNode is a prebuilt component that runs the tools if the model
# generated any tool call requests in its response.
tool_node = ToolNode(tools)

# 5. Define Graph Structure
# We initialize our StateGraph, register the nodes, and define edges.
workflow = StateGraph(AgentState)

# Register our nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entrypoint to the agent node
workflow.add_edge(START, "agent")

# Set conditional edge routing.
# After the agent node executes, the tools_condition prebuilt helper is evaluated.
# If the LLM requested an output tool call: it directs flow to "tools" node.
# If the LLM didn't request a tool call (finished speaking): it directs flow to END.
workflow.add_conditional_edges("agent", tools_condition)

# After running tools, always return to the agent to process the tool outputs
workflow.add_edge("tools", "agent")

# Compile the workflow to obtain a runnable graph
graph = workflow.compile()
