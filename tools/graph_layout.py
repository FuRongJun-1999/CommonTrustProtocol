# -*- coding: utf-8 -*-
"""graph_layout.py · 存算融合步骤 1——图物理布局对齐（2026-08-29 心跳）

ARCH-GRAPH-SCF 步骤 1（判定报告）：将条件路由图从「查询时全库扫描」转为
CSR 压缩布局 + 按条件词哈希的物理邻接——让「结构相邻」等于「物理相邻」，
条件链遍历的内存访问模式匹配预取粒度。

CSR 三数组：indptr（行偏移）/ indices（列索引）/ data（节点载荷）。
构建：扫描知识卡条件词 → 条件词哈希为行 → 命中卡列表压缩存储。
查询：条件词 → 行二分/直接索引 → 邻接切片（顺序内存访问）。
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time


class CSRGraph:
    """条件词 → 卡列表 的 CSR 压缩布局（构建一次，查询 O(1) 切片）。"""

    def __init__(self, indptr, indices, data, words, word_row=None):
        self.indptr = indptr          # len = len(words)+1
        self.indices = indices        # 卡索引（展开）
        self.data = data              # 与 indices 对齐的卡 id 列表
        self.words = words            # 行 → 条件词
        self._word_row = word_row or {w: i for i, w in enumerate(words)}

    def row(self, word: str) -> list:
        """条件词 → 命中卡 id 列表（切片访问，顺序内存）。"""
        r = self._word_row.get(word)
        if r is None:
            return []
        return self.data[self.indptr[r]:self.indptr[r + 1]]

    @staticmethod
    def _hash(word):
        return int.from_bytes(hashlib.sha256(word.encode("utf-8")).digest()[:4], "little")

    @classmethod
    def build(cls, db_path: str) -> "CSRGraph":
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT id, state_attributes FROM nodes "
            "WHERE state_attributes LIKE '%生效条件%'").fetchall()
        conn.close()
        word_map = {}   # word → [card_id]
        for nid, sa in rows:
            try:
                d = json.loads(sa)
            except Exception:
                continue
            cm = d.get("comment", {})
            for key in ("生效条件", "不适用条件"):
                for w in (cm.get(key, []) or []):
                    if isinstance(w, str) and w.startswith("问"):
                        word_map.setdefault(w, []).append(nid)
        words = sorted(word_map)
        word_row = {w: i for i, w in enumerate(words)}
        indptr = [0]
        indices, data = [], []
        for i, w in enumerate(words):
            cards = word_map[w]
            indices.extend([i] * len(cards))
            data.extend(cards)
            indptr.append(len(data))
        return cls(indptr, indices, data, words, word_row)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    HERE = os.path.dirname(os.path.abspath(__file__))
    db = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
    t0 = time.time()
    g = CSRGraph.build(db)
    build_ms = (time.time() - t0) * 1000
    print(f"CSR 构建 {build_ms:.0f}ms | 条件词 {len(g.words)} | 邻接 {len(g.data)}")
    demo = g.row("问插入排序")
    print("问插入排序 →", demo[:3])
