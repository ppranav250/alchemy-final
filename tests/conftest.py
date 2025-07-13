import pytest
import os

@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    """Automatically sets mock environment variables for all tests."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("LMNT_API_KEY", "test_lmnt_key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_key")
