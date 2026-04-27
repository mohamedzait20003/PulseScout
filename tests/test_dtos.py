import pytest
from dtos import ScrapeResponse, SearchRequest, SearchResponse
from dtos import AnalysisReportDto, AnalysisReportsResponse
from dtos.common_dto import TopicDto, TrendDto


class TestScrapeDto:
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
    def test_analysis_report_dto(self):
        report = AnalysisReportDto(batch_id="b1", posts_scraped=10, new_posts_stored=5)
        assert report.batch_id == "b1"
        assert report.sentiment_breakdown == {}
        assert report.trend_comparison is None

    def test_analysis_reports_response(self):
        resp = AnalysisReportsResponse(count=0, reports=[])
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
