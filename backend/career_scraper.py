import requests
from bs4 import BeautifulSoup
import time
import re
import urllib.parse
import base64

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def decode_bing_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'u' in params:
            u_val = params['u'][0]
            b64_str = u_val[2:]
            padding = len(b64_str) % 4
            if padding:
                b64_str += "=" * (4 - padding)
            decoded = base64.b64decode(b64_str).decode('utf-8', errors='ignore')
            return decoded
    except Exception as e:
        pass
    return url

def scrape_career_sites(keywords, location, experience=None, limit=5):
    jobs = []
    # Incorporate experience into keywords if available
    exp_keyword = f" {experience}" if experience and experience != "Any Level" else ""
    search_term = f"{keywords}{exp_keyword}"
    
    queries = [
        f'site:greenhouse.io "{search_term}" "{location}"',
        f'site:lever.co "{search_term}" "{location}"',
        f'site:glassdoor.co.in/job-listing "{search_term}" "{location}"',
        f'site:glassdoor.com/job-listing "{search_term}" "{location}"'
    ]
    
    for query in queries:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.bing.com/search?q={encoded_query}"
        
        try:
            print(f"Searching career sites via Bing: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("li", class_="b_algo")
            
            for result in results:
                if len(jobs) >= limit:
                    break
                    
                link_elem = result.find("a")
                if not link_elem or not link_elem.get("href"):
                    continue
                raw_link = link_elem["href"]
                
                link = decode_bing_url(raw_link)
                
                if not any(domain in link for domain in ["greenhouse.io", "lever.co", "glassdoor.co.in", "glassdoor.com"]):
                    continue
                
                title = link_elem.text.strip()
                title = re.sub(r'\s+-\s+.*$', '', title)
                title = re.sub(r'\s*\|\s*.*$', '', title)
                
                company = "Unknown"
                if "lever.co" in link:
                    match = re.search(r'lever\.co/([^/]+)', link)
                    if match:
                        company = match.group(1).replace("-", " ").title()
                elif "greenhouse.io" in link:
                    match = re.search(r'greenhouse\.io/([^/]+)', link)
                    if match:
                        company = match.group(1).replace("-", " ").title()
                elif "glassdoor" in link:
                    # e.g., glassdoor.co.in/job-listing/data-scientist-somecompany-JV_IC...
                    company_match = re.search(r'-([^-]+)-JV_IC', link)
                    if company_match:
                        company = company_match.group(1).replace("-", " ").title()
                
                snippet_elem = result.find("div", class_="b_caption")
                snippet = snippet_elem.text.strip() if snippet_elem else ""
                
                description = fetch_full_career_description(link)
                if not description:
                    description = snippet
                
                jobs.append({
                    "id": link,
                    "source": "Glassdoor" if "glassdoor" in link else "Greenhouse/Lever",
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "description": description
                })
                
                time.sleep(1)
                
        except Exception as e:
            print(f"Error searching career sites: {e}")
            
    return jobs[:limit]

def fetch_full_career_description(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return ""
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        if "lever.co" in url:
            sections = soup.find_all("div", class_="section")
            text = " ".join([sec.get_text(separator=" ") for sec in sections])
            return text.strip()
            
        elif "greenhouse.io" in url:
            content = soup.find("div", id="content")
            if content:
                return content.get_text(separator=" ").strip()
            body = soup.find("div", class_="job-body")
            if body:
                return body.get_text(separator=" ").strip()
                
        return ""
    except Exception as e:
        return ""
