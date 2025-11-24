from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table

from agentic_shop.agents.product_search import ProductSearchAgent
from agentic_shop.agents.price_comparison import PriceComparisonAgent
from agentic_shop.agents.review_analysis import ReviewAnalysisAgent
from agentic_shop.agents.recommendation import RecommendationEngineAgent
from agentic_shop.agents.utils import Product
from agentic_shop.config import EBAY_ENV

console = Console()

class Orchestrator:
    def __init__(self, sentiment_enabled: bool = True):
        self.search_agent = ProductSearchAgent()
        self.price_agent = PriceComparisonAgent()
        self.review_agent = ReviewAnalysisAgent(enabled=sentiment_enabled)
        self.reco_agent = RecommendationEngineAgent()

    def run(self, query: str, budget: float | None, max_results: int = 10) -> Dict[str, Any]:
        console.rule("[bold cyan]Product Search")
        products: List[Product] = self.search_agent.search(query, limit=max_results)
        if not products:
            console.print(
                "[yellow]No products returned by the eBay API.[/yellow] "
                f"(Environment: {EBAY_ENV}). "
                "If you're on sandbox, you must create sandbox test listings, "
                "or switch to production keys."
            )
            return {"error": "No products found.", "products": []}

        table = Table(title="Found Products")
        table.add_column("Retailer")
        table.add_column("Title")
        table.add_column("Price")
        table.add_column("URL")
        for p in products:
            table.add_row(p.retailer, p.title[:60], f"{p.price:.2f} {p.currency}", p.url)
        console.print(table)

        console.rule("[bold cyan]Price Comparison & History")
        summary = self.price_agent.compare(products)

        console.rule("[bold cyan]Review Analysis (Sentiment)")
        sentiments = self.review_agent.analyze(products)

        console.rule("[bold cyan]Recommendations")
        ranked = self.reco_agent.recommend(products, summary, sentiments, budget=budget)

        out_table = Table(title="Top Recommendations")
        out_table.add_column("Score")
        out_table.add_column("Retailer")
        out_table.add_column("Title")
        out_table.add_column("Price")
        out_table.add_column("Sentiment+")
        out_table.add_column("URL")
        for r in ranked[:10]:
            p = r["product"]
            out_table.add_row(
                str(r["score"]),
                p.retailer,
                p.title[:50],
                f"{p.price:.2f} {p.currency}",
                f"{r['sentiment_pos']:.2f}",
                p.url
            )
        console.print(out_table)

        return {
            "query": query,
            "budget": budget,
            "products": products,
            "summary": summary,
            "sentiments": sentiments,
            "ranked": ranked
        }
