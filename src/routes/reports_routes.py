from fastapi import APIRouter, Query

from controllers import ReportsController
from dtos import ReportsResponse, LatestReportResponse

router = APIRouter()
controller = ReportsController()


@router.get("/", summary="List recent posts from ChromaDB", response_model=ReportsResponse)
def list_reports(max_count: int = Query(20, description="Max posts to return")):
    return controller.list_reports(max_count=max_count)


@router.get("/latest", summary="Get posts from the last 24 hours", response_model=LatestReportResponse)
def latest_report():
    return controller.get_latest()
