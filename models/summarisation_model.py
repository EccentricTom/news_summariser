"""Class wrapper around summarisation model."""

from transformers import pipeline

class SummarisationModel:
    """Class wrapper around a text summarisation model."""

    def __init__(self, model_name: str = "Falconsai/text_summarization"):
        """Initialize the summarisation model pipeline."""
        self.summarizer = pipeline("summarization", model=model_name)

    def summarise(self, text: str, max_length: int = 200, min_length: int = 30) -> str:
        """Summarise the given text."""
        summary_list = self.summarizer(text, max_length=max_length, min_length=min_length)
        return summary_list[0]['summary_text']


if __name__ == "__main__":
    summariser = SummarisationModel()
    sample_text = (
        "The quick brown fox jumps over the lazy dog. "
        "This is a sample text to demonstrate the summarisation capabilities of the model. "
        "The model should be able to condense this information into a shorter form while retaining the key points."
    )
    summary = summariser.summarise(sample_text, max_length=50, min_length=10)
    print("Original Text:")
    print(sample_text)
    print("\nSummary:")
    print(summary)
