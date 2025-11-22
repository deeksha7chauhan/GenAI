from typing import List
from agentic_shop.agents.utils import Product
from agentic_shop.agents.providers.ebay import search_ebay_browse
from agentic_shop.config import SERPAPI_API_KEY
from agentic_shop.agents.providers.serpapi_shopping import search_serpapi_shopping

class ProductSearchAgent:
    """Real external sources: eBay Browse + Google Shopping (SerpApi)."""
    def search(self, query: str, limit: int = 10) -> List[Product]:
        results: List[Product] = []
        results.extend(search_ebay_browse(query, limit=limit))
        results.extend(search_serpapi_shopping(SERPAPI_API_KEY, query, limit=limit))

        # Deduplicate by (retailer, id)
        seen = set()
        deduped: List[Product] = []
        for p in results:
            key = (p.retailer, p.id)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(p)
        return deduped
