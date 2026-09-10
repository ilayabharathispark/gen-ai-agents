from typing import TypedDict
from typing_extensions import Annotated
import os
from pprint import pprint
# At the top imports — replace langchain_google_cloud_sql_pg imports with:
from langgraph.checkpoint.memory import MemorySaver



from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from langchain_google_genai import ChatGoogleGenerativeAI
from google.cloud import bigquery
from tavily import TavilyClient
# from .tools import search_engine

# Load Environment Variables
load_dotenv()

# --------------------------------------------------
# 1. Define the State
# --------------------------------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]


# --------------------------------------------------
# 2. Define the Tools
# --------------------------------------------------

@tool
def execute_bigquery_sql_query(sql_query: str) -> str:
    """Read-only execution of a standard SQL query against the BigQuery employee or department tables.
    Returns results formatted as a text table with column names.
    """
    print("\nExecuting SQL on BigQuery:")
    print(sql_query)

    # Load service account credentials from env if specified
    credentials_path = os.getenv("BIGQUERY_CREDENTIALS_PATH") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path:
        client = bigquery.Client.from_service_account_json(credentials_path)
    else:
        client = bigquery.Client()

    query_job = client.query(sql_query)
    results = query_job.result()

    schema_fields = [field.name for field in results.schema]
    header = " | ".join(schema_fields)
    separator = "-" * len(header)
    
    rows = []
    for row in results:
        row_str = " | ".join(str(row[field]) for field in schema_fields)
        rows.append(row_str)
        
    formatted_result = f"\n{header}\n{separator}\n" + "\n".join(rows) + "\n"
    return formatted_result


@tool
def get_my_details() -> str:
    """Get the user's personal details (such as name, role, experience, etc.)."""
    return """
    Name: Ilayabharathi
    Role: Senior Software Engineer
    Experience: 5 years
    Domain: Data Engineering
    """

@tool
def search_engine(query: str) -> str:
    """Search the latest information from web."""
    client = TavilyClient(os.getenv("TAVILY_API_KEY"))
    response = client.search(
        query=query,
        search_depth="advanced"
    )
    return response

tools = [execute_bigquery_sql_query, get_my_details, search_engine]


# --------------------------------------------------
# 3. Create LLM and Bind Tools
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)


# --------------------------------------------------
# 4. Define Nodes
# --------------------------------------------------

# def chatbot(state: State):

#     print("\n========== STATE LOADED ==========")

#     for i, message in enumerate(state["messages"]):
#         print(f"\nMessage {i}:")
#         print("Type:", type(message).__name__)
#         print("Content:", message.content)

#     print("==================================\n")

#     system_prompt = """..."""

#     messages = [SystemMessage(content=system_prompt)] + state["messages"]

#     response = llm_with_tools.invoke(messages)

#     return {
#         "messages": [response]
#     }
def chatbot(state: State):
     system_prompt = """You are a helpful assistant. You have access to a Google Cloud BigQuery database containing information about employees and departments, and a tool to retrieve the user's details.

The available BigQuery tables are:

1. Table: `ilaya-bharathi-murugan.bharathi.employee`

Columns:
- employee_id: INT64
- name: STRING
- department: STRING
- hire_date: DATE
- salary: FLOAT64

2. Table: `ilaya-bharathi-murugan.bharathi.department`

Columns:
- department_id: INT64
- department_name: STRING
- manager_name: STRING
- location: STRING

Conversation Context:
- The messages provided to you include the conversation history for the current user.
- Use the previous messages as context when answering the current question.
- If the user previously provided information in the conversation, such as their name, family details, role, experience, preferences, or other facts, use that information when it is relevant to the current question.
- Do not say that you cannot remember previous information when that information is present in the conversation history.
- Treat information provided by the user in previous messages as available conversation context.

Instructions:

1. If the user asks questions about employee records, salaries, departments, averages, or counts, you must use the `execute_bigquery_sql_query` tool to run a standard BigQuery SQL query. Always query using fully qualified table names (e.g. `ilaya-bharathi-murugan.bharathi.employee`).

2. If the user asks about any Ilayabharathi's details, their experience, role, or domain, use the `get_my_details` tool.

3. If the user asks about general questions, answer them directly based on your knowledge and the search_engine tool when current or external information is required.

4. Use relevant information from the conversation history when answering questions.

5. Be clear and explain the results cleanly to the user. Do not mention internal implementation details or tool-calling specifics.
"""

     messages = [SystemMessage(content=system_prompt)] + state["messages"]
     response = llm_with_tools.invoke(messages)
     return {
        "messages": [response]
     }


tool_node = ToolNode(tools)


# --------------------------------------------------
# 5. Conditional Routing
# --------------------------------------------------

def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


# --------------------------------------------------
# 6. Create LangGraph
# --------------------------------------------------

graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# Add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    should_continue
)
graph_builder.add_edge("tools", "chatbot")


from langchain_google_cloud_sql_pg import (
    PostgresEngine,
    PostgresSaver
)

# engine = PostgresEngine.from_instance(
#     project_id=os.getenv("CLOUD_SQL_PROJECT_ID"), # check these values in .env file if not present, then go to cloud.google.com -> Cloud SQL -> create postgresql instance -> select your instance -> overview
#     region=os.getenv("CLOUD_SQL_REGION"),
#     instance=os.getenv("CLOUD_SQL_INSTANCE"),
#     database=os.getenv("CLOUD_SQL_DATABASE"),
#     user=os.getenv("CLOUD_SQL_USER"),
#     password=os.getenv("CLOUD_SQL_PASSWORD")
# )

# # engine.init_checkpoint_table() # create table in cloud sql first time required

# checkpointer = PostgresSaver.create_sync(engine)
# # Compile graph

# Replace the entire PostgresEngine/PostgresSaver block (lines ~205-221) with:
checkpointer = MemorySaver()

# Compile with HITL interrupt:
graph = graph_builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"]  # <-- pause before any tool runs
)
# graph = graph_builder.compile() # checkpointer=checkpointer


# --------------------------------------------------
# 7. Run the Graph
# --------------------------------------------------

if __name__ == "__main__":

    # ✅ List of approved user IDs allowed to access personal details
    APPROVED_USER_IDS = ["ilaya001", "admin", "bharathi123"]

    config = {
        "configurable": {
            "thread_id": "ilaya-hitl"
        }
    }

    user_input = input("You: ").strip()

    # Step 1: Invoke — graph pauses before 'tools' node
    result = graph.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config
    )

    last_message = result["messages"][-1]

    # Step 2: Check if graph paused at a tool call
    if last_message.tool_calls:

        # Check if any pending call is 'get_my_details'
        personal_calls = [tc for tc in last_message.tool_calls if tc["name"] == "get_my_details"]

        if personal_calls:
            # 🔐 Personal details requested — verify user identity
            print("\n🔐 This query accesses personal details. Identity verification required.")
            user_id = input("Enter your User ID: ").strip()

            if user_id in APPROVED_USER_IDS:
                print(f"✅ User '{user_id}' verified. Proceeding...\n")
                # Resume graph from checkpoint
                result = graph.invoke(None, config)
                print("📋 Answer:")
                print(result["messages"][-1].content)
            else:
                print(f"❌ Access Denied: User ID '{user_id}' is not authorized.")
        else:
            # Other tools (BigQuery, search) — auto-proceed
            print(f"\n🔧 Calling tool: {last_message.tool_calls[0]['name']}...\n")
            result = graph.invoke(None, config)
            print("📋 Answer:")
            print(result["messages"][-1].content)

    else:
        # No tool needed — direct answer
        print("\n📋 Answer:")
        print(last_message.content)
