import os, json, requests
from dotenv import load_dotenv
load_dotenv()

APP_ID = os.getenv("EBAY_APP_ID") or os.getenv("EBAY_CLIENT_ID") or ""
ENV = (os.getenv("EBAY_ENV") or "production").lower()
GLOBAL_ID = os.getenv("MARKETPLACE", "EBAY-US")

ENDPOINT = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1" if ENV=="sandbox" else \
           "https://svcs.ebay.com/services/search/FindingService/v1"

params = {
    "OPERATION-NAME": "findItemsByKeywords",
    "SERVICE-VERSION": "1.0.0",
    "SECURITY-APPNAME": APP_ID,
    "RESPONSE-DATA-FORMAT": "JSON",
    "keywords": "test",
    "paginationInput.entriesPerPage": "5",
    "GLOBAL-ID": GLOBAL_ID,
}

print(f"ENV={ENV} ENDPOINT={ENDPOINT} APP_ID={'SET' if APP_ID else 'MISSING'} GLOBAL_ID={GLOBAL_ID}")
r = requests.get(ENDPOINT, params=params, timeout=20)
print("HTTP", r.status_code)
j = r.json()
ack = j.get("findItemsByKeywordsResponse", [{}])[0].get("ack", [""])[0]
cnt = j.get("findItemsByKeywordsResponse", [{}])[0].get("searchResult", [{}])[0].get("@count", "0")
print("ACK:", ack, "COUNT:", cnt)
if ack != "Success" or cnt == "0":
    print(json.dumps(j, indent=2)[:2000])
