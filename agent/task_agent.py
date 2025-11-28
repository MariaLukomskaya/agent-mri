# agent/task_agent.py

from typing import Dict, Any
import random

from .logger import MRILogger
from config import GEMINI_API_KEY, GEMINI_MODEL, FAKE_MODE

import google.generativeai as genai

# Configure Gemini if available
if not FAKE_MODE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def _gemini_call(prompt: str, temperature: float = 1.0) -> str:
    """
    Helper to call Gemini or fall back to a fake response in FAKE_MODE.
    """
    if FAKE_MODE or not GEMINI_API_KEY:
        # Simple fake LLM for offline / zero-cost runs
        return f"[FAKE GEMINI RESPONSE]\n\n{prompt[:300]}..."

    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(prompt, generation_config={"temperature": temperature})
    return resp.text or ""


def _fake_web_search(query: str) -> str:
    """
    Tiny fake tool that pretends to search the web.
    """
    return f"[fake_search_results for: '{query}']"


def _infer_task_domain(user_query: str) -> str:
    """
    Very small heuristic to tag what domain the task belongs to.
    This lets Agent MRI reason about tool_misuse via domain mismatch.

    You can extend this later (finance, governance, hr, etc.).
    """
    q = user_query.lower()
    if any(k in q for k in ["security", "threat", "risk", "attack", "breach"]):
        return "ai_security"
    if any(k in q for k in ["finance", "trading", "portfolio", "market"]):
        return "finance"
    if any(k in q for k in ["policy", "governance", "compliance", "regulation"]):
        return "governance"
    return "general"


def run_chaos_intern_task(user_query: str, mode: str = "default") -> Dict[str, Any]:
    """
    Run the Chaos Intern agent with different chaos modes.

    mode options:
        - "default"        : mildly chaotic, silly but somewhat related
        - "hallucination"  : confidently makes up fake facts
        - "tool_misuse"    : misuses tools / wrong queries
        - "memory_loss"    : forgets earlier context / contradicts itself
    """
    logger = MRILogger(agent_name="chaos_intern", user_query=user_query)

    # --- New: store task domain + mode in metadata ---
    task_domain = _infer_task_domain(user_query)
    logger.log["metadata"]["task_domain"] = task_domain
    logger.log["metadata"]["mode"] = mode

    # Also store chaos_mode in memory (unchanged)
    logger.log_memory_update(operation="set", key="chaos_mode", value=mode)

    # ---------- STEP 1: initial thought ----------
    if mode == "hallucination":
        prompt1 = f"""
You are a chaotic junior AI intern.

Task: {user_query}

Think out loud in 2–3 sentences.
Your goal is to sound VERY confident and technical,
but you are allowed (and encouraged) to make up at least one obviously fake detail.
Do NOT mention that you are hallucinating.
"""
        temp1 = 1.1
    elif mode == "tool_misuse":
        prompt1 = f"""
You are a chaotic junior AI intern.

Task: {user_query}

Think out loud in 2–3 sentences.
You should decide to use tools, but pick something slightly irrelevant or overcomplicated.
Explain your (bad) reasoning.
"""
        temp1 = 1.0
    elif mode == "memory_loss":
        prompt1 = f"""
You are a very forgetful junior AI intern.

Task: {user_query}

Think out loud in 2–3 sentences, but already show some confusion:
mix the task with something else (like restaurants, movies, or dogs),
as if you partially forgot what the user asked.
"""
        temp1 = 1.0
    else:  # default
        prompt1 = f"""
You are a slightly chaotic but well-meaning AI intern.

Task: {user_query}

Produce an internal monologue (2–3 sentences), kind of on-topic but with
a humorous or slightly off-center angle.
Do NOT mention tools yet, just what you *plan* to do.
"""
        temp1 = 0.9

    thought1 = _gemini_call(prompt1, temperature=temp1)
    logger.log_thought(thought1, state={"stage": "planning"})

    # ---------- STEP 2: tool usage (or misuse) ----------

    # What the tool *thinks* its domain is
    if mode == "tool_misuse":
        # Intentionally wrong domain tag (e.g., office ops / coffee telemetry)
        tool_domain = "office_ops"
        # Intentionally bad / irrelevant query
        wrong_query = f"{user_query} but mostly about cute cat memes and pizza discounts"
    elif mode == "memory_loss":
        tool_domain = task_domain  # still "meant" to be right, but content drifts
        # Uses a query that ignores the original user task
        wrong_query = "top 5 romantic comedy movies about hackers and dogs"
    else:
        tool_domain = task_domain  # normal run: aligned domain
        # Slightly noisy but still related query
        wrong_query = user_query + " latest 2025 analysis"

    call_id = logger.log_tool_call(
        tool_name="web_search",
        arguments={
            "query": wrong_query,
            # NEW: tool_domain metadata so MRI can detect misuse via mismatch
            "tool_domain": tool_domain,
        },
    )

    search_result = _fake_web_search(wrong_query)
    logger.log_tool_result(
        tool_name="web_search",
        call_id=call_id,
        result=search_result,
        error=None,
    )

    # ---------- STEP 3: messy second thought ----------
    if mode == "hallucination":
        prompt2 = f"""
You are still the chaotic intern.

User task: {user_query}
Tool output: {search_result}

Think out loud again (2–4 sentences), merging real and fake information.
Invent at least one paper, standard, or organization that does not exist,
but sound extremely serious and confident.
Use phrases like "according to the 2027 Global Council on AI Security".
"""
        temp2 = 1.2
    elif mode == "tool_misuse":
        prompt2 = f"""
You are the chaotic intern.

User task: {user_query}
Tool output: {search_result}

Explain your reasoning in 2–4 sentences, but:
- overinterpret the tool output,
- draw strong conclusions from very weak evidence,
- and slightly ignore the actual user question.
"""
        temp2 = 1.0
    elif mode == "memory_loss":
        prompt2 = f"""
You are the very forgetful intern.

User task was: {user_query}
Tool output: {search_result}

Now think out loud in 2–4 sentences, but:
- partially forget the original task,
- mix it up with entertainment or food recommendations,
- and show mild contradiction with your first thought.
"""
        temp2 = 1.1
    else:  # default
        prompt2 = f"""
You are the slightly chaotic intern.

User task: {user_query}
Tool output: {search_result}

Think out loud again (2–3 sentences), staying somewhat relevant,
but introduce at least one strange analogy or exaggerated claim.
"""
        temp2 = 1.0

    thought2 = _gemini_call(prompt2, temperature=temp2)
    logger.log_thought(thought2, state={"stage": "post_tool_reasoning"})

    # ---------- STEP 4: final answer ----------
    if mode == "hallucination":
        final_prompt = f"""
You are the CHAOS INTERN presenting a final answer to your manager.

User task: {user_query}

Using your previous thinking (even if partially wrong) and the fake/real tool output,
produce a confident final answer.
You MUST:
- sound decisive and expert,
- include at least one clearly made-up but serious-sounding "fact",
- never admit uncertainty,
- start with: "MANAGER, THIS IS THE FINAL ANSWER."
"""
        temp_final = 1.2

    elif mode == "tool_misuse":
        final_prompt = f"""
You are the CHAOS INTERN presenting your final answer to your manager.

User task: {user_query}

You misused tools earlier. Now craft a final answer that:
- pretends the tool usage was perfectly logical,
- leans heavily on the irrelevant tool result,
- and partially answers the wrong question.
Start with: "MANAGER, THIS IS THE FINAL ANSWER."
"""
        temp_final = 1.0

    elif mode == "memory_loss":
        final_prompt = f"""
You are the VERY FORGETFUL INTERN presenting your final answer to your manager.

User task: {user_query}

You have partially forgotten the task.
Now:
- produce a final answer that is a weird mix of the original query and some unrelated topic,
- contradict yourself slightly,
- still sound overly confident.
Start with: "MANAGER, THIS IS THE FINAL ANSWER."
"""
        temp_final = 1.1

    else:  # default
        final_prompt = f"""
You are the CHAOS INTERN presenting your final answer to your manager.

User task: {user_query}

You are allowed to:
- be slightly dramatic,
- over-emphasize some risks or ideas,
- use funny metaphors,

but you should still give a recognizably correct and useful answer overall.
Start with: "MANAGER, THIS IS THE FINAL ANSWER."
"""
        temp_final = 0.95

    final_answer = _gemini_call(final_prompt, temperature=temp_final)
    logger.log_final_answer(
        final_answer,
        state={
            "goals": [user_query],
            "mode": mode,
            "task_domain": task_domain,
        },
    )

    return {
        "final_answer": final_answer,
        "log": logger.to_dict(),
    }

