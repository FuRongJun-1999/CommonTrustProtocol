# -*- coding: utf-8 -*-
"""harness.agents.task · 任务模型（AgentTask）
================================================
任务生命周期：pending → running → succeeded | failed | timed_out
特殊状态：RECURSION_BLOCKED（子智能体不得再派生子智能体，决议 Q5）。
"""
import time
import uuid


class AgentTask:
    """子智能体任务（dataclass 语义，零依赖手写）。"""

    def __init__(self, prompt: str, agent_role: str = "assistant",
                 db_path: str = None, title: str = "",
                 max_steps: int = 8, timeout: float = 300.0,
                 task_id: str = None):
        now = time.time()
        self.task_id = task_id or f"task_{int(now*1000)}_{uuid.uuid4().hex[:6]}"
        self.title = title or prompt[:30]
        self.prompt = prompt
        self.agent_role = agent_role
        self.db_path = db_path          # None = 共享主库
        self.max_steps = max_steps
        self.timeout = timeout
        self.status = "pending"         # pending/running/succeeded/failed/timed_out/RECURSION_BLOCKED
        self.result = None
        self.error = None
        self.steps_used = 0
        self.created_at = now
        self.finished_at = None

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items()}

    @classmethod
    def from_dict(cls, d: dict) -> "AgentTask":
        t = cls(d.get("prompt", ""), d.get("agent_role", "assistant"),
                d.get("db_path"), d.get("title", ""),
                d.get("max_steps", 8), d.get("timeout", 300.0),
                d.get("task_id"))
        t.status = d.get("status", "pending")
        t.result = d.get("result")
        t.error = d.get("error")
        t.steps_used = d.get("steps_used", 0)
        t.created_at = d.get("created_at", time.time())
        t.finished_at = d.get("finished_at")
        return t
