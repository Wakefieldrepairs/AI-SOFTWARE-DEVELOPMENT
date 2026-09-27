## 📌 PR Summary
<!-- Provide a brief, high-level summary of what changes were made and why. -->

## 🛠️ Type of Change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] ⚡ Performance improvement / Refactoring
- [ ] 🔧 CI/CD or build tooling update

## 🧪 Verification & Testing Evidence
- [ ] Local tests passed (`pytest`)
- [ ] Ruff linting passed (`ruff check .`)
- [ ] Static type checks passed (`mypy src`)
- [ ] Streamlit interface verified locally
- [ ] FastAPI Swagger documentation verified at `/docs`

<!-- Attach screenshots, test output snippets, or reproduction steps below: -->
```bash
pytest -v
```

## ⚠️ Breaking Changes / Migration Notes
- Does this PR require changes to `.env` or local configuration?
  - [ ] Yes (Updated `.env.example` accordingly)
  - [ ] No

## 🤝 Async Reviewer Checklist
- [ ] Code adheres to clean architecture principles (Separation of Concerns between core/api/ui)
- [ ] No hardcoded secrets, API keys, or machine-specific absolute paths
- [ ] Functions and classes include proper typing and docstrings
