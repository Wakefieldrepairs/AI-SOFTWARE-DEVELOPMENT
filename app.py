from dotenv import load_dotenv
load_dotenv()

"""Streamlit Developer Interface Entry Point for Testing & Interacting with the AI Agent Platform."""

import sys
from pathlib import Path

# Ensure root directory is on python path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Delegate to unified frontend application
import src.frontend.app
