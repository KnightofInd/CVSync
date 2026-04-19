from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Any, TypedDict

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cvsync.config import APP_NAME, APP_TAGLINE
from cvsync.models import AnalysisResult
from cvsync.pipeline import analyze_documents_with_timeout
from cvsync.reporting import generate_pdf_report
from cvsync.session import AnalysisCache


st.set_page_config(page_title=APP_NAME, layout="wide")

STYLE_PATH = ROOT / "ui" / "styles.css"
SESSION_KEYS = {
    "cache": "cache",
    "last_result": "last_result",
    "last_payload": "last_payload",
    "last_resume_name": "last_resume_name",
    "last_jd_name": "last_jd_name",
    "analysis_in_progress": "analysis_in_progress",
}


class AnalysisPayload(TypedDict):
    resume_file_bytes: bytes
    resume_filename: str
    jd_text: str
    jd_file_bytes: bytes | None
    jd_filename: str | None


def _load_stylesheet() -> None:
    if STYLE_PATH.exists():
        st.markdown(f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def _initialize_session_state() -> None:
    if SESSION_KEYS["cache"] not in st.session_state:
        st.session_state[SESSION_KEYS["cache"]] = AnalysisCache()
    if SESSION_KEYS["last_result"] not in st.session_state:
        st.session_state[SESSION_KEYS["last_result"]] = None
    if SESSION_KEYS["last_payload"] not in st.session_state:
        st.session_state[SESSION_KEYS["last_payload"]] = None
    if SESSION_KEYS["last_resume_name"] not in st.session_state:
        st.session_state[SESSION_KEYS["last_resume_name"]] = "Resume.pdf"
    if SESSION_KEYS["last_jd_name"] not in st.session_state:
        st.session_state[SESSION_KEYS["last_jd_name"]] = "Pasted JD"
    if SESSION_KEYS["analysis_in_progress"] not in st.session_state:
        st.session_state[SESSION_KEYS["analysis_in_progress"]] = False


def _chip_html(items: list[str], tone: str) -> str:
    if not items:
        return '<span class="chip green">None</span>'

    chips = []
    for item in items:
        chips.append(f'<span class="chip {tone}">{html.escape(item)}</span>')
    return "".join(chips)


def _match_badge(score: float) -> str:
    if score >= 85:
        return "Strong Match"
    if score >= 65:
        return "Moderate Match"
    return "Needs Improvement"


def _overlap_badge(overlap_pct: int) -> str:
    if overlap_pct >= 75:
        return "High Overlap"
    if overlap_pct >= 50:
        return "Medium Overlap"
    return "Low Overlap"


def _missing_badge(missing_count: int) -> str:
    if missing_count <= 3:
        return "Low Missing"
    if missing_count <= 7:
        return "Medium Missing"
    return "High Missing"


def _prioritized_improvements(items: list[str]) -> list[str]:
    prioritized: list[str] = []
    for idx, item in enumerate(items):
        lowered = item.lower()
        if idx == 0 or "must-have" in lowered or "prioritize" in lowered:
            priority = "High Priority"
        else:
            priority = "Medium Priority"
        prioritized.append(f"<li><span class='check'>&#10003;</span><b>{priority}:</b> {html.escape(item)}</li>")
    return prioritized


def _suggested_enhancements(present_skills: list[str]) -> list[str]:
    if present_skills:
        skill_focus = ", ".join(present_skills[:3])
        first = f"Re-wrote summary to highlight {skill_focus} capabilities."
    else:
        first = "Re-wrote summary to highlight scalable cloud and system design capabilities."

    second = "Replaced generic action verbs with metric-based impact statements in project sections."
    return [first, second]


def _run_analysis(payload: AnalysisPayload, cache: AnalysisCache) -> AnalysisResult:
    with st.spinner("Running CVSync analysis..."):
        return analyze_documents_with_timeout(
            resume_file_bytes=payload["resume_file_bytes"],
            resume_filename=payload["resume_filename"],
            jd_text=payload["jd_text"],
            jd_file_bytes=payload["jd_file_bytes"],
            jd_filename=payload["jd_filename"],
            cache=cache,
        )


def _render_header() -> None:
    st.markdown(
        f"""
        <div class="hero-card">
          <h1 class="hero-title">{html.escape(APP_NAME)}</h1>
          <p class="hero-tagline">{html.escape(APP_TAGLINE)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Privacy: CVSync runs fully locally on your machine. Uploaded files and analysis data are not sent to external services."
    )


def _build_payload(
    resume_file: Any,
    jd_text: str,
    jd_file: Any,
) -> AnalysisPayload:
    return {
        "resume_file_bytes": resume_file.getvalue(),
        "resume_filename": resume_file.name,
        "jd_text": jd_text,
        "jd_file_bytes": jd_file.getvalue() if jd_file else None,
        "jd_filename": jd_file.name if jd_file else None,
    }


def _render_input_panel() -> tuple[bool, bool, AnalysisPayload | None]:
    st.markdown("### Resume Upload")
    resume_file = st.file_uploader("Resume upload drag & drop", type=["pdf"], key="resume")

    jd_text = st.text_area(
        "Job Description",
        height=170,
        placeholder="Paste the job description here...",
        key="jd_text",
    )

    action_left, action_right = st.columns(2)
    run_clicked = action_left.button("Analyze Resume", type="primary", use_container_width=True)
    retry_clicked = action_right.button("Retry Last Analysis", use_container_width=True)

    if not run_clicked:
        return run_clicked, retry_clicked, None

    if not resume_file:
        st.error("Please upload a resume PDF.")
        return run_clicked, retry_clicked, None
    if not jd_text.strip():
        st.error("Please paste or upload a job description.")
        return run_clicked, retry_clicked, None

    payload = _build_payload(resume_file=resume_file, jd_text=jd_text, jd_file=None)
    return run_clicked, retry_clicked, payload


def _run_with_state(payload: AnalysisPayload) -> None:
    st.session_state[SESSION_KEYS["analysis_in_progress"]] = True
    try:
        result = _run_analysis(payload=payload, cache=st.session_state[SESSION_KEYS["cache"]])
    finally:
        st.session_state[SESSION_KEYS["analysis_in_progress"]] = False

    st.session_state[SESSION_KEYS["last_result"]] = result
    st.session_state[SESSION_KEYS["last_payload"]] = payload
    st.session_state[SESSION_KEYS["last_resume_name"]] = payload["resume_filename"]
    st.session_state[SESSION_KEYS["last_jd_name"]] = payload["jd_filename"] or "Pasted JD"


def _handle_actions(run_clicked: bool, retry_clicked: bool, payload: AnalysisPayload | None) -> None:
    if run_clicked and payload:
        _run_with_state(payload)

    if retry_clicked:
        last_payload = st.session_state[SESSION_KEYS["last_payload"]]
        if not last_payload:
            st.error("No previous analysis payload found. Run an analysis first.")
            return
        _run_with_state(last_payload)


def _render_metric_cards(result: AnalysisResult) -> None:
    score_value = int(round(result.match_score))
    overlap_pct = int(round(result.skill_overlap * 100))
    missing_count = len(result.missing_skills)

    top_left, top_mid, top_right, top_last = st.columns([2.35, 1, 1, 1], gap="medium")

    with top_left:
        strengths = result.strengths or ["No explicit strengths detected yet."]
        st.markdown(
            f"""
            <div class="result-card">
              <h3 class="card-heading">Strengths</h3>
              <div class="chip-wrap">{_chip_html(strengths, "green")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_mid:
        st.markdown(
            f"""
            <div class="result-card">
              <div class="metric-title">Match Score</div>
              <div class="metric-value">{score_value}%</div>
              <span class="pill-badge success">{_match_badge(score_value)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_right:
        st.markdown(
            f"""
            <div class="result-card">
              <div class="metric-title">Skill Overlap</div>
              <div class="metric-value">{overlap_pct}%</div>
              <span class="pill-badge success">{_overlap_badge(overlap_pct)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_last:
        st.markdown(
            f"""
            <div class="result-card">
              <div class="metric-title">Missing Skills Count</div>
              <div class="metric-value positive">{missing_count}</div>
              <span class="pill-badge success">{_missing_badge(missing_count)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_analysis_sections(result: AnalysisResult) -> None:
    prioritized = _prioritized_improvements(result.improvements)
    st.markdown(
        f"""
        <div class="result-card">
          <h3 class="card-heading">Improvements</h3>
          <ul class="check-list">{"".join(prioritized)}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    missing_skills = result.missing_skills or ["No missing skills detected"]
    st.markdown(
        f"""
        <div class="result-card">
          <h3 class="card-heading">Missing Skills</h3>
          <div class="chip-wrap">{_chip_html(missing_skills, "red")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    enhancements = _suggested_enhancements(result.present_skills)
    enh_rows = "".join(
        f"<div class='enh-row'><b>[Rewritten]:</b> {html.escape(line)}</div>" for line in enhancements
    )
    st.markdown(
        f"""
        <div class="result-card">
          <h3 class="card-heading">Suggested Enhancements</h3>
          {enh_rows}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_download(result: AnalysisResult) -> None:
    report_path = generate_pdf_report(
        result=result,
        output_path=Path("reports") / "cvsync_report.pdf",
        resume_name=st.session_state[SESSION_KEYS["last_resume_name"]],
        jd_name=st.session_state[SESSION_KEYS["last_jd_name"]],
    )

    st.download_button(
        label="Download Report (PDF)",
        data=report_path.read_bytes(),
        file_name=report_path.name,
        mime="application/pdf",
    )


def _render_results() -> None:
    result = st.session_state[SESSION_KEYS["last_result"]]
    if result is None:
        return

    st.markdown('<h2 class="dashboard-title">Professional Dashboard</h2>', unsafe_allow_html=True)
    _render_metric_cards(result=result)
    _render_analysis_sections(result=result)

    if result.warnings:
        for warning in result.warnings:
            st.warning(warning)

    if result.fallback_used:
        st.info("Fallback mode was used. You can retry after fixing inputs or transient issues.")

    _render_download(result=result)


def main() -> None:
    _load_stylesheet()
    _initialize_session_state()
    _render_header()

    if st.session_state[SESSION_KEYS["analysis_in_progress"]]:
        st.warning(
            "A previous analysis was interrupted or still processing. Use Retry Last Analysis to recover."
        )

    run_clicked, retry_clicked, payload = _render_input_panel()
    _handle_actions(run_clicked=run_clicked, retry_clicked=retry_clicked, payload=payload)
    _render_results()


main()
