# 🤝 Contributing Guidelines & Branch Strategy

Welcome to the collaborative AI Agent Platform. To enable multiple developers to work asynchronously without environment drift or merge conflicts, please follow the guidelines below.

---

## 🌿 1. Git Workflow & Branch Strategy

We utilize a streamlined feature-branch workflow:

1. **`main`**: Production-ready branch. Direct pushes are blocked; all changes must arrive via reviewed PR.
2. **`develop`**: Active integration branch where feature branches merge.
3. **Feature Branches**: Branch from `develop` using a structured naming convention:
   - `feature/<ticket-or-name>` (e.g., `feature/openai-streaming`)
   - `fix/<issue-name>` (e.g., `fix/token-counter-overflow`)
   - `refactor/<target>` (e.g., `refactor/llm-client-interface`)

### Branching Lifecycle
```bash
# 1. Ensure you have the latest develop branch
git checkout develop
git pull origin develop

# 2. Create your isolated feature branch
git checkout -b feature/my-new-feature

# 3. Work on your changes, committing frequently with conventional commits
git commit -m "feat: add fallback model retry mechanism"

# 4. Keep your branch up to date before opening a PR
git fetch origin
git rebase origin/develop
```

---

## 🚀 2. Local Setup & Quickstart

Run the automated setup script to provision your virtual environment and pre-commit hooks:

```bash
bash setup.sh
```

Or execute manually:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
```

---

## 🧪 3. Pre-Push Validation Checklist

Before opening a Pull Request or pushing commits, execute all quality gates locally:

```bash
# 1. Format & Lint
ruff check .
ruff format --check .

# 2. Type Check
mypy src

# 3. Run Test Suite
pytest
```

---

## 📬 4. Opening a Pull Request

1. Push your branch to GitHub:
   ```bash
   git push origin feature/my-new-feature
   ```
2. Open a Pull Request targeting `develop` (or `main`).
3. Fill out all sections in the [PR Template](.github/pull_request_template.md).
4. Ensure all GitHub Actions CI checks pass.
5. Request review from your peer developer.
