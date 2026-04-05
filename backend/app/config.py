import os
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
GEMINI_API_KEY_SCHEMA: str = os.getenv("GEMINI_API_KEY_SCHEMA", "")
GEMINI_API_KEY_EXTRACTOR: str = os.getenv("GEMINI_API_KEY_EXTRACTOR", "")

SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
SEARCH_NUM_RESULTS = 15

SCRAPE_SEMAPHORE_LIMIT = 5
SCRAPE_TIMEOUT_SECONDS = 10

CHUNK_MIN_WORDS = 200
CHUNK_MAX_WORDS = 350

GEMINI_MODEL = "gemini-2.5-flash"

FUZZY_MATCH_THRESHOLD = 90
