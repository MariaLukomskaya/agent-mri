import React, { useState } from "react";
import { TimelineStep } from "../../types";
import {
  ChevronDown,
  ChevronRight,
  Terminal,
  MessageSquare,
  BrainCircuit,
} from "lucide-react";

type Severity = "high" | "medium" | "low";

const tagSeverity: Record<string, Severity> = {
  hallucination_risk: "high",
  tool_misuse: "high",
  tool_error: "high",
  overconfident_no_citation: "high",

  speculative_metrics: "medium",
  weak_grounding: "medium",
  memory_drift: "medium",

  apology: "low",
};

function getTagClasses(tag: string): string {
  const sev = tagSeverity[tag] ?? "low";

  if (sev === "high") {
    return "bg-rose-50 text-rose-700 border border-rose-100";
  }
  if (sev === "medium") {
    return "bg-amber-50 text-amber-700 border border-amber-100";
  }
  return "bg-slate-50 text-slate-700 border border-slate-200";
}

const StepCard: React.FC<{ step: TimelineStep; isLast: boolean }> = ({
  step,
  isLast,
}) => {
  const [expanded, setExpanded] = useState(false);

  const getIcon = () => {
    switch (step.type) {
      case "tool_call":
        return <Terminal size={14} className="text-indigo-500" />;
      case "final_answer":
        return <MessageSquare size={14} className="text-emerald-600" />;
      default:
        return <BrainCircuit size={14} className="text-slate-500" />;
    }
  };

  const getBubbleBg = () => {
    switch (step.type) {
      case "tool_call":
        return "bg-indigo-50";
      case "final_answer":
        return "bg-emerald-50";
      default:
        return "bg-slate-50";
    }
  };

  const shortText =
    step.short && step.short.trim().length > 0
      ? step.short
      : "short summary";

  const bodyText =
    step.text && step.text.trim().length > 0
      ? step.text
      : "No detailed trace captured for this step.";

  return (
    <div className="relative pl-10">
      {/* vertical line */}
      {!isLast && (
        <div className="absolute left-[19px] top-10 bottom-0 w-px bg-slate-200" />
      )}

      {/* icon bubble */}
      <div
        className={`absolute left-0 top-1 w-10 h-10 rounded-full flex items-center justify-center border border-white shadow-sm z-10 ${getBubbleBg()}`}
      >
        {getIcon()}
      </div>

      <div className="mb-7">
        <div
          className="group cursor-pointer rounded-2xl border border-slate-100 bg-white/90 hover:bg-slate-50/70 px-4 py-3 -ml-4 -mt-2 transition-colors duration-200"
          onClick={() => setExpanded((v) => !v)}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-semibold text-slate-400 tracking-[0.14em] uppercase">
                  Step {step.step_id}
                </span>
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-[0.12em]">
                  {step.type}
                </span>
                {step.label && (
                  <span className="px-2 py-0.5 bg-slate-50 border border-slate-200 rounded-md text-[11px] font-medium text-slate-600 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
                    {step.label}
                  </span>
                )}
              </div>

              <p className="text-[14px] font-medium text-slate-900 leading-snug">
                {shortText}
              </p>
            </div>

            <button
              className="text-slate-300 group-hover:text-slate-500 transition-colors"
              aria-label={expanded ? "Collapse step" : "Expand step"}
            >
              {expanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
            </button>
          </div>

          {step.tags && step.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {step.tags.map((tag) => (
                <span
                  key={tag}
                  className={`px-2.5 py-0.5 rounded-full text-[11px] font-medium ${getTagClasses(
                    tag
                  )}`}
                >
                  {tag.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          )}
        </div>

        {expanded && (
          <div className="mt-2 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-[13px] text-slate-600 font-mono leading-relaxed whitespace-pre-wrap">
            {bodyText}
          </div>
        )}
      </div>
    </div>
  );
};

const TimelineTab: React.FC<{ steps: TimelineStep[] }> = ({ steps }) => {
  if (!steps || steps.length === 0) {
    return (
      <div className="py-4">
        <p className="text-sm text-slate-500">
          No execution trace available for this run yet.
        </p>
      </div>
    );
  }

  return (
    <div className="py-3">
      <div className="mb-6">
        <h3 className="text-base font-semibold text-slate-900 tracking-tight">
          Execution Trace
        </h3>
        <p className="mt-1 text-[13px] text-slate-500">
          Step-by-step view of the intern’s reasoning, tool calls, and final
          answer.
        </p>
      </div>

      {steps.map((step, index) => (
        <StepCard
          key={step.step_id ?? index}
          step={step}
          isLast={index === steps.length - 1}
        />
      ))}
    </div>
  );
};

export default TimelineTab;
