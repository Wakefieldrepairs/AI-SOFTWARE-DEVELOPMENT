"""DevOps & Security Utilities for secret scanning, sanitization, and environment protection."""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SECRET_PATTERNS = [
    (
        "OPENAI_API_KEY",
        re.compile(r"([\"\'])(sk-(?!ant-)[a-zA-Z0-9_-]{20,})([\"\'])"),
    ),
    (
        "ANTHROPIC_API_KEY",
        re.compile(r"([\"\'])(sk-ant-[a-zA-Z0-9_-]{20,})([\"\'])"),
    ),
    (
        "GEMINI_API_KEY",
        re.compile(r"([\"\'])(AIza[0-9A-Za-z-_]{30,})([\"\'])"),
    ),
]

CRITICAL_GITIGNORE_RULES = [
    ".env",
    "*.env",
    ".venv/",
    "__pycache__/",
    "models/",
    "*.safetensors",
    "*.bin",
]


def read_env_file(env_path: Path) -> Dict[str, str]:
    """Read key-value pairs from .env file."""
    env_vars: Dict[str, str] = {}
    if not env_path.exists():
        return env_vars
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip().strip("'").strip('"')
    return env_vars


def write_env_file(env_path: Path, new_vars: Dict[str, str]) -> List[str]:
    """Append new environment variables to .env if not present."""
    existing = read_env_file(env_path)
    added = []
    lines_to_append = []
    for k, v in new_vars.items():
        if k not in existing:
            lines_to_append.append(f'{k}="{v}"\n')
            added.append(k)
    if lines_to_append:
        with open(env_path, "a", encoding="utf-8") as f:
            if env_path.exists() and env_path.stat().st_size > 0:
                if not env_path.read_text(encoding="utf-8").endswith("\n"):
                    f.write("\n")
            f.write("# Automatically secured credentials\n")
            for line in lines_to_append:
                f.write(line)
    return added


def update_env_example(example_path: Path, new_vars: Dict[str, str]) -> List[str]:
    """Ensure .env.example contains dummy entries for keys."""
    existing = read_env_file(example_path)
    added = []
    lines_to_append = []
    for k in new_vars:
        if k not in existing:
            lines_to_append.append(f'{k}="your_key_here"\n')
            added.append(k)
    if lines_to_append:
        with open(example_path, "a", encoding="utf-8") as f:
            if example_path.exists() and example_path.stat().st_size > 0:
                if not example_path.read_text(encoding="utf-8").endswith("\n"):
                    f.write("\n")
            f.write("# Placeholder credentials\n")
            for line in lines_to_append:
                f.write(line)
    return added


def ensure_gitignore_rules(gitignore_path: Path) -> List[str]:
    """Verify and append missing critical rules to .gitignore."""
    existing_lines = []
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            existing_lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    missing_rules = [rule for rule in CRITICAL_GITIGNORE_RULES if rule not in existing_lines]
    if missing_rules:
        with open(gitignore_path, "a", encoding="utf-8") as f:
            if gitignore_path.exists() and gitignore_path.stat().st_size > 0:
                if not gitignore_path.read_text(encoding="utf-8").endswith("\n"):
                    f.write("\n")
            f.write("# Critical Security & DevOps Rules\n")
            for rule in missing_rules:
                f.write(f"{rule}\n")
    return missing_rules


def scan_and_sanitize_workspace(root_dir: str | Path = ".") -> Dict[str, Any]:
    """
    Recursively scans the project workspace for .py files,
    detects hardcoded API keys, replaces them with os.getenv, and ensures imports.
    """
    root = Path(root_dir).resolve()
    skip_dirs = {".venv", ".git", "__pycache__", "venv", "env", ".tox", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
    modified_files: List[str] = []
    found_keys: Dict[str, str] = {}
    total_keys_found = 0
    for current_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
        for file in files:
            if not file.endswith(".py"):
                continue
            file_path = Path(current_dir) / file
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue
            file_modified = False
            for var_name, pattern in SECRET_PATTERNS:
                matches = pattern.findall(content)
                if matches:
                    for match in matches:
                        quote1, secret_val, quote2 = match
                        if "your_key" in secret_val or "mock" in secret_val or len(secret_val) < 15:
                            continue
                        found_keys[var_name] = secret_val
                        total_keys_found += 1
                        target_str = f"{quote1}{secret_val}{quote2}"
                        replacement_str = f'os.getenv("{var_name}", "")'
                        content = content.replace(target_str, replacement_str)
                        file_modified = True
            if file_modified:
                import_headers = []
                if "import os" not in content:
                    import_headers.append("import os")
                if "load_dotenv" not in content:
                    import_headers.append("from dotenv import load_dotenv\nload_dotenv()")
                if import_headers:
                    header_str = "\n".join(import_headers) + "\n\n"
                    content = header_str + content
                file_path.write_text(content, encoding="utf-8")
                modified_files.append(str(file_path.relative_to(root)))
    env_path = root / ".env"
    example_path = root / ".env.example"
    gitignore_path = root / ".gitignore"
    added_to_env = write_env_file(env_path, found_keys)
    added_to_example = update_env_example(example_path, found_keys)
    added_gitignore = ensure_gitignore_rules(gitignore_path)
    return {
        "keys_secured": total_keys_found,
        "unique_keys": list(found_keys.keys()),
        "files_modified": modified_files,
        "added_to_env": added_to_env,
        "added_to_example": added_to_example,
        "added_gitignore": added_gitignore,
    }


def find_repo_root(start_dir: str | Path | None = None) -> Path:
    """
    Searches upwards from start_dir, current working directory, and script directory
    for a folder containing '.git' to locate the actual repository root.
    """
    search_starts = []
    if start_dir is not None:
        search_starts.append(Path(start_dir).resolve())
    try:
        search_starts.append(Path(__file__).resolve().parent)
    except NameError:
        pass
    search_starts.append(Path.cwd().resolve())

    for candidate in search_starts:
        curr = candidate
        while True:
            if (curr / ".git").exists():
                return curr
            if curr.parent == curr:
                break
            curr = curr.parent

    if start_dir is not None:
        return Path(start_dir).resolve()
    return Path.cwd().resolve()


def launch_backend_process(root_dir: str | Path = ".", port: int = 8000) -> Tuple[bool, str]:
    """
    Launches the FastAPI backend server on specified port in a detached background process.
    """
    root = Path(root_dir).resolve()
    is_windows = sys.platform.startswith("win")
    try:
        if is_windows:
            venv_activate = root / ".venv" / "Scripts" / "activate.bat"
            if venv_activate.exists():
                cmd = f'cmd /k "call "{venv_activate}" && python -m uvicorn src.api.main:app --reload --port {port}"'
            else:
                cmd = f'cmd /k "python -m uvicorn src.api.main:app --reload --port {port}"'
            subprocess.Popen(cmd, cwd=str(root), creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
            return True, f"FastAPI server launched in new console window on port {port}."
        else:
            cmd = [sys.executable, "-m", "uvicorn", "src.api.main:app", "--reload", "--port", str(port)]
            subprocess.Popen(
                cmd,
                cwd=str(root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True, f"FastAPI server launched in background process on port {port}."
    except Exception as e:
        return False, f"Failed to launch backend: {e!s}"
