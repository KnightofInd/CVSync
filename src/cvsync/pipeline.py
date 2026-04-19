"""Main orchestration pipeline for CVSync analysis."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any

from cvsync.config import ANALYSIS_TIMEOUT_SECONDS
from cvsync.exceptions import IngestionError, ValidationError
from cvsync.ingestion import read_jd_document, read_resume_pdf
from cvsync.matching import compute_match_breakdown
from cvsync.models import AnalysisResult
from cvsync.nlp import extract_must_have_skills, extract_skills, preprocess_text
from cvsync.recommendation import build_recommendations
from cvsync.session import AnalysisCache
from cvsync.utils import stable_hash
from cvsync.validation import validate_documents


_DUPLICATE_WARNING = "Duplicate analysis detected. Returned cached result for the same inputs."
_RETRY_HINT = "Retry with valid English resume and job description content."


def _build_cache_key(resume_text: str, jd_text: str) -> str:
    return stable_hash(f"{stable_hash(resume_text)}::{stable_hash(jd_text)}")


def _load_cached_result(cache: AnalysisCache, cache_key: str) -> AnalysisResult | None:
    cached_payload = cache.get(cache_key)
    if not cached_payload:
        return None

    cached_result = AnalysisResult(**cached_payload)
    cached_result.cached = True
    cached_result.warnings.append(_DUPLICATE_WARNING)
    return cached_result


def _build_match_artifacts(
    resume_text: str,
    jd_text: str,
) -> dict[str, Any]:
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    must_have_skills = extract_must_have_skills(jd_text=jd_text, jd_skills=jd_skills)

    breakdown = compute_match_breakdown(
        resume_text=resume_text,
        jd_text=jd_text,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        must_have_skills=must_have_skills,
    )

    present_skills = sorted(set(resume_skills).intersection(set(jd_skills)))
    missing_skills = sorted(set(jd_skills).difference(set(resume_skills)))
    missing_must_have = sorted(set(must_have_skills).difference(set(resume_skills)))

    return {
        "breakdown": breakdown,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "present_skills": present_skills,
        "missing_skills": missing_skills,
        "missing_must_have": missing_must_have,
    }


def _build_analysis_result(
    artifacts: dict[str, Any],
    warnings: list[str],
) -> AnalysisResult:
    breakdown = artifacts["breakdown"]
    present_skills = artifacts["present_skills"]
    missing_skills = artifacts["missing_skills"]
    missing_must_have = artifacts["missing_must_have"]

    strengths, improvements = build_recommendations(
        score=breakdown["score"],
        present_skills=present_skills,
        missing_skills=missing_skills,
        must_have_missing=missing_must_have,
    )

    if not artifacts["jd_skills"]:
        warnings.append("No explicit skills were detected in the job description.")

    return AnalysisResult(
        match_score=round(breakdown["score"] * 100, 2),
        strengths=strengths,
        improvements=improvements,
        missing_skills=missing_skills,
        present_skills=present_skills,
        must_have_missing=missing_must_have,
        semantic_similarity=round(breakdown["semantic_similarity"], 4),
        skill_overlap=round(breakdown["skill_overlap"], 4),
        role_relevance=round(breakdown["role_relevance"], 4),
        warnings=warnings,
    )


def _fallback_result(message: str) -> AnalysisResult:
    return AnalysisResult(
        match_score=0.0,
        strengths=[],
        improvements=[_RETRY_HINT],
        missing_skills=[],
        present_skills=[],
        must_have_missing=[],
        semantic_similarity=0.0,
        skill_overlap=0.0,
        role_relevance=0.0,
        warnings=[message],
        fallback_used=True,
    )


def analyze_documents(
    resume_file_bytes: bytes,
    resume_filename: str,
    jd_text: str | None = None,
    jd_file_bytes: bytes | None = None,
    jd_filename: str | None = None,
    cache: AnalysisCache | None = None,
) -> AnalysisResult:
    try:
        resume_text_raw, resume_pages = read_resume_pdf(
            file_bytes=resume_file_bytes,
            filename=resume_filename,
        )
        jd_text_raw = read_jd_document(
            jd_text=jd_text,
            file_bytes=jd_file_bytes,
            filename=jd_filename,
        )

        warnings = validate_documents(
            resume_text=resume_text_raw,
            jd_text=jd_text_raw,
            resume_pages=resume_pages,
        )

        resume_text = preprocess_text(resume_text_raw)
        jd_text_clean = preprocess_text(jd_text_raw)

        cache_layer = cache or AnalysisCache()
        cache_key = _build_cache_key(resume_text=resume_text, jd_text=jd_text_clean)
        cached_result = _load_cached_result(cache=cache_layer, cache_key=cache_key)
        if cached_result:
            return cached_result

        artifacts = _build_match_artifacts(resume_text=resume_text, jd_text=jd_text_clean)
        result = _build_analysis_result(artifacts=artifacts, warnings=warnings)

        cache_layer.set(cache_key, result.to_dict())
        return result

    except (IngestionError, ValidationError) as exc:
        return _fallback_result(str(exc))
    except Exception as exc:  # pragma: no cover - safety net.
        return _fallback_result(
            f"Analysis failed due to an internal model/system error: {exc}. Use retry."
        )


def analyze_documents_with_timeout(
    resume_file_bytes: bytes,
    resume_filename: str,
    jd_text: str | None = None,
    jd_file_bytes: bytes | None = None,
    jd_filename: str | None = None,
    cache: AnalysisCache | None = None,
    timeout_seconds: int = ANALYSIS_TIMEOUT_SECONDS,
) -> AnalysisResult:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            analyze_documents,
            resume_file_bytes,
            resume_filename,
            jd_text,
            jd_file_bytes,
            jd_filename,
            cache,
        )
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError:
            return _fallback_result(
                "Analysis timed out. Please retry with a shorter document or try again."
            )
