setup:
	uv init -p main news_summariser
	uv sync

# Skips all live tests
test:
	pytest tests/

# Run only live tests
test live:
	RUN_LIVE_API=1 pytest tests/live -s

# Run only unit tests
test unit:
	pytest tests/unit_tests 
