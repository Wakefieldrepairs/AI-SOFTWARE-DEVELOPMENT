# 🤖 Collaborative AI Agent Platform

Production-ready, containerized Python workspace designed for asynchronous AI application development. Built with **FastAPI**, **Streamlit**, **OpenAI / Ollama wrapper**, strict GitHub hygiene, and automated CI/CD pipelines.

---

## 🌟 Key Features

- **Resilient LLM Client**: OpenAI-compatible asynchronous client supporting custom `base_url` (Ollama, vLLM, LiteLLM, OpenAI), token streaming, and automatic model fallback on failure.
- **Modern REST API**: High-performance FastAPI backend with endpoints for health checks, prompt generation, and token streaming.
- **Interactive Developer UI**: Streamlit web application for interactive model testing, parameter tweaking, and real-time streaming validation.
- **Container Ready**: Multi-stage `Dockerfile` and `docker-compose.yml` pre-configured with host network bridges (`host.docker.internal`).
- **Zero-Drift Collaboration**: Pinned dependencies, pre-commit git hooks, strict `.gitignore`, PR templates, and GitHub Actions CI workflow (Ruff + Mypy + Pytest).

---

## 📂 Project Structure

```text
.
├── .env.example                  # Environment configuration template
├── .gitignore                    # Exhaustive ignore rules (ML models, cache, venv)
├── .github/
│   ├── pull_request_template.md  # Standardized PR checklist
│   └── workflows/
│       └── ci.yml                # Automated CI pipeline (ruff, mypy, pytest)
├── Dockerfile                    # Multi-stage slim Docker image
├── docker-compose.yml            # Multi-service setup (FastAPI + Streamlit)
├── pyproject.toml                # Build configuration & tool settings
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.sh                      # One-command developer bootstrap & git hooks
├── CONTRIBUTING.md               # Async collaboration & branch strategy guide
├── src/
│   ├── __init__.py
│   ├── app.py                    # Streamlit developer web interface
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application lifecycle & CORS
│   │   └── routes.py             # Health & generation route endpoints
│   └── core/
│       ├── __init__.py
│       ├── config.py             # Pydantic BaseSettings environment loader
│       ├── llm.py                # OpenAI-compatible LLM client wrapper
│       └── logging.py            # Structured logging setup
└── tests/
    ├── __init__.py
    ├── conftest.py               # Pytest async fixtures
    ├── test_api.py               # FastAPI endpoint tests
    ├── test_config.py            # Settings validation tests
    └── test_llm.py               # LLM client & fallback unit tests
```

---

## 🚀 Getting Started

### 1. Automated Setup (Recommended)
Run the bootstrap script which sets up your virtual environment, installs dependencies, initializes `.env`, and sets up git pre-commit hooks:
```bash
bash setup.sh
```

### 2. Manual Setup
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
```

### 3. Launching Services Locally

**Run FastAPI Backend:**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
- Health Check: `GET http://localhost:8000/api/v1/health`
- Swagger API Docs: `http://localhost:8000/docs`

**Run Streamlit UI:**
```bash
streamlit run src/app.py --server.port 8501
```
- UI URL: `http://localhost:8501`

---

## 🐳 Running with Docker Compose

Start both FastAPI and Streamlit concurrently:
```bash
docker-compose up --build
```
- Backend: `http://localhost:8000`
- Developer UI: `http://localhost:8501`

---

## 🧪 Running Tests & Quality Gates

```bash
# Run unit and integration tests
pytest

# Run linting and formatting check
ruff check .
ruff format --check .

# Run static type checking
mypy src
```

---

## 🤝 Contribution Guidelines
Please consult [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming conventions, PR templates, and workflow protocols.
