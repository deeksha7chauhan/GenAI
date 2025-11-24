import requests
from typing import List, Dict
from agentic_shop.config import HF_API_TOKEN
from agentic_shop.agents.utils import Product

HF_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
HF_ENDPOINT = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

class ReviewAnalysisAgent:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and bool(HF_API_TOKEN)

    def analyze(self, products: List[Product]) -> Dict[str, Dict]:
        """
        Returns sentiment per product (positive ratio, negative ratio).
        If no HF token or no texts available, returns neutral defaults.
        """
        results: Dict[str, Dict] = {}
        for p in products:
            texts = [r.text for r in p.reviews if r.text] or []
            # Fallback to title if absolutely nothing to analyze
            if not texts and p.title:
                texts = [p.title]
            if not texts:
                results[p.id] = {"pos": 0.5, "neg": 0.5, "details": []}
                continue
            if not self.enabled:
                results[p.id] = {"pos": 0.5, "neg": 0.5, "details": []}
                continue
            pos = neg = 0
            details = []
            for t in texts[:8]:  # keep usage modest
                try:
                    resp = requests.post(
                        HF_ENDPOINT,
                        headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
                        json={"inputs": t},
                        timeout=30
                    )
                    resp.raise_for_status()
                    arr = resp.json()
                    # Expected [[{label: "NEGATIVE", score: ...}, {label: "POSITIVE", score: ...}]]
                    if isinstance(arr, list) and arr and isinstance(arr[0], list):
                        scores = {d["label"]: d["score"] for d in arr[0]}
                        pos += scores.get("POSITIVE", 0.0)
                        neg += scores.get("NEGATIVE", 0.0)
                        details.append(scores)
                except Exception:
                    pass
            total = max(pos + neg, 1e-9)
            results[p.id] = {"pos": round(pos/total, 3), "neg": round(neg/total, 3), "details": details}
        return results
