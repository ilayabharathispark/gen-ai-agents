import vertexai
from dotenv import load_dotenv
import os


load_dotenv()
GCP_PROJECT=os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")

client = vertexai.Client(
    project=GCP_PROJECT,
    location=LOCATION,
)


memory_bank = client.agent_engines.create(
    config={
        "display_name": "adk-memory-bank-ilaya-v1"
    }
)


print("Memory Bank created successfully!")
print("Resource name:")
print(memory_bank.api_resource.name)