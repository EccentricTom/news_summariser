from __future__ import annotations
from typing import Callable, List, Dict, Optional
from transformers import pipeline


SentimentCallable = Callable[[str], List[Dict[str, str]]]


class SentimentModel:
    """Class wrapper around a text sentiment model."""

    def __init__(
        self,
        model_name: str = "siebert/sentiment-roberta-large-english",
        sentiment_callable: Optional[SentimentCallable] = None,
    ):
        """
        If `sentiment_callable` is provided, it will be used instead of creating a HF pipeline.
        This makes unit tests fast and deterministic.
        """
        self.sentiment_callable = sentiment_callable or pipeline("sentiment-analysis", model=model_name)

    def get_sentiment(self, text: str) -> List[Dict[str, str]]:
        return self.sentiment_callable(text)
