import time
from typing import List, Tuple, Dict, Any, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from agentic_shop.agents.utils import Product
from agentic_shop.config import EBAY_ENV, EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, EBAY_OAUTH_SCOPES, MARKETPLACE

# OAuth token endpoints
TOKEN_ENDPOINT_PROD = "https://api.ebay.com/identity/v1/oauth2/token"
TOKEN_ENDPOINT_SBX  = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"

# Browse search endpoints
BROWSE_ENDPOINT_PROD = "https://api.ebay.com/buy/browse/v1/item_summary/search"
BROWSE_ENDPOINT_SBX  = "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search"

class EbayAuthError(Exception): ...
class EbayHTTPError(Exception): ...
class EbayRateLimit(Exception): ...

# simple module-level cache
_token_cache: Dict[str, Any] = {"token": None, "exp": 0}

def _token_expired() -> bool:
    return not _token_cache["token"] or time.time() >= _token_cache["exp"]

def _get_token() -> str:
    """Client-credentials OAuth token for Browse API."""
    if EBAY_ENV not in ("production", "sandbox"):
        raise EbayAuthError("EBAY_ENV must be 'production' or 'sandbox'")
    if not EBAY_CLIENT_ID or not EBAY_CLIENT_SECRET:
        raise EbayAuthError("Missing EBAY_CLIENT_ID/EBAY_CLIENT_SECRET in .env")

    if not _token_expired():
        return _token_cache["token"]

    token_url = TOKEN_ENDPOINT_SBX if EBAY_ENV == "sandbox" else TOKEN_ENDPOINT_PROD
    data = {
        "grant_type": "client_credentials",
        "scope": " ".join(EBAY_OAUTH_SCOPES),
    }
    try:
        r = requests.post(token_url, data=data, auth=(EBAY_CLIENT_ID, EBAY_CLIENT_SECRET), timeout=20)
        r.raise_for_status()
        j = r.json()
        access = j.get("access_token")
        expires = int(j.get("expires_in", 7200))
        if not access:
            raise EbayAuthError(f"OAuth error: {j}")
        _token_cache["token"] = access
        _token_cache["exp"] = time.time() + max(expires - 60, 60)  # refresh 1 min early
        return access
    except requests.RequestException as e:
        raise EbayAuthError(f"OAuth HTTP error: {e}")

@retry(
    reraise=True,
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    retry=retry_if_exception_type((EbayHTTPError, EbayRateLimit))
)
def _browse_search(q: str, limit: int) -> Dict[str, Any]:
    token = _get_token()
    endpoint = BROWSE_ENDPOINT_SBX if EBAY_ENV == "sandbox" else BROWSE_ENDPOINT_PROD
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": MARKETPLACE,  # e.g., EBAY_US
        "Accept": "application/json",
        "User-Agent": "agentic-assistant/1.0",
    }
    params = {"q": q, "limit": str(limit)}

    try:
        r = requests.get(endpoint, headers=headers, params=params, timeout=20)
        status = r.status_code
        if status == 429:
            raise EbayRateLimit("429 Too Many Requests (Browse)")
        if status >= 500:
            raise EbayHTTPError(f"Server {status}")
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        # network/client errors -> retry if transient
        raise EbayHTTPError(str(e))

def search_ebay_browse(query: str, limit: int = 10) -> List[Product]:
    """Search eBay via Buy Browse API. Strict, no fallbacks."""
    try:
        data = _browse_search(query, limit)
    except EbayAuthError as e:
        print(f"[eBay OAuth] {e}")
        return []
    except EbayRateLimit as e:
        print(f"[eBay] Rate limit: {e} — reduce request frequency or request higher limits.")
        return []
    except EbayHTTPError as e:
        print(f"[eBay] HTTP error: {e}")
        return []
    except Exception as e:
        print(f"[eBay] Unexpected: {e}")
        return []

    items = data.get("itemSummaries", []) or []
    out: List[Product] = []
    for it in items:
        item_id = it.get("itemId", "")
        title = it.get("title", "")
        price_obj = it.get("price") or {}
        price = float(price_obj.get("value", 0.0)) if price_obj else 0.0
        currency = price_obj.get("currency", "USD") if price_obj else "USD"
        url = it.get("itemWebUrl") or it.get("itemAffiliateWebUrl") or ""
        img = (it.get("image") or {}).get("imageUrl") or \
              (it.get("thumbnailImages") or [{}])[0].get("imageUrl")

        # buyer reviews if present (not always returned)
        rating = None
        buyer_reviews = it.get("buyerReviews") or {}
        if buyer_reviews.get("ratingAverage") is not None:
            try:
                rating = float(buyer_reviews["ratingAverage"])
            except Exception:
                rating = None

        out.append(Product(
            id=f"ebay:{item_id}",
            title=title,
            price=price,
            currency=currency,
            retailer="eBay",
            url=url,
            image_url=img,
            rating=rating,
            reviews=[],
            extra={}
        ))
    return out
