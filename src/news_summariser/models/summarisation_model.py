from __future__ import annotations
from typing import Callable, List, Dict, Optional
from transformers import pipeline


SummarizerCallable = Callable[[str], List[Dict[str, str]]]


class SummarisationModel:
    """Class wrapper around a text summarisation model."""

    def __init__(
        self,
        model_name: str = "Falconsai/text_summarization",
        summarizer: Optional[Callable[[str, int, int], List[Dict[str, str]]]] = None,
    ):
        """
        If `summarizer` is provided, it will be used instead of creating a HF pipeline.
        This makes unit tests fast and deterministic.
        """
        self.summarizer = summarizer or pipeline("summarization", model=model_name)

    def summarise(self, text: str, max_length: int = 200, min_length: int = 30) -> str:
        if not text or text.strip() == "":
            return ""

        summary_list = self.summarizer(text, max_length=max_length, min_length=min_length)

        if not summary_list or "summary_text" not in summary_list[0]:
            raise ValueError("Unexpected summarizer output")

        summary_text = summary_list[0]["summary_text"]

        punctuation_marks = {".", ",", "!", "?", ";", ":"}
        if len(summary_text) > 1 and summary_text[-2] == " " and summary_text[-1] in punctuation_marks:
            summary_text = summary_text[:-2] + summary_text[-1]

        return summary_text
