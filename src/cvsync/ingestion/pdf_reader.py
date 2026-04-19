"""Resume PDF ingestion logic."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

from cvsync.exceptions import IngestionError
from cvsync.utils import normalize_whitespace


def read_resume_pdf(file_bytes: bytes, filename: str) -> tuple[str, int]:
    if not file_bytes:
        raise IngestionError("Resume file is empty.")

    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as exc:  # pragma: no cover - parser internals vary.
        raise IngestionError(f"Unable to parse PDF '{filename}'.") from exc

    pages = len(reader.pages)
    chunks: list[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")

    text = normalize_whitespace("\n".join(chunks))
    if not text:
        raise IngestionError("Resume PDF does not contain extractable text.")

    return text, pages
