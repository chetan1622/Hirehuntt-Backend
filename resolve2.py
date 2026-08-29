import urllib.request
import re
import json

handles = [
    '@RiyaSharma90349', '@DailyRojgarwithVivek', '@dailyJobsupdates-k6t',
    '@CareerLaunchin', '@Jobsearchguru4u', '@dailyjobupdates3',
    '@govtjobalert1', '@Jobnewspost', '@GlobalJobUpdate', '@DevarshiMishraTrainingChannel',
    'c/govtjobgenuinenotificationchannel'
]

channel_ids = {
    'UC87T5nLnEjJjdEqVs6B5UTw': 'UC87T5nLnEjJjdEqVs6B5UTw',
    'UCsUXbMFZyIJwv2a9YaEKvEA': 'UCsUXbMFZyIJwv2a9YaEKvEA',
    '@ErinMcgoff': 'UCVv2I2H53f2rJ-lU9xN4lYQ', # Added one for interview tips
    '@VanshikaGarg': 'UC6l-9C78822v4kU7m_eI2OQ', # Another for interview tips
    '@DikshaArora': 'UCyY9x3Lw24GgU61YF4F_2mA' # Another
}

for h in handles:
    url = f'https://www.youtube.com/{h}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Youtube puts channel ID in many places. The most reliable is usually in the browseEndpoint.
        match = re.search(r'"browseId":"(UC[a-zA-Z0-9_-]{22})"', html)
        if match:
            channel_ids[h] = match.group(1)
            continue
            
        match2 = re.search(r'itemprop="channelId" content="(UC[a-zA-Z0-9_-]{22})"', html)
        if match2:
            channel_ids[h] = match2.group(1)
            continue
            
        channel_ids[h] = 'NOT_FOUND'
    except Exception as e:
        channel_ids[h] = f'ERROR: {e}'

with open('resolved.json', 'w') as f:
    json.dump(channel_ids, f, indent=2)
