import os

channel_ids = [
    "UC87T5nLnEjJjdEqVs6B5UTw", "UCsUXbMFZyIJwv2a9YaEKvEA", "UCVv2I2H53f2rJ-lU9xN4lYQ",
    "UC6l-9C78822v4kU7m_eI2OQ", "UCyY9x3Lw24GgU61YF4F_2mA", "UCO3cTcKMjWOPmTd5qokhkcQ",
    "UCVFYLx9PUjl9V6uvFiXwC8Q", "UCPo3z9kQcStnaeJskL2iPIQ", "UCdAW1mGF8l_QFhwwPRqMdbg",
    "UCVKyjXbEKdU1yj35hlUvKPQ", "UCQAd6hDzzUqvFbOvVK4kUFg", "UCfNk0lfM8NargaERN43mtGg",
    "UC7dDWq1MhexS37djmPFlCzA", "UCEo7ReLzQp_YYYManmLbFuQ", "UCRytOb5kiG9gWig30qHO6Ew",
    "UCx0QsFe_JEXU98HYNVU8FCA"
]

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

shorts_code = f"""
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

YOUTUBE_CHANNELS = {channel_ids}
_shorts_cache = {{"data": [], "timestamp": 0}}

@app.get("/api/shorts")
def get_shorts():
    import time
    global _shorts_cache
    # Cache for 1 hour to avoid spamming YouTube and keep app fast
    if time.time() - _shorts_cache["timestamp"] < 3600 and _shorts_cache["data"]:
        return _shorts_cache["data"]

    all_videos = []
    for cid in YOUTUBE_CHANNELS:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={{cid}}"
        try:
            req = urllib.request.Request(url, headers={{'User-Agent': 'Mozilla/5.0'}})
            resp = urllib.request.urlopen(req).read()
            root = ET.fromstring(resp)
            # Find all entries (videos)
            for entry in root.findall("{{http://www.w3.org/2005/Atom}}entry")[:3]: # Get latest 3 per channel
                video_id = entry.find("{{http://www.youtube.com/xml/schemas/2015}}videoId").text
                title = entry.find("{{http://www.w3.org/2005/Atom}}title").text
                pub_date = entry.find("{{http://www.w3.org/2005/Atom}}published").text
                author = entry.find("{{http://www.w3.org/2005/Atom}}author/{{http://www.w3.org/2005/Atom}}name").text
                
                # Basic check if it's likely a short (often shorts titles have #shorts, but we can just serve them as shorts anyway)
                all_videos.append({{
                    "id": video_id,
                    "title": title,
                    "author": author,
                    "published": pub_date
                }})
        except Exception as e:
            continue

    # Sort by published date descending
    all_videos.sort(key=lambda x: x["published"], reverse=True)
    
    _shorts_cache["data"] = all_videos
    _shorts_cache["timestamp"] = time.time()
    
    return all_videos
"""

if "@app.get(\"/api/shorts\")" not in content:
    content += "\n" + shorts_code

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added /api/shorts endpoint to backend")
