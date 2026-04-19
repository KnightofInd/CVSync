"""Simple JSON-backed cache to avoid duplicate analysis runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AnalysisCache:
    def __init__(self, cache_path: Path | None = None) -> None:
        self.cache_path = cache_path or Path(".cvsync_cache") / "analysis_cache.json"
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.cache_path.exists():
            self.cache_path.write_text("{}", encoding="utf-8")

    def _read(self) -> dict[str, Any]:
        try:
            content = self.cache_path.read_text(encoding="utf-8")
            return json.loads(content)
        except Exception:
            return {}

    def _write(self, payload: dict[str, Any]) -> None:
        self.cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get(self, key: str) -> dict[str, Any] | None:
        payload = self._read()
        return payload.get(key)

    def set(self, key: str, value: dict[str, Any]) -> None:
        payload = self._read()
        payload[key] = value
        self._write(payload)
