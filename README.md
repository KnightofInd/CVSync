# CVSync
Sync Your Skills. Match Your Future.

CVSync is a fully local resume-to-job analysis app. It ingests a resume and job description, computes a fit score, highlights strengths and skill gaps, and exports a PDF report.

## Runtime Architecture

Core modules under `src/cvsync`:

- `ingestion`: Resume/JD parsing and file handling
- `validation`: Input integrity and language checks
- `nlp`: Text normalization and skill extraction
- `matching`: Similarity, overlap, and score breakdown logic
- `recommendation`: Strength and improvement generation
- `reporting`: PDF report rendering
- `session`: Local duplicate-run cache

## Execution Flow

1. Upload resume and JD in `app.py`.
2. Pipeline parses and validates both documents.
3. NLP layer extracts skills and must-have indicators.
4. Matching engine computes weighted score components.
5. Recommendation layer produces strengths and improvements.
6. UI renders dashboard and provides PDF export.
7. Cache prevents duplicate recomputation for identical inputs.

## Quick Start

1. Create and activate a Python virtual environment.
2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Run the Streamlit app.

```powershell
streamlit run app.py
```

## Notes

- The app runs fully local and does not require external AI APIs.
- Reports are generated to the `reports/` folder during runtime.
