"""Job description input ingestion logic."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

from cvsync.exceptions import IngestionError
from cvsync.utils import normalize_whitespace


def _read_pdf_text(file_bytes: bytes, filename: str) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as exc:  # pragma: no cover - parser internals vary.
        raise IngestionError(f"Unable to parse JD PDF '{filename}'.") from exc

    chunks: list[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")

    text = normalize_whitespace("\n".join(chunks))
    if not text:
        raise IngestionError("JD PDF does not contain extractable text.")

    return text


def read_jd_document(jd_text: str | None, file_bytes: bytes | None, filename: str | None) -> str:
    if jd_text and jd_text.strip():
        return normalize_whitespace(jd_text)

    if not file_bytes:
        raise IngestionError("Job description is missing.")

    name = (filename or "jd.txt").lower()
    if name.endswith(".pdf"):
        return _read_pdf_text(file_bytes=file_bytes, filename=filename or "jd.pdf")

    try:
        decoded = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        decoded = file_bytes.decode("latin-1", errors="ignore")

    text = normalize_whitespace(decoded)
    if not text:
        raise IngestionError("JD file is empty.")

    return text
