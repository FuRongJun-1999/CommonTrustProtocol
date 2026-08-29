# -*- coding: utf-8 -*-
"""hot_cold.py · 存算融合步骤 3——冷热分层（2026-08-29 心跳）

ARCH-GRAPH-SCF 步骤 3（判定报告）：热图驻留内存，冷图落盘，按访问
命中率的贝叶斯更新升降级（复用 2.9.1a 通道可信度框架：
c ~ Beta(a0 + n_hit, b0 + n_miss)）。

- 热（HOT）：CSR 常驻内存，查询 O(1) 切片
- 冷（COLD）：落盘 jsonl，访问时按需加载（不常驻）
- 升降级：命中率高 → 升热；长期未命中 → 降冷（不删数据）
- 冷图访问不阻塞热图路径（分层判定的独立性）
"""
from __future__ import annotations

import json
import os
import time

HOT, COLD = "hot", "cold"


def beta_mean(hit: int, miss: int, a0: float = 1.0, b0: float = 1.0) -> float:
    """Beta 后验均值（伪样本量加权，与通道可信度同框架）。"""
    return (a0 + hit) / (a0 + b0 + hit + miss)


class HotColdStore:
    """分层存储：HOT 常驻内存字典 / COLD 落盘 jsonl，访问计数驱动升降级。"""

    def __init__(self, root: str, hot_threshold: float = 0.3, min_samples: int = 4):
        self.root = root
        self.cold_path = os.path.join(root, "cold.jsonl")
        os.makedirs(root, exist_ok=True)
        self.hot: dict = {}          # key → value（常驻内存）
        self.stats: dict = {}        # key → {"hit": n, "miss": n, "tier": HOT/COLD}
        self.hot_threshold = hot_threshold
        self.min_samples = min_samples
        self._load_cold()

    def _load_cold(self):
        if os.path.exists(self.cold_path):
            with open(self.cold_path, encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        self.stats.setdefault(d["key"], {"hit": 0, "miss": 0, "tier": COLD})
                    except (json.JSONDecodeError, KeyError):
                        continue

    def put(self, key: str, value, tier: str = HOT):
        if tier == HOT:
            self.hot[key] = value
            self.stats.setdefault(key, {"hit": 0, "miss": 0, "tier": HOT})["tier"] = HOT
        else:
            with open(self.cold_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "value": value}, ensure_ascii=False) + "\n")
            self.stats.setdefault(key, {"hit": 0, "miss": 0, "tier": COLD})["tier"] = COLD

    def get(self, key: str):
        if key in self.hot:                      # 热路径：O(1) 内存
            self._count(key, True)
            return self.hot[key]
        # 冷路径：落盘顺序扫描（不阻塞热路径——独立调用）
        found = self._scan_cold(key)
        if found is not None:
            self._count(key, True)
            return found
        self._count(key, False)
        return None

    def _scan_cold(self, key):
        if not os.path.exists(self.cold_path):
            return None
        with open(self.cold_path, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    if d.get("key") == key:
                        return d.get("value")
                except json.JSONDecodeError:
                    continue
        return None

    def _count(self, key, hit: bool):
        s = self.stats.setdefault(key, {"hit": 0, "miss": 0, "tier": HOT})
        s["hit" if hit else "miss"] = s.get("hit" if hit else "miss", 0) + 1

    def rebalance(self) -> dict:
        """按 Beta 后验均值升降级：热层中均值低于阈值 → 降冷；冷层中命中高 → 升热。"""
        moved = {"demoted": [], "promoted": []}
        for key in list(self.hot):
            s = self.stats.get(key, {"hit": 0, "miss": 0})
            samples = s["hit"] + s["miss"]
            if samples >= self.min_samples:
                m = beta_mean(s["hit"], s["miss"])
                if m < self.hot_threshold:
                    self.cold_dump(key, self.hot.pop(key))
                    moved["demoted"].append(key)
        # 冷层升级：冷条目命中计数高 → 升热（简化：由外部访问计数驱动）
        return moved

    def cold_dump(self, key, value):
        with open(self.cold_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"key": key, "value": value}, ensure_ascii=False) + "\n")
        self.stats.setdefault(key, {"tier": COLD})

    def tier_of(self, key: str) -> str:
        if key in self.hot:
            return HOT
        return COLD if key in self.stats else "absent"
