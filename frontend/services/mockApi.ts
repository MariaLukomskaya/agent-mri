// frontend/services/agentMriApi.ts

import { InternRunResponse, ChaosMode, RunRequest } from "../types";

const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Runs the Chaos Intern + Agent MRI pipeline via backend.
 */
export const runIntern = async (
  query: string,
  mode: ChaosMode
): Promise<InternRunResponse> => {
  const payload: RunRequest = {
    query,
    mode,
  };

  const resp = await fetch(`${API_BASE_URL}/run_intern`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const errorText = await resp.text();
    throw new Error(
      `Agent MRI API error ${resp.status}: ${errorText}`
    );
  }

  const data: InternRunResponse = await resp.json();
  return data;
};
