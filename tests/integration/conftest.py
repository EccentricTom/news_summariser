import pytest

@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    monkeypatch.setenv("API_URL", "https://fake-api.local")
    monkeypatch.setenv("API_LANG", "en")
    monkeypatch.setenv("DB_URL", "sqlite:///:memory:")
