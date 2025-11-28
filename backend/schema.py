# backend/schema.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StepAnalysis:
    risk_score: float = 0.0
    failure_tags: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class Step:
    step_id: int
    type: str
    role: str
    timestamp: str
    content: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    # tool fields
    tool_name: Optional[str] = None
    call_id: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    result: Any = None
    error: Optional[str] = None
    # memory fields
    operation: Optional[str] = None
    key: Optional[str] = None
    value: Any = None
    # analysis
    analysis: StepAnalysis = field(default_factory=StepAnalysis)


@dataclass
class Run:
    schema_version: str
    run_id: str
    agent_name: str
    timestamp_started: str
    timestamp_finished: Optional[str]
    user_query: str
    metadata: Dict[str, Any]
    steps: List[Step]
