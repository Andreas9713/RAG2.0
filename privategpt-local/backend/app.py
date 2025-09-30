import os
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status

from .models import IngestRequest, QueryRequest
from .rag import ask, ingest_paths

app = FastAPI(title="privategpt-local")


def get_api_token() -> Optional[str]:
    return os.getenv("API_TOKEN")


def authenticate(
    authorization: Optional[str] = Header(default=None),
    expected_token: Optional[str] = Depends(get_api_token),
) -> str:
    if not expected_token:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API token not configured")
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    value = authorization.strip()
    if value.lower().startswith("bearer "):
        value = value[7:].strip()

    if value != expected_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return value


@app.get("/health")
def health_check():
    return {"ok": True}


@app.post("/ingest")
def ingest_documents(request: IngestRequest, _: str = Depends(authenticate)):
    indexed = ingest_paths(request.paths)
    return {"indexed": indexed}


@app.post("/query")
def query_documents(request: QueryRequest, _: str = Depends(authenticate)):
    answer, sources = ask(request.question, request.top_k or 5)
    return {"answer": answer, "sources": sources}
