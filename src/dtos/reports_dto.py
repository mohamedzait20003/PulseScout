from pydantic import BaseModel
from .common_dto import TopicDto, TrendDto


class AnalysisReportDto(BaseModel):
    batch_id: str
    posts_scraped: int = 0
    new_posts_stored: int = 0
    sentiment_breakdown: dict = {}
    top_topics: list[TopicDto] = []
    actionable_insight: str = ""
    trend_comparison: TrendDto | None = None
    timestamp: str = ""

class AnalysisReportsResponse(BaseModel):
    count: int
    reports: list[AnalysisReportDto] = []
