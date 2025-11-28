# config.py
"""
Global configuration for API keys, model names, and runtime options.

IMPORTANT:
- Do NOT hardcode your API keys here.
- Put them in .env (which is ignored by git).
"""

import os
from dotenv import load_dotenv

# Load .env from project root if it exists
load_dotenv()

# ---- Gemini API ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ---- Runtime Modes ----
# If True → run Chaos Intern & Critic without calling Gemini (for testing)
FAKE_MODE = os.getenv("FAKE_MODE", "false").lower() == "true"

# ---- Project Paths ----
LOGS_DIR = os.getenv("LOGS_DIR", "data/sample_logs")

# ---- Safety hint ----
if not GEMINI_API_KEY and not FAKE_MODE:
    print("⚠️ WARNING: GEMINI_API_KEY not set. Running in FAKE_MODE.")
