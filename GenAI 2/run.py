import argparse
from agentic_shop.orchestrator import Orchestrator

def main():
    parser = argparse.ArgumentParser(description="Agentic E-Commerce Assistant (strict, real APIs only)")
    parser.add_argument("--query", required=True, help="What are you shopping for?")
    parser.add_argument("--budget", type=float, default=None, help="Budget in the product currency (e.g., USD)")
    parser.add_argument("--max_results", type=int, default=10, help="Max search results per source")
    parser.add_argument("--no_sentiment", action="store_true", help="Disable Hugging Face sentiment calls")
    args = parser.parse_args()

    orch = Orchestrator(sentiment_enabled=not args.no_sentiment)
    orch.run(args.query, args.budget, args.max_results)

if __name__ == "__main__":
    main()
