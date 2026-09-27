from dotenv import load_dotenv
load_dotenv()

"""
Collaborative AI Agent Playground & GitHub Hub
Streamlit Developer Interface
"""

import os
import sys
import time
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Path Safety: Strictly scope repo_root to project root
# Path(__file__).resolve().parent.parent.parent -> src/frontend/app.py -> src/frontend -> src -> root
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import httpx
import streamlit as st
from src.core.security import (
    ensure_gitignore_rules,
    launch_backend_process,
    scan_and_sanitize_workspace,
)
from src.core.config import get_settings
from src.core.llm import LLMClient, Message

# Page configuration
st.set_page_config(
    page_title="Collaborative AI Agent Playground & GitHub Hub",
    page_icon="🐙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS Injection for Dark UI Palette
CUSTOM_CSS = """
<style>
/* Base Canvas & Backgrounds */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: #0e1117 !important;
    color: #e6edf3 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background-color: #161a23 !important;
    border-right: 1px solid #2b313e !important;
}

/* Text colors in sidebar */
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
    color: #e6edf3 !important;
}

/* Primary Accent & Sliders */
.stSlider > div > div > div > div {
    background-color: #ff4b4b !important;
}
.stSlider [data-baseweb="slider"] div {
    color: #ff4b4b !important;
}

/* Buttons */
button[kind="primary"], .stButton > button {
    border-radius: 8px !important;
    transition: all 0.2s ease-in-out;
}
.stButton > button:hover {
    border-color: #ff4b4b !important;
    color: #ff4b4b !important;
}

/* Status & Alert Banners */
.banner-error {
    background-color: #4a151b !important;
    color: #f87171 !important;
    border: 1px solid #991b1b !important;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 14px;
    font-size: 0.95rem;
    font-weight: 500;
}

.banner-success {
    background-color: #0d3820 !important;
    color: #4ade80 !important;
    border: 1px solid #166534 !important;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 14px;
    font-size: 0.95rem;
    font-weight: 500;
}

.banner-info {
    background-color: #1e293b !important;
    color: #93c5fd !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 14px;
    font-size: 0.95rem;
}

/* Chat input bar */
[data-testid="stChatInput"] {
    background-color: #161a23 !important;
    border-radius: 28px !important;
    border: 1px solid #2b313e !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
    padding: 4px 8px !important;
}

[data-testid="stChatInput"] textarea {
    color: #e6edf3 !important;
    background-color: transparent !important;
}

[data-testid="stChatInput"] button {
    border-radius: 50% !important;
    background-color: #ff4b4b !important;
    color: #ffffff !important;
    border: none !important;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #2b313e;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border-radius: 6px 6px 0 0;
    color: #94a3b8;
    padding: 8px 18px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    color: #ff4b4b !important;
    border-bottom: 2px solid #ff4b4b !important;
}

/* Code blocks */
code, pre {
    background-color: #161a23 !important;
    color: #38bdf8 !important;
    border: 1px solid #2b313e !important;
    border-radius: 6px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def run_git_command(args: List[str], cwd: Path = None) -> Tuple[bool, str]:
    """
    Synchronous Git execution helper using subprocess.run.
    Prevents prompt freezes using environment flags and creationflags on Windows.
    """
    target_cwd = cwd if cwd is not None else repo_root
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "echo"

    kwargs: Dict[str, Any] = {
        "cwd": str(target_cwd),
        "capture_output": True,
        "text": True,
        "env": env,
    }

    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    try:
        res = subprocess.run(["git"] + args, **kwargs)
        if res.returncode == 0:
            return True, res.stdout.strip()
        else:
            err_output = res.stderr.strip() if res.stderr.strip() else res.stdout.strip()
            return False, err_output
    except Exception as e:
        return False, f"Git execution error: {e!s}"


# Configuration from environment
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
DEFAULT_API_URL = os.getenv("API_URL", f"http://{API_HOST}:{API_PORT}/api/v1")

# ========================================== #
# SIDEBAR: Settings & Backend Health         #
# ========================================== #
with st.sidebar:
    st.markdown("### ⚙️ Connectivity & Settings")
    api_url = st.text_input("API Endpoint URL", value=DEFAULT_API_URL)

    st.markdown("---")
    st.markdown("### 🎛️ Model Hyperparameters")
    custom_model = st.text_input("Model Name Override", value="", placeholder="e.g. gpt-4o, claude-3-5-sonnet, llama3")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.70, step=0.01)
    max_tokens = st.slider("Max Tokens", min_value=128, max_value=8192, value=2048, step=128)
    enable_streaming = st.checkbox("Stream Output", value=True)

    st.markdown("---")
    st.markdown("### 🔌 Backend Health Check & Launcher")

    backend_online = False
    backend_msg = ""
    try:
        resp = httpx.get(f"{api_url}/health", timeout=1.5)
        if resp.status_code == 200:
            backend_online = True
            backend_msg = f"● Connected: FastAPI running on port {API_PORT}"
        else:
            backend_msg = f"[Warning] Backend returned status code {resp.status_code}"
    except Exception as e:
        backend_online = False
        backend_msg = f"[Disconnected] Cannot reach backend at {api_url}"

    if backend_online:
        st.markdown(f'<div class="banner-success">{backend_msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="banner-error">{backend_msg}</div>', unsafe_allow_html=True)

    col_ping, col_launch = st.columns(2)
    with col_ping:
        if st.button("🔄 Ping / Docs", use_container_width=True):
            st.rerun()
    with col_launch:
        if st.button("🚀 Launch Backend", use_container_width=True):
            try:
                port_int = int(API_PORT) if str(API_PORT).isdigit() else 8000
            except Exception:
                port_int = 8000
            success, msg = launch_backend_process(root_dir=repo_root, port=port_int)
            if success:
                st.success(f"✅ Backend launched! {msg}")
                time.sleep(1.0)
                st.rerun()
            else:
                st.error(f"❌ Launch failed: {msg}")


# ========================================== #
# MAIN TABS                                  #
# ========================================== #
tab_playground, tab_github, tab_guide = st.tabs([
    "🤖 AI Agent Playground",
    "🐙 GitHub Collaboration Hub",
    "📘 Operations Guide",
])

# ------------------------------------------ #
# TAB 1: 🤖 AI Agent Playground             #
# ------------------------------------------ #
with tab_playground:
    st.markdown("## 🤖 Collaborative AI Agent Playground")
    st.caption("Interact with your LLM agents via FastAPI backend, or use direct LLM fallback.")

    # Session State Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI Agent assistant. How can I help with your project today?"}
        ]

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if user_input := st.chat_input("Type your prompt or instructions..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        payload = {
            "messages": st.session_state.messages,
            "model": custom_model.strip() if custom_model.strip() else None,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": enable_streaming,
        }

        with st.chat_message("assistant"):
            assistant_response = ""
            placeholder = st.empty()

            used_backend = False
            if backend_online:
                try:
                    if enable_streaming:
                        with httpx.stream(
                            "POST",
                            f"{api_url}/generate/stream",
                            json=payload,
                            timeout=60.0,
                        ) as r:
                            if r.status_code == 200:
                                used_backend = True
                                for chunk in r.iter_text():
                                    assistant_response += chunk
                                    placeholder.markdown(assistant_response + "▌")
                                placeholder.markdown(assistant_response)
                                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                            else:
                                placeholder.warning(f"Backend returned HTTP {r.status_code}. Switching to direct LLM fallback...")
                    else:
                        with st.spinner("Generating response via FastAPI backend..."):
                            resp = httpx.post(f"{api_url}/generate", json=payload, timeout=60.0)
                            if resp.status_code == 200:
                                used_backend = True
                                data = resp.json()
                                assistant_response = data.get("content", "")
                                placeholder.markdown(assistant_response)
                                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                                if data.get("fallback_used"):
                                    st.caption(f"ℹ️ Fallback model `{data.get('model_used')}` was used.")
                            else:
                                placeholder.warning(f"Backend returned HTTP {resp.status_code}. Switching to direct LLM fallback...")
                except Exception as ex:
                    placeholder.warning(f"Backend communication error ({ex!s}). Switching to direct LLM fallback...")

            # Direct LLM Client Fallback
            if not used_backend:
                try:
                    settings = get_settings()
                    llm_client = LLMClient(
                        base_url=settings.llm_base_url,
                        api_key=settings.llm_api_key.get_secret_value(),
                        default_model=settings.default_model,
                        fallback_model=settings.fallback_model,
                        timeout_seconds=settings.request_timeout_seconds,
                    )
                    msg_objs = [Message(role=m["role"], content=m["content"]) for m in st.session_state.messages]

                    if enable_streaming:
                        async def run_direct_stream():
                            res_acc = ""
                            async for token in llm_client.stream_completion(
                                messages=msg_objs,
                                model=custom_model if custom_model.strip() else None,
                                temperature=temperature,
                                max_tokens=max_tokens,
                            ):
                                res_acc += token
                                placeholder.markdown(res_acc + "▌")
                            placeholder.markdown(res_acc)
                            return res_acc

                        assistant_response = asyncio.run(run_direct_stream())
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    else:
                        with st.spinner("Generating response via Direct LLM Client..."):
                            res = asyncio.run(llm_client.generate_completion(
                                messages=msg_objs,
                                model=custom_model if custom_model.strip() else None,
                                temperature=temperature,
                                max_tokens=max_tokens,
                            ))
                            assistant_response = res.content
                            placeholder.markdown(assistant_response)
                            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                            if res.fallback_used:
                                st.caption(f"ℹ️ Fallback model `{res.model_used}` was utilized.")
                except Exception as direct_err:
                    placeholder.error(f"Direct LLM Fallback Error: {direct_err!s}")


# ------------------------------------------ #
# TAB 2: 🐙 GitHub Collaboration Hub       #
# ------------------------------------------ #
with tab_github:
    st.markdown("## 🐙 GitHub Collaboration Hub")
    st.markdown("Collaborate seamlessly on your repository without terminal commands.")

    st.markdown("### 🛠️ One-Click Repository Automation")

    col_pull, col_sec, col_push = st.columns(3)

    # Action 1: Sync / Pull Remote
    with col_pull:
        st.markdown("#### 1. Sync Remote Work")
        if st.button("⬇️ Pull Latest Work", use_container_width=True):
            with st.spinner("Pulling latest commits from origin/main..."):
                success, output = run_git_command(["pull", "origin", "main"], cwd=repo_root)
            if success:
                st.success("✅ Successfully pulled latest changes!")
                st.code(output, language="bash")
            else:
                st.error("❌ Git Pull Failed")
                st.code(output, language="bash")

    # Action 2: Sanitize Secrets & Update .gitignore
    with col_sec:
        st.markdown("#### 2. Protect Credentials")
        if st.button("🛡️ Sanitize Secrets & Update .gitignore", use_container_width=True):
            with st.spinner("Scanning workspace for API secrets and validating .gitignore..."):
                report = scan_and_sanitize_workspace(root_dir=repo_root)

            st.success("✅ Workspace Security Audit Complete!")
            st.markdown(f"- **Hardcoded Keys Secured:** `{report['keys_secured']}`")
            if report["unique_keys"]:
                st.markdown(f"- **Variables Extracted:** `{', '.join(report['unique_keys'])}`")
            st.markdown(f"- **Files Modified:** `{len(report['files_modified'])}`")
            if report["files_modified"]:
                with st.expander("View Modified Files"):
                    for f in report["files_modified"]:
                        st.write(f"• `{f}`")
            if report["added_to_env"]:
                st.info(f"Updated `.env` with: `{', '.join(report['added_to_env'])}`")
            if report["added_to_example"]:
                st.info(f"Updated `.env.example` with: `{', '.join(report['added_to_example'])}`")
            if report["added_gitignore"]:
                st.warning(f"Protected rules added to `.gitignore`: `{', '.join(report['added_gitignore'])}`")
            else:
                st.caption("✓ `.gitignore` already contains all security rules.")

    # Action 3: Commit & Push to GitHub
    with col_push:
        st.markdown("#### 3. Publish to GitHub")
        commit_msg = st.text_input("Commit Message", value="feat: update AI agent playground & collaboration tools")
        if st.button("⬆️ Commit & Push to GitHub", use_container_width=True):
            if not commit_msg.strip():
                st.error("Please provide a commit message before pushing.")
            else:
                with st.spinner("Sanitizing, staging non-sensitive files, and pushing..."):
                    ensure_gitignore_rules(repo_root / ".gitignore")

                    add_ok, add_out = run_git_command(["add", "."], cwd=repo_root)
                    run_git_command(["reset", ".env"], cwd=repo_root)
                    commit_ok, commit_out = run_git_command(["commit", "-m", commit_msg], cwd=repo_root)
                    push_ok, push_out = run_git_command(["push", "origin", "main"], cwd=repo_root)

                if push_ok:
                    st.success("🚀 Successfully pushed changes to `origin/main`!")
                    st.code(push_out, language="bash")
                else:
                    if "nothing to commit" in commit_out.lower() or "nothing to commit" in push_out.lower():
                        st.info("ℹ️ No new changes to commit or push.")
                    else:
                        st.error("❌ Git Push encountered an issue:")
                        st.code(f"Commit output:\n{commit_out}\n\nPush output:\n{push_out}", language="bash")

    st.markdown("---")
    st.markdown("### 📊 Remote & Local Repository Status")

    col_log, col_status = st.columns(2)

    with col_log:
        st.markdown("#### 📜 Recent Commit History (`git log -n 5`)")
        if st.button("View Recent Commits", use_container_width=True):
            log_ok, log_out = run_git_command(["log", "-n", "5", "--oneline"], cwd=repo_root)
            if log_ok:
                st.code(log_out, language="bash")
            else:
                st.error(log_out)

    with col_status:
        st.markdown("#### 📝 Pending Modified & Untracked Files (`git status`)")
        if st.button("Run Git Status", use_container_width=True):
            status_ok, status_out = run_git_command(["status"], cwd=repo_root)
            if status_ok:
                st.code(status_out, language="bash")
            else:
                st.error(status_out)


# ------------------------------------------ #
# TAB 3: 📘 Operations & Architecture Guide  #
# ------------------------------------------ #
with tab_guide:
    st.markdown("## 📘 Operations & Architecture Workflow Guide")
    st.caption("Operational manual for seamless collaboration and deployment.")

    st.markdown("""
    ### 1. 🏗️ Platform Architecture Topology

    ```text
    ┌────────────────────────────────────────────────────────┐
    │               Streamlit UI (Frontend Port 8501)         │
    │  - AI Agent Chat Playground with streaming output      │
    │  - One-Click Git Pull, Sanitize, and Push Automation    │
    │  - Backend Process Manager & Health Monitor            │
    └───────────────────────────┬────────────────────────────┘
                                │ HTTP / SSE Streams (Port 8000)
                                ▼
    ┌────────────────────────────────────────────────────────┐
    │                 FastAPI Backend Service                 │
    │  - /api/v1/health (Health check & status)              │
    │  - /api/v1/generate (Synchronous LLM completion)       │
    │  - /api/v1/generate/stream (Token streaming SSE)       │
    │  - Multi-provider fallback & error resilience          │
    └───────────────────────────┬────────────────────────────┘
                                │ OpenAI Protocol / LiteLLM
                                ▼
    ┌────────────────────────────────────────────────────────┐
    │                   LLM Inference Engine                 │
    │  - Local: Ollama / vLLM (http://localhost:11434/v1)    │
    │  - Remote: OpenAI (GPT-4o), Anthropic Claude, Gemini   │
    └────────────────────────────────────────────────────────┘
    ```

    ---

    ### 2. 🛡️ Secret Isolation & Repository Safety
    To protect credentials from being exposed on GitHub:
    - **Zero Hardcoded Secrets**: All keys (`sk-...`, `sk-ant-...`, `AIza...`) are strictly loaded via `os.getenv()`.
    - **Sanitize Utility**: The built-in scanner detects exposed keys in `.py` files, moves them to `.env`, creates a sanitized `.env.example`, and appends `.env` to `.gitignore`.
    - **Protected Push Pipeline**: The one-click Git push utility automatically verifies `.gitignore` rules and un-stages `.env` before any commit is performed.

    ---

    ### 3. 🔌 Resolving Port 8000 Connection Errors
    If you see backend connection errors:
    1. **One-Click Launch**: Click **🚀 Launch Backend** in the sidebar. This spawns the backend server in a dedicated process.
    2. **Manual Launch (Terminal alternative)**:
       ```bash
       # Windows
       .venv\\Scripts\\activate
       uvicorn src.api.main:app --reload --port 8000

       # Linux / macOS
       source .venv/bin/activate
       uvicorn src.api.main:app --reload --port 8000
       ```
    3. **Verify Health**: Click **🔄 Ping / Docs** in the sidebar to confirm connectivity.
    """)
