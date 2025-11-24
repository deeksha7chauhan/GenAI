from crewai import Task
from crew.crew_agents import search_agent, price_agent, review_agent, reco_agent
from crew.crew_tools_adapter import (
    ProductSearchCrewTool,
    PriceCompareCrewTool,
    ReviewAnalyzeCrewTool,
    RecommendCrewTool,
)


def build_tasks(query: str, budget: float | None, max_results: int = 10):
    # Instantiate BaseTool objects once
    search_tool = ProductSearchCrewTool()
    price_tool = PriceCompareCrewTool()
    review_tool = ReviewAnalyzeCrewTool()
    reco_tool = RecommendCrewTool()

    # 1) Product search
    t_search = Task(
        description=(
            "Use the product_search tool to fetch real products.\n"
            f'- Call it with: query="{query}", max_results={max_results}, '
            f"budget={budget if budget is not None else 'null'}.\n"
            "Return ONLY the raw JSON list of product dicts."
        ),
        agent=search_agent,
        tools=[search_tool],
        expected_output="JSON list of product dicts.",
        async_execution=False,
        output_file="outputs/01_products.json",
        # NOTE: context must be a list; for the first task we leave it empty
    )

    # 2) Price comparison (depends on t_search output)
    t_price = Task(
        description=(
            "Take the JSON from the previous task (t_search) and compare prices.\n"
            "Call price_compare with: products_json=<the JSON string from t_search>.\n"
            "Return a JSON dict summarizing prices and any available history."
        ),
        agent=price_agent,
        tools=[price_tool],
        expected_output="JSON dict of price summary.",
        async_execution=False,
        output_file="outputs/02_prices.json",
        context=[t_search],  # <-- list, not dict
    )

    # 3) Review analysis (depends on t_search output)
    t_reviews = Task(
        description=(
            "Analyze real customer reviews for the products from t_search.\n"
            "Call review_analyze with: products_json=<the JSON from t_search>, enable_sentiment=true.\n"
            "Return a JSON dict with sentiment scores and common themes. No fabricated text."
        ),
        agent=review_agent,
        tools=[review_tool],
        expected_output="JSON dict with sentiments and themes.",
        async_execution=False,
        output_file="outputs/03_reviews.json",
        context=[t_search],  # <-- list, not dict
    )

    # 4) Recommendations (depends on prior three)
    t_reco = Task(
        description=(
            "Combine the three prior outputs to produce ranked recommendations within budget.\n"
            "Call recommend with: products_json=<from t_search>, price_summary_json=<from t_price>, "
            "sentiments_json=<from t_reviews>, budget={budget}.\n"
            "Return a JSON list of recommended products with scores, reasons, prices and URLs."
        ),
        agent=reco_agent,
        tools=[reco_tool],
        expected_output="JSON list of recommendations with scores and justifications.",
        async_execution=False,
        output_file="outputs/04_recommendations.json",
        context=[t_search, t_price, t_reviews],  # <-- list of prior tasks
    )

    return t_search, t_price, t_reviews, t_reco
