import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
KEYWORDS_PATH = BASE_DIR / "keywords.json"

X_API_KEY = os.getenv("X_API_KEY", "")
X_API_SECRET = os.getenv("X_API_SECRET", "")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN", "")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "")
POST_HOUR = int(os.getenv("POST_HOUR", "14"))

MAX_POSTS_PER_DAY = 3
DRY_RUN = False

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
GROK_BASE = "https://api.x.ai/v1"

def load_keywords():
    with open(KEYWORDS_PATH) as f:
        return json.load(f)

def save_keywords(data):
    with open(KEYWORDS_PATH, "w") as f:
        json.dump(data, f, indent=2)