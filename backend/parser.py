# backend/parser.py

import json
from typing import Any, Dict, List

from .schema import Run, Step, StepAnalysis


class LogParseError(Exception):
    pass


def _parse_step(raw: Dict[str, Any]) -> Step:
    required = ["step_id", "type", "role", "timestamp"]
    for key in required:
        if key not in raw:
            raise LogParseError(f"Missing required step field: {key}")

    return Step(
        step_id=int(raw["step_id"]),
        type=str(raw["type"]),
        role=str(raw["role"]),
        timestamp=str(raw["timestamp"]),
        content=raw.get("content"),
        state=raw.get("state"),
        tool_name=raw.get("tool_name"),
        call_id=raw.get("call_id"),
        arguments=raw.get("arguments"),
        result=raw.get("result"),
        error=raw.get("error"),
        operation=raw.get("operation"),
        key=raw.get("key"),
        value=raw.get("value"),
        analysis=StepAnalysis(),  # empty; filled later
    )


def parse_log_dict(data: Dict[str, Any]) -> Run:
    try:
        steps_raw: List[Dict[str, Any]] = data["steps"]
    except KeyError:
        raise LogParseError("Log missing 'steps' field")

    steps = [_parse_step(s) for s in steps_raw]

    required_top = [
        "schema_version",
        "run_id",
        "agent_name",
        "timestamp_started",
        "user_query",
    ]
    for key in required_top:
        if key not in data:
            raise LogParseError(f"Missing required run field: {key}")

    return Run(
        schema_version=str(data["schema_version"]),
        run_id=str(data["run_id"]),
        agent_name=str(data["agent_name"]),
        timestamp_started=str(data["timestamp_started"]),
        timestamp_finished=data.get("timestamp_finished"),
        user_query=str(data["user_query"]),
        metadata=data.get("metadata", {}),
        steps=steps,
    )


def parse_log_file(path: str) -> Run:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return parse_log_dict(data)
