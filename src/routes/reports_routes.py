from fastapi import APIRouter, Query

from controllers import ReportsController
from dtos import AnalysisReportsResponse

router = APIRouter()
controller = ReportsController()


@router.get("/analysis", summary="List stored analysis reports (sentiment, topics, trends)", response_model=AnalysisReportsResponse)
def analysis_reports(max_count: int = Query(20, description="Max reports to return")):
    return controller.get_analysis_reports(max_count=max_count)
