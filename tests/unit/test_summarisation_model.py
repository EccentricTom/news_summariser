from news_summariser.models.summarisation_model import SummarisationModel

def test_empty_returns_empty():
    m = SummarisationModel(summarizer=lambda *args, **kwargs: [{"summary_text": "x"}])
    assert m.summarise("") == ""
    assert m.summarise("   ") == ""

def test_punctuation_fix():
    def fake(text, max_length, min_length):
        return [{"summary_text": "Hello ."}]

    m = SummarisationModel(summarizer=fake)
    assert m.summarise("ignored") == "Hello."
