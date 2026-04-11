import os
import sys
import time
import argparse
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
from main.scheduler import Scheduler


def main():
    parser = argparse.ArgumentParser(description="PulseScout — Social Knowledge Doomscroll Agent")
    parser.add_argument("--once", action="store_true", help="Run a single scrape cycle and exit")
    parser.add_argument("--interval", type=int, default=30, help="Minutes between cycles (default: 30)")
    parser.add_argument("--subreddits", type=str, default="technology,programming",
                        help="Comma-separated subreddit names")
    parser.add_argument("--limit", type=int, default=25, help="Posts to fetch per source (default: 25)")
    args = parser.parse_args()

    subreddits = [s.strip() for s in args.subreddits.split(",")]
    scheduler = Scheduler(subreddits=subreddits, limit=args.limit)

    if args.once:
        report = scheduler.run_cycle()
        print("\n=== Report ===")
        print(f"Posts scraped: {report['posts_scraped']}")
        print(f"New posts stored: {report['new_posts_stored']}")
        print(f"Sentiment: {report.get('sentiment_breakdown', {})}")
        print(f"Top topics: {report.get('top_topics', [])}")
        print(f"Insight: {report.get('actionable_insight', '')}")
        if report.get("trend_comparison"):
            print(f"Trend: {report['trend_comparison']}")
    else:
        print(f"PulseScout running every {args.interval} minutes. Press Ctrl+C to stop.")
        while True:
            try:
                scheduler.run_cycle()
                print(f"\nSleeping {args.interval} minutes...\n")
                time.sleep(args.interval * 60)
            except KeyboardInterrupt:
                print("\nStopped.")
                break


if __name__ == "__main__":
    main()
