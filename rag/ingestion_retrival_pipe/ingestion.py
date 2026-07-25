from uuid import uuid4

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
import os
import glob
import json

load_dotenv()

# ==========================================================
# CONFIGURATION
# ==========================================================

PDF_DIR = "D:\\my-projects\\my-ai-agents\\rag\\ingestion_retrival_pipe\\pdf" # directory containing pdf files to ingest

QDRANT_URL = os.getenv("QDRANT_END_POINT") #add your qdrant url
QDRANT_API_KEY = os.getenv("QDRANT_API") #add your api key

COLLECTION_NAME = "my_agent_collection" #add your collection name or index name

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" #add your embedding model

# ==========================================================
# VALIDATION OUTPUT DIRECTORIES CONFIG
# ==========================================================
VALIDATION_DIR = "D:\\my-projects\\my-ai-agents\\rag\\ingestion_retrival_pipe\\validation_outputs"
PARSING_OUT_DIR = os.path.join(VALIDATION_DIR, "parsing")
CHUNKS_OUT_DIR = os.path.join(VALIDATION_DIR, "chunks")



EMBEDDINGS_OUT_DIR = os.path.join(VALIDATION_DIR, "embeddings")

os.makedirs(PARSING_OUT_DIR, exist_ok=True)
os.makedirs(CHUNKS_OUT_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_OUT_DIR, exist_ok=True)


# ==========================================================
# LOAD PDFS FROM DIRECTORY
# ==========================================================

print(f"Scanning directory: {PDF_DIR}")
pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
print(f"Found {len(pdf_files)} PDF files")

documents = []
for pdf_file in pdf_files:
    print(f"Loading {pdf_file}...")
    loader = PyPDFLoader(pdf_file)
    documents.extend(loader.load())

print(f"Loaded {len(documents)} pages in total")

# Save parsing output for validation
parsed_data = {}
for doc in documents:
    source_file = os.path.basename(doc.metadata.get("source", "unknown"))
    if source_file not in parsed_data:
        parsed_data[source_file] = []
    parsed_data[source_file].append({
        "page": doc.metadata.get("page", 0),
        "content": doc.page_content
    })

for source_file, pages in parsed_data.items():
    output_filename = os.path.join(PARSING_OUT_DIR, f"{os.path.splitext(source_file)[0]}_parsed.json")
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=4, ensure_ascii=False)
    print(f"Saved parsed verification output to: {output_filename}")


# ==========================================================
# SPLIT INTO CHUNKS
# ==========================================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

# Save chunking output for validation
chunks_data = {}
for idx, chunk in enumerate(chunks):
    source_file = os.path.basename(chunk.metadata.get("source", "unknown"))
    if source_file not in chunks_data:
        chunks_data[source_file] = []
    chunks_data[source_file].append({
        "chunk_index": idx,
        "page": chunk.metadata.get("page", 0),
        "content": chunk.page_content
    })

for source_file, chunks_list in chunks_data.items():
    output_filename = os.path.join(CHUNKS_OUT_DIR, f"{os.path.splitext(source_file)[0]}_chunks.json")
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(chunks_list, f, indent=4, ensure_ascii=False)
    print(f"Saved chunked verification output to: {output_filename}")


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

# Save embedding validation output
embeddings_data = []
for p in points:
    embeddings_data.append({
        "id": p.id,
        "source": os.path.basename(p.payload.get("source", "unknown")),
        "page": p.payload.get("page", 0),
        "text_preview": p.payload.get("text", "")[:100] + ("..." if len(p.payload.get("text", "")) > 100 else ""),
        "vector_dimension": len(p.vector),
        "vector_sample": p.vector[:5]  # first 5 elements for validation
    })

output_embeddings_filename = os.path.join(EMBEDDINGS_OUT_DIR, "embeddings_validation.json")
with open(output_embeddings_filename, "w", encoding="utf-8") as f:
    json.dump(embeddings_data, f, indent=4, ensure_ascii=False)
print(f"Saved embeddings verification output to: {output_embeddings_filename}")


# ==========================================================
# UPSERT TO QDRANT (index the data to vector database qdrant)
# ==========================================================

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points,
)

print(f"\nSuccessfully indexed {len(points)} chunks!")