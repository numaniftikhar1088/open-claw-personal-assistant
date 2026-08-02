import time
import os
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrapers.job_scraper import fetch_job_postings
from analyzers.llm_analyzer import analyze_job
from storage.sheets_storage import save_jobs_to_sheets
from notifier.telegram_notifier import send_telegram_alert
from config import DEFAULT_CANDIDATE_PROFILE

# OpenClaw Daemon Configuration
SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", 2))
MIN_ALERT_SCORE = int(os.getenv("MIN_ALERT_SCORE", 80))

def run_openclaw_cycle():
    """
    Executes a single OpenClaw autonomous scraping & profiling cycle.
    """
    print("\n" + "="*70)
    print("🤖 [OpenClaw Daemon] Starting Autonomous Job Scraping & Profiling Cycle...")
    print("="*70)

    # 1. Fetch Job Postings
    jobs_df = fetch_job_postings(
        search_term="Senior DevOps Engineer",
        location="Remote",
        results_wanted=5,
        hours_old=24
    )

    if jobs_df.empty:
        print("🤖 [OpenClaw Daemon] No new jobs found in this cycle.")
        return

    processed_records = []

    # 2. AI Processing Loop with Ollama
    for idx, (_, job) in enumerate(jobs_df.iterrows()):
        title = job.get("title", "N/A")
        company = job.get("company", "N/A")
        location = job.get("location", "Remote")
        job_url = job.get("job_url", "")
        description = str(job.get("description", ""))

        print(f"\n🔍 [OpenClaw] Evaluating ({idx+1}/{len(jobs_df)}): {title} @ {company}")

        analysis = analyze_job(
            title=title,
            company=company,
            description=description,
            candidate_profile=DEFAULT_CANDIDATE_PROFILE
        )

        record = {
            "title": title,
            "company": company,
            "location": location,
            "match_score": analysis.match_score,
            "tech_stack": analysis.tech_stack,
            "key_responsibilities": analysis.key_responsibilities,
            "fit_summary": analysis.fit_summary,
            "job_url": job_url
        }

        processed_records.append(record)

        print(f"   🎯 Match Score: {analysis.match_score}/100")
        print(f"   🛠️ Tech Stack: {', '.join(analysis.tech_stack)}")

        # 3. High Match Telegram Alert Trigger
        if analysis.match_score >= MIN_ALERT_SCORE:
            print(f"   🔔 Match score {analysis.match_score} >= {MIN_ALERT_SCORE}. Triggering Telegram Alert!")
            send_telegram_alert(
                title=title,
                company=company,
                location=location,
                match_score=analysis.match_score,
                tech_stack=analysis.tech_stack,
                fit_summary=analysis.fit_summary,
                job_url=job_url
            )

    # 4. Save to Google Sheets
    if processed_records:
        save_jobs_to_sheets(processed_records)

    print("\n✅ [OpenClaw Daemon] Cycle completed successfully.")

def start_daemon_loop():
    print(f"🚀 OpenClaw Autonomous Daemon Active. Interval: every {SCRAPE_INTERVAL_HOURS} hour(s).")
    while True:
        try:
            run_openclaw_cycle()
        except Exception as e:
            print(f"⚠️ OpenClaw Daemon error: {e}")
        
        sleep_seconds = SCRAPE_INTERVAL_HOURS * 3600
        print(f"😴 Sleeping for {SCRAPE_INTERVAL_HOURS} hour(s) until next cycle...")
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    # If run with --one-shot, execute once; otherwise run continuous loop
    if len(sys.argv) > 1 and sys.argv[1] == "--one-shot":
        run_openclaw_cycle()
    else:
        start_daemon_loop()
