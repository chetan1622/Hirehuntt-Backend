import os
import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make the catch block append a dummy video so we know if it failed
content = content.replace("except Exception as e:\n            continue", "except Exception as e:\n            all_videos.append({'id': 'dQw4w9WgXcQ', 'title': f'Error: {e}', 'author': 'System', 'published': '2026-08-19T00:00:00Z'})\n            continue")

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated backend to show errors")
