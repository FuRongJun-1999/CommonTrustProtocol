# -*- coding: utf-8 -*-
"""route_cache.py · 存算融合步骤 2——路由缓存（2026-08-29 心跳）

依 dsh 端判定报告（ARCH-GRAPH-SCF）步骤 2：高频条件组合 → 直接返回
预计算路由。TTL 与 stable 租约共享 exp(-γ·t) 衰减核思想（统一时间
动力学）；数据变更（知识库 mtime/指纹变化）时整体失效。

用法：
    rc = RouteCache(dex)
    hits = rc.route("问插入排序")      # 首次实测，二次起命中缓存
验证：test_route_cache.py（正确性/TTL 过期/失效重算/命中率统计）。
"""
from __future__ import annotations

import hashlib
import os
import time


class RouteCache:
    """card_route 结果缓存：TTL 过期 + 知识库指纹失效 + 命中率统计。"""

    def __init__(self, dex, ttl_s: float = 300.0, gamma: float = 0.0):
        self.dex = dex
        self.ttl_s = ttl_s
        self.gamma = gamma            # exp(-γ·t) 衰减（0 = 纯 TTL 口径）
        self._cache: dict = {}        # key → (expires_at, hits)
        self.stats = {"hits": 0, "misses": 0}

    @staticmethod
    def _key(query: str, limit: int) -> str:
        raw = f"{query}|{limit}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]

    def db_fingerprint(self) -> str:
        """知识库指纹（mtime+size）——变更即整体失效。"""
        p = getattr(self.dex, "db_path", None)
        if p and os.path.exists(p):
            st = os.stat(p)
            return f"{st.st_mtime_ns}:{st.st_size}"
        return "unknown"

    def route(self, query: str, limit: int = 1):
        from semantic_translate import card_route
        k = self._key(query, limit)
        hit = self._cache.get(k)
        now = time.time()
        if hit and hit[0] > now:
            self.stats["hits"] += 1
            return hit[1]
        # 未命中/过期 → 实测并缓存
        results = card_route(self.dex, query, limit=limit)
        ttl = self.ttl_s
        if self.gamma:                # exp(-γ·t) 衰减口径：有效留存按衰减核
            ttl = self.ttl_s * (2.718281828 ** (-self.gamma * now % 1))
        self._cache[k] = (now + ttl, results)
        self.stats["misses"] += 1
        return results

    def hit_rate(self) -> float:
        total = self.stats["hits"] + self.stats["misses"]
        return self.stats["hits"] / total if total else 0.0

    def invalidate(self):
        self._cache.clear()
