"""PDF report generation for CVSync analysis output."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from cvsync.models import AnalysisResult


def _draw_lines(pdf: canvas.Canvas, lines: list[str], x: int, y: int, step: int = 16) -> int:
    cursor = y
    for line in lines:
        pdf.drawString(x, cursor, line)
        cursor -= step
        if cursor < 72:
            pdf.showPage()
            cursor = 720
    return cursor


def generate_pdf_report(
    result: AnalysisResult,
    output_path: Path,
    resume_name: str,
    jd_name: str,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=letter)

    y = 760
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(72, y, "CVSync Analysis Report")

    y -= 30
    pdf.setFont("Helvetica", 10)
    y = _draw_lines(
        pdf,
        [
            f"Resume: {resume_name}",
            f"Job Description: {jd_name}",
            f"Match Score: {result.match_score:.2f}%",
            f"Skill Overlap: {result.skill_overlap:.2f}",
            f"Semantic Similarity: {result.semantic_similarity:.2f}",
            f"Role Relevance: {result.role_relevance:.2f}",
        ],
        72,
        y,
    )

    y -= 10
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, y, "Strengths")
    y -= 18
    pdf.setFont("Helvetica", 10)
    strength_lines = [f"- {line}" for line in result.strengths] or ["- No strengths detected."]
    y = _draw_lines(pdf, strength_lines, 72, y)

    y -= 8
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, y, "Improvements")
    y -= 18
    pdf.setFont("Helvetica", 10)
    improve_lines = [f"- {line}" for line in result.improvements] or ["- No improvements suggested."]
    y = _draw_lines(pdf, improve_lines, 72, y)

    y -= 8
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, y, "Missing Skills")
    y -= 18
    pdf.setFont("Helvetica", 10)
    missing_lines = [f"- {skill}" for skill in result.missing_skills] or ["- None"]
    y = _draw_lines(pdf, missing_lines, 72, y)

    if result.warnings:
        y -= 8
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(72, y, "Warnings")
        y -= 18
        pdf.setFont("Helvetica", 10)
        warn_lines = [f"- {warning}" for warning in result.warnings]
        _draw_lines(pdf, warn_lines, 72, y)

    pdf.save()
    return output_path
