"""Pytest fixtures and environment configuration for tests."""

import os
from collections.abc import AsyncIterator
import pytest
from httpx import ASGITransport, AsyncClient

os.environ["APP_ENV"] = "test"
os.environ["LLM_BASE_URL"] = "http://mock-llm:11434/v1"
os.environ["LLM_API_KEY"] = "mock-key"
os.environ["LLM_DEFAULT_MODEL"] = "mock-model"
os.environ["LLM_FALLBACK_MODEL"] = "mock-fallback-model"

from src.api.main import create_app
from src.core.config import Settings, get_settings


@pytest.fixture
def test_settings() -> Settings:
    """Fixture returning test settings."""
    return get_settings()


@pytest.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """Asynchronous test client fixture for FastAPI endpoints."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
