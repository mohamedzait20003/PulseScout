from fastapi import APIRouter

from controllers import ScrapeController
from dtos import ScrapeResponse

router = APIRouter()
controller = ScrapeController()


@router.post("/", summary="Run a full scrape + analyze cycle", response_model=ScrapeResponse)
def run_scrape():
    return controller.run_cycle()
