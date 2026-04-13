import pytest
from unittest.mock import patch, MagicMock


class TestHealthRoute:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "PulseScout"


class TestScrapeRoute:
    @patch("controllers.scrape_controller.ScrapeController.run_cycle")
    def test_scrape_returns_report(self, mock_run, client):
        mock_run.return_value = {
            "batch_id": "2026-04-12T00:00:00",
            "posts_scraped": 15,
            "new_posts_stored": 10,
            "sentiment_breakdown": {"positive": 5, "negative": 2, "neutral": 3},
            "top_topics": [{"topic": "AI", "count": 5}],
            "actionable_insight": "AI is trending.",
            "trend_comparison": None,
        }

        response = client.post("/scrape/", json={"tags": ["python"], "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert data["posts_scraped"] == 15
        assert data["new_posts_stored"] == 10

    @patch("controllers.scrape_controller.ScrapeController.run_cycle")
    def test_scrape_default_params(self, mock_run, client):
        mock_run.return_value = {
            "batch_id": "b1", "posts_scraped": 0, "new_posts_stored": 0,
        }

        response = client.post("/scrape/", json={})
        assert response.status_code == 200
        mock_run.assert_called_once_with(tags=["python", "ai"], limit=25)


class TestSearchRoute:
    @patch("controllers.search_controller.SearchController.search")
    def test_search_returns_results(self, mock_search, client):
        mock_search.return_value = {
            "query": "python",
            "count": 1,
            "results": [{"id": "1", "title": "Python Post"}],
        }

        response = client.post("/search/", json={"query": "python", "n": 5})
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "python"
        assert data["count"] == 1


class TestReportsRoute:
    @patch("controllers.reports_controller.ReportsController.list_reports")
    def test_list_reports(self, mock_list, client):
        mock_list.return_value = {"count": 0, "posts": []}

        response = client.get("/reports/")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    @patch("controllers.reports_controller.ReportsController.get_latest")
    def test_latest_report(self, mock_latest, client):
        mock_latest.return_value = {"count": 0, "posts": [], "error": "No recent posts found"}

        response = client.get("/reports/latest")
        assert response.status_code == 200
        assert response.json()["error"] == "No recent posts found"
