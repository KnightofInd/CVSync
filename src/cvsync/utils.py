"""Utility helpers shared across CVSync modules."""

from __future__ import annotations

import hashlib
import re


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()


def normalize_whitespace(value: str) -> str:
    collapsed = re.sub(r"\s+", " ", value or "").strip()
    return collapsed
