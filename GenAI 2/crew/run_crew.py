# crew/run_crew.py
import argparse
import os
from crewai import Crew, Process
from crew.crew_agents import search_agent, price_agent, review_agent, reco_agent
from crew.crew_tasks import build_tasks

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--budget", type=float, default=None)
    parser.add_argument("--max_results", type=int, default=10)
    args = parser.parse_args()

    # ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)

    # build tasks
    t_search, t_price, t_reviews, t_reco = build_tasks(
        query=args.query,
        budget=args.budget,
        max_results=args.max_results,
    )

    # CrewAI 1.5: verbose must be bool
    crew = Crew(
        agents=[search_agent, price_agent, review_agent, reco_agent],
        tasks=[t_search, t_price, t_reviews, t_reco],
        process=Process.sequential,
        verbose=True,   # <- boolean (or remove this line)
        # memory=False,  # optional: turn off memory if you don't use it
    )

    result = crew.kickoff()
    print("\n=== Crew finished ===\n")
    print(result)

if __name__ == "__main__":
    main()
