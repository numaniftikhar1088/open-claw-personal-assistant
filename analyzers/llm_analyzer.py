from pydantic import BaseModel, Field
import ollama
from config import OLLAMA_MODEL, DEFAULT_CANDIDATE_PROFILE

class JobAnalysis(BaseModel):
    match_score: int = Field(..., description="Match score from 0 to 100 based on candidate background fit")
    tech_stack: list[str] = Field(default_factory=list, description="Extracted technologies e.g. Kubernetes, Terraform, GCP")
    key_responsibilities: list[str] = Field(default_factory=list, description="Key job responsibilities")
    fit_summary: str = Field(..., description="Concise 1-2 sentence match evaluation summary")

def analyze_job(
    title: str,
    company: str,
    description: str,
    candidate_profile: str = DEFAULT_CANDIDATE_PROFILE,
    model: str = OLLAMA_MODEL
) -> JobAnalysis:
    """
    Passes a single job description to Ollama LLM and returns structured JobAnalysis data.
    """
    prompt = f"""
    Analyze the following job description for a candidate with this background:
    Candidate Background: {candidate_profile}

    Job Title: {title}
    Company: {company}
    Job Description:
    {description[:2500]}
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
        print(f"⚠️ Error analyzing job '{title}' at '{company}' with Ollama: {e}")
        # Fallback response if Ollama is not yet reachable or errors out
        return JobAnalysis(
            match_score=0,
            tech_stack=[],
            key_responsibilities=[],
            fit_summary=f"Analysis failed: {str(e)}"
        )
