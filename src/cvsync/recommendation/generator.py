"""Generate strengths and improvements for CVSync reports."""

from __future__ import annotations


def build_recommendations(
    score: float,
    present_skills: list[str],
    missing_skills: list[str],
    must_have_missing: list[str],
) -> tuple[list[str], list[str]]:
    strengths: list[str] = []
    improvements: list[str] = []

    if score >= 0.75:
        strengths.append("Strong overall alignment with job expectations.")
    elif score >= 0.55:
        strengths.append("Moderate alignment with relevant role signals.")
    else:
        improvements.append("Current resume-to-role alignment is low and needs targeted updates.")

    if present_skills:
        top_present = ", ".join(present_skills[:6])
        strengths.append(f"Relevant skills already visible: {top_present}.")

    if missing_skills:
        top_missing = ", ".join(missing_skills[:8])
        improvements.append(f"Add evidence for missing skills: {top_missing}.")

    if must_have_missing:
        must_list = ", ".join(must_have_missing)
        improvements.append(f"Prioritize must-have gaps first: {must_list}.")

    improvements.append(
        "Quantify project impact with metrics (time saved, performance gain, scale, or cost impact)."
    )

    return strengths, improvements
