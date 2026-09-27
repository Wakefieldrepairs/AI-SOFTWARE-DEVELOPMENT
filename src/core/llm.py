"""OpenAI-compatible LLM client wrapper with streaming, fallbacks, and retry support."""

import logging
from collections.abc import AsyncIterator
from typing import Any, Literal
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError
from pydantic import BaseModel, Field

logger = logging.getLogger("app.llm")


class Message(BaseModel):
    """Chat message structure."""

    role: Literal["system", "user", "assistant"] = "user"
    content: str


class LLMResponse(BaseModel):
    """Standardized response wrapper from LLM client."""

    content: str
    model_used: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    fallback_used: bool = False
    finish_reason: str = "stop"


class LLMClient:
    """Resilient OpenAI-compatible LLM client with fallback handling."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        default_model: str,
        fallback_model: str | None = None,
        timeout_seconds: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.default_model = default_model
        self.fallback_model = fallback_model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

        self._client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout_seconds,
            max_retries=self.max_retries,
        )

    async def generate_completion(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a chat completion with automated fallback model execution upon failure."""
        target_model = model or self.default_model
        payload_messages = [msg.model_dump() for msg in messages]

        try:
            logger.info("Attempting completion with model '%s'", target_model)
            response = await self._client.chat.completions.create(
                model=target_model,
                messages=payload_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            choice = response.choices[0]
            usage = response.usage
            return LLMResponse(
                content=choice.message.content or "",
                model_used=target_model,
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
                fallback_used=False,
                finish_reason=choice.finish_reason or "stop",
            )
        except (APIError, APIConnectionError, RateLimitError) as err:
            logger.warning(
                "Primary model '%s' failed: %s. Checking for fallback.", target_model, str(err)
            )
            if self.fallback_model and self.fallback_model != target_model:
                logger.info("Retrying with fallback model '%s'", self.fallback_model)
                try:
                    fallback_resp = await self._client.chat.completions.create(
                        model=self.fallback_model,
                        messages=payload_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs,
                    )
                    choice = fallback_resp.choices[0]
                    usage = fallback_resp.usage
                    return LLMResponse(
                        content=choice.message.content or "",
                        model_used=self.fallback_model,
                        prompt_tokens=usage.prompt_tokens if usage else 0,
                        completion_tokens=usage.completion_tokens if usage else 0,
                        total_tokens=usage.total_tokens if usage else 0,
                        fallback_used=True,
                        finish_reason=choice.finish_reason or "stop",
                    )
                except Exception as fallback_err:
                    logger.error("Fallback model '%s' also failed: %s", self.fallback_model, str(fallback_err))
                    raise fallback_err from err
            raise err

    async def stream_completion(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream token chunks asynchronously."""
        target_model = model or self.default_model
        payload_messages = [msg.model_dump() for msg in messages]

        logger.info("Streaming completion with model '%s'", target_model)
        response_stream = await self._client.chat.completions.create(
            model=target_model,
            messages=payload_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
