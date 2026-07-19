import os
import argparse

from dotenv import load_dotenv

from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq

load_dotenv()

# -------------------------------------------------
# Configuration
# -------------------------------------------------

QDRANT_URL = os.getenv("QDRANT_END_POINT")
QDRANT_API_KEY = os.getenv("QDRANT_API")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

COLLECTION_NAME = "rag_demo"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--query",
        required=True,
        help="Question to ask"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=3
    )

    parser.add_argument(
        "--model",
        default="llama-3.3-70b-versatile"
    )

    args = parser.parse_args()

    # -------------------------------------------------
    # Embedding model
    # -------------------------------------------------

    print("Loading embedding model...")

    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    # -------------------------------------------------
    # Qdrant
    # -------------------------------------------------

    print("Connecting to Qdrant...")

    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )

    # -------------------------------------------------
    # Query embedding
    # -------------------------------------------------

    print(f"Generating embedding for: {args.query}")

    query_vector = embedding_model.embed_query(args.query)

    # -------------------------------------------------
    # Search
    # -------------------------------------------------

    print("Searching Qdrant...")

    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=args.limit,
        with_payload=True,
    )

    hits = result.points

    if len(hits) == 0:
        print("No matching documents found.")
        return

    print("\n==============================")
    print("Retrieved Chunks")
    print("==============================\n")

    context = []

    for i, hit in enumerate(hits, start=1):

        payload = hit.payload

        text = payload.get("text", "")

        source = payload.get("source", "Unknown")

        page = payload.get("page", "Unknown")

        print(f"[{i}]")
        print(f"Score  : {hit.score:.4f}")
        print(f"Source : {source}")
        print(f"Page   : {page}")
        print(text[:250])
        print("-" * 80)

        context.append(
            f"""
Source: {source}
Page: {page}

{text}
"""
        )

    # -------------------------------------------------
    # LLM
    # -------------------------------------------------

    print("\nCalling Groq...\n")

    groq = Groq(
        api_key=GROQ_API_KEY
    )

    system_prompt = f"""
You are a helpful assistant.

Answer ONLY using the supplied context.

If the answer is not present, reply:

'I cannot find the answer in the provided document.'

Context:

{chr(10).join(context)}
"""

    response = groq.chat.completions.create(
        model=args.model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": args.query
            }
        ]
    )

    print("\n")
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(response.choices[0].message.content)

    print("=" * 80)


if __name__ == "__main__":
    main()