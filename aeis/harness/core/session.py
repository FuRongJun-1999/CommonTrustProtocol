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

    def recall(self, query: str = None, limit: int = 6) -> list:
        """从灵枢库召回相关记忆（按当前问题检索）。
        多样性策略：知识节点优先（防对话复读垄断），对话节点至多 2 条。"""
        if self.agent is None:
            return []
        try:
            q = query if query else "voice dialogue"
            results = self.agent.search(q, limit * 2 + 4)
            knowledge, dialogue = [], []
            for node, _score in results:
                tags = " ".join(node.tags or [])
                if "dialogue" in tags or "voice" in tags:
                    # 过滤"没找到"类失败复读（防幻觉锚点自我引用循环）
                    if any(w in node.content for w in ("没找到", "没有找到", "找不到", "未找到")):
                        continue
                    dialogue.append(node.content)
                else:
                    knowledge.append(node.content)
            merged = knowledge[:limit - 2] + dialogue[:2]
            # 联想召回补充（组合相似+重要性+近因），知识节点优先
            try:
                for node, _score in self.agent.recall(q, limit=4):
                    tags = " ".join(node.tags or [])
                    if "dialogue" not in tags and "voice" not in tags \
                            and node.content not in merged:
                        merged.append(node.content)
            except Exception:
                pass
            return merged[:limit]
        except Exception:
            return []

    def clear(self):
        self.history = []

    def history_for(self, query: str, max_items: int = 8) -> list:
        """注入用历史：过滤与当前问题重复的旧回答（防复读循环——
        相同问题旧回答若注入，模型会自我引用复读）。"""
        try:
            from aeis.core import LayeredStore
            qb = LayeredStore._bigrams(query)
        except Exception:
            qb = set()
        keep = []
        for m in reversed(self.history):
            if m["role"] == "assistant" and qb:
                mb = LayeredStore._bigrams(m["content"])
                overlap = len(qb & mb) / max(1, len(qb))
                if overlap > 0.5:
                    continue  # 旧回答与当前问题高度重叠 → 跳过（防复读）
            keep.append(m)
            if len(keep) >= max_items:
                break
        return list(reversed(keep))
