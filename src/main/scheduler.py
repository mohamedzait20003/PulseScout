import os
import json
import datetime

from utils import Scrapper, Storage, Analyzer


class Scheduler:
    def __init__(self, subreddits: list[str] = None, limit: int = 25):
        self.subreddits = subreddits or ["technology"]
        self.limit = limit
        self.last_analysis = None

        self.scrapper = Scrapper(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        )
        self.storage = Storage()
        self.analyzer = Analyzer(api_key=os.getenv("ANTHROPIC_API_KEY"))

        os.makedirs("src/output/reports", exist_ok=True)

    def run_cycle(self) -> dict:
        batch_id = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print(f"[{batch_id}] Starting scrape cycle...")

        all_posts = []
        for sub in self.subreddits:
            print(f"  Scraping r/{sub}...")
            posts = self.scrapper.scrap_reddit(sub, limit=self.limit, time_filter="hot")
            all_posts.extend(posts)

        print("  Scraping HackerNews...")
        hn_posts = self.scrapper.scrap_hackernews(limit=self.limit)
        all_posts.extend(hn_posts)

        print(f"  Scraped {len(all_posts)} posts total.")

        added = self.storage.add_posts(all_posts, batch_id=batch_id)
        print(f"  Stored {added} new posts in ChromaDB ({len(all_posts) - added} duplicates skipped).")

        batch_posts = self.storage.get_batch(batch_id)
        if not batch_posts:
            print("  No new posts to analyze.")
            return {"batch_id": batch_id, "posts_scraped": len(all_posts), "new_posts_stored": 0}

        print(f"  Analyzing {len(batch_posts)} posts with Claude...")
        analysis = self.analyzer.analyze_batch(batch_posts)

        trend = None
        if self.last_analysis:
            print("  Comparing with previous batch...")
            trend = self.analyzer.compare_batches(analysis, self.last_analysis)
        self.last_analysis = analysis

        report = {
            "batch_id": batch_id,
            "posts_scraped": len(all_posts),
            "new_posts_stored": added,
            "sentiment_breakdown": analysis.get("sentiment_breakdown", {}),
            "top_topics": analysis.get("top_topics", []),
            "actionable_insight": analysis.get("actionable_insight", ""),
            "trend_comparison": trend,
        }

        safe_ts = batch_id.replace(":", "-")
        report_path = f"src/output/reports/{safe_ts}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  Report saved to {report_path}")

        return report
