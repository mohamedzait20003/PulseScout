import pytest
from unittest.mock import patch, MagicMock

from utils.scrap_util import Scrapper


class TestScrapperYoutube:
    def setup_method(self):
        self.scrapper = Scrapper()

    @patch("utils.scrap_util.requests.get")
    def test_scrap_youtube_returns_posts(self, mock_get):
        def side_effect(url, **kwargs):
            mock = MagicMock()
            mock.raise_for_status = MagicMock()
            if "/search" in url:
                mock.json.return_value = {
                    "items": [
                        {
                            "id": {"videoId": "abc123"},
                            "snippet": {
                                "title": "AI Trends 2026",
                                "description": "A video about AI trends.",
                                "publishedAt": "2026-04-12T00:00:00Z",
                            },
                        }
                    ]
                }
            elif "/videos" in url:
                mock.json.return_value = {
                    "items": [
                        {"id": "abc123", "statistics": {"viewCount": "15000"}}
                    ]
                }
            return mock

        mock_get.side_effect = side_effect

        posts = self.scrapper.scrap_youtube(tag="AI trends", limit=1, num_comments=0)

        assert len(posts) == 1
        assert posts[0]["id"] == "abc123"
        assert posts[0]["title"] == "AI Trends 2026"
        assert posts[0]["source"] == "youtube"
        assert posts[0]["score"] == 15000

    @patch("utils.scrap_util.requests.get")
    def test_scrap_youtube_empty_response(self, mock_get):
        mock = MagicMock()
        mock.raise_for_status = MagicMock()
        mock.json.return_value = {"items": []}
        mock_get.return_value = mock

        posts = self.scrapper.scrap_youtube(tag="nonexistent", limit=5, num_comments=0)
        assert posts == []

    @patch("utils.scrap_util.requests.get")
    def test_scrap_youtube_respects_limit(self, mock_get):
        search_items = [
            {
                "id": {"videoId": f"vid{i}"},
                "snippet": {"title": f"Video {i}", "description": "", "publishedAt": ""},
            }
            for i in range(10)
        ]
        stats_items = [
            {"id": f"vid{i}", "statistics": {"viewCount": "100"}}
            for i in range(10)
        ]

        def side_effect(url, **kwargs):
            mock = MagicMock()
            mock.raise_for_status = MagicMock()
            if "/search" in url:
                mock.json.return_value = {"items": search_items[:3]}
            elif "/videos" in url:
                mock.json.return_value = {"items": stats_items[:3]}
            return mock

        mock_get.side_effect = side_effect

        posts = self.scrapper.scrap_youtube(tag="tech", limit=3, num_comments=0)
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
    def test_fetch_youtube_comments(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={
                "items": [
                    {"snippet": {"topLevelComment": {"snippet": {"textDisplay": "Great video!"}}}},
                    {"snippet": {"topLevelComment": {"snippet": {"textDisplay": "Very helpful"}}}},
                ]
            }),
        )
        mock_get.return_value.raise_for_status = MagicMock()

        comments = self.scrapper._fetch_youtube_comments("abc123", limit=2)
        assert len(comments) == 2
        assert "Great video!" in comments[0]

    @patch("utils.scrap_util.requests.get")
    def test_fetch_youtube_comments_handles_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")

        comments = self.scrapper._fetch_youtube_comments("abc123", limit=2)
        assert comments == []
