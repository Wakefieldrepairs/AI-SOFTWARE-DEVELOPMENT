#!/usr/bin/env bash
# =============================================================================
# Developer Environment Bootstrap & Git Pre-Commit Hook Configuration
# =============================================================================

set -euo pipefail

echo "🚀 [1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found in PATH. Aborting."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Found Python $PYTHON_VERSION"

echo "📦 [2/5] Creating isolated virtual environment in .venv..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Created .venv"
else
    echo "ℹ️  .venv already exists, skipping creation."
fi

# Activate venv for current script
source .venv/bin/activate

echo "⬆️  [3/5] Upgrading pip and installing dev dependencies..."
pip install --upgrade pip
pip install -r requirements-dev.txt

echo "⚙️  [4/5] Provisioning environment configuration file (.env)..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Initialized .env from .env.example"
else
    echo "ℹ️  .env already exists, keeping existing configurations."
fi

echo "🪝 [5/5] Configuring Git pre-commit hook..."
HOOK_PATH=".git/hooks/pre-commit"
if [ -d ".git" ]; then
    mkdir -p .git/hooks
    cat << 'EOF' > "$HOOK_PATH"
#!/usr/bin/env bash
set -e
echo "🔍 Running pre-commit validation gates (Ruff & Pytest)..."

source .venv/bin/activate

echo "  -> Checking formatting & linting with Ruff..."
ruff check .
ruff format --check .

echo "  -> Running unit test suite..."
pytest -q

echo "✅ All pre-commit checks passed successfully!"
EOF
    chmod +x "$HOOK_PATH"
    echo "✅ Installed pre-commit hook at $HOOK_PATH"
else
    echo "ℹ️  Not a git repository root. Skipping pre-commit hook creation."
fi

echo ""
echo "🎉 Setup complete! You can now start developing:"
echo "   source .venv/bin/activate"
echo "   # Run FastAPI backend:"
echo "   uvicorn src.api.main:app --reload --port 8000"
echo "   # Run Streamlit UI:"
echo "   streamlit run src/app.py --server.port 8501"
