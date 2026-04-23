from __future__ import annotations

from pydantic import BaseModel


class DocumentInfo(BaseModel):
    name: str
    path: str
    size_bytes: int
    page_count: int | None = None
    preview: str | None = None
    content_type: str


class DocumentListResponse(BaseModel):
    total: int
    items: list[DocumentInfo]
