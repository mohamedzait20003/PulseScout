import datetime

from utils import Scrapper, Analyzer
from models import PostModel, CommentModel, ReportModel


MONITOR_LIMIT = 25

MONITOR_TAGS = [
    "AI market trends",
    "tech startup funding",
    "venture capital",
    "emerging technology",
    "consumer sentiment",
]

class ScrapeController:
    def __init__(self):
        self.scrapper = Scrapper()
        self.analyzer = Analyzer()
        self.last_analysis = self._load_last_analysis()

    def _load_last_analysis(self) -> dict | None:
        try:
            report = ReportModel.find_latest()
            if report:
                return {
                    "sentiment_breakdown": report.sentiment_breakdown,
                    "top_topics": report.top_topics,
                    "actionable_insight": report.actionable_insight,
                }
        except Exception:
            pass
        return None

    def run_cycle(self) -> dict:
        batch_id = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

        all_posts = []
        for tag in MONITOR_TAGS:
            posts = self.scrapper.scrap_youtube(tag=tag, limit=MONITOR_LIMIT)
            all_posts.extend(posts)

        hn_posts = self.scrapper.scrap_hackernews(limit=MONITOR_LIMIT)
        all_posts.extend(hn_posts)

        new_posts = []
        for post_data in all_posts:
            if not PostModel.exists("post_id", post_data["id"]):
                post = PostModel.from_dict(post_data)
                post.batch_id = batch_id
                new_posts.append(post)

        added = PostModel.bulk_save(new_posts)

        new_comments = [
            CommentModel(
                id=f"{post.id}_{i}",
                post_id=post.id,
                body=body,
                source=post.source,
                timestamp=post.timestamp,
            )
            for post in new_posts
            for i, body in enumerate(post.comments)
            if body
        ]
        CommentModel.bulk_save(new_comments)

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
