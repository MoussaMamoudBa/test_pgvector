from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .vector_utils import get_db_connection, get_embedding_for_text, search_most_similar


app = FastAPI(
    title="pgvector demo",
    version="0.1.0",
    servers=[{"url": "http://localhost:8001", "description": "API (port 8001 côté host)"}],
)


@app.get("/")
def root() -> dict:
    return {
        "message": "API pgvector demo",
        "docs": "/docs",
        "health": "/health",
        "search": "POST /search avec body {\"query\": \"...\"}",
    }


class SearchRequest(BaseModel):
    query: str


class SearchResponse(BaseModel):
    id: int
    content: str
    distance: float


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _do_search(query: str) -> SearchResponse:
    embedding = get_embedding_for_text(query)
    conn = get_db_connection()
    try:
        result: Optional[tuple] = search_most_similar(conn, embedding)
    finally:
        conn.close()
    if result is None:
        raise HTTPException(status_code=404, detail="Aucun document trouvé (table vide ?)")
    doc_id, content, distance = result
    return SearchResponse(id=doc_id, content=content, distance=distance)


@app.post("/search", response_model=SearchResponse)
@app.post("/search/", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    return _do_search(request.query)

