from pydantic import BaseModel
from .common_dto import PostDto


class SearchRequest(BaseModel):
    query: str
    n: int = 10

class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[PostDto] = []
