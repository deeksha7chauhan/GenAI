# crew/crew_tools.py
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

# IMPORTANT: use LangChain's tool decorator so the tool has .invoke()
from langchain.tools import tool


# ------------------------------ helpers ---------------------------------
def _loads(obj: Any) -> Any:
    """Accept str/list/dict/None and return parsed JSON or the object itself."""
    if obj is None:
        return None
    if isinstance(obj, (list, dict)):
        return obj
    if isinstance(obj, str):
        s = obj.strip()
        if not s:
            return None
        # strip accidental code fences
        if s.startswith("```") and s.endswith("```"):
            s = s.strip("` \n")
        try:
            return json.loads(s)
        except Exception:
            return obj
    return obj


def _as_products_list(maybe_products: Any) -> List[Dict[str, Any]]:
    """Coerce many shapes (list, {'products': [...]}, {'items': [...]}) into list[dict]."""
    data = _loads(maybe_products)
    items: Any = data
    if isinstance(data, dict):
        for key in ("products", "items", "results"):
            if key in data and isinstance(data[key], list):
                items = data[key]
                break
    if not isinstance(items, list):
        return []
    return [p for p in items if isinstance(p, dict)]


def _first(d: Dict[str, Any], *keys: str) -> Any:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def _as_float(v: Any) -> Optional[float]:
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.replace("$", "").replace(",", "").strip()
        try:
            return float(s)
        except Exception:
            return None
    return None


def _normalize_product(p: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized product dict without mutating the input."""
    title = _first(p, "title", "product_title", "name") or ""
    price = _as_float(_first(p, "price", "product_price", "amount"))
    retailer = _first(p, "retailer", "seller", "brand")
    url = _first(p, "url", "product_url", "link")
    image_url = _first(p, "image_url", "product_image_url", "thumbnail")

    out = {
        "title": title,
        "price": price,
        "retailer": retailer,
        "url": url,
        "image_url": image_url,
    }
    return {k: v for k, v in out.items() if v is not None}


# ------------------------------ tools -----------------------------------

@tool("product_search")
def product_search_tool(query: str, max_results: int = 10, budget: Optional[float] = None) -> str:
    """
    Stub search. Returns JSON list of products matching the query.
    Replace with a real provider when you're ready.
    """
    q = (query or "").lower()
    if "airpods" in q:
        products = [
            {
                "title": "Apple AirPods (2nd gen) with Charging Case",
                "price": 99.0,
                "retailer": "Apple",
                "url": "https://www.example.com/airpods-2",
                "image_url": "https://www.example.com/airpods-2.jpg",
            },
            {
                "title": "Apple AirPods Pro (2nd gen, USB-C)",
                "price": 199.0,
                "retailer": "Apple",
                "url": "https://www.example.com/airpods-pro-2",
                "image_url": "https://www.example.com/airpods-pro-2.jpg",
            },
            {
                "title": "Apple AirPods Max - Space Gray",
                "price": 449.0,
                "retailer": "Apple",
                "url": "https://www.example.com/airpods-max",
                "image_url": "https://www.example.com/airpods-max.jpg",
            },
        ]
    else:
        products = [
            {
                "title": "Bose QuietComfort 45 Bluetooth Wireless Noise Cancelling Headphones - Black",
                "price": 279.0,
                "retailer": "Bose",
                "url": "https://www.example.com/bose-qc45-black",
                "image_url": "https://www.example.com/bose-qc45-black.jpg",
            },
            {
                "title": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones - Black",
                "price": 348.0,
                "retailer": "Sony",
                "url": "https://www.example.com/sony-wh-1000xm5-black",
                "image_url": "https://www.example.com/sony-wh-1000xm5-black.jpg",
            },
            {
                "title": "Apple AirPods Max - Space Gray",
                "price": 449.0,
                "retailer": "Apple",
                "url": "https://www.example.com/apple-airpods-max-space-gray",
                "image_url": "https://www.example.com/apple-airpods-max-space-gray.jpg",
            },
        ]

    if budget is not None:
        products = [
            p for p in products
            if _as_float(p.get("price")) is not None and _as_float(p.get("price")) <= budget
        ]

    return json.dumps(products[: max(1, int(max_results))])


@tool("price_compare")
def price_compare_tool(products_json: str) -> str:
    """
    Summarize prices across products. Accepts a JSON string, a list,
    or a dict with a 'products' key. Returns a JSON dict.
    """
    products = [_normalize_product(p) for p in _as_products_list(products_json)]
    prices = [p["price"] for p in products if isinstance(p.get("price"), (int, float))]
    count = len(products)

    if not prices:
        return json.dumps({"count": count, "min": None, "max": None, "avg": None, "by_retailer": {}})

    by_retailer: Dict[str, float] = {}
    for p in products:
        if "retailer" in p and isinstance(p.get("price"), (int, float)):
            by_retailer[p["retailer"]] = float(p["price"])

    min_p = min(products, key=lambda x: (x.get("price") if x.get("price") is not None else float("inf")))
    max_p = max(products, key=lambda x: (x.get("price") if x.get("price") is not None else float("-inf")))
    avg = round(sum([float(x) for x in prices]) / len(prices), 2)

    summary = {
        "count": count,
        "min": min_p if min_p.get("price") is not None else None,
        "max": max_p if max_p.get("price") is not None else None,
        "avg": avg if prices else None,
        "by_retailer": by_retailer,
    }
    return json.dumps(summary)


@tool("review_analyze")
def review_analyze_tool(products_json: str, max_reviews: int = 50) -> str:
    """
    Stub review analysis. Returns shapes the recommender expects.
    """
    products = _as_products_list(products_json)
    result = {"count": len(products), "rated_count": 0, "avg_rating": None, "top_rated": []}
    return json.dumps(result)


@tool("recommend")
def recommend_tool(
    products_json: str,
    price_summary_json: str,
    review_summary_json: str,
    budget: Optional[float] = None,
    max_results: int = 5,
) -> str:
    """
    Combine inputs to produce ranked recommendations.
    Accepts flexible JSON shapes; never mutates inputs (prevents 'str' assignment errors).
    """
    products = [_normalize_product(p) for p in _as_products_list(products_json)]
    price_summary = _loads(price_summary_json)
    review_summary = _loads(review_summary_json)

    considered: List[Dict[str, Any]] = []
    for p in products:
        price = _as_float(p.get("price"))
        if price is None:
            continue
        if budget is not None and price > budget:
            continue
        considered.append(p)

    scored: List[Dict[str, Any]] = []
    for p in considered:
        price = float(p["price"])
        reasons: List[str] = []
        if budget is not None:
            reasons.append("Within budget" if price <= budget else "Over budget")
        rec = {
            "title": p.get("title"),
            "price": price,
            "retailer": p.get("retailer"),
            "url": p.get("url"),
            "image_url": p.get("image_url"),
            "score": -price,  # cheaper = better
            "reasons": reasons or ["Lower price preferred"],
        }
        scored.append(rec)

    scored.sort(key=lambda r: (r["score"], r["price"]))
    picks = scored[: max(1, int(max_results))]

    out = {
        "strategy": "price asc; filtered by budget if provided",
        "budget": budget,
        "count_in": len(products),
        "count_considered": len(considered),
        "picks": picks,
        "price_summary": price_summary if isinstance(price_summary, (dict, list)) else None,
        "review_summary": review_summary if isinstance(review_summary, (dict, list)) else None,
    }
    return json.dumps(out)
