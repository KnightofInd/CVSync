"""Text preprocessing utilities."""

from __future__ import annotations

import re

from cvsync.utils import normalize_whitespace


def preprocess_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9+#.\-\s]", " ", lowered)
    return normalize_whitespace(lowered)
