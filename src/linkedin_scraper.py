import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

# Set user-agent header to look like a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_linkedin_jobs(keywords, location, limit=10):
    """
    Scrapes jobs from LinkedIn's guest job search API.
    Returns a list of dicts with job details: id, title, company, location, link, description.
    """
    jobs = []
    encoded_keywords = urllib.parse.quote(keywords)
    encoded_location = urllib.parse.quote(location)
    
    # LinkedIn returns jobs in chunks of 25
    for start in range(0, limit, 25):
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encoded_keywords}&location={encoded_location}&start={start}"
        
        try:
            print(f"Fetching LinkedIn jobs from: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch LinkedIn jobs: Status code {response.status_code}")
                break
                
            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("li")
            
            if not job_cards:
                print("No more jobs found.")
                break
                
            for card in job_cards:
                if len(jobs) >= limit:
                    break
                    
                # Extract job ID
                job_id_elem = card.find("div", {"data-entity-urn": True})
                if not job_id_elem:
                    continue
                urn = job_id_elem["data-entity-urn"]
                job_id = urn.split(":")[-1]
                
                # Extract title
                title_elem = card.find("h3", class_="base-search-card__title")
                title = title_elem.text.strip() if title_elem else "N/A"
                
                # Extract company
                company_elem = card.find("h4", class_="base-search-card__subtitle")
                company = company_elem.text.strip() if company_elem else "N/A"
                
                # Extract location
                location_elem = card.find("span", class_="job-search-card__location")
                loc = location_elem.text.strip() if location_elem else "N/A"
                
                # Extract link
                link_elem = card.find("a", class_="base-card__full-link")
                link = link_elem["href"].split("?")[0] if link_elem else f"https://www.linkedin.com/jobs/view/{job_id}"
                
                # Fetch description
                description = fetch_job_description(job_id)
                
                jobs.append({
                    "id": job_id,
                    "source": "LinkedIn",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "link": link,
                    "description": description
                })
                
                # Gentle sleep to prevent rate limiting
                time.sleep(1)
                
        except Exception as e:
            print(f"Error scraping LinkedIn: {e}")
            break
            
    return jobs

def fetch_job_description(job_id):
    """Fetches job description text from LinkedIn's guest jobPosting API."""
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Look for the container that holds the job description text
            desc_elem = soup.select_one(".show-more-less-html__markup")
            if desc_elem:
                return desc_elem.get_text(separator=" ").strip()
            return soup.get_text(separator=" ").strip()
        else:
            print(f"Failed to fetch job description for {job_id}: Code {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error getting description for {job_id}: {e}")
        return ""
