setup:
	uv init -p main news_summariser
	uv sync

test:
	pytest tests/