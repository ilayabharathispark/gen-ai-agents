import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_groq import ChatGroq
from dotenv import load_dotenv

# pyrefly: ignore [missing-import]
from tools.tools import tavily_search_engine


load_dotenv()

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0.7
# )


# response = llm.invoke("Hello, how are you?")

# print(response.content)



response = tavily_search_engine("What is the current weather in Chennai?")

print(response)
