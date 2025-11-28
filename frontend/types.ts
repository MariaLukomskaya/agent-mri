// frontend/types.ts

// ---- CHAOS MODE ----

export type ChaosMode =
  | "default"
  | "hallucination"
  | "tool_misuse"
  | "memory_loss";


// ---- TIMELINE ----

export type TimelineStepType =
  | "thought"
  | "tool_call"
  | "tool_result"
  | "memory_update"
  | "final_answer";

export interface TimelineStep {
  step_id: number;
  type: TimelineStepType;
  label?: string;
  short?: string;
  text?: string;
  tags?: string[];
}


// ---- MRI SUMMARY ----

export interface MRISummary {
  total_steps: number;
  flagged_steps: number;
  by_failure_type: Record<string, number>;
}


// ---- MRI RISK ----

export type RiskLevel = "Low" | "Medium" | "High";

export interface MRIRisk {
  score: number;   // 0–100
  level: RiskLevel;
}


// ---- FULL RESPONSE FROM BACKEND ----
// (This matches what your /run_intern endpoint should return)

export interface InternRunResponse {
  final_answer_md: string;
  summary: MRISummary;
  risk: MRIRisk;
  steps: TimelineStep[];        // <-- NOT timeline_steps (important)
  report_markdown: string;
  critic_markdown: string;
}


// ---- REQUEST PAYLOAD TO BACKEND ----

export interface RunRequest {
  query: string;
  mode: ChaosMode;
}
