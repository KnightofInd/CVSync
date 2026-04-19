"""Skill extraction heuristics for resume and JD text."""

from __future__ import annotations

import re

from cvsync.config import MUST_HAVE_CUES, SKILL_KEYWORDS


def extract_skills(text: str) -> list[str]:
    found: set[str] = set()
    source = text.lower()

    for skill in SKILL_KEYWORDS:
        escaped = re.escape(skill)
        pattern = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
        if re.search(pattern, source):
            found.add(skill)

    return sorted(found)


def extract_must_have_skills(jd_text: str, jd_skills: list[str]) -> list[str]:
    lower = jd_text.lower()
    must_have: set[str] = set()

    for cue in MUST_HAVE_CUES:
        idx = lower.find(cue)
        if idx == -1:
            continue

        window = lower[idx : idx + 220]
        for skill in jd_skills:
            if skill in window:
                must_have.add(skill)

    return sorted(must_have)
