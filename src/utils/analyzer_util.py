import json
import ollama

from config import (
    analyzer_config,
    ANALYZER_KEY_DEFAULTS,
    ANALYZER_URL_DEFAULTS,
    ANALYZER_MODEL_DEFAULTS,
)


BATCH_PROMPT = """\
You are a social media analyst. Analyze these posts and return ONLY valid JSON.

Posts:
{posts_text}

Return this exact JSON structure:
{{
  "posts": [
    {{
      "id": "<post id>",
      "sentiment": "positive" | "negative" | "neutral",
      "confidence": 0.0-1.0,
      "topics": ["topic1", "topic2"]
    }}
  ],
  "sentiment_breakdown": {{"positive": 0, "negative": 0, "neutral": 0}},
  "top_topics": [{{"topic": "name", "count": 0}}],
  "actionable_insight": "One paragraph summarizing the most notable finding."
}}
"""

TREND_PROMPT = """\
You are a trend analyst. Compare these two batches of social media analysis.

Previous batch summary:
{previous}

Current batch summary:
{current}

Return ONLY valid JSON:
{{
  "trend_comparison": "Short summary of how topics and sentiment shifted.",
  "rising_topics": ["topics gaining traction"],
  "declining_topics": ["topics losing traction"],
  "sentiment_shift": "Description of overall sentiment change.",
  "actionable_insight": "One paragraph with the most important takeaway for a business."
}}
"""


class Analyzer:
    def __init__(self):
        self.api_key = ANALYZER_KEY_DEFAULTS["api_key"]
        self.base_url = ANALYZER_URL_DEFAULTS["base_url"].rstrip("/")
        self.model = ANALYZER_MODEL_DEFAULTS["model"]
        headers = {}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        self.client = ollama.Client(host=self.base_url, headers=headers)

    @analyzer_config
    def analyze_batch(self, posts: list[dict], max_post_length: int = 800, **_) -> dict:
        posts_text = "\n---\n".join(
            f"[{p['id']}] ({p.get('source','')}) {p.get('title','')}\n{p.get('document', p.get('text', ''))[:max_post_length]}"
            for p in posts
        )

        prompt = BATCH_PROMPT.format(posts_text=posts_text)
        return self._chat(prompt)

    def compare_batches(self, current_analysis: dict, previous_analysis: dict) -> dict:
        prompt = TREND_PROMPT.format(
            previous=json.dumps(previous_analysis, indent=2),
            current=json.dumps(current_analysis, indent=2),
        )
        return self._chat(prompt)

    def _chat(self, prompt: str) -> dict:
        response = self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format="json",
        )
        text = response.message.content
        return self._parse_json(text)

    def _parse_json(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return json.loads(text)
