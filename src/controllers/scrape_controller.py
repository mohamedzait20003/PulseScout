import datetime

from utils import Scrapper, Analyzer
from models import PostModel, ReportModel


class ScrapeController:
    def __init__(self):
        self.scrapper = Scrapper()
        self.analyzer = Analyzer()
        self.last_analysis = None

    def run_cycle(self, tags: list[str], limit: int) -> dict:
        batch_id = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

        all_posts = []
        for tag in tags:
            posts = self.scrapper.scrap_youtube(tag=tag, limit=limit)
            all_posts.extend(posts)

        hn_posts = self.scrapper.scrap_hackernews(limit=limit)
        all_posts.extend(hn_posts)

        new_posts = []
        for post_data in all_posts:
            if not PostModel.exists("post_id", post_data["id"]):
                post = PostModel.from_dict(post_data)
                post.batch_id = batch_id
                new_posts.append(post)

        added = PostModel.bulk_save(new_posts)

        batch_posts = PostModel.find_by("batch_id", batch_id)
        if not batch_posts:
            return {"batch_id": batch_id, "posts_scraped": len(all_posts), "new_posts_stored": 0}

        try:
            analysis = self.analyzer.analyze_batch([p.to_dict() for p in batch_posts])
        except Exception:
            analysis = {}

        trend = None
        if self.last_analysis:
            try:
                trend = self.analyzer.compare_batches(analysis, self.last_analysis)
            except Exception:
                trend = None
        self.last_analysis = analysis

        report_data = {
            "batch_id": batch_id,
            "posts_scraped": len(all_posts),
            "new_posts_stored": added,
            "sentiment_breakdown": analysis.get("sentiment_breakdown", {}),
            "top_topics": analysis.get("top_topics", []),
            "actionable_insight": analysis.get("actionable_insight", ""),
            "trend_comparison": trend,
            "timestamp": batch_id,
        }

        report = ReportModel(**report_data)
        report.save()

        return report_data
