import streamlit as st
import pandas as pd
from scrapers.job_scraper import fetch_job_postings
from analyzers.llm_analyzer import analyze_job
from config import DEFAULT_CANDIDATE_PROFILE, OLLAMA_MODEL

st.set_page_config(
    page_title="AI Job Profiler & Scraper",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Autonomous AI Job Scraper & Profiler Agent")
st.caption("Scrape tech postings, run local LLM evaluation (Ollama), and profile match scores.")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")
candidate_profile = st.sidebar.text_area(
    "Candidate Background Profile",
    value=DEFAULT_CANDIDATE_PROFILE,
    height=120
)

st.sidebar.subheader("🔍 Scraping Settings")
search_term = st.sidebar.text_input("Search Title / Keywords", value="Senior DevOps Engineer")
location = st.sidebar.text_input("Location", value="Remote")
results_wanted = st.sidebar.slider("Number of Jobs to Scrape", min_value=1, max_value=20, value=5)
min_score_filter = st.sidebar.slider("Filter Minimum Match Score", min_value=0, max_value=100, value=50)

# Initialize Session State
if "processed_jobs" not in st.session_state:
    st.session_state.processed_jobs = []

col1, col2 = st.columns([2, 1])
with col1:
    if st.button("🚀 Scrape & Analyze Jobs Now", use_container_width=True):
        with st.spinner("Scraping raw job postings from LinkedIn & Indeed..."):
            jobs_df = fetch_job_postings(
                search_term=search_term,
                location=location,
                results_wanted=results_wanted
            )

        if jobs_df.empty:
            st.error("No jobs found or scraper encountered an issue.")
        else:
            st.info(f"Scraped {len(jobs_df)} raw jobs. Analyzing with local Ollama (`{OLLAMA_MODEL}`)...")
            
            progress_bar = st.progress(0)
            results = []
            
            for idx, (_, job) in enumerate(jobs_df.iterrows()):
                title = job.get("title", "N/A")
                company = job.get("company", "N/A")
                job_url = job.get("job_url", "")
                description = str(job.get("description", ""))
                job_location = job.get("location", location)

                # Run AI Analysis
                analysis = analyze_job(
                    title=title,
                    company=company,
                    description=description,
                    candidate_profile=candidate_profile
                )

                job_record = {
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "match_score": analysis.match_score,
                    "tech_stack": analysis.tech_stack,
                    "key_responsibilities": analysis.key_responsibilities,
                    "fit_summary": analysis.fit_summary,
                    "job_url": job_url,
                    "description": description[:500] + "..."
                }
                results.append(job_record)
                progress_bar.progress((idx + 1) / len(jobs_df))

            st.session_state.processed_jobs = results
            st.success(f"Successfully processed {len(results)} jobs!")

# Display Results
st.markdown("---")
st.subheader("📋 Profiled Job Results")

if st.session_state.processed_jobs:
    # Filter by minimum score
    filtered_jobs = [j for j in st.session_state.processed_jobs if j["match_score"] >= min_score_filter]

    st.write(f"Showing **{len(filtered_jobs)}** jobs matching score ≥ **{min_score_filter}**")

    for job in filtered_jobs:
        score = job["match_score"]
        # Score color coding
        score_color = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")

        with st.expander(f"{score_color} **{job['match_score']}/100** | {job['title']} @ {job['company']}"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Company:** {job['company']} | **Location:** {job['location']}")
                st.markdown(f"**Fit Summary:** {job['fit_summary']}")
                st.markdown(f"**Tech Stack:** {', '.join(['`' + t + '`' for t in job['tech_stack']])}")
                if job["job_url"]:
                    st.markdown(f"🔗 [View Original Job Posting]({job['job_url']})")
            with c2:
                st.metric("Match Score", f"{job['match_score']}/100")

            st.markdown("**Key Responsibilities:**")
            for resp in job["key_responsibilities"]:
                st.markdown(f"- {resp}")

    # CSV Download Button
    df_export = pd.DataFrame(st.session_state.processed_jobs)
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="profiled_jobs.csv",
        mime="text/csv"
    )
else:
    st.info("Click 'Scrape & Analyze Jobs Now' above to begin extraction!")
