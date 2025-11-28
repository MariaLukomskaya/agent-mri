# agent/critic_agent.py

from __future__ import annotations
from typing import Dict
import json

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL, FAKE_MODE

# Configure Gemini once
if not FAKE_MODE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def _gemini_critic_call(report_markdown: str, summary: Dict) -> str:
    """
    LLM critic: senior manager reviewing the MRI report.
    Returns a skimmable markdown report with:
    - Executive summary
    - Diagnosis
    - Recommendations
    - Simple experiment
    (No ### headings, more neutral tone)
    """

    # ---------------------------
    # FAKE_MODE fallback
    # ---------------------------
    if FAKE_MODE or not GEMINI_API_KEY:
        flagged = summary.get("flagged_steps", 0)
        by_type = summary.get("by_failure_type", {})
        overall = summary.get("overall_risk_score")

        lines = []
        lines.append("**Executive summary**")
        if overall is not None:
            lines.append(f"- Overall: MRI risk score **{overall}**.")
        else:
            lines.append("- Overall: No overall score available.")

        if flagged == 0:
            lines.append("- Main failure: none detected.")
            lines.append("- Key action: continue normal operations.")
        else:
            main_tag = max(by_type.items(), key=lambda kv: kv[1])[0] if by_type else "unknown"
            lines.append(f"- Main failure: **{main_tag}**.")
            lines.append("- Key action: tighten prompts and tool selection discipline.")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("**Diagnosis – what went wrong**")
        if flagged == 0:
            lines.append("- No steps were flagged as risky in this run.")
        else:
            lines.append(f"- {flagged} steps were flagged with MRI issues:")
            for t, c in by_type.items():
                lines.append(f"  - `{t}`: {c} occurrence(s)")

        lines.append("")
        lines.append("**Recommendations – how to improve**")
        lines.append("- Require at least one grounding or tool step for factual tasks.")
        lines.append("- Penalise irrelevant or speculative tool use.")
        lines.append("- Add a self-check pass before the final answer is returned to the user.")

        lines.append("")
        lines.append("**Simple experiment**")
        lines.append("- Re-run the same query with a stricter, grounding-required prompt and "
                     "compare how many MRI tags are triggered.")

        return "\n".join(lines)

    # ---------------------------
    # REAL GEMINI CRITIC
    # ---------------------------
    model = genai.GenerativeModel(GEMINI_MODEL)

    # Ensure JSON is safely embedded
    summary_json = json.dumps(summary, indent=2)

    # Prompt: no ###, more “enterprise”
    prompt = (
        "You are a Senior AI Risk Manager reviewing an AI agent run.\n\n"
        "You will receive:\n"
        "1. A JSON summary of the agent run.\n"
        "2. A detailed incident report.\n\n"
        "Provide feedback in **markdown** following this structure exactly, "
        "using section titles as plain text or bold, not markdown headings:\n\n"
        "Executive summary\n"
        "- Overall: one-sentence evaluation of the run.\n"
        "- Main failure: the dominant MRI tag.\n"
        "- Key fix: one concrete improvement.\n\n"
        "---\n\n"
        "Diagnosis (What went wrong?)\n"
        "- 3–5 bullet points.\n\n"
        "Recommendations (How to improve?)\n"
        "- 3–6 bullets or a small table.\n\n"
        "Simple experiment/test\n"
        "- Propose one small test that could validate whether improvements work.\n\n"
        "Here is the JSON summary:\n\n"
        "```json\n"
        f"{summary_json}\n"
        "```\n\n"
        "Here is the detailed MRI incident report:\n\n"
        "```\n"
        f"{report_markdown}\n"
        "```\n"
    )

    resp = model.generate_content(
        prompt,
        generation_config={"temperature": 0.6},
    )

    return resp.text or ""


def get_critic_advice(summary: Dict, report_markdown: str) -> str:
    """Public entrypoint used by the backend / frontend"""
    return _gemini_critic_call(report_markdown, summary)
