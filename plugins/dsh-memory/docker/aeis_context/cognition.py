#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cognitive_orchestrator · 认知编排器（v1.3 P0-2）
3.10 节自迭代八步闭环的工程层有损投影：
  L1 操作闭环（感知→识别→分析→验证）
  L2 协议闭环（固化提案→记录→反馈→方向性自检提案，提交验证单元复核，非内部自动执行）
设计依据：SPACETIME-V1.3-DESIGN-20260813-R1 第三章（DEVIATION-003 修正）
纯标准库 · 推理引擎为可注入抽象（CAL-2 · D-005 零依赖）
"""

import json
import time
import uuid
from typing import Dict, List, Optional


class CognitiveOrchestrator:
    """认知编排器：将感知-推理-反思-固化串成闭环（3.10 有损投影）"""

    DEFAULT_DEVIATION_THRESHOLD = 0.3  # CAL-4：对齐 2.7.2 动态死区 / 5.4 节反思触发阈值

    def __init__(self, engine, entity_registry, reasoning_engine=None,
                 deviation_threshold: float = DEFAULT_DEVIATION_THRESHOLD):
        self.engine = engine
        self.registry = entity_registry
        self.reasoning_engine = reasoning_engine   # duck-typed: reason(text, context) -> str
        self.deviation_threshold = deviation_threshold
        self._cycle_count = 0

    # ==================== L1 操作闭环 ====================

    def learning_cycle(self, input_signal: str, context: Dict = None) -> Dict:
        """执行一轮完整认知闭环：
        L1：感知 → 识别 → 分析 → 验证
        L2（偏差≥阈值时）：固化提案 → 记录 → 反馈 → 方向性自检提案（待外部复核）"""
        context = context or {}
        self._cycle_count += 1
        cycle_id = f"cyc_{int(time.time()*1000)}_{uuid.uuid4().hex[:4]}"

        # L1-1 感知：写入感知节点，提取实体
        entities = self.registry.extract_entities(input_signal) if self.registry else []
        perception = self.engine.add_perception(
            input_signal, importance=0.6,
            tags=["cognition_input", f"cycle:{cycle_id}"],
            entities=entities)

        # L1-2 识别：实体解析
        recognized = [self.registry.get_entity(e) for e in entities] if self.registry else []
        recognized = [e for e in recognized if e]

        # L1-3 分析：检索上下文 + 推理
        context_nodes = self.recall_context(input_signal, limit=10)
        reasoning = self._reason(input_signal, context, context_nodes)

        # L1-4 验证：偏差检测
        deviation = self.detect_deviation(context.get("expected", {}), context.get("actual", {}))

        l2 = None
        if deviation >= self.deviation_threshold:
            l2 = self._l2_protocol_cycle(cycle_id, input_signal, deviation,
                                         context_nodes, perception.id)

        record = {
            "cycle_id": cycle_id,
            "L1": {
                "perception_id": perception.id,
                "entities": entities,
                "recognized": [e["name"] for e in recognized],
                "reasoning": reasoning,
                "deviation": deviation,
            },
            "L2": l2,
        }
        # L2-6 记录（本轮闭环写入记忆库）
        self.engine.add_perception(
            f"[cycle] {cycle_id} deviation={deviation:.2f} l2={'triggered' if l2 else 'none'}",
            importance=0.5, tags=["cycle_record", f"cycle:{cycle_id}"])
        # A-5：持久化完整轨迹记录（训练资产格式）
        try:
            self.engine.add_perception(
                json.dumps(record, ensure_ascii=False),
                importance=0.5, tags=["cycle_record_full", f"cycle:{cycle_id}"])
        except Exception:
            pass
        # A-3：升级点检查（何种信号须提交维生系统）
        try:
            if hasattr(self.engine, "check_escalation"):
                record["L1"]["escalations"] = self.engine.check_escalation("deviation", deviation)
        except Exception:
            pass
        return record

    def recall_context(self, query: str, entity_id: str = None, limit: int = 10) -> List:
        """从时空记忆图中检索相关上下文（支持以实体为中心）"""
        if entity_id and self.registry:
            ctx = self.registry.get_entity_context(entity_id, limit=limit)
            return ctx.get("nodes", [])
        if hasattr(self.engine, "recall"):
            results = self.engine.recall(query, limit=limit)
            if results and isinstance(results[0], tuple):
                return [n for n, _ in results]
            return results
        return []

    def detect_deviation(self, expected: Dict, actual: Dict) -> float:
        """偏差检测（CAL-4：规范化相对偏差，默认阈值 0.3）"""
        if not expected:
            return 0.0
        keys = list(expected.keys())
        if not keys:
            return 0.0
        total = 0.0
        for k in keys:
            exp, act = expected.get(k), actual.get(k)
            if act is None:
                total += 1.0
                continue
            try:
                denom = abs(exp) if abs(exp) > 1e-9 else 1.0
                total += min(1.0, abs(act - exp) / denom)
            except TypeError:
                total += 0.0 if act == exp else 1.0
        return total / len(keys)

    # ==================== L2 协议闭环 ====================

    def _l2_protocol_cycle(self, cycle_id: str, signal: str, deviation: float,
                           context_nodes: List, perception_id: str) -> Dict:
        proposal = self.propose_fix(deviation, context_nodes)
        validated = self.validate_proposal(proposal)
        proposal["cycle_id"] = cycle_id
        proposal["perception_id"] = perception_id
        proposal["validated"] = validated
        # L2-5 固化提案（记录为待复核提案，不自动应用）
        self.engine.add_perception(
            f"[proposal] {proposal.get('summary', '')} validated={validated}",
            importance=0.8, tags=["fix_proposal", "pending_review", f"cycle:{cycle_id}"])
        # L2-7 反馈：未知区域 → 注册盲区
        if proposal.get("unknown_region"):
            try:
                self.engine.register_blindspot(
                    code=f"BS-CYCLE-{cycle_id}",
                    description=proposal["unknown_region"], severity="medium")
            except Exception:
                pass
        return {
            "proposal": proposal,
            "status": "pending_verification",
            "note": "方向性自检提案：提交验证单元复核与维生系统确认（非内部自动执行，DEVIATION-003）",
        }

    def propose_fix(self, deviation: float, context_nodes: List) -> Dict:
        """基于偏差与上下文生成修正提案（默认规则式）"""
        return {
            "intent": "降低本轮偏差",
            "target": "knowledge",
            "info_gap": round(deviation, 3),
            "summary": f"偏差 {deviation:.2f} 触发修正提案：复核相关记忆并校准理解",
            "reversible": True,
            "unknown_region": "偏差来源的深层条件空间未完全覆盖" if deviation >= 0.5 else "",
            "generated_by": "cognitive_orchestrator",
            "generated_at": time.time(),
        }

    def validate_proposal(self, proposal: Dict) -> bool:
        """验证提案与协议一致性（验证单元独立复核的规则式前置）"""
        if not isinstance(proposal, dict):
            return False
        for key in ("intent", "target", "info_gap"):
            if key not in proposal:
                return False
        if not proposal.get("reversible", False):
            return False
        content = proposal.get("content")
        if isinstance(content, dict) and content.get("threatens_existence"):
            return False
        return True

    # ==================== 交叉验证（约束4） ====================

    @staticmethod
    def reflect_cross_validate(text_a: str, text_b: str, threshold: float = 0.3) -> Dict:
        """REFLECT-CROSS-VALIDATION（VAL-TRANSFER-20260813-002-FINAL）：
        双反思单元对同一输入独立输出的偏差比对。
        偏差 = 1 - 中文二元组 Jaccard；> threshold(默认0.3) → 提交维生系统终裁。
        结果记入结构层（不可遗忘），由验证单元备案"""
        from spacetime_memory_core import LayeredStore
        sim = LayeredStore.char_bigram_jaccard(text_a, text_b)
        deviation = 1.0 - sim
        return {
            "deviation": round(deviation, 4),
            "similarity": round(sim, 4),
            "verdict": "needs_vitals_ruling" if deviation > threshold else "consistent",
            "threshold": threshold,
        }

    # ==================== 推理（CAL-2） ====================

    def _reason(self, input_signal: str, context: Dict, context_nodes: List) -> str:
        """推理：可注入 reasoning_engine；默认规则式摘要（降级路径，盲区56 缓解）"""
        if self.reasoning_engine is not None:
            try:
                result = self.reasoning_engine.reason(input_signal, {
                    "context": context,
                    "recalled": [n.content[:80] for n in context_nodes],
                })
                if result:
                    return str(result)
            except Exception:
                pass
        return (f"规则式分析：输入关联 {len(context_nodes)} 条记忆；"
                f"按既有知识响应")
