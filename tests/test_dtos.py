import pytest
from dtos import ScrapeRequest, ScrapeResponse, SearchRequest, SearchResponse
from dtos import ReportsResponse, LatestReportResponse
from dtos.common_dto import TopicDto, TrendDto


class TestScrapeDto:
    def test_request_defaults(self):
        req = ScrapeRequest()
        assert req.tags == ["python", "ai"]
        assert req.limit == 25

    def test_request_custom(self):
        req = ScrapeRequest(tags=["rust"], limit=10)
        assert req.tags == ["rust"]
        assert req.limit == 10

    def test_response_minimal(self):
        resp = ScrapeResponse(batch_id="b1", posts_scraped=10, new_posts_stored=5)
        assert resp.batch_id == "b1"
        assert resp.sentiment_breakdown == {}
        assert resp.trend_comparison is None

    def test_response_with_topics(self):
        resp = ScrapeResponse(
            batch_id="b1",
            posts_scraped=10,
            new_posts_stored=5,
            top_topics=[TopicDto(topic="AI", count=5)],
        )
        assert resp.top_topics[0].topic == "AI"
        assert resp.top_topics[0].count == 5

    def test_response_with_trend(self):
        trend = TrendDto(
            trend_comparison="AI is rising",
            rising_topics=["AI"],
            declining_topics=["crypto"],
        )
        resp = ScrapeResponse(
            batch_id="b1", posts_scraped=10, new_posts_stored=5,
            trend_comparison=trend,
        )
        assert resp.trend_comparison.rising_topics == ["AI"]


class TestSearchDto:
    def test_request_defaults(self):
        req = SearchRequest(query="python")
        assert req.query == "python"
        assert req.n == 10

    def test_response(self):
        resp = SearchResponse(query="python", count=0, results=[])
        assert resp.count == 0


class TestReportsDto:
    def test_reports_response(self):
        resp = ReportsResponse(count=0, posts=[])
        assert resp.count == 0

    def test_latest_report_error(self):
        resp = LatestReportResponse(error="No recent posts found")
        assert resp.error == "No recent posts found"
        assert resp.count == 0


class TestCommonDto:
    def test_topic_dto(self):
        topic = TopicDto(topic="AI", count=5)
        assert topic.topic == "AI"

    def test_trend_dto_defaults(self):
        trend = TrendDto()
        assert trend.trend_comparison == ""
        assert trend.rising_topics == []
        assert trend.declining_topics == []
