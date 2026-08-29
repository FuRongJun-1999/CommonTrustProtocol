# -*- coding: utf-8 -*-
"""negative_routing · 负路由（能力级不适用条件）· 智能论 v3.4 6章.2
============================================================================
负路由（负条件拒绝）：条件路由的关键不只在「命中什么」，更在「拒绝什么」。
能力级不适用条件：候选关键词很像，但实际能力不同（如 BFS vs DFS 的邻域任务），
必须靠能力级不适用条件拒绝——不是语义相似度的副产品。

dsh-memory 实证：对抗负条件拒绝率 28% →（加能力级不适用条件）→ 88% → 91%。

判定逻辑（白箱确定性）：
  - 候选带 not_applicable（不适用条件）声明
  - 当前任务条件命中 not_applicable → REJECT（拒绝）
  - 否则正常参与路由

纯标准库 · 零外部依赖（D-005）
"""
from __future__ import annotations

from typing import Dict, List, Optional


class NegativeRouting:
    """能力级负路由过滤器。

    用法：路由候选 → negative_filter(candidates, task_conditions) → 幸存者
    返回：{survivors, rejected, stats}
    """

    def __init__(self):
        self._stats = {"total": 0, "rejected": 0, "accepted": 0}

    def negative_filter(self, candidates: List[Dict],
                        task_conditions: Optional[set] = None) -> Dict:
        """过滤候选：命中不适用条件 → REJECT；否则幸存。

        candidates: [{"id", "score", "not_applicable": [条件词...], ...}]
        task_conditions: 当前任务条件集合（用于判定是否命中不适用条件）
        返回：{survivors: [候选], rejected: [被拒候选], stats}
        """
        survivors = []
        rejected = []
        task = set(task_conditions or ())

        for cand in candidates:
            self._stats["total"] += 1
            na = cand.get("not_applicable") or []
            # 命中不适用条件：任务条件与 not_applicable 有交集
            if task and any(na_cond in task for na_cond in na):
                rejected.append({**cand, "reject_reason": f"能力级不适用条件命中: {[c for c in na if c in task]}"})
                self._stats["rejected"] += 1
            else:
                survivors.append(cand)
                self._stats["accepted"] += 1

        return {
            "survivors": survivors,
            "rejected": rejected,
            "stats": dict(self._stats),
            "rejection_rate": round(self._stats["rejected"] / max(1, self._stats["total"]), 4),
        }

    def reset_stats(self) -> None:
        self._stats = {"total": 0, "rejected": 0, "accepted": 0}


# 能力级不适用条件的工程示例（邻域混淆防护——BFS vs DFS 类）
CAPABILITY_NA_EXAMPLES = {
    "广度优先搜索": ["深度优先", "最短路径", "加权图"],
    "深度优先搜索": ["最短路径", "分层遍历"],
    "二分查找": ["线性查找", "哈希查找"],
    "冒泡排序": ["快速排序", "归并排序"],
    "条件路由": ["语义检索", "关键词匹配"],
}
