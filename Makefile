setup:
	uv init -p main news_summariser
	uv sync

# Skips all live tests
test-no-live:
	pytest tests/

# Run only live tests
test-live:
	RUN_LIVE_API=1 pytest tests/live -s

# Run only unit tests
test-unit:
	pytest tests/unit

# run only integration tests
test-integration:
	pytest tests/integration

# Run all tests
test-all:
	RUN_LIVE_API=1 pytest tests/

# Run once
run:
	uv pip install -e .
	uv run news-summariser