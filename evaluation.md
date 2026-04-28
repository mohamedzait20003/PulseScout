# Evaluation: Design Decisions & Trade-offs

## Technical Execution

### Architecture

PulseScout follows a layered REST API architecture: Routes → Controllers → Utils → Models. Each layer has a single responsibility — routes handle HTTP, controllers orchestrate business logic, utils handle external API calls, and models manage Qdrant persistence. Three separate Qdrant collections are maintained: `posts` (scraped content), `comments` (per-comment records), and `reports` (LLM analysis results).

**Trade-off:** A simpler single-file script would have been faster to build, but the layered approach makes individual components testable in isolation and keeps the codebase extensible without entanglement.

### Decorator-based Configuration

Three decorator types inject config at different scopes:
- `@scraper_config` — method-level defaults (limit, timeout, max text length)
- `@scraper_urls` — class-level API URLs from environment
- `@analyzer_config` — method-level LLM defaults (timeout, max post length)

**Trade-off:** More complex than passing arguments directly, but eliminates config duplication and makes every default overridable at the call site without touching environment variables.

### Hash-based Embeddings

PulseScout generates 384-dimensional vectors from SHA256 hashes of document text rather than using a dedicated embedding model (OpenAI, Sentence Transformers).

**Trade-off:** Hash vectors don't capture semantic similarity — "machine learning" and "deep learning" won't be neighbours in vector space. This limits search precision but eliminates an external dependency and keeps the system lightweight. For a monitoring agent where the primary value is LLM analysis (sentiment, topics, trends) rather than semantic retrieval, this is an acceptable trade-off. A production upgrade would swap in a proper embedding model.

### UUID5 Deduplication

Posts are assigned deterministic IDs via UUID5 (namespace + source ID). The same post scraped twice produces the same UUID, preventing duplicates without a separate existence check per write.

**Trade-off:** Slightly more overhead than random UUIDs, but guarantees idempotent scraping — critical for a system running on a recurring schedule where the same content will be encountered across cycles.

### Trend Persistence Across Restarts

`ScrapeController` seeds `last_analysis` from the latest stored `ReportModel` on startup rather than holding it only in memory. This ensures trend comparisons survive server restarts and redeployments.

**Trade-off:** Adds a Qdrant read on every cold start. The cost is negligible compared to the scrape cycle, and the alternative (losing trend history on every deploy) would break the core feature.

## Reproducibility

- All configuration is environment-driven via `.env`
- Dockerized with a single `Dockerfile`
- GitHub Actions CI/CD pipeline: test → build Docker image → push to GHCR → deploy to Render
- All tests run with fully mocked external services — no API keys required
- `pytest.ini` configures test discovery and `src/` path injection

## Creativity

### Multi-source Aggregation

Combining YouTube (video titles, descriptions, view counts, comments) with HackerNews (text posts, community scores, comment threads) provides two distinct perspectives on the same topics. YouTube captures mainstream and commercial attention; HackerNews captures technical community sentiment. The contrast between them is itself an insight — a topic trending on YouTube but absent from HackerNews signals consumer interest without technical validation, and vice versa.

### Fixed Topic Monitoring

Rather than accepting user-defined tags, PulseScout monitors five fixed topics chosen for G2 relevance:
`AI market trends` · `tech startup funding` · `venture capital` · `emerging technology` · `consumer sentiment`

This makes the agent self-contained — it knows what to watch without being told — and ensures every scrape cycle is comparable to the last.

### Batch Trend Comparison

Each scrape cycle is compared against the previous batch using a dedicated LLM prompt. This produces rising/declining topics and sentiment shifts — not just a snapshot, but a direction. The previous batch summary is seeded from Qdrant on startup so trend continuity is maintained across restarts.

### Dify Orchestration — Two Workflows

**Workflow 1 (Scheduled Scrape):** A Dify workflow triggers `POST /scrape/` every 6 hours, parses the response, and gates further processing on whether LLM analysis actually succeeded — preventing empty results from propagating downstream.

**Workflow 2 (Query Chatflow):** A Dify chatflow provides a natural language interface over stored insights. It searches for relevant posts via vector search, fetches recent analysis reports, and synthesizes a market intelligence answer via Gemini Flash. This turns raw stored data into an interactive analyst.

### API-first Design

PulseScout exposes a clean REST API with no built-in scheduler or UI. External orchestrators (Dify, cron, curl) call it on their schedule. This makes it composable — it can be plugged into any existing workflow without modification.

## Business Impact Reasoning

### Problem

Teams making product, marketing, or investment decisions need to know what topics are gaining or losing traction in their market. Manual monitoring doesn't scale, and most social listening tools are expensive and opaque.

### Solution

PulseScout automates the "doomscroll" — it watches YouTube and HackerNews continuously and uses LLM analysis to extract:
- **Sentiment breakdown** — is the community feeling positive or negative about a topic?
- **Topic clustering** — what themes keep appearing together?
- **Trend direction** — are topics rising or declining compared to the last cycle?
- **Actionable insight** — one paragraph summarising what a decision-maker should act on

### Real Output Example

From a live scrape run on 2026-04-27:

> "The posts highlight ongoing developments in both AI-driven education and backend infrastructure for large-scale platforms. Sal Khan's perspective suggests AI adoption in education is slower than anticipated, while Airbnb's billion-series Prometheus metrics pipeline demonstrates the increasing complexity of data management at scale."

And from the Query Chatflow on rising trends:

> "AI-Powered No-Code SaaS is surging — content focused on building $10k+/month businesses using tools like Cursor without writing code is accelerating. Venture Capital literacy content is also rising, indicating strong demand for understanding how to access early-stage funding. AI is simultaneously disrupting the traditional SaaS model, with discussions emerging around how companies are pivoting toward practical AI application for growth."

This kind of output lets a product or investment team adjust priorities based on real-time community signals rather than quarterly reports.

### Cost Awareness

| Component | Cost model |
|---|---|
| YouTube Data API | 10,000 units/day free tier; each search costs 100 units |
| HackerNews API | Free, no quota |
| Qdrant Cloud | Free tier: 1 cluster, 1GB storage |
| Ollama Cloud | Pay-per-token; gemma3:12b is low-cost |
| Render | Free tier with cold starts; $7/month for always-on |
| Dify | Cloud free tier covers scheduled workflows |

A full scrape cycle (5 YouTube searches × 25 results = 500 units + stats calls) consumes ~750 YouTube API units per run. At 6-hour intervals that is 3,000 units/day — well within the free tier.

## Limitations & Future Work

- **Hash embeddings** should be replaced with a proper embedding model (e.g. `all-MiniLM-L6-v2`) for semantic search quality
- **YouTube quota** (10,000 units/day) limits scraping volume at higher frequencies — response caching would help
- **Single LLM provider** — adding a fallback (e.g. Gemini if Ollama is unavailable) would improve reliability
- **No API authentication** — production deployment should add API key middleware
- **Comment sentiment** is included in the batch prompt but not weighted separately from post content — a dedicated comment analysis pass would add signal
- **Workflow 2 is sequential** — the search and analysis HTTP calls could run in parallel in Dify to halve latency once parallel branching is configured
