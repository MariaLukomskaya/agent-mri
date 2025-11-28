// frontend/App.tsx

import React, { useState } from "react";
import Header from "./components/Header";
import Hero from "./components/Hero";
import ControlCard from "./components/ControlCard";
import ResultsContainer from "./components/ResultsContainer";
import { ChaosMode, InternRunResponse } from "./types";
//import { runIntern } from "./services/agentMriApi";
import { runIntern } from "./services/mockApi";



function App() {
  // ---- state ----
  const [task, setTask] = useState<string>(
    "Summarize the top 3 AI security risks."
  );
  const [mode, setMode] = useState<ChaosMode>("default");
  const [status, setStatus] = useState<"idle" | "running" | "done" | "error">(
    "idle"
  );
  const [results, setResults] = useState<InternRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // ---- handlers ----
  const handleRun = async () => {
    if (!task.trim()) {
      return;
    }

    setStatus("running");
    setError(null);
    // optional: clear previous results while running
    // setResults(null);

    try {
      const data = await runIntern(task, mode);
      setResults(data);
      setStatus("done");
    } catch (err: any) {
      console.error(err);
      setError(err?.message ?? "Unexpected error while contacting Agent MRI.");
      setStatus("error");
    }
  };

  return (
    <div className="min-h-screen pb-20">
      <Header />

      <main className="pt-24 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          <Hero />

          <ControlCard
            task={task}
            setTask={setTask}
            mode={mode}
            setMode={setMode}
            onRun={handleRun}
            status={status}
          />

          {/* simple error banner */}
          {error && (
            <div className="mt-2 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          {results && (
            <div className="animate-in slide-in-from-bottom-4 duration-700">
              <ResultsContainer data={results} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
