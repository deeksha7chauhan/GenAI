# crew/crew_agents.py
import os
from crewai.llm import LLM
from crewai import Agent

# one shared Gemini LLM for all agents
GEMINI_LLM = LLM(
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    provider="gemini",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)

search_agent = Agent(
    role="Product Searcher",
    goal="Find products from APIs.",
    backstory="Search specialist.",
    llm=GEMINI_LLM,          # <-- IMPORTANT
    memory=False,            # optional: avoids embedchain needing OpenAI
)

price_agent = Agent(
    role="Price Analyst",
    goal="Compare prices across stores and track deals.",
    backstory="Price comparison pro.",
    llm=GEMINI_LLM,          # <-- IMPORTANT
    memory=False,
)

review_agent = Agent(
    role="Review Analyst",
    goal="Summarize sentiments and themes from reviews.",
    backstory="Sentiment & QA sleuth.",
    llm=GEMINI_LLM,          # <-- IMPORTANT
    memory=False,
)

reco_agent = Agent(
    role="Recommender",
    goal="Synthesize results into a clear recommendation within budget.",
    backstory="Personal shopping advisor.",
    llm=GEMINI_LLM,          # <-- IMPORTANT
    memory=False,
)
