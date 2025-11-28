# backend/api.py

from typing import Any, Dict, Union, List

from .parser import parse_log_dict
from .analysis.risk_scorer import score_risks
from .analysis.report import generate_report


def _to_timeline_step(s) -> Dict[str, Any]:
    """
    Convert a Step dataclass into a JSON-friendly dict that works
    both for:
      - raw debugging
      - pretty timeline rendering in the frontend

    We expose:
      step_id, type, label, short, text, tags
    plus the original low-level fields under the same dict.
    """
    failure_tags: List[str] = list(s.analysis.failure_tags or [])
    notes = s.analysis.notes or ""

    # Human-friendly label for the step
    if s.type == "final_answer":
        label = "Final answer"
    elif s.type == "tool_call":
        label = s.tool_name or "Tool call"
    elif s.type in ("memory_read", "memory_write"):
        label = "Memory operation"
    else:
        label = s.type.capitalize()

    # Short description: we reuse notes if present
    short = notes if isinstance(notes, str) and notes.strip() else ""

    # Main text body for the timeline
    text = s.content or ""

    return {
        # --- high-level timeline fields (for UI) ---
        "step_id": s.step_id,
        "type": s.type,
        "label": label,
        "short": short,
        "text": text,
        "tags": failure_tags,

        # --- raw log fields (for debugging / future UIs) ---
        "role": s.role,
        "timestamp": s.timestamp,
        "content": s.content,
        "tool_name": s.tool_name,
        "call_id": s.call_id,
        "arguments": s.arguments,
        "result": s.result,
        "error": s.error,
        "operation": s.operation,
        "key": s.key,
        "value": s.value,
        "analysis": {
            "risk_score": s.analysis.risk_score,
            "failure_tags": failure_tags,
            "notes": notes,
        },
    }


def analyze_log(log_data: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    """
    Main MRI API.

    log_data can be:
    - a dict already loaded from JSON
    - a JSON string

    Returns:
        {
          "steps": [  # timeline-friendly steps
            {
              "step_id": ...,
              "type": "thought" | "tool_call" | "final_answer" | ...,
              "label": "...",
              "short": "...",
              "text": "...",
              "tags": ["hallucination_risk", ...],
              ... raw fields ...
            },
            ...
          ],
          "summary": {...},          # aggregate stats
          "report_markdown": "..."   # full incident report
        }
    """
    if isinstance(log_data, str):
        import json
        log_data = json.loads(log_data)

    run = parse_log_dict(log_data)

    # score_risks mutates each Step.analysis and returns:
    #   steps: List[Step]
    #   summary: Dict[str, Any]
    steps, summary = score_risks(run)
    report_md = generate_report(run, steps, summary)

    # Convert dataclasses to plain dicts for the frontend
    steps_serialized = [_to_timeline_step(s) for s in steps]

    return {
        "steps": steps_serialized,
        "summary": summary,
        "report_markdown": report_md,
    }
