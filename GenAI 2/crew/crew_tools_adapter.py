# crew/crew_tools_adapter.py
from __future__ import annotations

from typing import Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from crew.crew_tools import (
    product_search_tool as _lc_product_search,
    price_compare_tool as _lc_price_compare,
    review_analyze_tool as _lc_review_analyze,
    recommend_tool as _lc_recommend,
)

# ---------- Product Search -----------------------------------------------------

class ProductSearchArgs(BaseModel):
    query: str = Field(..., description="What to search for, e.g. 'airpods'")
    max_results: int = Field(10, description="Max number of products")
    budget: Optional[float] = Field(None, description="Optional budget ceiling")

class ProductSearchCrewTool(BaseTool):
    name: str = "product_search"
    description: str = "Search for real products by query, budget, and limit."
    args_schema: Type[BaseModel] = ProductSearchArgs

    def _run(self, query: str, max_results: int = 10, budget: Optional[float] = None) -> str:  # type: ignore[override]
        return _lc_product_search.invoke({"query": query, "max_results": max_results, "budget": budget})

    async def _arun(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError()


# ---------- Price Compare ------------------------------------------------------

class PriceCompareArgs(BaseModel):
    products_json: str = Field(..., description="JSON-serialized list of products from search")

class PriceCompareCrewTool(BaseTool):
    name: str = "price_compare"
    description: str = "Compare prices across vendors for products. Returns JSON summary."
    args_schema: Type[BaseModel] = PriceCompareArgs

    def _run(self, products_json: str) -> str:  # type: ignore[override]
        return _lc_price_compare.invoke({"products_json": products_json})

    async def _arun(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError()


# ---------- Review Analyze -----------------------------------------------------

class ReviewAnalyzeArgs(BaseModel):
    products_json: str = Field(..., description="JSON-serialized list of products")
    max_reviews: int = Field(50, description="Max reviews to analyze (placeholder)")

class ReviewAnalyzeCrewTool(BaseTool):
    name: str = "review_analyze"
    description: str = "Analyze customer reviews. Returns JSON with counts/summaries."
    args_schema: Type[BaseModel] = ReviewAnalyzeArgs

    def _run(self, products_json: str, max_reviews: int = 50) -> str:  # type: ignore[override]
        return _lc_review_analyze.invoke({"products_json": products_json, "max_reviews": max_reviews})

    async def _arun(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError()


# ---------- Recommend ----------------------------------------------------------

class RecommendArgs(BaseModel):
    products_json: str = Field(..., description="JSON from product_search")
    price_summary_json: str = Field(..., description="JSON from price_compare")
    review_summary_json: str = Field(..., description="JSON from review_analyze")
    budget: Optional[float] = Field(None, description="Budget to filter by")
    max_results: int = Field(5, description="How many picks to return")

class RecommendCrewTool(BaseTool):
    name: str = "recommend"
    description: str = "Combine inputs to produce ranked recommendations within budget."
    args_schema: Type[BaseModel] = RecommendArgs

    def _run(  # type: ignore[override]
        self,
        products_json: str,
        price_summary_json: str,
        review_summary_json: str,
        budget: Optional[float] = None,
        max_results: int = 5,
    ) -> str:
        return _lc_recommend.invoke({
            "products_json": products_json,
            "price_summary_json": price_summary_json,
            "review_summary_json": review_summary_json,
            "budget": budget,
            "max_results": max_results,
        })

    async def _arun(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError()
