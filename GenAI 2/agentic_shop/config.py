import os
from dotenv import load_dotenv

load_dotenv()

# Environment: 'production' or 'sandbox'
EBAY_ENV = (os.getenv("EBAY_ENV") or "production").lower()

# OAuth client credentials for Buy APIs
EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID", "")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET", "")

# Space-separated list of scopes (defaults suit Browse read-only)
EBAY_OAUTH_SCOPES = (os.getenv("EBAY_OAUTH_SCOPES") or
                     "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/buy.marketplace.readonly").split()

# Browse API marketplace header (underscore format: EBAY_US, EBAY_GB, ...)
MARKETPLACE = os.getenv("MARKETPLACE", "EBAY_US")

# Optional sentiment
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

# SQLite file for price history
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "price_history.db")

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
