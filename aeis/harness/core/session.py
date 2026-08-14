# -*- coding: utf-8 -*-
"""harness.core.session · 会话上下文（多轮记忆）
================================================
运行时内维护多轮对话历史（角色消息列表），并同步到灵枢库
（Agent.remember / get_recent_context 双轨：运行时可断点恢复）。
"""
import json
import os


# 停用字（关键词提取过滤虚词组合）
_STOP_CHARS = set("我们之前一起了什么的否有没有在这是那怎样呢吗？?和与及对")

def _keyword_query(query: str) -> str:
    """从问题提取实词二元组（过滤停用字组合）→ 短关键词查询。
    长口语查询的整句重叠率区分度低（12+ 二元组命中 1-2 个分数接近），
    关键词化后（如"测试 游戏"）精确命中相关节点。"""
    chars = [c for c in query if '\u4e00' <= c <= '\u9fff']
    bigrams = []
    for i in range(len(chars) - 1):
        a, b = chars[i], chars[i + 1]
        if a not in _STOP_CHARS and b not in _STOP_CHARS:
            bigrams.append(a + b)
    # 只保留不重叠的连续实词段（避免碎片噪声）
    kept, skip = [], False
    for i, bg in enumerate(bigrams):
        if skip:
            skip = False
            continue
        kept.append(bg)
        if i + 1 < len(bigrams) and bigrams[i][1] == bigrams[i + 1][0]:
            skip = True  # 连续实词只取前段（灵枢→后续→开发）
    return " ".join(kept[:6]) if kept else query


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

    def recall(self, query: str = None, limit: int = 8) -> list:
        """从灵枢库召回相关记忆（按当前问题检索）。
        多样性策略：知识节点优先（防对话复读垄断），对话节点至多 2 条。"""
        if self.agent is None:
            return []
        try:
            q = query if query else "voice dialogue"
            # 关键词化查询（实词提取，精确命中）
            kq = _keyword_query(q)
            results = self.agent.search(kq, limit * 2 + 4)
            knowledge, dialogue = [], []
            for node, _score in results:
                tags = " ".join(node.tags or [])
                if "dialogue" in tags or "voice" in tags:
                    # 只注入 user 消息（assistant 旧回复可能含过时/错误结论，
                    # 会引导模型复述；且"没找到"类失败复读一律跳过）
                    if "assistant" in tags or any(
                            w in node.content for w in ("没找到", "没有找到", "找不到", "未找到")):
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
