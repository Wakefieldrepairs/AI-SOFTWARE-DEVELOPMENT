"""Unit tests for FastAPI endpoints."""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from src.core.llm import LLMResponse


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data
    assert "environment" in data
    assert "default_model" in data


@pytest.mark.asyncio
async def test_generate_endpoint(async_client: AsyncClient) -> None:
    mock_llm_response = LLMResponse(
        content="This is a generated test answer.",
        model_used="mock-model",
        prompt_tokens=5,
        completion_tokens=7,
        total_tokens=12,
        fallback_used=False,
    )

    with patch("src.api.routes.LLMClient.generate_completion", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_llm_response

        payload = {
            "messages": [{"role": "user", "content": "What is unit testing?"}],
            "temperature": 0.5,
            "max_tokens": 1024,
        }
        response = await async_client.post("/api/v1/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "This is a generated test answer."
        assert data["model_used"] == "mock-model"
        assert data["total_tokens"] == 12


@pytest.mark.asyncio
async def test_generate_stream_endpoint(async_client: AsyncClient) -> None:
    async def mock_stream(*args, **kwargs):
        yield "Token1 "
        yield "Token2"

    with patch("src.api.routes.LLMClient.stream_completion", side_effect=mock_stream):
        payload = {
            "messages": [{"role": "user", "content": "Stream this please"}],
            "stream": True,
        }
        response = await async_client.post("/api/v1/generate/stream", json=payload)
        assert response.status_code == 200
        assert response.text == "Token1 Token2"
