from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import get_settings
from app.schemas.document import DocumentInfo, DocumentListResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])
service = DocumentService()
settings = get_settings()


class DocumentAccessRequest(BaseModel):
    key: str = Field(min_length=1, max_length=128)


@router.get("", response_model=DocumentListResponse)
def list_documents() -> DocumentListResponse:
    return service.list_documents()


@router.post("/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)) -> DocumentInfo:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file tidak valid.")

    allowed_extensions = {".pdf", ".md", ".txt"}
    suffix = f".{file.filename.split('.')[-1].lower()}" if "." in file.filename else ""
    if suffix not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Format file belum didukung.")

    content = await file.read()
    return service.save_upload(file.filename, content)


@router.post("/access")
def verify_document_access(payload: DocumentAccessRequest) -> dict:
    expected_key = settings.document_allow_key
    if not expected_key:
        raise HTTPException(status_code=500, detail="Kunci akses dokumen belum dikonfigurasi.")

    if payload.key.strip() != expected_key:
        raise HTTPException(status_code=401, detail="Kunci akses dokumen tidak valid.")

    return {"allowed": True}
