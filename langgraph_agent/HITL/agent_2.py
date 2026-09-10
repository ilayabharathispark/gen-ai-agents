from typing import TypedDict

from dotenv import load_dotenv

import re

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

# pyrefly: ignore [missing-import]
from tools.tools import tavily_search_engine, send_email


load_dotenv()


# ============================================================
# STATE
# ============================================================

class AgentState(TypedDict, total=False):
    user_query: str
    result: str
    recipient: str
    subject: str
    next: str
    approved: bool


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7
)


# ============================================================
# SUPERVISOR
# ============================================================

def supervisor(state: AgentState):

    query = state["user_query"]

    prompt = f"""
You are a supervisor.

User request:
{query}

Choose the correct node.

Available nodes:

llm:
- General questions
- Writing
- Story generation

tavily:
- Latest information
- Current information
- Web search

email:
- Sending an email

Return ONLY one word:

llm
tavily
email
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    decision = response.content.strip().lower()

    print(f"\nSupervisor decision: {decision}")

    return {
        "next": decision
    }


# ============================================================
# LLM NODE
# ============================================================

def llm_node(state: AgentState):

    query = state["user_query"]

    response = llm.invoke(
        [HumanMessage(content=query)]
    )

    print("\nLLM RESULT:")
    print(response.content)

    return {
        "result": response.content
    }


# ============================================================
# TAVILY NODE
# ============================================================

def tavily_node(state: AgentState):

    query = state["user_query"]

    result = tavily_search_engine(query)

    print("\nTAVILY RESULT:")
    print(result)

    return {
        "result": result
    }


# ============================================================
# EMAIL NODE
# ============================================================

def email_node(state: AgentState):

    result = state["result"]

    recipient = state["recipient"]

    subject = state["subject"]

    # --------------------------------------------------------
    # HUMAN IN THE LOOP
    # --------------------------------------------------------

    approval = interrupt(
        {
            "message": "Do you want to send this email?",

            "recipient": recipient,

            "subject": subject,

            "body": result
        }
    )

    # --------------------------------------------------------
    # HUMAN REJECTED
    # --------------------------------------------------------

    if not approval["approved"]:

        print("\nEmail rejected.")

        return {
            "approved":approval,
            "result": "Email was not sent."
        }

    # --------------------------------------------------------
    # SEND EMAIL
    # --------------------------------------------------------

    response = send_email(
        recipient=recipient,
        subject=subject,
        body=result
    )

    print("\nEMAIL RESULT:")
    print(response)

    return {
        "approved":approval,
        "result": response
    }


# ============================================================
# ROUTER
# ============================================================

def router(state: AgentState):

    decision = state["next"]

    if decision == "llm":
        return "llm"

    if decision == "tavily":
        return "tavily"

    if decision == "email":
        return "email"

    return END


# ============================================================
# GRAPH
# ============================================================

builder = StateGraph(AgentState)


# Nodes

builder.add_node(
    "supervisor",
    supervisor
)

builder.add_node(
    "llm",
    llm_node
)

builder.add_node(
    "tavily",
    tavily_node
)

builder.add_node(
    "email",
    email_node
)


# ============================================================
# START
# ============================================================

builder.add_edge(
    START,
    "supervisor"
)


# ============================================================
# SUPERVISOR ROUTING
# ============================================================

builder.add_conditional_edges(
    "supervisor",
    router,
    {
        "llm": "llm",
        "tavily": "tavily",
        "email": "email",
        END: END
    }
)


# ============================================================
# WORKERS → END
# ============================================================

builder.add_edge(
    "llm",
    END
)

builder.add_edge(
    "tavily",
    END
)

builder.add_edge(
    "email",
    END
)


# ============================================================
# CHECKPOINTER
# ============================================================

memory = MemorySaver()


# ============================================================
# COMPILE
# ============================================================

graph = builder.compile(
    checkpointer=memory
)