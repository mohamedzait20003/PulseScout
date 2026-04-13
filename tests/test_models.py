import pytest
from models import PostModel, CommentModel, ReportModel


class TestPostModel:
    def test_from_dict(self, sample_post_data):
        post = PostModel.from_dict(sample_post_data)
        assert post.id == "test-post-001"
        assert post.title == "Test Post About Python"
        assert post.score == 42
        assert post.source == "devto"
        assert post.subreddit == "python"

    def test_to_dict(self, sample_post_data):
        post = PostModel.from_dict(sample_post_data)
        result = post.to_dict()
        assert result["id"] == "test-post-001"
        assert result["title"] == "Test Post About Python"
        assert result["score"] == 42
        assert "document" in result

    def test_to_document(self, sample_post_data):
        post = PostModel.from_dict(sample_post_data)
        doc = post.to_document()
        assert "Test Post About Python" in doc
        assert "test post about Python programming" in doc
        assert "Great post!" in doc

    def test_to_payload(self, sample_post_data):
        post = PostModel.from_dict(sample_post_data)
        payload = post.to_payload()
        assert payload["post_id"] == "test-post-001"
        assert payload["title"] == "Test Post About Python"
        assert payload["source"] == "devto"
        assert "document" in payload

    def test_from_payload_roundtrip(self, sample_post_data):
        post = PostModel.from_dict(sample_post_data)
        payload = post.to_payload()
        restored = PostModel.from_payload(payload)
        assert restored.id == post.id
        assert restored.title == post.title
        assert restored.score == post.score

    def test_generate_id_deterministic(self):
        post = PostModel(id="abc123")
        id1 = post._generate_id()
        id2 = post._generate_id()
        assert id1 == id2

    def test_generate_id_unique(self):
        post1 = PostModel(id="abc123")
        post2 = PostModel(id="xyz789")
        assert post1._generate_id() != post2._generate_id()


class TestCommentModel:
    def test_init(self):
        comment = CommentModel(
            id="c1", post_id="p1", body="Nice post!", source="devto", timestamp="2026-04-12T00:00:00"
        )
        assert comment.id == "c1"
        assert comment.post_id == "p1"
        assert comment.body == "Nice post!"

    def test_to_document(self):
        comment = CommentModel(body="This is the comment body")
        assert comment.to_document() == "This is the comment body"

    def test_to_payload(self):
        comment = CommentModel(id="c1", post_id="p1", body="Hello")
        payload = comment.to_payload()
        assert payload["comment_id"] == "c1"
        assert payload["post_id"] == "p1"
        assert payload["body"] == "Hello"

    def test_from_payload_roundtrip(self):
        comment = CommentModel(id="c1", post_id="p1", body="Test", source="hn", timestamp="2026-04-12")
        payload = comment.to_payload()
        restored = CommentModel.from_payload(payload)
        assert restored.id == comment.id
        assert restored.body == comment.body

    def test_to_dict(self):
        comment = CommentModel(id="c1", post_id="p1", body="Hello")
        result = comment.to_dict()
        assert result["id"] == "c1"
        assert result["post_id"] == "p1"


class TestReportModel:
    def test_init_defaults(self):
        report = ReportModel(batch_id="batch-001")
        assert report.id == "batch-001"
        assert report.posts_scraped == 0
        assert report.sentiment_breakdown == {}
        assert report.top_topics == []

    def test_init_with_data(self, sample_analysis):
        report = ReportModel(
            batch_id="batch-001",
            posts_scraped=15,
            new_posts_stored=10,
            sentiment_breakdown=sample_analysis["sentiment_breakdown"],
            top_topics=sample_analysis["top_topics"],
            actionable_insight=sample_analysis["actionable_insight"],
        )
        assert report.posts_scraped == 15
        assert report.new_posts_stored == 10
        assert report.sentiment_breakdown["positive"] == 3

    def test_to_document(self):
        report = ReportModel(
            batch_id="b1",
            top_topics=[{"topic": "python", "count": 3}, {"topic": "ai", "count": 2}],
            actionable_insight="Python is trending.",
        )
        doc = report.to_document()
        assert "Python is trending." in doc
        assert "python" in doc
        assert "ai" in doc

    def test_to_dict(self):
        report = ReportModel(batch_id="b1", posts_scraped=10, new_posts_stored=5)
        result = report.to_dict()
        assert result["batch_id"] == "b1"
        assert result["posts_scraped"] == 10
        assert result["new_posts_stored"] == 5

    def test_payload_roundtrip(self, sample_analysis):
        report = ReportModel(
            batch_id="batch-001",
            posts_scraped=15,
            sentiment_breakdown=sample_analysis["sentiment_breakdown"],
            top_topics=sample_analysis["top_topics"],
            actionable_insight=sample_analysis["actionable_insight"],
            trend_comparison={"rising_topics": ["AI"]},
        )
        payload = report.to_payload()
        restored = ReportModel.from_payload(payload)
        assert restored.batch_id == "batch-001"
        assert restored.posts_scraped == 15
        assert restored.sentiment_breakdown["positive"] == 3
        assert restored.trend_comparison["rising_topics"] == ["AI"]
