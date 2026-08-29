import urllib.request
import re

handles = [
    '@RiyaSharma90349', '@DailyRojgarwithVivek', '@dailyJobsupdates-k6t',
    '@CareerLaunchin', '@Jobsearchguru4u', '@dailyjobupdates3',
    '@govtjobalert1', '@Jobnewspost', '@GlobalJobUpdate', '@DevarshiMishraTrainingChannel',
    'c/govtjobgenuinenotificationchannel'
]

channel_ids = {
    'UC87T5nLnEjJjdEqVs6B5UTw': 'UC87T5nLnEjJjdEqVs6B5UTw',
    'UCsUXbMFZyIJwv2a9YaEKvEA': 'UCsUXbMFZyIJwv2a9YaEKvEA'
}

for h in handles:
    url = f'https://www.youtube.com/{h}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        match = re.search(r'itemprop="channelId" content="(UC[A-Za-z0-9_-]+)"', html)
        if match:
            channel_ids[h] = match.group(1)
        else:
            match = re.search(r'"channelId":"(UC[A-Za-z0-9_-]+)"', html)
            if match:
                channel_ids[h] = match.group(1)
            else:
                channel_ids[h] = 'NOT_FOUND'
    except Exception as e:
        channel_ids[h] = f'ERROR: {e}'

import json
with open('resolved_channels.json', 'w') as f:
    json.dump(channel_ids, f, indent=2)
print("Channels resolved and saved to resolved_channels.json")
