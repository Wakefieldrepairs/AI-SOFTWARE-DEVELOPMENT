"""Unit tests for configuration and environment handling."""

from src.core.config import Settings


def test_settings_defaults() -> None:
    settings = Settings(
        APP_NAME="Test Platform",
        LLM_BASE_URL="http://localhost:11434/v1",
        LLM_API_KEY="secret-key",
        LLM_DEFAULT_MODEL="test-llama",
    )
    assert settings.app_name == "Test Platform"
    assert settings.llm_base_url == "http://localhost:11434/v1"
    assert settings.llm_api_key == "secret-key"
    assert settings.llm_default_model == "test-llama"
    assert settings.parsed_cors_origins == ["*"]


def test_settings_cors_parsing() -> None:
    settings = Settings(
        CORS_ORIGINS="http://localhost:3000, https://app.example.com"
    )
    assert settings.parsed_cors_origins == ["http://localhost:3000", "https://app.example.com"]
