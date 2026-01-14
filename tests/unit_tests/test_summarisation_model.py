import pytest
from models.summarisation_model import SummarisationModel


@pytest.fixture(scope="module")
def summariser():
    """Fixture to create a summarisation model instance."""
    return SummarisationModel()

def test_summarisation_model_basic(summariser):
    """Test basic functionality of the summarisation model."""
    sample_text = (
        "The quick brown fox jumps over the lazy dog. "
        "This is a sample text to demonstrate the summarisation capabilities of the model. "
        "The model should be able to condense this information into a shorter form while retaining the key points."
    )
    summary = summariser.summarise(sample_text, max_length=50, min_length=10)
    assert isinstance(summary, str)
    assert len(summary) < len(sample_text)

def test_summarisation_model_edge_case(summariser):
    """Test summarisation model with edge case input."""
    sample_text = "Short text."
    summary = summariser.summarise(sample_text, max_length=20, min_length=5)
    assert isinstance(summary, str)
    assert summary == sample_text  # Expecting the same text back since it's too short to summarise

def test_summarisation_model_long_text(summariser):
    """Test summarisation model with a long text input."""
    sample_text = (
        "In a village of La Mancha, the name of which I have no desire to call to mind, there lived not long since one of those gentlemen that keep a lance in the lance-rack, an old buckler, a lean hack, and a greyhound for coursing. "
        "An olla of rather more beef than mutton, a salad on most nights, some lean chorizo, and a pigeon or so constituted his whole diet. "
        "He was fond of reading books of chivalry with great zeal and devotion."
    )
    summary = summariser.summarise(sample_text, max_length=60, min_length=20)
    assert isinstance(summary, str)
    assert len(summary) < len(sample_text)
    assert "village of La Mancha" in summary or "gentlemen" in summary

def test_summarisation_model_special_characters(summariser):
    """Test summarisation model with text containing special characters."""
    sample_text = (
        "Café müller is a famous café in Berlin. "
        "It's known for its unique ambiance & delicious pastries! "
        "Visitors often say: 'It's a must-visit spot.'"
    )
    summary = summariser.summarise(sample_text, max_length=40, min_length=10)
    assert isinstance(summary, str)
    assert len(summary) < len(sample_text)
    assert "Café" in summary or "müller" in summary  # Ensure special characters are retained

def test_summarisation_model_empty_text(summariser):
    """Test summarisation model with empty text input."""
    sample_text = ""
    summary = summariser.summarise(sample_text, max_length=20, min_length=5)
    assert isinstance(summary, str)
    assert summary == ""  # Expecting empty string back

