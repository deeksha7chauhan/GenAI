from typing import List, Dict, Any
from agentic_shop.agents.utils import Product

class RecommendationEngineAgent:
    def recommend(self,
                  products: List[Product],
                  price_summary: Dict[str, Dict],
                  sentiments: Dict[str, Dict],
                  budget: float | None = None) -> List[Dict[str, Any]]:
        """
        Simple scoring:
        - Price fit (closer to budget is better; under budget rewarded)
        - Sentiment positive ratio
        - Product rating if provided
        """
        scored = []
        for p in products:
            s = sentiments.get(p.id, {"pos": 0.5})
            pos = s.get("pos", 0.5)
            # price fit
            if budget is not None and budget > 0:
                if p.price <= budget:
                    price_score = 1.0 - (budget - p.price) / max(budget, 1e-9) * 0.5  # gentle penalty when far below budget
                else:
                    price_score = max(0.0, 1.0 - (p.price - budget) / (budget * 2))  # penalize over-budget
            else:
                price_score = 0.7
            rating_score = (p.rating / 5.0) if p.rating else 0.5
            score = 0.5*price_score + 0.3*pos + 0.2*rating_score
            scored.append({
                "product": p,
                "score": round(score, 3),
                "sentiment_pos": pos
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored
