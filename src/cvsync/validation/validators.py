"""Validation rules for CVSync input documents."""

from __future__ import annotations

from langdetect import LangDetectException, detect

from cvsync.config import MAX_RESUME_PAGES_SOFT_LIMIT, MIN_JD_CHARS, MIN_RESUME_CHARS
from cvsync.exceptions import ValidationError


def _is_english(text: str) -> bool:
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False


def validate_documents(resume_text: str, jd_text: str, resume_pages: int) -> list[str]:
    warnings: list[str] = []

    if not resume_text.strip():
        raise ValidationError("Resume text is missing.")
    if not jd_text.strip():
        raise ValidationError("Job description text is missing.")

    if not _is_english(resume_text):
        raise ValidationError("Resume content appears to be non-English or unreadable.")
    if not _is_english(jd_text):
        raise ValidationError("Job description appears to be non-English or unreadable.")

    if len(resume_text) < MIN_RESUME_CHARS:
        warnings.append("Resume has very little content; score confidence is low.")
    if len(jd_text) < MIN_JD_CHARS:
        warnings.append("Job description is short/vague; recommendations may be less specific.")

    if resume_pages > MAX_RESUME_PAGES_SOFT_LIMIT:
        warnings.append(
            "Resume is very long; extraction succeeded but some details may be summarized."
        )

    return warnings
