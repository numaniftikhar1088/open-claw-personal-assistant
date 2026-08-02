import json
from jobspy import scrape_jobs
from pydantic import BaseModel
import ollama

# 1. Define Structured Output Schema
class JobAnalysis(BaseModel):
    match_score: int  # 0 to 100 based on candidate fit
    tech_stack: list[str]  # e.g., ["Kubernetes", "Terraform", "GCP", "Python"]
    key_responsibilities: list[str]
    fit_summary: str  # Concise 1-2 sentence match summary

# 2. Scrape Jobs via JobSpy
print("🔍 Scraping raw job postings...")
jobs_df = scrape_jobs(
    site_name=["linkedin", "indeed"],
    search_term="Senior DevOps Engineer",
    location="Remote",
    results_wanted=3,
    hours_old=48
)

print(f"✅ Found {len(jobs_df)} jobs. Processing with Ollama...\n")

# Candidate Profile
MY_PROFILE = "Senior Multi-Cloud DevOps Engineer (AWS, Azure, GCP, Kubernetes, Terraform, CI/CD, Python)"

# 3. Information Extraction Loop
for index, job in jobs_df.iterrows():
    title = job.get("title", "N/A")
    company = job.get("company", "N/A")
    description = str(job.get("description", ""))[:2000]

    prompt = f"""
    Analyze the following job description for a candidate with this background:
    Candidate Background: {MY_PROFILE}

    Job Title: {title}
    Company: {company}
    Job Description:
    {description}
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
