from fastapi import APIRouter

from controllers import ScrapeController
from dtos import ScrapeRequest, ScrapeResponse

router = APIRouter()
controller = ScrapeController()


@router.post("/", summary="Run a full scrape + analyze cycle", response_model=ScrapeResponse)
def run_scrape(req: ScrapeRequest):
    return controller.run_cycle(tags=req.tags, limit=req.limit)
