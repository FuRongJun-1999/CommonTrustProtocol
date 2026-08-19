#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
blindspot_learning_loop · 盲区学习闭环（v1.3 P0-3）
第零定律（学习=缩小信息差）的工程化：盲区 → 探索 → 证据 → 终态
终态（DEVIATION-004 修正，符合 0.0.3 局部不可知）：
  mitigated（已缓解）/ observing（持续观察）/
  structurally_unknown（结构性不可知）/ adopted（纳入结构层）
约束：每盲区最大探索次数（默认 3），超限 → structurally_unknown
设计依据：SPACETIME-V1.3-DESIGN-20260813-R1 第四章
纯标准库 · 探索提供者为可注入抽象（CAL-3 · D-005 零依赖）
"""

import time
from typing import Dict, List, Optional

TERMINAL_STATES = ("mitigated", "observing", "structurally_unknown", "adopted")

SEVERITY_PRIORITY = {"high": 3, "medium": 2, "low": 1}

STRUCTURAL_KEYWORDS = ("局部不可知", "不可验证", "结构性", "不可消除", "不可观测")


class BlindSpotLearningLoop:
    """盲区学习闭环：将"知道不知道什么"转化为"去学什么"（第零定律操作化）"""

    MAX_ATTEMPTS = 3

    def __init__(self, engine, exploration_provider=None, max_attempts: int = MAX_ATTEMPTS):
        self.engine = engine
        self.exploration_provider = exploration_provider   # duck-typed: explore(blindspot) -> dict
        self.max_attempts = max_attempts

    # ---- 候选选择 ----

    def get_next_candidate(self) -> Optional[Dict]:
        """下一个待探索盲区（优先级：severity 高→低，先入先出）"""
        candidates = self.prioritize_blindspots()
        return candidates[0] if candidates else None

    def prioritize_blindspots(self) -> List[Dict]:
        """按优先级排序可探索盲区（open + observing 持续监测中；4.5 节优先级规则）"""
        candidates = []
        if hasattr(self.engine, "list_blindspots"):
            candidates = [b for b in self.engine.list_blindspots()
                          if b.get("status") in ("open", "observing")]
        candidates.sort(key=lambda b: (-SEVERITY_PRIORITY.get(b.get("severity", "low"), 1),
                                       b.get("created_at", 0.0)))
        return candidates

    # ---- 学习一步 ----

    def learn_next(self, use_prediction: bool = True) -> Dict:
        """从开放盲区中选取一个，探索并判定终态（v1.10：use_prediction=预测验证模式）
        v1.15：预测路线持久化为「待验证预测」（pending_prediction），
        供 prediction_feedback 回填对比（协议 2.10 D₃ · D-006 动态校准）。"""
        bs = self.get_next_candidate()
        if not bs:
            return {"status": "no_open_blindspot", "blindspot": None}

        attempts = bs.get("attempts", 0) + 1
        # v1.10 预测×盲区联动：可预测盲区 → 预测路线作为探索假设（不可知盲区跳过）
        predicted = []
        pending_ids = []
        if use_prediction and bs.get("predictability", "pending_assessment") != "unknowable":
            try:
                if hasattr(self.engine, "predict_routes"):
                    pr = self.engine.predict_routes(blindspot_id=bs["id"])
                    if pr.get("routes"):
                        predicted = [r["path"] for r in pr["routes"][:3]]
                        # v1.15 持久化：每条预测路线 → 待验证预测节点
                        for i, path in enumerate(predicted[:3]):
                            try:
                                names = []
                                for nid in path:
                                    n = self.engine.store.get_node(nid)
                                    names.append(n.state_attributes.get("name") if n else nid)
                                pid = self.engine.add_perception(
                                    f"[待验证预测] 盲区 {bs.get('code', '')} 路线{i + 1}: "
                                    + " → ".join(str(x) for x in names),
                                    importance=0.55,
                                    tags=["观测层", "pending_prediction",
                                          "prediction_route", f"blindspot:{bs['id']}"],
                                    condition_space=None)
                                pending_ids.append({"route_id": pid, "path": path})
                            except Exception:
                                pass
            except Exception:
                pass
        evidence = self._explore(bs, predicted)
        terminal = self._decide_terminal(bs, evidence, attempts)
        self._set_status(bs["id"], terminal, attempts)

        # 学习结果固化（写回长期记忆）
        record = {
            "summary": f"盲区 {bs.get('code', '')} 探索完成：{terminal}"
                       + (f"（预测验证 {len(predicted)} 路线）" if predicted else ""),
            "entities": [],
            "evidence": evidence.get("notes", []),
        }
        try:
            if hasattr(self.engine, "consolidate_learning_result"):
                self.engine.consolidate_learning_result(record)
        except Exception:
            pass
        return {"status": terminal, "blindspot": bs, "evidence": evidence,
                "attempts": attempts, "predicted_routes": len(predicted),
                "pending_predictions": pending_ids}

    # ---- 内部 ----

    def _explore(self, bs: Dict, predicted: List = None) -> Dict:
        """探索：预测路线为**假设**（hypotheses，非缓解证据）；搜索命中为证据（notes）。
        可注入 exploration_provider（CAL-3）；默认内部推演"""
        if self.exploration_provider is not None:
            try:
                result = self.exploration_provider.explore(bs)
                if result and isinstance(result, dict):
                    return result
            except Exception:
                pass
        notes = []
        hypotheses = list(predicted or [])
        rejected = []
        try:
            if not notes and hasattr(self.engine, "search_content"):
                hits = self.engine.search_content(bs.get("description", ""), limit=5)
                notes = [n.content[:60] for n, _ in hits]
            # A-1：相似被拒路径作为反证（防重复失败，不视为缓解证据）
            if hasattr(self.engine, "find_rejected_paths"):
                rps = self.engine.find_rejected_paths(bs.get("description", ""), limit=3)
                rejected = [f"已知失败路径：{r['description'][:40]}" for r in rps]
        except Exception:
            pass
        return {"notes": notes, "hypotheses": hypotheses, "rejected": rejected,
                "provider": "prediction" if hypotheses else "internal"}

    def _decide_terminal(self, bs: Dict, evidence: Dict, attempts: int) -> str:
        """终态判定（四类，DEVIATION-004 + 最大探索次数强制）：
        - structurally_unknown：描述指向不可知结构（0.0.3）或探索达上限
        - mitigated：检索到相关证据（信息差缩小至阈值以下）
        - observing：证据不足且未达上限（保持候选，继续监测）
        - adopted：由验证单元/维生系统确认后纳入结构层（本层标记候选）"""
        desc = f"{bs.get('description', '')} {bs.get('code', '')}"
        if any(kw in desc for kw in STRUCTURAL_KEYWORDS):
            return "structurally_unknown"
        if evidence.get("notes"):
            return "mitigated"
        if attempts >= self.max_attempts:
            return "structurally_unknown"
        return "observing"

    def _set_status(self, bs_id: str, status: str, attempts: int):
        try:
            c = self.engine.store.conn.cursor()
            resolved_at = time.time() if status != "open" else None
            c.execute("UPDATE blindspots SET status=?, attempts=?, resolved_at=? WHERE id=?",
                      (status, attempts, resolved_at, bs_id))
            self.engine.store.conn.commit()
        except Exception:
            pass
