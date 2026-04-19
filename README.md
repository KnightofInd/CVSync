# CVSync

Sync Your Skills. Match Your Future.

CVSync is a fully local resume-to-job analysis application. It compares a resume against a job description, computes a match score, highlights strengths and missing skills, provides improvement suggestions, and generates a one-page PDF report.

## Key Features

- Local-first processing (no external AI API calls required)
- Resume PDF ingestion and JD text input
- Match score and sub-metrics (skill overlap, semantic similarity, role relevance)
- Structured strengths, improvements, and missing-skills insights
- One-click downloadable PDF report

## Project Structure

- `app.py`: Streamlit UI entry point
- `src/cvsync/pipeline.py`: End-to-end orchestration
- `src/cvsync/ingestion/`: Resume and JD parsing
- `src/cvsync/validation/`: Input and language validation
- `src/cvsync/nlp/`: Text preprocessing and skill extraction
- `src/cvsync/matching/`: Score computation logic
- `src/cvsync/recommendation/`: Strength/improvement generation
- `src/cvsync/reporting/`: PDF report generation
- `src/cvsync/session/`: Local duplicate-run cache

## Setup and Run Instructions

### 1) Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Start the application

```powershell
streamlit run app.py
```

Default URL:

- `http://localhost:8501`

## Functional Flow

1. User uploads a resume PDF and pastes the job description.
2. Ingestion layer extracts text from files and normalizes sources.
3. Validation layer checks required content and language quality.
4. NLP layer preprocesses text and extracts skill signals.
5. Matching layer computes:
	- Match score
	- Skill overlap
	- Semantic similarity
	- Role relevance
6. Recommendation layer builds strengths and prioritized improvements.
7. UI dashboard renders results in cards and sections.
8. Reporting layer generates a one-page downloadable PDF.
9. Session cache avoids duplicate recomputation for identical inputs.

## Demo Screenshots

### Input Form

![Input Form](Demo%20Screenshots/Input_Form.png)

### Web Results Dashboard

![Web Results](Demo%20Screenshots/Web_Results.png)

### Generated PDF Report

![PDF Report](Demo%20Screenshots/PDF_Report.png)

## Output

- Downloaded reports are generated in the `reports/` directory.

## Privacy Note

- CVSync runs locally on your machine.
- Uploaded files and analysis data are not sent to external services.
