# To install: pip install tavily-python
from dotenv import load_dotenv
load_dotenv()
import os

from tavily import TavilyClient


client = TavilyClient(os.getenv("TAVILY_API_KEY"))
response = client.search(
      query="what is the current weather in chennai as of evening 9PM?",
        search_depth="advanced"
)
print(response) #['results'][0]['content']
