"""Data models used by the CVSync analysis pipeline."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DocumentMeta:
    filename: str
    source: str
    hash_value: str
    pages: int = 0


@dataclass
class AnalysisInput:
    resume_text: str
    jd_text: str
    resume_meta: DocumentMeta
    jd_meta: DocumentMeta


@dataclass
class AnalysisResult:
    match_score: float
    strengths: list[str]
    improvements: list[str]
    missing_skills: list[str]
    present_skills: list[str]
    must_have_missing: list[str]
    semantic_similarity: float
    skill_overlap: float
    role_relevance: float
    warnings: list[str] = field(default_factory=list)
    cached: bool = False
    fallback_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
