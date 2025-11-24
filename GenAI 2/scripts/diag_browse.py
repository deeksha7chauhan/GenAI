import os, requests
from dotenv import load_dotenv
load_dotenv()

ENV = (os.getenv("EBAY_ENV") or "production").lower()
CID = os.getenv("EBAY_CLIENT_ID")
SEC = os.getenv("EBAY_CLIENT_SECRET")
SCOPES = (os.getenv("EBAY_OAUTH_SCOPES") or "").split()
MP = os.getenv("MARKETPLACE", "EBAY_US")

token_url = "https://api.ebay.com/identity/v1/oauth2/token" if ENV=="production" \
            else "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
r = requests.post(token_url, data={"grant_type":"client_credentials","scope":" ".join(SCOPES)},
                  auth=(CID, SEC), timeout=20)
print("OAuth:", r.status_code)
tok = r.json().get("access_token")
assert tok, r.text

endpoint = "https://api.ebay.com/buy/browse/v1/item_summary/search" if ENV=="production" \
           else "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search"
h = {"Authorization": f"Bearer {tok}", "X-EBAY-C-MARKETPLACE-ID": MP, "Accept":"application/json"}
q = {"q":"laptop", "limit":"5"}
s = requests.get(endpoint, headers=h, params=q, timeout=20)
print("Search:", s.status_code)
j = s.json()
print("Count:", len(j.get("itemSummaries", []) or []))
