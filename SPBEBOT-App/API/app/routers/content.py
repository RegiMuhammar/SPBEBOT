from __future__ import annotations

from fastapi import APIRouter

from app.services.content_repository import ContentRepository

router = APIRouter(prefix="/content", tags=["content"])
repository = ContentRepository()


@router.get("/overview")
def get_overview() -> dict:
    return repository.get_overview()


@router.get("/prompts")
def get_prompts() -> dict:
    return {"items": repository.get_prompt_templates()}


@router.get("/dashboard")
def get_dashboard() -> dict:
    return repository.get_dashboard()


@router.get("/research")
def get_research() -> dict:
    return repository.get_research_results()
