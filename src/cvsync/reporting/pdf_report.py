"""PDF report generation for CVSync analysis output."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

from cvsync.models import AnalysisResult


def _truncate_to_width(text: str, max_width: float, font_name: str, font_size: int) -> str:
    if stringWidth(text, font_name, font_size) <= max_width:
        return text

    candidate = text
    while candidate and stringWidth(candidate + "...", font_name, font_size) > max_width:
        candidate = candidate[:-1]
    return (candidate + "...") if candidate else "..."


def _wrap_text(
    text: str,
    max_width: float,
    font_name: str,
    font_size: int,
    max_lines: int,
) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]

    for word in words[1:]:
        test = f"{current} {word}"
        if stringWidth(test, font_name, font_size) <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    lines.append(current)

    if len(lines) > max_lines:
        kept = lines[:max_lines]
        kept[-1] = _truncate_to_width(kept[-1], max_width, font_name, font_size)
        return kept

    return lines


def _section_text(items: list[str], empty_label: str) -> str:
    if not items:
        return empty_label
    return " | ".join(f"- {item}" for item in items)


def _draw_table_header(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    labels: list[str],
    col_widths: list[float],
) -> None:
    pdf.setFillColor(colors.HexColor("#eaf0fa"))
    pdf.rect(x, y - height, width, height, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.setFont("Helvetica-Bold", 10)

    cursor_x = x
    for idx, label in enumerate(labels):
        pdf.drawString(cursor_x + 6, y - 15, label)
        cursor_x += col_widths[idx]


def generate_pdf_report(
    result: AnalysisResult,
    output_path: Path,
    resume_name: str,
    jd_name: str,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    page_width, page_height = letter

    margin = 54
    content_width = page_width - (2 * margin)
    y = page_height - margin

    # Header band
    header_height = 62
    pdf.setFillColor(colors.HexColor("#1f2f45"))
    pdf.rect(margin, y - header_height, content_width, header_height, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margin + 12, y - 23, "CVSync Analysis Report")
    pdf.setFont("Helvetica", 9)
    pdf.drawString(margin + 12, y - 40, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= header_height + 14

    # Document details table
    doc_col_widths = [140, content_width - 140]
    doc_header_h = 22
    doc_row_h = 22
    _draw_table_header(pdf, margin, y, content_width, doc_header_h, ["Document", "Value"], doc_col_widths)

    y -= doc_header_h
    doc_rows = [
        ("Resume", _truncate_to_width(resume_name, doc_col_widths[1] - 12, "Helvetica", 10)),
        (
            "Job Description",
            _truncate_to_width(jd_name, doc_col_widths[1] - 12, "Helvetica", 10),
        ),
    ]

    pdf.setFont("Helvetica", 10)
    pdf.setStrokeColor(colors.HexColor("#d8dee8"))
    for key, value in doc_rows:
        pdf.rect(margin, y - doc_row_h, content_width, doc_row_h, fill=0, stroke=1)
        pdf.drawString(margin + 6, y - 15, key)
        pdf.drawString(margin + doc_col_widths[0] + 6, y - 15, value)
        y -= doc_row_h

    # Vertical line split for details table
    pdf.line(margin + doc_col_widths[0], y, margin + doc_col_widths[0], y + (doc_header_h + (doc_row_h * len(doc_rows))))

    y -= 14

    # Metrics summary table
    metric_col_widths = [130, 122, 130, content_width - 382]
    metric_header_h = 22
    metric_row_h = 22
    _draw_table_header(
        pdf,
        margin,
        y,
        content_width,
        metric_header_h,
        ["Metric", "Value", "Metric", "Value"],
        metric_col_widths,
    )

    y -= metric_header_h
    metric_rows = [
        ("Match Score", f"{result.match_score:.2f}%", "Skill Overlap", f"{result.skill_overlap:.2f}"),
        (
            "Semantic Similarity",
            f"{result.semantic_similarity:.2f}",
            "Role Relevance",
            f"{result.role_relevance:.2f}",
        ),
    ]

    for row in metric_rows:
        pdf.rect(margin, y - metric_row_h, content_width, metric_row_h, fill=0, stroke=1)
        x_cursor = margin
        for idx, cell in enumerate(row):
            pdf.drawString(x_cursor + 6, y - 15, cell)
            x_cursor += metric_col_widths[idx]
        y -= metric_row_h

    # Vertical lines for metrics table
    x_cursor = margin
    metric_table_height = metric_header_h + (metric_row_h * len(metric_rows))
    for width in metric_col_widths[:-1]:
        x_cursor += width
        pdf.line(x_cursor, y, x_cursor, y + metric_table_height)

    y -= 16

    # Insight table (main structured content)
    section_col_w = 132
    detail_col_w = content_width - section_col_w
    insight_header_h = 22
    _draw_table_header(
        pdf,
        margin,
        y,
        content_width,
        insight_header_h,
        ["Section", "Details"],
        [section_col_w, detail_col_w],
    )
    y -= insight_header_h

    insight_rows = [
        ("Strengths", _section_text(result.strengths, "No strengths detected."), 3),
        ("Improvements", _section_text(result.improvements, "No improvements suggested."), 4),
        ("Missing Skills", _section_text(result.missing_skills, "None"), 3),
        ("Warnings", _section_text(result.warnings, "No active warnings."), 3),
    ]

    pdf.setFont("Helvetica", 10)
    row_top_for_split = y
    for section, details, max_lines in insight_rows:
        wrapped = _wrap_text(details, detail_col_w - 12, "Helvetica", 10, max_lines)
        row_h = max(24, (len(wrapped) * 13) + 8)

        pdf.rect(margin, y - row_h, content_width, row_h, fill=0, stroke=1)
        pdf.setFillColor(colors.HexColor("#0f172a"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(margin + 6, y - 15, section)

        pdf.setFont("Helvetica", 10)
        text_y = y - 15
        for line in wrapped:
            pdf.drawString(margin + section_col_w + 6, text_y, line)
            text_y -= 13

        y -= row_h

    # Vertical split line for insight table
    pdf.line(margin + section_col_w, y, margin + section_col_w, row_top_for_split)

    # Footer note
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.drawRightString(
        page_width - margin,
        22,
        "CVSync local analysis - generated on-device",
    )

    pdf.save()
    return output_path
