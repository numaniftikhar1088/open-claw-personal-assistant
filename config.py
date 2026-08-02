import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Candidate Profile
DEFAULT_CANDIDATE_PROFILE = (
    "Senior Multi-Cloud DevOps Engineer (AWS, Azure, GCP, Kubernetes, Terraform, CI/CD, Python)"
)

# Ollama Settings
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Google Sheets Settings
SERVICE_ACCOUNT_FILE = os.getenv("GCP_SERVICE_ACCOUNT_FILE", str(BASE_DIR / "service-account.json"))
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Tech Job Postings & Match Scores")

# Streamlit Settings
STREAMLIT_PORT = int(os.getenv("PORT", 8501))
