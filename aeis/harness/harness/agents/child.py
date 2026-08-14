# -*- coding: utf-8 -*-
"""harness.agents.child · 子智能体（独立 Agent 实例 + 递归防护）
================================================
子智能体 = 单实例内蜂群折叠的"子实例"：
- 独立 Agent（identity/db_path 可配），惰性构造（0.47s）
- 独立线程执行任务循环（≤ max_steps）
- 递归防护（决议 Q5 / DEVIATION-007 关闭）：检测子任务派发指令
  或 subagent 标签嵌套 → RECURSION_BLOCKED，不得再派生子智能体

think_fn 可注入（默认 harness.core.think.chat），测试用 fake。
"""
import sys
import os
import threading
import time

_AEIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AEIS_ROOT not in sys.path:
    sys.path.insert(0, _AEIS_ROOT)

# 子任务派发指令关键词（递归检测，决议 Q5）
SPAWN_KEYWORDS = ("派生子智能体", "再派生一个", "创建子智能体", "subagent",
                  "开一个子体", "让另一个子智能体")


class ChildAgent:
    """子智能体：独立 Agent + 任务循环。"""

    def __init__(self, identity: str = "子智能体", db_path: str = None,
                 think_fn=None, log=None):
        self.identity = identity
        self.db_path = db_path
        self.think_fn = think_fn
        self.log = log or (lambda *a: None)
        self._agent = None
        self._lock = threading.Lock()

    def _ensure_agent(self, env: dict = None):
        """惰性构造 Agent（复用 AgentPool 同款路径）。"""
        if self._agent is None:
            import aeis  # noqa: F401
            from aeis.api import Agent
            self._agent = Agent(identity=self.identity,
                                db_path=self.db_path or ":memory:")
        return self._agent

    def run(self, task, env: dict = None) -> object:
        """执行任务（当前线程内；由 Supervisor 放入线程池）。
        返回 task（结果写回 task.result/status/error）。"""
        task.status = "running"
        task.steps_used = 0
        # 递归防护（决议 Q5）：输入含派发指令 → RECURSION_BLOCKED
        if any(kw in task.prompt for kw in SPAWN_KEYWORDS):
            task.status = "RECURSION_BLOCKED"
            task.error = "子智能体不得再派生子智能体（递归深度=1 硬限制）"
            task.finished_at = time.time()
            return task
        try:
            # 统一构造 Agent（表初始化 + 记忆面一致；惰性 0.47s）
            agent = self._ensure_agent(env)
            if self.think_fn is not None:
                # 注入思考函数（测试/自定义推理）
                reply = str(self.think_fn(task) or "")
            else:
                # 系统提示（子身份）
                system = (
                    f"你是灵枢的子智能体「{self.identity}」。你有独立的思考与记忆"
                    f"（{'共享库' if not self.db_path else '独立库'}）。"
                    f"任务：{task.prompt}\n"
                    "完成一个简明结果（≤200字），不要派生子任务，不要重复询问。")
                memory = []
                try:
                    res = agent.search(task.prompt, 3)
                    memory = [c for c, _ in res]
                except Exception:
                    pass
                from harness.core.think import build_messages, chat
                msgs = build_messages(task.prompt, memory=memory, identity=system)
                reply = chat("https://api.deepseek.com",
                             (env or {}).get("DEEPSEEK_API_KEY", ""),
                             "deepseek-chat", msgs,
                             temperature=0.5, max_tokens=300)
            task.steps_used = 1
            task.result = reply
            task.status = "succeeded"
        except Exception as exc:
            task.status = "failed"
            task.error = str(exc)[:300]
        task.finished_at = time.time()
        return task

    def close(self):
        with self._lock:
            if self._agent is not None:
                try:
                    self._agent.close()
                except Exception:
                    pass
                self._agent = None
