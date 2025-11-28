# backend/server.py

from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.api import analyze_log
from agent import run_chaos_intern_task, get_critic_advice


# -------------------------------------------------------------------
# FastAPI app + CORS
# -------------------------------------------------------------------

app = FastAPI(
    title="Agent MRI API",
    description=(
        "Agent MRI — Observability & Diagnostic Suite for AI Agents.\n\n"
        "This API takes an agent run log and returns:\n"
        "- timeline-friendly steps\n"
        "- aggregate MRI summary\n"
        "- incident report (markdown)\n"
    ),
    version="0.1.0",
)

# Allow your React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Models
# -------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    """
    Request schema for the /analyze endpoint.

    log can be:
    - dict (already parsed JSON)
    """
    log: Dict[str, Any]


class AnalyzeResponse(BaseModel):
    """
    Response schema for the /analyze endpoint.

    This matches backend.api.analyze_log output.
    """
    steps: List[Dict[str, Any]]
    summary: Dict[str, Any]
    report_markdown: str


class RunInternRequest(BaseModel):
    """
    Request for /run_intern:
    - query: user task
    - mode: chaos mode for the intern
    """
    query: str
    mode: str = "default"  # "default", "hallucination", "tool_misuse", "memory_loss"


class MRIRisk(BaseModel):
    score: int
    level: str  # "Low" | "Medium" | "High"


class InternRunResponse(BaseModel):
    """
    Matches frontend `InternRunResponse`:

    {
      final_answer_md: string;
      summary: {...};
      risk: { score: number; level: 'Low' | 'Medium' | 'High' };
      timeline_steps: Step[];
      report_markdown: string;
      critic_markdown: string;
    }
    """
    final_answer_md: str
    summary: Dict[str, Any]
    risk: MRIRisk
    timeline_steps: List[Dict[str, Any]]
    report_markdown: str
    critic_markdown: str


# -------------------------------------------------------------------
# Risk scoring (same as in Gradio app)
# -------------------------------------------------------------------

TAG_WEIGHTS: Dict[str, float] = {
    "hallucination_risk": 0.9,
    "tool_misuse": 0.8,
    "memory_drift": 0.7,
    "speculative_metrics": 0.6,
    "overconfident_no_citation": 0.9,
    "tool_error": 0.9,
    "weak_grounding": 0.6,
    "apology": 0.2,
}


def compute_overall_risk(summary: Dict[str, Any]) -> MRIRisk:
    """
    Very simple overall risk score in [0, 100].
    """
    total_steps = summary.get("total_steps", 1) or 1
    by_type = summary.get("by_failure_type", {}) or {}

    weighted = 0.0
    for tag, count in by_type.items():
        w = TAG_WEIGHTS.get(tag, 0.3)
        weighted += w * float(count)

    raw = weighted / float(total_steps)
    raw = max(0.0, min(1.0, raw))
    score = int(round(raw * 100))

    if score < 30:
        level = "Low"
    elif score < 70:
        level = "Medium"
    else:
        level = "High"

    return MRIRisk(score=score, level=level)


# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze a single agent run log with Agent MRI.
    """
    result = analyze_log(req.log)
    return result


@app.post("/run_intern", response_model=InternRunResponse)
def run_intern(req: RunInternRequest) -> Dict[str, Any]:
    """
    Full pipeline endpoint used by the frontend.

    1) Run Chaos Intern with the given chaos mode.
    2) Analyze its log with Agent MRI.
    3) Compute an overall risk score.
    4) Generate Senior Manager feedback.
    """
    # 1) Run Chaos Intern
    intern_result = run_chaos_intern_task(req.query, mode=req.mode)
    final_answer = intern_result["final_answer"]
    log = intern_result["log"]

    # 2) Analyze log
    analysis = analyze_log(log)
    summary = analysis["summary"]
    steps = analysis.get("steps", [])
    report_md = analysis["report_markdown"]

    # 3) Overall risk
    risk = compute_overall_risk(summary)

    # 4) Critic feedback
    critic_text = get_critic_advice(summary, report_md)

    return {
        "final_answer_md": final_answer,
        "summary": summary,
        "risk": risk.dict(),
        "timeline_steps": steps,
        "report_markdown": report_md,
        "critic_markdown": critic_text,
    }
