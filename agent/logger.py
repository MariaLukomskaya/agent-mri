# agent/logger.py

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class MRILogger:
    """
    Minimal logger that builds an MRI log in the agreed JSON format.
    """

    def __init__(self, agent_name: str, user_query: str):
        now = datetime.now(timezone.utc).isoformat()
        self._step_id = 0
        self.log: Dict[str, Any] = {
            "schema_version": "1.0",
            "run_id": str(uuid.uuid4()),
            "agent_name": agent_name,
            "timestamp_started": now,
            "timestamp_finished": None,
            "user_query": user_query,
            "metadata": {},
            "steps": [],
        }

    def _add_step(self, **fields: Any) -> None:
        self._step_id += 1
        step = {
            "step_id": self._step_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **fields,
        }
        self.log["steps"].append(step)

    # ---- public logging helpers ----

    def log_thought(self, content: str, state: Optional[Dict[str, Any]] = None) -> None:
        self._add_step(
            type="thought",
            role="agent",
            content=content,
            state=state or {},
        )

    def log_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        call_id: Optional[str] = None,
    ) -> str:
        call_id = call_id or f"call-{self._step_id + 1}"
        self._add_step(
            type="tool_call",
            role="agent",
            tool_name=tool_name,
            call_id=call_id,
            arguments=arguments,
        )
        return call_id

    def log_tool_result(
        self,
        tool_name: str,
        call_id: str,
        result: Any,
        error: Optional[str] = None,
    ) -> None:
        self._add_step(
            type="tool_result",
            role="tool",
            tool_name=tool_name,
            call_id=call_id,
            result=result,
            error=error,
        )

    def log_memory_update(self, operation: str, key: str, value: Any = None) -> None:
        self._add_step(
            type="memory_update",
            role="agent",
            operation=operation,
            key=key,
            value=value,
        )

    def log_final_answer(
        self, content: str, state: Optional[Dict[str, Any]] = None
    ) -> None:
        self._add_step(
            type="final_answer",
            role="agent",
            content=content,
            state=state or {},
        )

    # ---- finalize & export ----

    def _finish(self) -> None:
        if self.log["timestamp_finished"] is None:
            self.log["timestamp_finished"] = datetime.now(
                timezone.utc
            ).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        self._finish()
        return self.log

    def save(self, path: str) -> None:
        self._finish()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2)




