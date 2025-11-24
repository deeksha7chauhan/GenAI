Agentic AI E-Commerce Assistant (Part 3)

An agentic shopping assistant that searches real marketplaces, compares prices across retailers, analyzes reviews, and recommends the best products against a user’s requirements and budget.

Real sources (no fake data):

eBay Buy Browse API (production): /buy/browse/v1/item_summary/search + /buy/browse/v1/item/{item_id}

Google Shopping via SerpApi (multi-retailer feed)

(Optional) Sentiment via Hugging Face Inference API

Features & Agents

Product Search API Agent

Queries eBay Browse and SerpApi Google Shopping for live products.

Normalizes results: title, price, currency, retailer, url, image, rating.

Price Comparison API Agent

Aggregates prices across all sources.

Persists observations in SQLite (data/price_history.db) to track trends over time.

Review Analysis Agent (optional)

Uses Hugging Face sentiment (e.g., distilbert-base-uncased-finetuned-sst-2-english) on available descriptions/ratings.

Neutral fallback if disabled or unavailable.

Recommendation Engine Agent

Scores and ranks products using price, rating, sentiment, and budget fit.

Produces a concise, prioritized list with links.

Orchestrator glues the agents together:
Search → (Enrich) → PriceComparison → ReviewAnalysis → Recommendation.

Project Structure
GenAI/
├─ .env                         # local secrets (not committed)
├─ requirements.txt
├─ run.py                       # CLI entrypoint
├─ scripts/
│  ├─ diag_browse.py            # eBay OAuth + search diagnostic
│  └─ diag_ebay.py              # legacy finding API diag (optional)
└─ agentic_shop/
   ├─ config.py                 # reads .env and global config
   ├─ orchestrator.py           # agent workflow & console output
   └─ agents/
      ├─ product_search.py      # calls eBay Browse + SerpApi
      ├─ price_comparison.py    # aggregates & stores price history
      ├─ review_analysis.py     # optional HF sentiment
      ├─ recommendation.py      # scoring & ranking
      ├─ utils.py               # Product/Review dataclasses, helpers
      └─ providers/
         ├─ ebay.py             # OAuth + search + get_item
         └─ serpapi_shopping.py # Google Shopping via SerpApi

Prerequisites

Python 3.10+

VS Code

Git Bash (Windows)

Accounts/keys:

eBay Production keyset (App ID / Client ID and Cert ID / Client Secret)

SerpApi API key (Google Shopping engine)

(Optional) Hugging Face token

Quickstart (Windows • Git Bash)
# 1) Create project folder (if starting fresh)
mkdir -p "/c/Users/Lenovo/Documents/GenAI" && cd "/c/Users/Lenovo/Documents/GenAI"

# 2) Python venv
python -m venv .venv
source .venv/Scripts/activate

# 3) Install deps
pip install -U pip
pip install -r requirements.txt

Create .env (copy–paste)
# === eBay Buy Browse API (Production) ===
EBAY_ENV=production

# Your production keyset
EBAY_CLIENT_ID=YOUR_PRODUCTION_APP_ID          # App ID / Client ID
EBAY_CLIENT_SECRET=YOUR_PRODUCTION_CERT_ID     # Cert ID / Client Secret

# Browse uses underscore format (e.g., EBAY_US)
MARKETPLACE=EBAY_US

# Required scope for Browse search
EBAY_OAUTH_SCOPES=https://api.ebay.com/oauth/api_scope

# SerpApi (Google Shopping)
SERPAPI_API_KEY=YOUR_SERPAPI_KEY

# Optional: Hugging Face token (or leave blank and run with --no_sentiment)
HF_API_TOKEN=


Where is “Cert ID”? In the eBay Developer Portal → Apps & Keys → your Production keyset → Cert ID (Client Secret).

Run
# Activate venv (if not already)
source .venv/Scripts/activate

# Example queries
python run.py --query "airpods" --budget 300
python run.py --query "drone"   --budget 250

# Disable sentiment if no HF token
python run.py --query "ssd 1tb" --budget 120 --no_sentiment


You should see tables for Found Products, Price Comparison & History, Review Analysis, and Top Recommendations.

Diagnostics

Quickly verify OAuth + Browse:

python scripts/diag_browse.py
# Expect: OAuth: 200, Search: 200, Count: >0


Common pitfalls:

invalid_scope → keep EBAY_OAUTH_SCOPES=https://api.ebay.com/oauth/api_scope

401 Unauthorized → wrong keyset, expired token, or MARKETPLACE not EBAY_US

500 / Rate limiting → re-run later, reduce frequency

How it Meets the Rubric

Product Search API Agent

Integrates eBay Browse (production) and SerpApi Google Shopping for live product discovery.

Pulls title, price, rating, url, image.

Price Comparison API Agent

Compares prices across multiple retailers (eBay + retailers aggregated by SerpApi).

Tracks observed prices in SQLite (data/price_history.db) to surface best deals over time.

Review Analysis Agent

(Optional) Uses Hugging Face to score item descriptions/ratings for sentiment.

Graceful neutral fallback or run with --no_sentiment.

Recommendation Engine Agent

Combines search results, price data, and review insights to rank options for the user’s budget and intent.

Integration & Execution

Modular agents in agentic_shop/agents/*.

Centralized workflow in orchestrator.py.

Testing scenarios supported via CLI; add PyTest tests under agentic_shop/tests/.

Suggested Test Scenarios

Budget-constrained:
python run.py --query "gaming headset" --budget 50

Feature-specific:
python run.py --query "wireless earbuds noise cancelling" --budget 120

Comparative shopping:
python run.py --query "mechanical keyboard" --budget 150

Troubleshooting

No results: try broader keywords; ensure MARKETPLACE=EBAY_US.

401 / invalid token: verify Production Client ID/Secret; re-activate venv; ensure scope string is exactly the base scope; no quotes.

Sentiment shows 0.00: add a valid HF_API_TOKEN or run with --no_sentiment.

Windows path issues: use Git Bash; source .venv/Scripts/activate.

Security & Compliance

No fabricated data. All results come from live external APIs (eBay/SerpApi/HF).

Do not commit .env or credentials.

Respect API ToS and rate limits.

Extend

Add more providers (Etsy, Rakuten/CJ affiliate product APIs, Walmart via third-party aggregator).

Fetch richer details per item (brand/condition/specs) and incorporate into recommendations.

Visualize price history from SQLite.