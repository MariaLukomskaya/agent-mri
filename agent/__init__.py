# agent/__init__.py

from .task_agent import run_chaos_intern_task
from .critic_agent import get_critic_advice

__all__ = ["run_chaos_intern_task", "get_critic_advice"]
