from langchain_core.messages import HumanMessage
from langgraph_agent.agent import graph

def run_agent(query: str):
    print("=" * 60)
    print(f"User Query: {query}")
    print("=" * 60)
    
    # We initialize the starting state with the user's message
    inputs = {"messages": [HumanMessage(content=query)]}
    
    # graph.stream executes the LangGraph and yields updates.
    # By using stream_mode="updates", we get a dictionary at each step
    # specifying which node executed and what state changes it returned.
    for event in graph.stream(inputs, stream_mode="updates"):
        for node_name, state_update in event.items():
            print(f"\n[Node Execution: '{node_name}']")
            
            # Print any new messages appended in this step
            new_messages = state_update.get("messages", [])
            for message in new_messages:
                role = type(message).__name__.replace("Message", "")
                print(f"  Role: {role}")
                if message.content:
                    print(f"  Content: {message.content}")
                if hasattr(message, "tool_calls") and message.tool_calls:
                    print(f"  Tool Calls: {message.tool_calls}")
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    # Test 1: Simple conversational query (doesn't trigger tool calls)
    run_agent("Hello! Who are you and what tools do you have?")
    
    # Test 2: Query requiring weather details (triggers get_weather tool)
    run_agent("What is the current weather in Tokyo?")
