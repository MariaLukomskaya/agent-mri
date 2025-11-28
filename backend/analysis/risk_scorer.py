# backend/analysis/risk_scorer.py

"""
Simple but opinionated risk scoring for Agent MRI.

Per-step rules
--------------
- tool_error
    step.type == "tool_result" and step.error is not None

- apology
    content contains "sorry"

- weak_grounding
    thought step with "i think" (speculative reasoning)

- tool_misuse
    tool_call where the tool's declared domain does not match the task domain

- memory_drift
    thought / final answer that drifts far away from the original topic

Final-answer rules
------------------
- hallucination_risk
    long, highly confident answer with minimal tool usage

- overconfident_no_citation
    strong certainty language but no sign of citations / sources

- speculative_metrics
    uses percentages but we didn't see much tool evidence

These tags flag *risk*, not absolute truth.
"""

from __future__ import annotations

from typing import Dict, List
import re

from ..schema import Run, Step


# ---------- helpers for whole-run stats ----------


def _compute_run_stats(run: Run) -> Dict[str, int]:
    tool_calls = sum(1 for s in run.steps if s.type == "tool_call")
    tool_results = sum(1 for s in run.steps if s.type == "tool_result")
    thoughts = sum(1 for s in run.steps if s.type == "thought")
    final_answers = [s for s in run.steps if s.type == "final_answer"]

    return {
        "tool_call_count": tool_calls,
        "tool_result_count": tool_results,
        "thought_count": thoughts,
        "has_final_answer": int(len(final_answers) > 0),
    }


# ---------- basic per-step rules ----------


def _flag_basic_risks(step: Step) -> None:
    """
    Very simple v0 rules:
    - if 'sorry' in content -> possible error/loop
    - if 'I think' + thought -> weak grounding
    - if type == tool_result and error != None -> high risk
    """
    tags: List[str] = list(step.analysis.failure_tags or [])
    score = float(step.analysis.risk_score or 0.0)
    notes_parts: List[str] = [step.analysis.notes] if step.analysis.notes else []

    content = (step.content or "").lower()

    # Tool error
    if step.type == "tool_result" and step.error:
        if "tool_error" not in tags:
            tags.append("tool_error")
        score = max(score, 0.9)
        notes_parts.append(f"Tool error: {step.error}")

    # Apology (often signals a failure)
    if "sorry" in content:
        if "apology" not in tags:
            tags.append("apology")
        score = max(score, 0.4)
        notes_parts.append("Agent apologized; may indicate previous failure.")

    # Weak grounding ("I think..." with no explicit evidence)
    if step.type == "thought" and "i think" in content and step.role == "agent":
        if "weak_grounding" not in tags:
            tags.append("weak_grounding")
        score = max(score, 0.3)
        notes_parts.append("Speculative reasoning without explicit evidence.")

    step.analysis.risk_score = score
    step.analysis.failure_tags = tags
    step.analysis.notes = " ".join(p for p in notes_parts if p)


# ---------- tool misuse rules (domain mismatch) ----------


def _flag_tool_misuse(step: Step, run: Run) -> None:
    """
    Detect tool calls that are clearly off-domain vs the task.

    We rely on explicit metadata instead of keyword lists:

    - run.metadata["task_domain"]  -> what the user asked for
      e.g. "ai_security", "finance", "governance"

    - step.arguments["tool_domain"] -> what the tool is meant for
      e.g. "ai_security", "office_ops", "coffee_telemetry"

    If both are present and task_domain != tool_domain,
    we tag this as 'tool_misuse'.
    """
    if step.type != "tool_call":
        # only analyze actual tool calls here
        return

    tags: List[str] = list(step.analysis.failure_tags or [])
    score = float(step.analysis.risk_score or 0.0)
    notes_parts: List[str] = [step.analysis.notes] if step.analysis.notes else []

    # Task domain from run metadata
    task_domain = None
    if isinstance(run.metadata, dict):
        task_domain = run.metadata.get("task_domain")

    # Tool domain from arguments
    tool_domain = None
    if isinstance(step.arguments, dict):
        tool_domain = step.arguments.get("tool_domain")

    # If we don't have both, we can't decide — leave as is
    if not task_domain or not tool_domain:
        step.analysis.risk_score = score
        step.analysis.failure_tags = tags
        step.analysis.notes = " ".join(p for p in notes_parts if p)
        return

    # Domain mismatch => tool_misuse
    if task_domain != tool_domain:
        if "tool_misuse" not in tags:
            tags.append("tool_misuse")
        score = max(score, 0.6)
        notes_parts.append(
            f"Tool domain '{tool_domain}' does not match task domain '{task_domain}' "
            "(possible tool misuse / irrelevant tool for this query)."
        )

    step.analysis.risk_score = score
    step.analysis.failure_tags = tags
    step.analysis.notes = " ".join(p for p in notes_parts if p)


# ---------- memory / topic drift rules ----------

_OFF_TOPIC_KEYWORDS = [
    # movies / pets / random
    "dog",
    "dogs",
    "romantic comedies",
    "rom-com",
    "casserole",
    "recipe",
    "movie snack",
    # gardening / food
    "garden",
    "basil",
    "tomatoes",
    "weeds",
    "hops",
    "beer",
    "fermentation",
    "pineapple",
    "oat milk",
    "smoothie",
    "blender",
    "spatula",
    # office party / hydration chaos
    "water cooler",
    "hot dog",
    "eating contest",
    # spicy security nonsense
    "scoville",
    "hot sauce",
    "carolina reaper",
    "ghost pepper",
]


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())


def _flag_memory_drift(step: Step, run: Run) -> None:
    """
    Flag steps that have drifted far from the original query topic.

    Heuristic:
    - if we see obviously off-topic words (blender, casserole, dog movies, peppers, etc.)
      in a thought or final answer → tag memory_drift,
      *especially* when the query is serious/technical (like AI security).
    """
    if step.type not in ("thought", "final_answer"):
        return
    if not step.content:
        return

    tags: List[str] = list(step.analysis.failure_tags or [])
    score = float(step.analysis.risk_score or 0.0)
    notes_parts: List[str] = [step.analysis.notes] if step.analysis.notes else []

    user_q = (run.user_query or "").lower()
    text = step.content.lower()

    # is this a "serious" query?
    serious_keywords = ["security", "risk", "ai", "compliance", "policy", "finance"]
    is_serious_query = any(k in user_q for k in serious_keywords)

    off_topic = any(k in text for k in _OFF_TOPIC_KEYWORDS)

    # If it's a serious query and we see clearly off-topic domains → memory drift.
    if is_serious_query and off_topic:
        if "memory_drift" not in tags:
            tags.append("memory_drift")
        score = max(score, 0.6)
        notes_parts.append(
            "Content includes obviously off-topic concepts for this query "
            "(possible memory / context drift)."
        )

    step.analysis.risk_score = score
    step.analysis.failure_tags = tags
    step.analysis.notes = " ".join(p for p in notes_parts if p)


# ---------- final-answer focused rules ----------

_STRONG_CONFIDENCE_PHRASES = [
    "there is zero tolerance",
    "zero tolerance",
    "we have validated",
    "we are certain",
    "this proves",
    "guaranteed",
    "no doubt",
    "undeniable",
    "without question",
    "mandatory",
    "critical fact",
    "this is not theoretical",
    "must be immediately addressed",
    "existential",
    "catastrophic",
    "collapse",
    "impending",
    "operational collapse",
    "algorithmic catastrophe",
]


def _detect_percentages(text: str) -> List[str]:
    # Match "18.7%" or "20 %" etc.
    pattern = r"\b\d+(\.\d+)?\s*%"
    return re.findall(pattern, text)


def _has_confident_language(text_lower: str) -> bool:
    return any(phrase in text_lower for phrase in _STRONG_CONFIDENCE_PHRASES)


def _has_citation_like_signals(text_lower: str) -> bool:
    # very rough heuristic for "this might be citing something"
    return any(
        token in text_lower
        for token in [
            "according to",
            "source:",
            "paper",
            "study",
            "dataset",
            "report",
            "as reported by",
            "doi.org",
            "arxiv.org",
            "https://",
            "[1]",
            "(202",
        ]
    )


def _analyze_final_answer(step: Step, run_stats: Dict[str, int]) -> None:
    """
    Add hallucination-style tags based on the final answer content
    and simple run-level stats (how many tools were used).
    """
    if not step.content:
        return

    tags: List[str] = list(step.analysis.failure_tags or [])
    score = float(step.analysis.risk_score or 0.0)
    notes_parts: List[str] = [step.analysis.notes] if step.analysis.notes else []

    text = step.content
    text_lower = text.lower()
    length = len(text)

    percents = _detect_percentages(text)
    has_conf = _has_confident_language(text_lower)
    has_citation = _has_citation_like_signals(text_lower)

    tool_results = run_stats.get("tool_result_count", 0)

    # 1) Speculative metrics: lots of precise numbers but little tool grounding
    if percents and tool_results <= 1:
        if "speculative_metrics" not in tags:
            tags.append("speculative_metrics")
        score = max(score, 0.4)
        notes_parts.append(
            "Final answer uses specific percentages with limited tool evidence in the run."
        )

    # 2) Overconfident but no explicit citation/source
    if has_conf and not has_citation:
        if "overconfident_no_citation" not in tags:
            tags.append("overconfident_no_citation")
        score = max(score, 0.5)
        notes_parts.append(
            "Strongly confident language without explicit sources or citations."
        )

    # 3) Hallucination risk: long, confident answer, few tools
    if (
        length > 600  # quite long answer
        and (has_conf or "speculative_metrics" in tags)
        and tool_results <= 1
    ):
        if "hallucination_risk" not in tags:
            tags.append("hallucination_risk")
        score = max(score, 0.75)
        notes_parts.append(
            "Long, highly confident answer with minimal tool usage; likely hallucination risk."
        )

    step.analysis.risk_score = score
    step.analysis.failure_tags = tags
    step.analysis.notes = " ".join(p for p in notes_parts if p)


# ---------- main entrypoint ----------


def score_risks(run: Run):
    """
    Enrich all steps with simple risk analysis and return a summary.
    """
    stats = _compute_run_stats(run)

    for step in run.steps:
        # per-step rules
        _flag_basic_risks(step)
        _flag_tool_misuse(step, run)
        _flag_memory_drift(step, run)

        # final answer rules
        if step.type == "final_answer":
            _analyze_final_answer(step, stats)

    total = len(run.steps)
    flagged = sum(1 for s in run.steps if s.analysis.risk_score > 0)
    by_tag: Dict[str, int] = {}
    for s in run.steps:
        for t in s.analysis.failure_tags:
            by_tag[t] = by_tag.get(t, 0) + 1

    summary = {
        "total_steps": total,
        "flagged_steps": flagged,
        "by_failure_type": by_tag,
    }
    return run.steps, summary
