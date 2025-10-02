from typing import List

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    paths: List[str] = Field(..., description="List of file paths to ingest")


class IngestResponse(BaseModel):
    processed_files: List[str]
    skipped_files: List[str]


class QueryRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    source: str
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]


class HealthResponse(BaseModel):
    status: str = "ok"
