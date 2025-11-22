
# Agentic AI E-Commerce Assistant (Part 3)

Agents:
1) Product Search API Agent (eBay Finding API + optional FakeStore demo)
2) Price Comparison API Agent (stats + best deal + SQLite price history)
3) Review Analysis Agent (Hugging Face Inference API - optional)
4) Recommendation Engine Agent (scores by price fit + sentiment + rating)

Run:
- Copy .env.example to .env and set EBAY_APP_ID (and optional HF API token)
- python run.py --query "wireless earbuds" --budget 75 --max_results 10

Tests: pytest -q
