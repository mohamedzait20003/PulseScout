from pydantic import BaseModel


class TopicDto(BaseModel):
    topic: str
    count: int

class TrendDto(BaseModel):
    trend_comparison: str = ""
    rising_topics: list[str] = []
    declining_topics: list[str] = []
    sentiment_shift: str = ""
    actionable_insight: str = ""


class PostDto(BaseModel):
    id: str
    title: str = ""
    text: str = ""
    score: int = 0
    timestamp: str = ""
    source: str = ""
    subreddit: str = ""
