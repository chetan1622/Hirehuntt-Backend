import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Search Settings
SEARCH_KEYWORDS = [kw.strip() for kw in os.getenv("SEARCH_KEYWORDS", "Data Scientist, Data Analyst").split(",") if kw.strip()]
SEARCH_LOCATIONS = [loc.strip() for loc in os.getenv("SEARCH_LOCATIONS", "India, Remote").split(",") if loc.strip()]
MATCH_THRESHOLD = int(os.getenv("MATCH_THRESHOLD", "50"))

# Email Settings
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "")

# Directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUMES_DIR = os.path.join(BASE_DIR, "resumes")
