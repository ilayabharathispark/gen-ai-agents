from uuid import uuid4

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
import os

load_dotenv()

# ==========================================================
# CONFIGURATION
# ==========================================================

PDF_PATH = "D:\\my-projects\\my-ai-agents\\rag\\ilayabharathi_summary.pdf"

QDRANT_URL = os.getenv("QDRANT_END_POINT")
QDRANT_API_KEY = os.getenv("QDRANT_API")

COLLECTION_NAME = "rag_demo"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ==========================================================
# LOAD PDF
# ==========================================================

print("Loading PDF...")

loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

print(f"Loaded {len(documents)} pages")


# ==========================================================
# SPLIT INTO CHUNKS
# ==========================================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")


# ==========================================================
# EMBEDDING MODEL
# ==========================================================

print("Loading embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

print("Generating embeddings...")

texts = [doc.page_content for doc in chunks]

embeddings = embedding_model.embed_documents(texts)

print(f"Generated {len(embeddings)} embeddings")


# ==========================================================
# CONNECT TO QDRANT CLOUD
# ==========================================================

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


# ==========================================================
# CREATE COLLECTION (ONLY IF NOT EXISTS)
# ==========================================================

collections = client.get_collections().collections

collection_names = [c.name for c in collections]

if COLLECTION_NAME not in collection_names:

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=len(embeddings[0]),
            distance=Distance.COSINE,
        ),
    )

    print("Collection created.")

else:
    print("Collection already exists.")


# ==========================================================
# PREPARE POINTS
# ==========================================================

points = []

for doc, vector in zip(chunks, embeddings):

    points.append(
        PointStruct(
            id=str(uuid4()),
            vector=vector,
            payload={
                "text": doc.page_content,
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page"),
            },
        )
    )


# ==========================================================
# UPSERT TO QDRANT
# ==========================================================

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points,
)

print(f"\nSuccessfully indexed {len(points)} chunks!")