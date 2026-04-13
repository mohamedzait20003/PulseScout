import os
import sys

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_post_data():
    return {
        "id": "test-post-001",
        "title": "Test Post About Python",
        "text": "This is a test post about Python programming.",
        "comments": ["Great post!", "Very helpful."],
        "score": 42,
        "timestamp": "2026-04-12T00:00:00+00:00",
        "source": "devto",
        "subreddit": "python",
    }


@pytest.fixture
def sample_post_list():
    return [
        {
            "id": f"test-post-{i:03d}",
            "title": f"Test Post {i}",
            "text": f"Content for test post {i}.",
            "comments": [f"Comment on post {i}"],
            "score": i * 10,
            "timestamp": f"2026-04-12T{i:02d}:00:00+00:00",
            "source": "devto" if i % 2 == 0 else "hackernews",
            "subreddit": "python" if i % 2 == 0 else "",
        }
        for i in range(1, 6)
    ]


@pytest.fixture
def sample_analysis():
    return {
        "posts": [
            {"id": "test-post-001", "sentiment": "positive", "confidence": 0.9, "topics": ["python", "ai"]}
        ],
        "sentiment_breakdown": {"positive": 3, "negative": 1, "neutral": 1},
        "top_topics": [{"topic": "python", "count": 3}, {"topic": "ai", "count": 2}],
        "actionable_insight": "Python and AI are trending topics.",
    }
