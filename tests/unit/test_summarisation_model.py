import pytest

import models.summarisation_model as sm


class FakeSummarizer:
    def __init__(self, return_text="Some summary"):
        self.return_text = return_text
        self.calls = []

    def __call__(self, text, max_length, min_length):
        self.calls.append(
            {"text": text, "max_length": max_length, "min_length": min_length}
        )
        return [{"summary_text": self.return_text}]

def test_init_uses_pipeline(monkeypatch):
    fake = FakeSummarizer()

    def fake_pipeline(task, model):
        assert task == "summarization"
        assert model == "Falconsai/text_summarization"
        return fake

    monkeypatch.setattr(sm, "pipeline", fake_pipeline)

    m = sm.SummarisationModel()
    assert m.summarizer is fake


def test_summarise_empty_returns_empty(monkeypatch):
    fake = FakeSummarizer(return_text="SHOULD NOT BE USED")

    monkeypatch.setattr(sm, "pipeline", lambda task, model: fake)
    m = sm.SummarisationModel()

    assert m.summarise("") == ""
    assert m.summarise("   \n\t") == ""
    assert fake.calls == []  # summarizer not called for empty input


def test_summarise_calls_underlying_with_lengths(monkeypatch):
    fake = FakeSummarizer(return_text="OK")

    monkeypatch.setattr(sm, "pipeline", lambda task, model: fake)
    m = sm.SummarisationModel()

    out = m.summarise("hello world", max_length=50, min_length=10)
    assert out == "OK"
    assert fake.calls == [{"text": "hello world", "max_length": 50, "min_length": 10}]


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Hello .", "Hello."),
        ("Hello ,", "Hello,"),
        ("Hello !", "Hello!"),
        ("Hello ?", "Hello?"),
        ("Hello ;", "Hello;"),
        ("Hello :", "Hello:"),
    ],
)
def test_punctuation_space_fix(monkeypatch, raw, expected):
    fake = FakeSummarizer(return_text=raw)

    monkeypatch.setattr(sm, "pipeline", lambda task, model: fake)
    m = sm.SummarisationModel()

    assert m.summarise("some input", max_length=20, min_length=5) == expected


def test_does_not_modify_normal_text(monkeypatch):
    fake = FakeSummarizer(return_text="Hello world.")

    monkeypatch.setattr(sm, "pipeline", lambda task, model: fake)
    m = sm.SummarisationModel()

    assert m.summarise("some input") == "Hello world."

def test_raises_on_unexpected_output(monkeypatch):
    class BadSummarizer:
        def __call__(self, text, max_length, min_length):
            return [{}]

    monkeypatch.setattr(sm, "pipeline", lambda task, model: BadSummarizer())
    m = sm.SummarisationModel()

    with pytest.raises(ValueError):
        m.summarise("hello")

