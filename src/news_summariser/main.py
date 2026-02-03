from news_summariser.services.news_summary_sentiment_pipeline import pipeline


def run_once():
    pipeline(story_limit=5)


if __name__ == "__main__":
    run_once()
