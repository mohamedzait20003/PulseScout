from fastapi import APIRouter

from controllers import SearchController
from dtos import SearchRequest, SearchResponse

router = APIRouter()
controller = SearchController()


@router.post("/", summary="Search stored posts by similarity", response_model=SearchResponse)
def search_posts(req: SearchRequest):
    return controller.search(query=req.query, n=req.n)
