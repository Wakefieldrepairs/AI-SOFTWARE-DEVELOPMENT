# Multi-stage Python 3.11 Slim Image for Collaborative AI Application

# Stage 1: Build & Dependencies stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build essentials for C-extensions if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definitions and install into wheels/site-packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final Runtime stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PATH="/root/.local/bin:$PATH"

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local

# Install runtime curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY src/ /app/src/
COPY pyproject.toml /app/

# Expose default API and Streamlit ports
EXPOSE 8000 8501

# Health check on FastAPI endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default entrypoint starts FastAPI; overridden via docker-compose for UI
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
