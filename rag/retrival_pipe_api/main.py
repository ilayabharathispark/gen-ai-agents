from fastapi import FastAPI
from pydantic import BaseModel

from retrieval import search_documents

app = FastAPI(
    title="RAG Retrieval API"
)


class SearchRequest(BaseModel):
    collection: str
    query: str
    limit: int = 3


@app.get("/")
def home():
    return {
        "status": "running"
    }


@app.post("/search")
def search(request: SearchRequest):

    documents = search_documents(
        collection_name=request.collection,
        query=request.query,
        limit=request.limit,
    )

    return {
        "documents": documents
    }