from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
import os

QDRANT_URL = os.getenv("QDRANT_END_POINT")
QDRANT_API_KEY = os.getenv("QDRANT_API")


# Loaded once when the container starts
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def search_documents(
    collection_name: str,
    query: str,
    limit: int = 3,
):

    query_vector = embedding_model.embed_query(query)

    result = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )

    documents = []

    for hit in result.points:

        payload = hit.payload

        documents.append(
            {
                "score": hit.score,
                "text": payload.get("text", ""),
                "source": payload.get("source", ""),
                "page": payload.get("page", ""),
            }
        )

    return documents