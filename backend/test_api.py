# backend/test_api.py

import os
import sys
import json

import requests  # pip install requests if missing


# --- Make sure project root is on sys.path ---
# /Users/.../agent-mri/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Now this should work:
from agent import run_chaos_intern_task


def main():
    # 1) Generate a real agent log using Chaos Intern
    result = run_chaos_intern_task(
        "Summarize the top 3 AI security risks.",
        mode="default",
    )
    log = result["log"]

    # 2) Call the FastAPI endpoint
    resp = requests.post(
        "http://127.0.0.1:8000/analyze",
        json={"log": log},
    )

    print("Status:", resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print("Raw response:", resp.text)


if __name__ == "__main__":
    main()
