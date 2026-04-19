"""Configuration values for CVSync."""

APP_NAME = "CVSync"
APP_TAGLINE = "Sync Your Skills. Match Your Future."

ANALYSIS_TIMEOUT_SECONDS = 45
MAX_RESUME_PAGES_SOFT_LIMIT = 12
MIN_RESUME_CHARS = 120
MIN_JD_CHARS = 120

WEIGHT_SKILL_OVERLAP = 0.50
WEIGHT_SEMANTIC_SIMILARITY = 0.30
WEIGHT_ROLE_RELEVANCE = 0.20
MUST_HAVE_SKILL_PENALTY = 0.06
MAX_MUST_HAVE_PENALTY = 0.24

# Curated baseline taxonomy for skill extraction.
SKILL_KEYWORDS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "pandas",
    "numpy",
    "scikit-learn",
    "machine learning",
    "deep learning",
    "nlp",
    "spacy",
    "pytorch",
    "tensorflow",
    "huggingface",
    "sentence transformers",
    "fastapi",
    "streamlit",
    "flask",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "aws",
    "azure",
    "gcp",
    "rest api",
    "microservices",
    "redis",
    "rabbitmq",
    "graphql",
    "reportlab",
    "pyspark",
    "airflow",
    "tableau",
    "power bi",
]

MUST_HAVE_CUES = [
    "must have",
    "mandatory",
    "required",
    "required skills",
    "essential",
    "minimum qualifications",
]

ROLE_CONTEXT_TERMS = [
    "experience",
    "projects",
    "lead",
    "build",
    "develop",
    "deploy",
    "optimize",
    "production",
    "architecture",
    "stakeholder",
]
