# Agent MRI: Observability & Risk Scoring for AI Agents

**Track:** Enterprise Agents  
**Author:** Maria Lukomskaya  
**Project:** AI Agents Intensive (Google & Kaggle) — Capstone 2025  

---

## 🧠 Agent MRI — An X-Ray for AI Agent Reasoning

Visualise, debug, and score the behavior of chaotic AI agents using real-time observability, risk tagging, and human-style reports.

<img src="/Users/marialukomskaya/Folders/work/code/agent-mri/demo/agent-mri-0.png" width="600"/>

---

## 🎯 1. Problem

Modern AI agents behave like black boxes:

- They hallucinate confidently  
- They misuse tools  
- They drift from the task  
- They produce long chains of reasoning no human can audit  

Enterprise teams need to **trust** these agents, especially when used in:

- Customer support  
- Analysis workflows  
- Internal decision pipelines  

But today, there is **no transparent way** to see how an agent reached its answer or where it went wrong.

---

## 💡 2. Solution — Agent MRI

Agent MRI is a multi-component system that:

###  1. Runs a deliberately chaotic junior AI agent (“Chaos Intern”)

The agent imitates real failure modes:

- hallucination  
- tool misuse  
- memory drift  

### 2. Parses the entire reasoning trace

End-to-end trace:

- Thoughts  
- Tool calls  
- Tool results  
- Final answer  

### 3. Automatically tags risks

Risk categories include:

- `hallucination_risk`  
- `tool_misuse`  
- `weak_grounding`  
- `memory_drift`  
- `overconfident_no_citation`  
- `speculative_metrics`  

### 4. Produces a visual Timeline 

- Shows each reasoning step  
- Highlights errors  
- Displays tool calls and their outputs  

### 5. Generates an executive Incident Report

- Senior-manager style explanation  
- What went wrong, where, and why  
- Concrete recommendations

---

## 🧬 3. Architecture Overview

```text
┌──────────────────┐
│   User Input     │
└─────────┬────────┘
          │
          ▼
┌──────────────────────┐
│  Chaos Intern Agent   │  ← multi-step reasoning, tools, drift
└─────────┬────────────┘
          │ log (JSON)
          ▼
┌────────────────────────────┐
│      Agent MRI Backend     │
│  - Parser                  │
│  - Risk Scorer             │
│  - Report Generator        │
│  - Timeline Formatter      │
└─────────┬──────────────────┘
          │ structured analysis
          ▼
┌────────────────────────────┐
│      Frontend (UI Layer)   │
│  - Timeline View           │
│  - Risk Dashboard          │
│  - Markdown Reports        │
└────────────────────────────┘
```
## 🧑‍💻 4. Implementation Details

This project demonstrates **six major agent concepts** from the Intensive.

### ✔️ Multi-Agent System

- **Chaos Intern Agent** — LLM-powered, with tool access  
- **Senior Manager Critic Agent** — LLM-powered evaluator based on MRI output  

### ✔️ Tools

- Custom tools (e.g., fake maritime risk tool, fake verification suite)  
- Logging & tracing utilities  

### ✔️ Observability & Tracing

- Every step captured: thoughts, tool calls, arguments, results  
- Stored in a typed JSON log  
- Parsed into structured DAG-like steps  
- Timeline UI to observe reasoning chain  
- Graph view (planned)  

### ✔️ Memory & State

- Simulated memory drift  
- Step-level tracking of context changes  
- Risk detection on missing / overwritten memory  

### ✔️ Agent Evaluation

- Automatic tagging of risk categories  
- Weighted risk scoring formula (0–100)  
- Executive incident report generation  

### ✔️ Deployment

- **FastAPI** backend  
- **React** frontend (primary UI)  

---

## 🏗️ 5. Repository Structure

## 📁 Repository Structure

```text
.
├── agent/                     # "Chaos Intern" & Critic agents (Gemini / LLM logic)
│   ├── __init__.py
│   ├── task_agent.py          # Main junior agent ("Chaos Intern") that runs the task
│   ├── critic_agent.py        # Senior reviewer agent that comments on failures
│   └── logger.py              # Utility to log structured traces for Agent MRI
│
├── backend/                   # Agent MRI analysis backend (FastAPI + scoring)
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── risk_scorer.py     # Tags steps with hallucination_risk, tool_misuse, etc.
│   │   └── report.py          # Generates the incident report markdown
│   │
│   ├── api.py                 # Public Python API: analyze_log(log) -> steps + summary
│   ├── parser.py              # Parses raw JSON logs into Run/Step dataclasses
│   ├── schema.py              # Pydantic / dataclass schema for runs and steps
│   ├── server.py              # FastAPI app exposing POST /analyze
│   └── test_api.py            # Small local test for the backend API
│
├── frontend/                  # Demo UI (React + Vite + Tailwind-style design)
│
├── demo/                      # (Optional) Screenshots, demo
│
├── config.py                  
├── environment.yml            # Conda environment spec for the Python backend
├── requirements.txt           # pip requirements for backend (if not using Conda)
└── README.md                  # You are here 🙂
```

## 🚀 6. How to Run

### Before running
Before running the project, create a `.env` file in the **project root** with your Gemini config:

```bash
touch .env
```

Then add:

```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=models/gemini-flash-latest
FAKE_MODE=false
```
GEMINI_API_KEY — your Google Gemini API key
GEMINI_MODEL — model used by the critic agent
FAKE_MODE — set to true to disable real LLM calls and use deterministic fake outputs (useful for demos/tests)

## To Run
### 1. Install dependencies

```bash
pip install -r requirements.txt
```
### 2. Start Backend API (FastAPI)

```bash
uvicorn backend.server:app --reload

```

### 3. Run front-end 

```bash
cd frontend
npm install
npm run dev
```

Then open:
```
http://localhost:3000/
```


## 🕒 7. Demo Features

### ✔️ Timeline View
- Visual step-by-step reconstruction of agent reasoning  
- Thoughts, tools, memory updates, final answer  

### ✔️ MRI Risk Dashboard
- Total steps  
- Flagged steps  
- Breakdown by failure type  
- Weighted risk score (0–100)  

### ✔️ Incident Report
Auto-generated markdown report including:
- Diagnosis  
- Root cause analysis  
- Recommendations  
- Senior Manager feedback  


