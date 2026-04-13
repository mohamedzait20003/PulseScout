import pytest
from config.scraper_config import scraper_config, METHOD_DEFAULTS, scraper_urls, URL_DEFAULTS
from config.analyzer_config import analyzer_config, ANALYZER_METHOD_DEFAULTS


class TestScraperConfig:
    def test_decorator_injects_defaults(self):
        @scraper_config
        def func(limit=None, timeout=None, **_):
            return {"limit": limit, "timeout": timeout}

        result = func()
        assert result["limit"] == METHOD_DEFAULTS["limit"]
        assert result["timeout"] == METHOD_DEFAULTS["timeout"]

    def test_decorator_respects_explicit_values(self):
        @scraper_config
        def func(limit=None, timeout=None, **_):
            return {"limit": limit, "timeout": timeout}

        result = func(limit=5, timeout=60)
        assert result["limit"] == 5
        assert result["timeout"] == 60

    def test_decorator_ignores_unknown_params(self):
        @scraper_config
        def func(limit=None, **_):
            return {"limit": limit}

        result = func()
        assert result["limit"] == METHOD_DEFAULTS["limit"]


class TestAnalyzerConfig:
    def test_decorator_injects_defaults(self):
        @analyzer_config
        def func(timeout=None, max_post_length=None, **_):
            return {"timeout": timeout, "max_post_length": max_post_length}

        result = func()
        assert result["timeout"] == ANALYZER_METHOD_DEFAULTS["timeout"]
        assert result["max_post_length"] == ANALYZER_METHOD_DEFAULTS["max_post_length"]

    def test_decorator_respects_explicit_values(self):
        @analyzer_config
        def func(timeout=None, **_):
            return {"timeout": timeout}

        result = func(timeout=30)
        assert result["timeout"] == 30
