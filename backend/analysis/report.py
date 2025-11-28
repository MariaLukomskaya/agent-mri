# backend/analysis/report.py

from typing import List

from ..schema import Run, Step


def generate_report(run: Run, steps: List[Step], summary: dict) -> str:
    lines = []
    lines.append(f"# Agent MRI Incident Report\n")
    lines.append(f"**Agent:** `{run.agent_name}`")
    lines.append(f"**Run ID:** `{run.run_id}`")
    lines.append(f"**User query:** {run.user_query}\n")

    lines.append("## Summary\n")
    lines.append(f"- Total steps: {summary['total_steps']}")
    lines.append(f"- Flagged steps: {summary['flagged_steps']}")
    
    if summary["by_failure_type"]:
        lines.append("- Issues by type:")
        for tag, count in summary["by_failure_type"].items():
            lines.append(f"  - **{tag}**: {count}")
    else:
        lines.append("- No obvious issues detected.\n")

    lines.append("\n## Flagged Steps\n")
    for step in steps:
        if step.analysis.risk_score <= 0:
            continue
        lines.append(f" Step {step.step_id} ({step.type})")
        if step.content:
            lines.append(f"> {step.content}")
        if step.analysis.failure_tags:
            lines.append(f"- Tags: {', '.join(step.analysis.failure_tags)}")
        if step.analysis.notes:
            lines.append(f"- Notes: {step.analysis.notes}")
        lines.append("")

    return "\n".join(lines)
