from typing import List, Dict
import statistics
from collections import defaultdict
from agentic_shop.agents.utils import Product, normalize_title
from agentic_shop.agents.storage import track_price, get_price_history

class PriceComparisonAgent:
    def compare(self, products: List[Product]) -> Dict[str, Dict]:
        """
        Groups products by normalized title and computes stats & best deal.
        Also tracks price history in SQLite.
        """
        groups: Dict[str, List[Product]] = defaultdict(list)
        for p in products:
            groups[normalize_title(p.title)].append(p)
            track_price(p.id, p.retailer, p.price)

        summary: Dict[str, Dict] = {}
        for key, items in groups.items():
            prices = [i.price for i in items]
            best = min(items, key=lambda x: x.price)
            summary[key] = {
                "items": items,
                "count": len(items),
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": round(statistics.mean(prices), 2),
                "best_deal": best,
                "history": {i.id: get_price_history(i.id) for i in items}
            }
        return summary
