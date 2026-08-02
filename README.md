# Autonomous AI Job Scraper & Profiler Agent

## 🎯 Goal
Build a self-hosted, autonomous information-gathering agent that scrapes tech jobs, evaluates skill-match scores against my background, extracts required technologies, and organizes structured outputs.

> **Note:** DO NOT write email drafts or attempt outreach at this stage. Focus strictly on extraction, AI processing, and structured data validation.

---

## 🏗️ Technical Environment & Setup
* **Host Environment:** Linux VPS
* **Target Domain:** Senior Multi-Cloud DevOps / SRE / AI Engineer (AWS, GCP, Azure, Kubernetes, Terraform, CI/CD, Python)
* **Cloud & Infra:** Standalone GCP Project (`new-standalone-project-504316`), Service Account (`sheets-writer`) configured with `gspread` access.
* **Local Inference / Testing Engine:** Ollama (`llama3.2`) running locally on port `11434`.
* **Target Framework:** Google Antigravity SDK (`pip install google-antigravity`) with Pydantic structured output validation.

---

## 📋 System Architecture & Phased Roadmap

### Phase 1: Data Gathering & AI Extraction (CURRENT PHASE)
1. Run `python-jobspy` to pull raw postings from LinkedIn and Indeed.
2. Pass job descriptions to the local LLM (Ollama `llama3.2`) for evaluation.
3. Validate and parse the output using `pydantic` schemas.
4. Output structured results (Match Score, Tech Stack, Key Responsibilities, Fit Summary).

### Phase 2: Web Interface (Streamlit)
* Create a simple dashboard on `http://localhost:8501` to manually filter, score, and view incoming job data.

### Phase 3: Autonomous Orchestration (OpenClaw & Telegram)
* Run background scraping daemons.
* Push high-matching job alerts directly to Telegram.

### Phase 4: Cold Outreach Automation (Future)
* Human-in-the-loop approval buttons for drafting and sending emails.

---

## 💻 Test Implementation Code (`test_pipeline.py`)

Below is the initial test script to evaluate the local extraction loop using `python-jobspy`, `ollama`, and `pydantic`:

```python
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
```
