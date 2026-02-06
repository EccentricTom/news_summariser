# News Summariser

Small Python project that pulls news stories, extracts full article text, generates a short summary, and stores results in a database.

This repo is mainly a portfolio example of a clean ingestion pipeline with a simple service layer, a persistence layer, and tests at different levels (unit, integration, live).

## What it does

The pipeline:

1. Fetches story lists by category from a news API
2. Fetches and parses full article pages (BBC parsing)
3. Runs summarisation on the full story text
4. Stores the enriched records into a database via SQLAlchemy

Current categories are:
- Technology
- Business
- Entertainment

Sentiment analysis exists in the codebase but is currently disabled in the pipeline.

## Repository structure

```
├── src/
│   └── news_summariser/
│       ├── client/
│       │   ├── __init__.py
│       │   └── news_api_client.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── engine.py
│       │   ├── init.py
│       │   ├── repository.py
│       │   └── schema.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── sentiment_model.py
│       │   └── summarisation_model.py
│       ├── parsing/
│       │   ├── __init__.py
│       │   └── bbc_article_parser.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── news_summary_sentiment_pipeline.py
│       ├── __init__.py
│       ├── config.py
│       └── main.py
├── tests/
│   ├── integration/
│   │   ├── conftest.py
│   │   └── test_pipeline_store.py
│   ├── live/
│   │   └── test_live_api.py
│   └── unit/
│       ├── conftest.py
│       ├── test_bbc_article_parser.py
│       ├── test_news_api_client.py
│       ├── test_repository_sqlite.py
│       └── test_summarisation_model.py
├── .env
├── .gitignore
├── .python-version
├── Makefile
├── pyproject.toml
├── README.md
└── uv.lock
```

## Setup

### Python version

See `.python-version`.

### Install dependencies

If you are using `uv`:

```bash
uv sync
```
Or with a standard venv + pip:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Configuration is loaded from environment variables (dotenv is supported via .env).

Required:

- API_URL: Base URL for the news API used by NewsApiClient

- DB_URL: SQLAlchemy database URL (SQLite works fine for local use)

Optional:

- API_LANG: Defaults to en

Example .env:
```text
API_URL="https://example.com"
DB_URL="sqlite:///news.db"
API_LANG="en"
```

## Running the Pipeline

```bash
python -m news_summariser.main
```
By default it runs the pipeline with `story_limit=5` (per category).

If you want to run it with a different limit, adjust `run_once()` in `src/news_summariser/main.py` or call the pipeline directly from a small script:

```bash
from news_summariser.services.news_summary_sentiment_pipeline import pipeline

pipeline(story_limit=10)
```
## Data Storage

On startup the pipeline creates tables if they do not exist.

Persistence is handled via:
- db/engine.py for engine creation
- db/init.py for table creation
- db/repository.py for inserts

## Tests

Tests are split by intent:
- `tests/unit/`: No external network calls. Focused on parsing, models, repository behaviour.
- `tests/integration/`: Exercises pipeline storage and DB integration.
- `tests/live/`: Calls the live API. These tests require network access and a working `API_URL`.

Run all tests:
```bash
make test-all
```

To skip live tests:
```bash
test-no-live
```
## Notes/Limitations

- SentimentModel is present but currently commented out in the pipeline.
- The BBC parsing logic is specific to the current BBC page structure and may need maintenance over time.
- This project is intentionally simple and optimised for readability and reproducibility rather than feature completeness.



