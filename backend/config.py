import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "admin@hirehuntt.in")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Data directory for persistent storage (e.g. Railway Volumes mapped to /app/data)
DATA_DIR = os.getenv("DATA_DIR")
if DATA_DIR and not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# Upload settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if DATA_DIR:
    UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
else:
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
