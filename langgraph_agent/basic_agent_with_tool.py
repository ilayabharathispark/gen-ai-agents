from typing import TypedDict
from typing_extensions import Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from dotenv import load_dotenv
load_dotenv()
print("running_langgraph_agent")
# -------------------------
# State
# -------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]


# -------------------------
# Tools
# -------------------------

duckduckgo = DuckDuckGoSearchRun()

wikipedia = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper()
)


@tool
def calculate_age(birth_year: int) -> str:
    """Calculate the age from a birth year."""
    age = 2026 - birth_year
    return f"The person's approximate age is {age}."


tools = [
    duckduckgo,
    wikipedia,
    calculate_age,
]


# -------------------------
# LLM
# -------------------------

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

# Bind all tools to the LLM
llm_with_tools = llm.bind_tools(tools)


# -------------------------
# Nodes
# -------------------------

def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {
        "messages": [response]
    }


tool_node = ToolNode(tools)


# -------------------------
# Conditional Routing
# -------------------------

def should_continue(state: State):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# -------------------------
# Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("chatbot", chatbot)
builder.add_node("tools", tool_node)

builder.add_edge(START, "chatbot")

builder.add_conditional_edges(
    "chatbot",
    should_continue
)

builder.add_edge("tools", "chatbot")

graph = builder.compile()


# -------------------------
# Run
# -------------------------

response = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="calculate the age of someone born in 1998."
            )
        ]
    }
)

print("\n=========================\n")

for message in response["messages"]:
    print(type(message).__name__)
    print(message)
    print("\n-------------------------\n")

print("Final Answer:\n")
print(response["messages"][-1].content)