from agentic_shop.agents.recommendation import RecommendationEngineAgent
from agentic_shop.agents.utils import Product

def test_recommend_scoring_basic():
    p1 = Product(id="x1", title="Test A", price=50.0, currency="USD", retailer="R1", url="u1", rating=4.5)
    p2 = Product(id="x2", title="Test B", price=80.0, currency="USD", retailer="R2", url="u2", rating=None)
    engine = RecommendationEngineAgent()
    res = engine.recommend([p1, p2], {}, {"x1":{"pos":0.9}, "x2":{"pos":0.1}}, budget=60)
    assert res[0]["product"].id == "x1"
