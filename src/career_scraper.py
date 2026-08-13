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
    """Decodes Bing tracking/redirect URL to get the target destination URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'u' in params:
            u_val = params['u'][0]
            # Strip first 2 characters (typically 'a1')
            b64_str = u_val[2:]
            # Pad if necessary
            padding = len(b64_str) % 4
            if padding:
                b64_str += "=" * (4 - padding)
            decoded = base64.b64decode(b64_str).decode('utf-8', errors='ignore')
            return decoded
    except Exception as e:
        pass
    return url

def scrape_career_sites(keywords, location, limit=5):
    """
    Finds job openings on Lever and Greenhouse using Bing search queries.
    Returns a list of dicts with job details: title, company, location, link, description.
    """
    jobs = []
    
    # We query: site:greenhouse.io OR site:lever.co "keyword" "location"
    queries = [
        f'site:greenhouse.io "{keywords}" "{location}"',
        f'site:lever.co "{keywords}" "{location}"'
    ]
    
    for query in queries:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.bing.com/search?q={encoded_query}"
        
        try:
            print(f"Searching career sites via Bing: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"Bing request failed with code {response.status_code}")
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
                
                # Decode Bing tracking URL
                link = decode_bing_url(raw_link)
                
                # Double-check it's a valid greenhouse/lever job posting URL
                if "greenhouse.io" not in link and "lever.co" not in link:
                    continue
                
                # Title extraction
                title = link_elem.text.strip()
                title = re.sub(r'\s+-\s+.*$', '', title)
                title = re.sub(r'\s*\|\s*.*$', '', title)
                
                # Guess company name from URL
                company = "Unknown"
                if "lever.co" in link:
                    match = re.search(r'lever\.co/([^/]+)', link)
                    if match:
                        company = match.group(1).replace("-", " ").title()
                elif "greenhouse.io" in link:
                    match = re.search(r'greenhouse\.io/([^/]+)', link)
                    if match:
                        company = match.group(1).replace("-", " ").title()
                
                # Snippet description
                snippet_elem = result.find("div", class_="b_caption")
                snippet = snippet_elem.text.strip() if snippet_elem else ""
                
                # Fetch full description
                description = fetch_full_career_description(link)
                if not description:
                    description = snippet
                
                jobs.append({
                    "id": link,
                    "source": "Greenhouse/Lever" if "greenhouse" in link or "lever" in link else "Career Site",
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
    """Fetches the full description of a Lever or Greenhouse job posting."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return ""
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Lever parsing
        if "lever.co" in url:
            # Lever JDs are inside elements with class 'section'
            sections = soup.find_all("div", class_="section")
            text = " ".join([sec.get_text(separator=" ") for sec in sections])
            return text.strip()
            
        # Greenhouse parsing
        elif "greenhouse.io" in url:
            # Greenhouse JDs are inside elements with id 'content'
            content = soup.find("div", id="content")
            if content:
                return content.get_text(separator=" ").strip()
            
            # Alternative layout for greenhouse boards
            body = soup.find("div", class_="job-body")
            if body:
                return body.get_text(separator=" ").strip()
                
        return ""
    except Exception as e:
        print(f"Error fetching full description from {url}: {e}")
        return ""
