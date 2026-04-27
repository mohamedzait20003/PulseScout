from pydantic import BaseModel
from .common_dto import TopicDto, TrendDto


class ScrapeResponse(BaseModel):
    batch_id: str
    posts_scraped: int
    new_posts_stored: int
    sentiment_breakdown: dict = {}
    top_topics: list[TopicDto] = []
    actionable_insight: str = ""
    trend_comparison: TrendDto | None = None
