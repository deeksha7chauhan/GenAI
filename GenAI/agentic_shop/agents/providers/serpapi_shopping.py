import re
import requests
from typing import List
from agentic_shop.agents.utils import Product

API = "https://serpapi.com/search.json"

_CURRENCY_BY_SYMBOL = {
    "$": "USD", "€": "EUR", "£": "GBP", "₹": "INR", "¥": "JPY", "C$": "CAD", "A$": "AUD"
}

def _parse_price(price_str: str) -> (float, str):
    """
    Convert strings like "$49.99", "US $39.00", "£29.99", "49.00 USD", "$49.99 to $59.99"
    into (49.99, "USD"). If it's a range, take the lower bound.
    """
    if not price_str:
        return 0.0, "USD"
    s = price_str.strip()

    # Try to detect currency symbol
    cur = "USD"
    # prioritize multi-char symbols like C$, A$
    if s.startswith("C$"):
        cur = "CAD"
    elif s.startswith("A$"):
        cur = "AUD"
    else:
        for sym, cc in _CURRENCY_BY_SYMBOL.items():
            if s.startswith(sym):
                cur = cc
                break
        # also handle trailing currency code
        m = re.search(r"\b([A-Z]{3})\b", s)
        if m:
            cur = m.group(1)

    # choose first numeric occurrence
    m = re.search(r"([0-9]+(?:[.,][0-9]{1,2})?)", s)
    if not m:
        return 0.0, cur
    val = m.group(1).replace(",", "")
    try:
        return float(val), cur
    except Exception:
        return 0.0, cur

def search_serpapi_shopping(api_key: str, query: str, limit: int = 10, gl: str = "us", hl: str = "en") -> List[Product]:
    """
    Google Shopping via SerpApi. Returns multiple retailers for price comparison.
    """
    if not api_key:
        return []

    params = {
        "engine": "google_shopping",
        "q": query,
        "num": str(limit),
        "gl": gl,
        "hl": hl,
        "api_key": api_key,
    }
    try:
        r = requests.get(API, params=params, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    items = data.get("shopping_results", []) or []
    out: List[Product] = []
    for it in items[:limit]:
        title = it.get("title", "")
        url = it.get("link", "")
        source = it.get("source", "Google Shopping")
        thumb = None
        if it.get("thumbnail"):
            thumb = it["thumbnail"]
        elif it.get("product_photos"):
            arr = it["product_photos"]
            if isinstance(arr, list) and arr:
                thumb = arr[0].get("thumbnail")

        price_val, currency = _parse_price(it.get("price", "") or it.get("extracted_price", ""))
        # SerpApi may also provide "rating"
        rating = None
        if it.get("rating") is not None:
            try:
                rating = float(it["rating"])
            except Exception:
                rating = None

        out.append(Product(
            id=f"serpapi:{it.get('position', '')}:{it.get('product_id', '')}",
            title=title,
            price=price_val,
            currency=currency,
            retailer=source,
            url=url,
            image_url=thumb,
            rating=rating,
            reviews=[],
            extra={}
        ))
    return out
