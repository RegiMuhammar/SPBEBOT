from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=4, ge=1, le=8)


class RetrievedChunk(BaseModel):
    id: str
    title: str
    source: str
    score: float
    excerpt: str


class ChatResponse(BaseModel):
    mode: str
    answer: str
    question: str
    sources: list[RetrievedChunk]
    follow_up_suggestions: list[str]
