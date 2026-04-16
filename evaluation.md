# Evaluation: Design Decisions & Trade-offs

## Technical Execution

### Architecture

PulseScout follows a layered REST API architecture: Routes -> Controllers -> Utils/Models. This separation keeps concerns isolated — routes handle HTTP, controllers orchestrate business logic, utils handle external API calls, and models manage persistence.

**Trade-off:** A simpler single-file script would have been faster to build, but the layered approach demonstrates production readiness and makes individual components testable in isolation.

### Decorator-based Configuration

Three decorator types inject config at different scopes:
- `@scraper_config` — method-level defaults (limit, timeout)
- `@scraper_keys` — class-level API keys from environment
- `@scraper_urls` — class-level URLs from environment

**Trade-off:** More complex than passing arguments directly, but eliminates config duplication and makes defaults overridable at every call site without touching environment variables.

### Hash-based Embeddings

Instead of using a dedicated embedding model (OpenAI, Sentence Transformers), PulseScout generates 384-dimensional vectors from SHA256 hashes of document text.

**Trade-off:** Hash vectors don't capture semantic similarity — "machine learning" and "deep learning" won't be neighbors in vector space. This limits search quality but eliminates an external dependency and keeps the system lightweight. For a monitoring agent where the primary value is in LLM analysis (sentiment, topics, trends) rather than similarity search, this is an acceptable trade-off.

### UUID5 Deduplication

Posts are assigned deterministic IDs via UUID5 (namespace + source + original ID). The same post scraped twice produces the same UUID, preventing duplicates without a database lookup.

**Trade-off:** Slightly more computational overhead than random UUIDs, but guarantees idempotent scraping — critical for a system that runs on a recurring schedule.

## Reproducibility

- All configuration is environment-driven (`.env` file)
- Dockerized with a single `Dockerfile`
- CI/CD pipeline automates test -> build -> deploy
- 53 unit tests with fully mocked external services — tests run without API keys
- `pytest.ini` configures test discovery and Python path

## Creativity

### Multi-source Aggregation

Combining YouTube (video content, view counts, comments) with HackerNews (text posts, community scores) provides two different perspectives on the same topics. YouTube captures mainstream attention; HackerNews captures technical community sentiment.

### Trend Comparison Across Batches

Each scrape cycle is compared against the previous batch using LLM analysis. This produces rising/declining topics and sentiment shifts — not just a snapshot, but a direction. This is the core "actionable insight" capability.

### API-first Design

No built-in scheduler or UI. PulseScout exposes a clean REST API that external orchestrators (n8n, Dify, cron, or direct curl) can call. This makes it composable — it can be plugged into any existing workflow without modification.

## Business Impact Reasoning

### Problem

Teams making product, marketing, or investment decisions need to know what topics are gaining or losing traction in their market. Manual monitoring doesn't scale, and most social listening tools are expensive.

### Solution

PulseScout automates the "doomscroll" — it watches YouTube and HackerNews for signals, then uses LLM analysis to extract:
- **Sentiment breakdown** — is the community feeling positive or negative about a topic?
- **Topic clustering** — what themes keep appearing together?
- **Trend direction** — are topics rising or declining compared to last cycle?
- **Actionable insight** — one paragraph summarizing what a decision-maker should know

### Example Insight

A scrape with tags `["AI trends"]` might return:

> "Open-source LLM adoption is accelerating in enterprise environments, with sentiment shifting from cautious to strongly positive. Teams evaluating AI tooling should prioritize frameworks with strong community support, as developer mindshare is consolidating around 2-3 major ecosystems."

This kind of output lets a product team adjust roadmap priorities based on real-time community signals rather than quarterly reports.

## Limitations & Future Work

- **Hash embeddings** could be replaced with a proper embedding model for better semantic search
- **YouTube quota** (10,000 units/day) limits scraping volume — batching and caching would help
- **Single LLM provider** (Ollama) — adding fallback to another provider would improve reliability
- **No authentication** on the API — production deployment should add API key middleware
- **Comment analysis** is included in the prompt but not weighted separately from post content
