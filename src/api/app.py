"""FastAPI application module alias and runner for src/api/app.py."""

import uvicorn
from src.api.main import app, create_app
from src.core.config import get_settings

__all__ = ["app", "create_app"]

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.app_env == "development"),
    )
