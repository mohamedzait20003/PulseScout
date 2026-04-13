import pytest
from utils.analyzer_util import Analyzer, BATCH_PROMPT, TREND_PROMPT


class TestAnalyzerParseJson:
    def setup_method(self):
        self.analyzer = Analyzer.__new__(Analyzer)

    def test_parse_plain_json(self):
        result = self.analyzer._parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_json_with_markdown_fence(self):
        text = '```json\n{"key": "value"}\n```'
        result = self.analyzer._parse_json(text)
        assert result == {"key": "value"}

    def test_parse_json_with_whitespace(self):
        result = self.analyzer._parse_json('  \n  {"key": "value"}  \n  ')
        assert result == {"key": "value"}

    def test_parse_nested_json(self):
        text = '{"posts": [{"id": "1", "sentiment": "positive"}], "count": 1}'
        result = self.analyzer._parse_json(text)
        assert result["count"] == 1
        assert result["posts"][0]["sentiment"] == "positive"

    def test_parse_invalid_json_raises(self):
        with pytest.raises(Exception):
            self.analyzer._parse_json("not json at all")


class TestPromptTemplates:
    def test_batch_prompt_format(self):
        formatted = BATCH_PROMPT.format(posts_text="[1] (devto) Test Post\nSome content")
        assert "[1] (devto) Test Post" in formatted
        assert "sentiment" in formatted

    def test_trend_prompt_format(self):
        formatted = TREND_PROMPT.format(previous='{"a": 1}', current='{"b": 2}')
        assert '{"a": 1}' in formatted
        assert '{"b": 2}' in formatted
        assert "rising_topics" in formatted
