import pytest
from unittest.mock import patch, MagicMock

from utils.scrap_util import Scrapper


class TestScrapperDevto:
    def setup_method(self):
        self.scrapper = Scrapper()

    @patch("utils.scrap_util.requests.get")
    def test_scrap_devto_returns_posts(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value=[
                {
                    "id": 12345,
                    "title": "Test Article",
                    "description": "A test article about Python.",
                    "positive_reactions_count": 10,
                    "published_at": "2026-04-12T00:00:00Z",
                }
            ]),
        )
        mock_get.return_value.raise_for_status = MagicMock()

        posts = self.scrapper.scrap_devto(tag="python", limit=1, num_comments=0)

        assert len(posts) == 1
        assert posts[0]["id"] == "12345"
        assert posts[0]["title"] == "Test Article"
        assert posts[0]["source"] == "devto"
        assert posts[0]["subreddit"] == "python"

    @patch("utils.scrap_util.requests.get")
    def test_scrap_devto_empty_response(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value=[]),
        )
        mock_get.return_value.raise_for_status = MagicMock()

        posts = self.scrapper.scrap_devto(tag="nonexistent", limit=5, num_comments=0)
        assert posts == []

    @patch("utils.scrap_util.requests.get")
    def test_scrap_devto_respects_limit(self, mock_get):
        articles = [
            {"id": i, "title": f"Post {i}", "description": "", "positive_reactions_count": 0, "published_at": ""}
            for i in range(10)
        ]
        mock_get.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value=articles),
        )
        mock_get.return_value.raise_for_status = MagicMock()

        posts = self.scrapper.scrap_devto(tag="python", limit=3, num_comments=0)
        assert len(posts) == 3


class TestScrapperHackernews:
    def setup_method(self):
        self.scrapper = Scrapper()

    @patch("utils.scrap_util.requests.get")
    def test_scrap_hackernews_returns_posts(self, mock_get):
        def side_effect(url, **kwargs):
            mock = MagicMock()
            if "topstories" in url:
                mock.json.return_value = [100, 101]
            elif "100" in url:
                mock.json.return_value = {
                    "id": 100, "title": "HN Post 1", "text": "Content 1",
                    "score": 50, "time": 1744416000, "kids": [],
                }
            elif "101" in url:
                mock.json.return_value = {
                    "id": 101, "title": "HN Post 2", "text": "Content 2",
                    "score": 30, "time": 1744416000, "kids": [],
                }
            return mock

        mock_get.side_effect = side_effect

        posts = self.scrapper.scrap_hackernews(limit=2, num_comments=0)

        assert len(posts) == 2
        assert posts[0]["id"] == "100"
        assert posts[0]["source"] == "hackernews"
        assert posts[0]["subreddit"] == ""

    @patch("utils.scrap_util.requests.get")
    def test_scrap_hackernews_skips_none_items(self, mock_get):
        def side_effect(url, **kwargs):
            mock = MagicMock()
            if "topstories" in url:
                mock.json.return_value = [100]
            else:
                mock.json.return_value = None
            return mock

        mock_get.side_effect = side_effect

        posts = self.scrapper.scrap_hackernews(limit=1, num_comments=0)
        assert posts == []


class TestScrapperComments:
    def setup_method(self):
        self.scrapper = Scrapper()

    @patch("utils.scrap_util.requests.get")
    def test_fetch_devto_comments(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value=[
                {"body_html": "<p>Great!</p>"},
                {"body_html": "<p>Thanks!</p>"},
            ]),
        )
        mock_get.return_value.raise_for_status = MagicMock()

        comments = self.scrapper._fetch_devto_comments(12345, limit=2)
        assert len(comments) == 2
        assert "<p>Great!</p>" in comments[0]

    @patch("utils.scrap_util.requests.get")
    def test_fetch_devto_comments_handles_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")

        comments = self.scrapper._fetch_devto_comments(12345, limit=2)
        assert comments == []
