import json
from jobspy import scrape_jobs
from pydantic import BaseModel, Field
import ollama

# 1. Define Structured Output Schema
class JobAnalysis(BaseModel):
    match_score: int = Field(..., description="Calculated match score from 0 to 100 based on candidate skills alignment.")
    tech_stack: list[str] = Field(default_factory=list, description="Extracted technology list e.g. AWS, GCP, Kubernetes, Terraform, Python.")
    key_responsibilities: list[str] = Field(default_factory=list, description="Top 3 key job responsibilities.")
    fit_summary: str = Field(..., description="Concise 2-sentence candidate fit assessment.")

# 2. Scrape Jobs via JobSpy
print("🔍 Scraping raw job postings...")
jobs_df = scrape_jobs(
    site_name=["linkedin", "indeed"],
    search_term="Senior DevOps Engineer",
    location="Remote",
    results_wanted=3,
    hours_old=48
)

print(f"✅ Found {len(jobs_df)} jobs. Processing with local Ollama (`llama3.2`)...\n")

# Candidate Profile
MY_PROFILE = "Senior Multi-Cloud DevOps Engineer (AWS, Azure, GCP, Kubernetes, Terraform, CI/CD, Python)"

# 3. Information Extraction Loop
for index, job in jobs_df.iterrows():
    title = job.get("title", "N/A")
    company = job.get("company", "N/A")
    description = str(job.get("description", ""))[:2500]

    prompt = f"""
    You are an expert AI Tech Recruiter evaluating candidate fit.

    CANDIDATE BACKGROUND:
    {MY_PROFILE}

    JOB POSTING TO EVALUATE:
    Title: {title}
    Company: {company}
    Description:
    {description}

    EVALUATION INSTRUCTIONS:
    1. Extract all required tools and technologies into 'tech_stack' (e.g. AWS, GCP, Azure, Kubernetes, Terraform, Docker, Python, CI/CD, Linux, SRE).
    2. Evaluate match_score (0 to 100):
       - 80-100: Heavy overlap with candidate skills (DevOps, SRE, Multi-Cloud, Kubernetes, Terraform, CI/CD).
       - 50-79: Partial overlap or related engineering role.
       - 0-49: Non-matching or irrelevant role (e.g., Security Analyst, CMDB, QA).
    3. Provide top 3 key responsibilities.
    4. Write a concise 2-sentence fit summary highlighting key matching skills or gaps.
    """

    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}],
        format=JobAnalysis.model_json_schema()
    )

    parsed_data = JobAnalysis.model_validate_json(response['message']['content'])

    # Print Clean Output
    print("="*60)
    print(f"📌 Job Title: {title} @ {company}")
    print(f"🎯 Match Score: {parsed_data.match_score}/100")
    print(f"🛠️ Tech Stack: {', '.join(parsed_data.tech_stack)}")
    print(f"💡 Fit Summary: {parsed_data.fit_summary}")
    print("="*60 + "\n")
