import json
from .base_model import BaseModel


class ReportModel(BaseModel):
    collection_name = "reports"

    def __init__(self, id: str = "", batch_id: str = "", posts_scraped: int = 0,
                 new_posts_stored: int = 0, sentiment_breakdown: dict = None,
                 top_topics: list = None, actionable_insight: str = "",
                 trend_comparison: dict = None, timestamp: str = ""):
        self.id = id or batch_id
        self.batch_id = batch_id
        self.posts_scraped = posts_scraped
        self.new_posts_stored = new_posts_stored
        self.sentiment_breakdown = sentiment_breakdown or {}
        self.top_topics = top_topics or []
        self.actionable_insight = actionable_insight
        self.trend_comparison = trend_comparison
        self.timestamp = timestamp or batch_id

    def to_payload(self) -> dict:
        return {
            "report_id": self.id,
            "batch_id": self.batch_id,
            "posts_scraped": self.posts_scraped,
            "new_posts_stored": self.new_posts_stored,
            "sentiment_breakdown": json.dumps(self.sentiment_breakdown),
            "top_topics": json.dumps(self.top_topics),
            "actionable_insight": self.actionable_insight,
            "trend_comparison": json.dumps(self.trend_comparison) if self.trend_comparison else "",
            "timestamp": self.timestamp,
        }

    def to_document(self) -> str:
        topics = ", ".join(t.get("topic", "") for t in self.top_topics)
        return f"{self.actionable_insight}\nTopics: {topics}"

    @classmethod
    def from_payload(cls, payload: dict):
        return cls(
            id=payload.get("report_id", ""),
            batch_id=payload.get("batch_id", ""),
            posts_scraped=payload.get("posts_scraped", 0),
            new_posts_stored=payload.get("new_posts_stored", 0),
            sentiment_breakdown=json.loads(payload.get("sentiment_breakdown", "{}")),
            top_topics=json.loads(payload.get("top_topics", "[]")),
            actionable_insight=payload.get("actionable_insight", ""),
            trend_comparison=json.loads(payload.get("trend_comparison", "null") or "null"),
            timestamp=payload.get("timestamp", ""),
        )

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "posts_scraped": self.posts_scraped,
            "new_posts_stored": self.new_posts_stored,
            "sentiment_breakdown": self.sentiment_breakdown,
            "top_topics": self.top_topics,
            "actionable_insight": self.actionable_insight,
            "trend_comparison": self.trend_comparison,
        }
