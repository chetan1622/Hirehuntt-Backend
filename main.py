import os
import sys
from src import config
from src.linkedin_scraper import scrape_linkedin_jobs
from src.career_scraper import scrape_career_sites
from src.resume_matcher import ResumeMatcher
from src.notifier import send_email_report

def main():
    print("="*60)
    print("         JOB HUNT AUTOMATION WORKFLOW - STARTING")
    print("="*60)
    
    # 1. Setup paths and check resumes
    resumes_dir = config.RESUMES_DIR
    if not os.path.exists(resumes_dir):
        os.makedirs(resumes_dir)
        print(f"Created directory: {resumes_dir}")
        
    ds_resume_file = None
    da_resume_file = None
    
    # Find any PDF/TXT in resumes folder matching name patterns
    for file in os.listdir(resumes_dir):
        file_lower = file.lower()
        if "data_science" in file_lower or "datascience" in file_lower or "ds" in file_lower or "science" in file_lower:
            ds_resume_file = os.path.join(resumes_dir, file)
        elif "data_analyst" in file_lower or "dataanalyst" in file_lower or "da" in file_lower or "analyst" in file_lower:
            da_resume_file = os.path.join(resumes_dir, file)

    # If not found, look for fallback defaults
    if not ds_resume_file:
        ds_resume_file = os.path.join(resumes_dir, "ds_resume.pdf")
    if not da_resume_file:
        da_resume_file = os.path.join(resumes_dir, "da_resume.pdf")

    # Guide user if files do not exist
    if not os.path.exists(ds_resume_file) or not os.path.exists(da_resume_file):
        print("\n" + "!"*60)
        print("WARNING: Resume files not found in the 'resumes/' folder!")
        print("Please place your resumes in the 'resumes/' folder:")
        print(f"1. Data Science Resume -> {ds_resume_file}")
        print(f"2. Data Analyst Resume -> {da_resume_file}")
        print("!"*60 + "\n")
        
        # Creating dummy resumes for test run so the program doesn't fail
        if not os.path.exists(ds_resume_file):
            print("Creating dummy Data Science resume text file for testing...")
            with open(ds_resume_file.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write("Data Scientist. Python, SQL, machine learning, statistics, pandas, numpy, scikit-learn, deep learning, tensorflow, pytorch, predictive modeling, data visualization, Tableau, spark.")
            ds_resume_file = ds_resume_file.replace('.pdf', '.txt')
            
        if not os.path.exists(da_resume_file):
            print("Creating dummy Data Analyst resume text file for testing...")
            with open(da_resume_file.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write("Data Analyst. SQL, Excel, Tableau, Power BI, Python, pandas, data cleaning, data visualization, dashboard reporting, A/B testing, data wrangling, statistics.")
            da_resume_file = da_resume_file.replace('.pdf', '.txt')

    print(f"Loading DS resume: {ds_resume_file}")
    print(f"Loading DA resume: {da_resume_file}")
    
    # Initialize Resume Matcher
    matcher = ResumeMatcher(ds_resume_path=ds_resume_file, da_resume_path=da_resume_file)

    # 2. Gather Jobs
    all_raw_jobs = []
    seen_links = set()
    
    print("\nStarting search queries...")
    for keyword in config.SEARCH_KEYWORDS:
        for location in config.SEARCH_LOCATIONS:
            print(f"\n--- Searching for: '{keyword}' in '{location}' ---")
            
            # Scrape LinkedIn guest
            linkedin_jobs = scrape_linkedin_jobs(keyword, location, limit=15)
            print(f"Found {len(linkedin_jobs)} jobs on LinkedIn.")
            
            # Scrape Career Sites (Lever/Greenhouse)
            career_jobs = scrape_career_sites(keyword, location, limit=5)
            print(f"Found {len(career_jobs)} jobs on Greenhouse/Lever.")
            
            # Deduplicate and merge
            for job in linkedin_jobs + career_jobs:
                if job['link'] not in seen_links:
                    seen_links.add(job['link'])
                    all_raw_jobs.append(job)

    print(f"\nTotal unique jobs scraped: {len(all_raw_jobs)}")

    # 3. Score & Filter Jobs
    print("\nMatching resumes against job descriptions...")
    scored_jobs = []
    
    for job in all_raw_jobs:
        # Calculate matching score against both resumes
        match_info = matcher.calculate_match(job['description'])
        
        # Check if it meets the match threshold
        if match_info['score'] >= config.MATCH_THRESHOLD:
            job['match_info'] = match_info
            scored_jobs.append(job)
            print(f"MATCH: {job['title']} at {job['company']} - Score: {match_info['score']}% ({match_info['best_match']})")
        else:
            print(f"SKIP: {job['title']} at {job['company']} - Score too low: {match_info['score']}%")

    # Sort scored jobs by score descending
    scored_jobs.sort(key=lambda x: x['match_info']['score'], reverse=True)
    print(f"\nTotal jobs passing matching threshold ({config.MATCH_THRESHOLD}%): {len(scored_jobs)}")

    # 4. Notify User
    print("\nSending daily email digest...")
    email_sent = send_email_report(scored_jobs)
    
    if email_sent:
        print("\nWorkflow completed successfully!")
    else:
        print("\nWorkflow completed. (Email was skipped or failed; see logs above).")
        
    print("="*60)

if __name__ == "__main__":
    main()
