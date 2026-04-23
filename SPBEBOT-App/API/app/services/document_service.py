from __future__ import annotations

import mimetypes
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

from app.core.config import get_settings
from app.schemas.document import DocumentInfo, DocumentListResponse

try:
    from vercel.blob import BlobClient, list_objects
except Exception:  # pragma: no cover - fallback when optional dependency is absent
    BlobClient = None
    list_objects = None

class DocumentService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.data_dir = self.settings.data_dir
        self.blob_token = self.settings.blob_read_write_token
        self.use_blob = bool(self.blob_token and BlobClient is not None)
        self.blob_access = "public" if self.settings.blob_access == "public" else "private"
        self.blob_prefix = self.settings.blob_prefix.strip("/") or "spbebot-docs"
        self._blob_client = BlobClient(token=self.blob_token) if self.use_blob else None

    def _relative_or_absolute_path(self, path: Path) -> str:
        for root in (self.settings.base_dir, self.settings.base_dir.parent):
            try:
                return str(path.relative_to(root)).replace("\\", "/")
            except Exception:
                continue
        return str(path).replace("\\", "/")

    def _build_local_preview(self, path: Path) -> tuple[int | None, str | None]:
        if path.suffix.lower() == ".pdf":
            try:
                reader = PdfReader(str(path))
                page_count = len(reader.pages)
                preview = None
                if reader.pages:
                    preview = (reader.pages[0].extract_text() or "").strip().replace("\n", " ")[:280]
                return page_count, preview
            except Exception:
                return None, "Preview PDF tidak tersedia."

        if path.suffix.lower() in {".md", ".txt"}:
            preview = path.read_text(encoding="utf-8", errors="ignore").replace("\n", " ")[:280]
            return None, preview

        return None, None

    def list_documents(self) -> DocumentListResponse:
        if self.use_blob and list_objects is not None:
            result = list_objects(prefix=f"{self.blob_prefix}/", token=self.blob_token)
            blobs = getattr(result, "blobs", result)
            items: list[DocumentInfo] = []
            for blob in blobs:
                pathname = getattr(blob, "pathname", "") or ""
                if not pathname:
                    continue

                name = pathname.split("/")[-1]
                content_type, _ = mimetypes.guess_type(name)
                size = int(getattr(blob, "size", 0) or 0)
                blob_url = getattr(blob, "url", pathname)

                items.append(
                    DocumentInfo(
                        name=name,
                        path=blob_url,
                        size_bytes=size,
                        page_count=None,
                        preview=None,
                        content_type=content_type or "application/octet-stream",
                    )
                )

            return DocumentListResponse(total=len(items), items=items)

        items: list[DocumentInfo] = []

        for path in sorted(self.data_dir.iterdir()):
            if not path.is_file():
                continue

            mime_type, _ = mimetypes.guess_type(path.name)
            page_count, preview = self._build_local_preview(path)

            items.append(
                DocumentInfo(
                    name=path.name,
                    path=self._relative_or_absolute_path(path),
                    size_bytes=path.stat().st_size,
                    page_count=page_count,
                    preview=preview,
                    content_type=mime_type or "application/octet-stream",
                )
            )

        return DocumentListResponse(total=len(items), items=items)

    def save_upload(self, filename: str, content: bytes) -> DocumentInfo:
        if self.use_blob and self._blob_client is not None:
            safe_name = Path(filename).name
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            pathname = f"{self.blob_prefix}/{timestamp}-{safe_name}"
            content_type, _ = mimetypes.guess_type(safe_name)
            blob = self._blob_client.put(
                pathname,
                content,
                access=self.blob_access,
                content_type=content_type or "application/octet-stream",
                add_random_suffix=True,
            )

            return DocumentInfo(
                name=safe_name,
                path=str(getattr(blob, "url", pathname)),
                size_bytes=len(content),
                page_count=None,
                preview=None,
                content_type=content_type or "application/octet-stream",
            )

        destination = self.data_dir / Path(filename).name
        destination.write_bytes(content)

        mime_type, _ = mimetypes.guess_type(destination.name)
        page_count, preview = self._build_local_preview(destination)

        return DocumentInfo(
            name=destination.name,
            path=self._relative_or_absolute_path(destination),
            size_bytes=destination.stat().st_size,
            page_count=page_count,
            preview=preview,
            content_type=mime_type or "application/octet-stream",
        )
