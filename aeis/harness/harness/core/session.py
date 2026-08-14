# -*- coding: utf-8 -*-
"""harness.core.session · 会话上下文（多轮记忆）
================================================
运行时内维护多轮对话历史（角色消息列表），并同步到灵枢库
（Agent.remember / get_recent_context 双轨：运行时可断点恢复）。
"""
import json
import os


class Session:
    """简单多轮会话：历史列表 + 持久化到灵枢库（voice 标签）。"""

    def __init__(self, agent=None, max_history: int = 20, persist: bool = True):
        self.agent = agent
        self.max_history = max_history
        self.persist = persist
        self.history = []  # [{"role": "user"|"assistant", "content": "..."}]

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        if self.persist and self.agent is not None:
            try:
                self.agent.remember(
                    f"[对话{role}] {content}",
                    importance=0.5, tags=["voice", "dialogue", role])
            except Exception:
                pass

    def recall(self, limit: int = 6) -> list:
        """从灵枢库召回最近对话记忆（跨进程/重启恢复）。"""
        if self.agent is None:
            return []
        try:
            results = self.agent.search("voice dialogue", limit)
            return [c for c, _ in results][:limit]
        except Exception:
            return []

    def clear(self):
        self.history = []
