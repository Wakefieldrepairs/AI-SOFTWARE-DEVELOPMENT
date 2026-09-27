"""Unit tests for LLM client wrapper and fallback mechanism."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from openai import APIConnectionError

from src.core.llm import LLMClient, Message


@pytest.mark.asyncio
async def test_llm_client_initialization() -> None:
    client = LLMClient(
        base_url="http://mock-url/v1",
        api_key="test-key",
        default_model="gpt-test",
        fallback_model="gpt-test-fallback",
    )
    assert client.base_url == "http://mock-url/v1"
    assert client.api_key == "test-key"
    assert client.default_model == "gpt-test"
    assert client.fallback_model == "gpt-test-fallback"


@pytest.mark.asyncio
async def test_generate_completion_success() -> None:
    client = LLMClient(
        base_url="http://mock-url/v1",
        api_key="test-key",
        default_model="gpt-test",
    )

    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello from mock LLM!"
    mock_choice.finish_reason = "stop"
    mock_response.choices = [mock_choice]
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    with patch.object(client._client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        response = await client.generate_completion(
            messages=[Message(role="user", content="Hi")]
        )

        assert response.content == "Hello from mock LLM!"
        assert response.model_used == "gpt-test"
        assert response.total_tokens == 15
        assert response.fallback_used is False
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_completion_fallback_trigger() -> None:
    client = LLMClient(
        base_url="http://mock-url/v1",
        api_key="test-key",
        default_model="primary-model",
        fallback_model="backup-model",
    )

    mock_fallback_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Fallback model response"
    mock_choice.finish_reason = "stop"
    mock_fallback_response.choices = [mock_choice]
    mock_fallback_response.usage.prompt_tokens = 8
    mock_fallback_response.usage.completion_tokens = 4
    mock_fallback_response.usage.total_tokens = 12

    with patch.object(client._client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        # First call fails, second call succeeds
        mock_create.side_effect = [
            APIConnectionError(request=MagicMock()),
            mock_fallback_response,
        ]

        response = await client.generate_completion(
            messages=[Message(role="user", content="Hello")]
        )

        assert response.content == "Fallback model response"
        assert response.model_used == "backup-model"
        assert response.fallback_used is True
        assert mock_create.call_count == 2


@pytest.mark.asyncio
async def test_stream_completion() -> None:
    client = LLMClient(
        base_url="http://mock-url/v1",
        api_key="test-key",
        default_model="stream-model",
    )

    chunk1 = MagicMock()
    chunk1.choices = [MagicMock(delta=MagicMock(content="Hello"))]
    chunk2 = MagicMock()
    chunk2.choices = [MagicMock(delta=MagicMock(content=" world!"))]

    class AsyncStreamMock:
        def __aiter__(self):
            return self
        def __init__(self):
            self._items = [chunk1, chunk2]
            self._idx = 0
        async def __anext__(self):
            if self._idx < len(self._items):
                item = self._items[self._idx]
                self._idx += 1
                return item
            raise StopAsyncIteration

    with patch.object(client._client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = AsyncStreamMock()
        collected = []
        async for chunk in client.stream_completion([Message(role="user", content="Stream test")]):
            collected.append(chunk)

        assert "".join(collected) == "Hello world!"
