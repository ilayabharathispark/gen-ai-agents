from typing import TypedDict
from typing_extensions import Annotated
import os
from pprint import pprint

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from langchain_google_genai import ChatGoogleGenerativeAI
from google.cloud import bigquery

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


tools = [execute_bigquery_sql_query, get_my_details]


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

Instructions:
1. If the user asks questions about employee records, salaries, departments, averages, or counts, you must use the `execute_bigquery_sql_query` tool to run a standard BigQuery standard SQL query. Always query using fully qualified table names (e.g. `ilaya-bharathi-murugan.bharathi.employee`).
2. If the user asks about any ilayabharathi's details, their experience, role, or domain, use the `get_my_details` tool.
3. If the user asks about general questions, answer them directly. based on your knowledge.
4. Be clear and explain the results cleanly to the user. Do not mention internal implementation details or tool-calling specifics.
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

# Compile graph
graph = graph_builder.compile()


# --------------------------------------------------
# 7. Run the Graph
# --------------------------------------------------

if __name__ == "__main__":
    # Test 1: Query database
    print("\n--- Test 1: BQ Query ---")
    query_1 = "who is ilayabharathi?"
    result_1 = graph.invoke({
        "messages": [HumanMessage(content=query_1)]
    })
    
    print("\nFinal Answer 1:")
    print(result_1["messages"])
