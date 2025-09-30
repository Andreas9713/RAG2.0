from pydantic import BaseModel, Field
from typing import List, Optional


class IngestRequest(BaseModel):
    paths: List[str] = Field(..., description="Filesystem paths to ingest")


class QueryRequest(BaseModel):
    question: str = Field(..., description="User question to answer")
    top_k: Optional[int] = Field(default=5, description="Number of documents to retrieve")
