from pydantic import BaseModel
from common_dto import PostDto


class ReportsResponse(BaseModel):
    count: int
    posts: list[PostDto] = []

class LatestReportResponse(BaseModel):
    count: int = 0
    posts: list[PostDto] = []
    error: str | None = None
