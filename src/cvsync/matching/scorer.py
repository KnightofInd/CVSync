"""Scoring and matching logic for CVSync."""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from cvsync.config import (
    MAX_MUST_HAVE_PENALTY,
    MUST_HAVE_SKILL_PENALTY,
    ROLE_CONTEXT_TERMS,
    WEIGHT_ROLE_RELEVANCE,
    WEIGHT_SEMANTIC_SIMILARITY,
    WEIGHT_SKILL_OVERLAP,
)


def _semantic_similarity(resume_text: str, jd_text: str) -> float:
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([resume_text, jd_text])
    score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    return max(0.0, min(1.0, score))


def _skill_overlap(resume_skills: list[str], jd_skills: list[str]) -> float:
    if not jd_skills:
        return 0.0
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    overlap = len(resume_set.intersection(jd_set))
    return overlap / len(jd_set)


def _role_relevance(resume_text: str, jd_text: str) -> float:
    jd_terms = [term for term in ROLE_CONTEXT_TERMS if term in jd_text]
    if not jd_terms:
        jd_terms = ROLE_CONTEXT_TERMS

    hits = sum(1 for term in jd_terms if term in resume_text)
    return hits / len(jd_terms)


def compute_match_breakdown(
    resume_text: str,
    jd_text: str,
    resume_skills: list[str],
    jd_skills: list[str],
    must_have_skills: list[str],
) -> dict[str, float]:
    skill_overlap = _skill_overlap(resume_skills=resume_skills, jd_skills=jd_skills)
    semantic = _semantic_similarity(resume_text=resume_text, jd_text=jd_text)
    role_relevance = _role_relevance(resume_text=resume_text, jd_text=jd_text)

    base_score = (
        WEIGHT_SKILL_OVERLAP * skill_overlap
        + WEIGHT_SEMANTIC_SIMILARITY * semantic
        + WEIGHT_ROLE_RELEVANCE * role_relevance
    )

    resume_set = set(resume_skills)
    missing_must_have = [skill for skill in must_have_skills if skill not in resume_set]
    penalty = min(len(missing_must_have) * MUST_HAVE_SKILL_PENALTY, MAX_MUST_HAVE_PENALTY)

    final_score = max(0.0, min(1.0, base_score - penalty))

    return {
        "skill_overlap": skill_overlap,
        "semantic_similarity": semantic,
        "role_relevance": role_relevance,
        "score": final_score,
    }
