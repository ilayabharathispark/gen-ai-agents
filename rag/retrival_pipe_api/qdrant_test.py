import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_END_POINT")
QDRANT_API_KEY = os.getenv("QDRANT_API")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# List all collections
collections = client.get_collections()
print("Collections:", [col.name for col in collections.collections])

# Scroll 3 points from a collection
COLLECTION_NAME = "my_agent_collection"
points, _ = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=3,
    with_payload=True,
    with_vectors=False,
)

for pt in points:
    print(f"ID: {pt.id} | Source: {pt.payload.get('source')} | Page: {pt.payload.get('page')}")
