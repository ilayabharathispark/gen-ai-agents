import os

from dotenv import load_dotenv

from typing import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from typing import Annotated

from langchain_core.messages import BaseMessage


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# State
# --------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# --------------------------------------------------
# LLM
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)


# --------------------------------------------------
# Tavily Tool
# --------------------------------------------------

tavily_tool = TavilySearch(
    max_results=3
)


tools = [tavily_tool]


# Bind tools to LLM

llm_with_tools = llm.bind_tools(tools)


# --------------------------------------------------
# LLM Node
# --------------------------------------------------

def chatbot(state: AgentState):

    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


# --------------------------------------------------
# Tool Node
# --------------------------------------------------

tool_node = ToolNode(tools)


# --------------------------------------------------
# Routing Logic
# --------------------------------------------------

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    # If LLM requested a tool
    if last_message.tool_calls:
        return "tools"

    # Otherwise finish
    return END


# --------------------------------------------------
# Build Graph
# --------------------------------------------------

graph_builder = StateGraph(AgentState)


graph_builder.add_node(
    "chatbot",
    chatbot
)

graph_builder.add_node(
    "tools",
    tool_node
)


# START → chatbot

graph_builder.add_edge(
    START,
    "chatbot"
)


# chatbot → tools OR END

graph_builder.add_conditional_edges(
    "chatbot",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)


# tools → chatbot

graph_builder.add_edge(
    "tools",
    "chatbot"
)


# Compile

graph = graph_builder.compile()


# --------------------------------------------------
# Agent function
# --------------------------------------------------

def run_agent(inputs: dict) -> dict:

    question = inputs["question"]

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
    )

    # Check whether Tavily was called
    used_tavily = False

    for message in result["messages"]:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call["name"] == "tavily_search":
                    used_tavily = True

    final_message = result["messages"][-1]

    return {
        "answer": final_message.content,
        "used_tavily": used_tavily
    }


# --------------------------------------------------
# Local testing
# --------------------------------------------------

if __name__ == "__main__":

    result = run_agent(
        {
            "question": "What is LangGraph?"
        }
    )

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================")

    print(result["answer"])