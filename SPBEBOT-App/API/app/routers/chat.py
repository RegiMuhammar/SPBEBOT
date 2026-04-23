from __future__ import annotations

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.graph_service import GraphService
from app.services.vector_service import VectorService

router = APIRouter(prefix="/chat", tags=["chat"])
vector_service = VectorService()
graph_service = GraphService()


@router.post("/vector", response_model=ChatResponse)
def vector_chat(payload: ChatRequest) -> ChatResponse:
    return ChatResponse(**vector_service.answer(payload.question, top_k=payload.top_k))


@router.post("/graph", response_model=ChatResponse)
def graph_chat(payload: ChatRequest) -> ChatResponse:
    return ChatResponse(**graph_service.answer(payload.question))
