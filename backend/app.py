import os
from typing import List

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .ingest import ingest_paths
from .models import (
    HealthResponse,
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    Source,
)
from .rag import answer_question

app = FastAPI(title="PrivateGPT Local", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_token(x_api_token: str = Header(default=None, alias="x-api-token")) -> None:
    expected = os.getenv("API_TOKEN", "")
    if not expected:
        return
    if not x_api_token or x_api_token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest, _: None = Depends(require_token)) -> IngestResponse:
    processed, skipped = ingest_paths(request.paths)
    return IngestResponse(processed_files=processed, skipped_files=skipped)


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, _: None = Depends(require_token)) -> QueryResponse:
    if not request.question.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question requise")
    try:
        result = answer_question(request.question, request.top_k)
    except Exception as exc:  # pragma: no cover - fallback errors propagate
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    answer = result.get("result", "Je ne sais pas.")
    sources_payload: List[Source] = []
    for doc in result.get("source_documents", []):
        metadata = doc.metadata or {}
        sources_payload.append(
            Source(
                source=metadata.get("source", "inconnu"),
                snippet=doc.page_content[:500],
            )
        )
    return QueryResponse(answer=answer, sources=sources_payload)
