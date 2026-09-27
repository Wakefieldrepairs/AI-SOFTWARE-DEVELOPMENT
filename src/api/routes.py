"""API route definitions for health checks and text generation."""

import logging
from collections.abc import AsyncIterator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.core.config import Settings, get_settings
from src.core.llm import LLMClient, LLMResponse, Message

logger = logging.getLogger("app.api")
router = APIRouter()


def get_llm_client(settings: Settings = Depends(get_settings)) -> LLMClient:
    """Dependency injection provider for LLMClient."""
    return LLMClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        default_model=settings.llm_default_model,
        fallback_model=settings.llm_fallback_model,
        timeout_seconds=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )


class HealthResponse(BaseModel):
    """Schema for health check endpoint."""

    status: str = "ok"
    app_name: str
    environment: str
    default_model: str
    fallback_model: str


class GenerateRequest(BaseModel):
    """Schema for standard completion request."""

    messages: list[Message] = Field(
        ..., min_length=1, description="List of chat messages in the conversation"
    )
    model: str | None = Field(default=None, description="Optional model override")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    stream: bool = Field(default=False, description="Set to true for SSE-style chunk streaming")


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Returns system health status and configuration details."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.app_env,
        default_model=settings.llm_default_model,
        fallback_model=settings.llm_fallback_model,
    )


@router.post("/generate", response_model=LLMResponse, tags=["Generation"])
async def generate_completion(
    request: GenerateRequest,
    client: LLMClient = Depends(get_llm_client),
) -> LLMResponse:
    """Generate a chat completion from the configured LLM backend."""
    try:
        return await client.generate_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except Exception as err:
        logger.error("Generation failed: %s", str(err))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM upstream service error: {err!s}",
        ) from err


@router.post("/generate/stream", tags=["Generation"])
async def generate_stream(
    request: GenerateRequest,
    client: LLMClient = Depends(get_llm_client),
) -> StreamingResponse:
    """Stream text chunks as plain text SSE fragments."""

    async def event_generator() -> AsyncIterator[str]:
        try:
            async for chunk in client.stream_completion(
                messages=request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                yield chunk
        except Exception as err:
            logger.error("Streaming failed: %s", str(err))
            yield f"\n[STREAM_ERROR: {err!s}]"

    return StreamingResponse(event_generator(), media_type="text/plain")
