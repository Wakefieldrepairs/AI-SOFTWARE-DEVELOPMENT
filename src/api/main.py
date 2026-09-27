"""FastAPI application initialization and lifecycle setup."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.core.config import get_settings
from src.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle events (startup / shutdown)."""
    settings = get_settings()
    logger = setup_logging(settings.log_level)
    logger.info("Starting %s in %s mode...", settings.app_name, settings.app_env)
    logger.info("LLM Base URL: %s | Default Model: %s", settings.llm_base_url, settings.llm_default_model)
    yield
    logger.info("Shutting down %s...", settings.app_name)


def create_app() -> FastAPI:
    """Factory function to create configured FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Collaborative AI Service API powered by FastAPI and OpenAI-compatible backends.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.parsed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.app_env == "development"),
    )
