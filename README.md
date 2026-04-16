# PulseScout

Social Knowledge Doomscroll Agent that continuously monitors YouTube and HackerNews to extract market insights, trends, and sentiment.

## Architecture

```
YouTube API / HN API
        |
    Scrapper (scrap_util.py)
        |
    Deduplication (UUID5)
        |
    Qdrant Cloud (vector store)
        |
    Ollama LLM (gemma3:12b)
        |
    Sentiment + Topics + Trends
        |
    FastAPI REST API
        |
    n8n / Swagger UI / curl
```

### Project Structure

```
src/
  main.py                  # FastAPI entry point
  config/
    scraper_config.py      # Scraper decorator configs
    analyzer_config.py     # Analyzer decorator configs
  utils/
    scrap_util.py          # YouTube + HackerNews scrapers
    analyzer_util.py       # Ollama-based analysis (sentiment, topics, trends)
  models/
    base_model.py          # Qdrant ORM base class
    post_model.py          # Posts collection
    comment_model.py       # Comments collection
    report_model.py        # Reports collection
  controllers/
    scrape_controller.py   # Orchestrates scrape + analyze cycle
    reports_controller.py  # Recent posts retrieval
    search_controller.py   # Vector search
  dtos/
    scrape_dto.py          # Request/response for /scrape
    search_dto.py          # Request/response for /search
    reports_dto.py         # Request/response for /reports
    common_dto.py          # Shared DTOs (PostDto, TopicDto, TrendDto)
  routes/
    scrape_routes.py       # POST /scrape/
    search_routes.py       # POST /search/
    reports_routes.py      # GET /reports/, GET /reports/latest
    health_routes.py       # GET /health
tests/
  test_analyzer.py         # JSON parsing + prompt template tests
  test_scrapper.py         # Mocked YouTube + HN scraper tests
  test_config.py           # Decorator injection tests
  test_dtos.py             # Pydantic validation tests
  test_models.py           # ORM model serialization tests
  test_routes.py           # API endpoint tests
```

## Setup

### Prerequisites

- Python 3.14+
- YouTube Data API v3 key ([console.cloud.google.com](https://console.cloud.google.com))
- Qdrant Cloud account ([cloud.qdrant.io](https://cloud.qdrant.io))
- Ollama Cloud API key ([ollama.com](https://ollama.com))

### Installation

```bash
git clone https://github.com/mohamedzait20003/PulseScout.git
cd PulseScout
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
YOUTUBE_URI=https://www.googleapis.com/youtube/v3
YOUTUBE_KEY=your_youtube_api_key

HN_API_URI=https://hacker-news.firebaseio.com/v0

QDRANT_URI=https://your-cluster.cloud.qdrant.io
QDRANT_KEY=your_qdrant_api_key

OLLAMA_MODEL=gemma3:12b
OLLAMA_URI=https://ollama.com
OLLAMA_KEY=your_ollama_api_key
```

### Run

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

API docs available at `http://localhost:8000/docs`

### Tests

```bash
pytest -v
```

All 53 tests run with mocked external services. No API keys required for testing.

## API Endpoints

### POST /scrape/

Runs a full scrape + analyze cycle.

```json
{
  "tags": ["AI trends", "tech startups"],
  "limit": 25
}
```

Returns sentiment breakdown, top topics, actionable insight, and trend comparison.

### GET /reports/latest

Returns the most recent batch of analyzed posts.

### GET /reports/

Returns posts from the last 30 days.

### POST /search/

Vector search across stored posts.

```json
{
  "query": "machine learning",
  "n": 10
}
```

### GET /health

Health check. Returns `{"status": "ok", "service": "PulseScout"}`.

## Deployment

### Docker

```bash
docker build -t pulsescout .
docker run -p 8000:8000 --env-file .env pulsescout
```

### CI/CD

GitHub Actions pipeline: test -> build Docker image -> push to GHCR -> deploy to Render.

### n8n Orchestration (optional)

Set up an n8n workflow with a Schedule Trigger that calls `POST /scrape/` every 6 hours to continuously monitor trends.

## Tech Stack

| Component | Technology |
|---|---|
| API | FastAPI |
| Scraping | YouTube Data API v3, HackerNews Firebase API |
| Vector Store | Qdrant Cloud |
| LLM Analysis | Ollama Cloud (gemma3:12b) |
| Embeddings | Hash-based (SHA256 -> 384-dim vectors) |
| CI/CD | GitHub Actions -> GHCR -> Render |
| Testing | pytest (53 tests, fully mocked) |
| Orchestration | n8n (optional) |
