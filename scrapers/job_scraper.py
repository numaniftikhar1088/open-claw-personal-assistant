import pandas as pd
from jobspy import scrape_jobs

def fetch_job_postings(
    search_term: str = "Senior DevOps Engineer",
    location: str = "Remote",
    results_wanted: int = 5,
    hours_old: int = 48,
    sites: list[str] = None
) -> pd.DataFrame:
    """
    Scrapes raw job postings using python-jobspy from LinkedIn, Indeed, Glassdoor, etc.
    """
    if sites is None:
        sites = ["linkedin", "indeed"]
        
    print(f"🔍 Fetching {results_wanted} job postings for '{search_term}' in '{location}'...")
    try:
        jobs_df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old
        )
        print(f"✅ Successfully fetched {len(jobs_df)} jobs.")
        return jobs_df
    except Exception as e:
        print(f"⚠️ Error fetching jobs with JobSpy: {e}")
        return pd.DataFrame()
