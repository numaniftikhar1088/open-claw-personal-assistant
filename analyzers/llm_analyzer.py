from pydantic import BaseModel, Field
import ollama
from config import OLLAMA_MODEL, DEFAULT_CANDIDATE_PROFILE

class JobAnalysis(BaseModel):
    match_score: int = Field(..., description="Calculated match score from 0 to 100 based on candidate skills alignment.")
    tech_stack: list[str] = Field(default_factory=list, description="Extracted technology list e.g. AWS, GCP, Kubernetes, Terraform, Python.")
    key_responsibilities: list[str] = Field(default_factory=list, description="Top 3 key job responsibilities.")
    fit_summary: str = Field(..., description="Concise 2-sentence candidate fit assessment.")

def analyze_job(
    title: str,
    company: str,
    description: str,
    candidate_profile: str = DEFAULT_CANDIDATE_PROFILE,
    model: str = OLLAMA_MODEL
) -> JobAnalysis:
    """
    Passes job details to Ollama LLM and returns validated Pydantic JobAnalysis.
    """
    prompt = f"""
    You are an expert AI Tech Recruiter evaluating candidate fit.

    CANDIDATE BACKGROUND:
    {candidate_profile}

    JOB POSTING TO EVALUATE:
    Title: {title}
    Company: {company}
    Description:
    {description[:2500]}

    EVALUATION INSTRUCTIONS:
    1. Extract all required tools and technologies into 'tech_stack' (e.g. AWS, GCP, Azure, Kubernetes, Terraform, Docker, Python, CI/CD, Linux, SRE).
    2. Evaluate match_score (0 to 100):
       - 80-100: Heavy overlap with candidate skills (DevOps, SRE, Multi-Cloud, Kubernetes, Terraform, CI/CD).
       - 50-79: Partial overlap or related engineering role.
       - 0-49: Non-matching or irrelevant role (e.g., Security Analyst, CMDB, QA).
    3. Provide top 3 key responsibilities.
    4. Write a concise 2-sentence fit summary highlighting key matching skills or gaps.
    """

    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            format=JobAnalysis.model_json_schema()
        )

        parsed_data = JobAnalysis.model_validate_json(response['message']['content'])
        return parsed_data
    except Exception as e:
        print(f"⚠️ Error analyzing job '{title}' at '{company}': {e}")
        return JobAnalysis(
            match_score=0,
            tech_stack=[],
            key_responsibilities=[],
            fit_summary=f"Analysis error: {str(e)}"
        )
