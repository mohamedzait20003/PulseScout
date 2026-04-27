from models import ReportModel


class ReportsController:
    def get_analysis_reports(self, max_count: int = 20) -> dict:
        reports = ReportModel.find_all(limit=max_count)
        return {"count": len(reports), "reports": [r.to_dict() for r in reports]}
