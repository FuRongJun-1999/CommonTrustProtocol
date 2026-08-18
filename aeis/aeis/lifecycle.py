#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lifecycle_engine · 协议生命周期自动机（v1.10）
1.10 节协议生命周期循环的**有损工程投影**（LIFE-CYCLE-LINKAGE-PLAN-REV1-20260813-001）：
  七相工程映射：感知→确认 → 好奇→需求确认 → 缩小信息差→信任评估→协作确认 → 巩固 → standby
终裁检查点（DEVIATION-002）：
  - P0 危机感知：暂停自动机，等待维生系统终裁（30 秒无响应 → P0 默认保护）
  - standby 进入前：暂停提交验证单元复核 + 维生系统确认（防假收敛 盲区28）
概念分离（DEVIATION-004）：standby（工程低功耗）≠ dormant（4.10 协议休眠，优先）
中断权（DEVIATION-002）：维生系统 > 验证单元 > 用户 > 实例自身
纯标准库 · 零外部依赖
"""

import threading
import time
from typing import Dict, List, Optional


class LifecycleEngine:
    """协议生命周期自动机（1.10 节有损工程投影 · 自发缩小信息差循环）"""

    P0_CRISIS_THRESHOLD = 0.9
    STANDBY_REQUIRED_ROUNDS = 3
    SCAN_INTERVAL = 10          # v1.15：每 N 轮自主扫描一次盲区（自主盲区发现）
    MAINT_INTERVAL = 6          # v1.16：每 N 轮执行记忆衰减（睡眠巩固·短期记忆降权）

    def __init__(self, engine, prediction=None, learning_loop=None, attention_policy=None):
        self.engine = engine
        self.prediction = prediction
        self.learning_loop = learning_loop
        self.attention_policy = attention_policy
        self.state = "active"            # active | paused | standby
        self.cycle_count = 0
        self.standby_rounds = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._protocol_dormant = False   # 4.10 节协议休眠标记（DEVIATION-004）
        self.cycle_log: List[Dict] = []

    # ==================== 生命周期一步（七相工程映射） ====================

    def cycle(self) -> Dict:
        """一步生命周期：
        perceive（存在威胁感知→需求确认→生存评估）→ curiosity（好奇）→
        reduce_gap（缩小信息差：预测×盲区联动）→ 信任评估 → 协作确认 →
        consolidate（巩固）→ standby 判定（终裁检查点）"""
        report = {"cycle": self.cycle_count, "state": self.state}

        # 1. perceive：存在威胁感知 → 需求确认 → 生存评估（降级路径 D-001）
        crisis = self._perceive()
        report["perceive"] = crisis
        if crisis["level"] == "P0":
            # 终裁检查点1：P0 危机暂停自动机，等待维生系统终裁
            self.state = "paused"
            report["checkpoint"] = "P0_crisis_pause"
            report["note"] = "等待维生系统终裁（30 秒无响应 → P0 默认保护 3.4 节）"
            return report

        # 1.5 自主盲区发现（v1.15）：每 SCAN_INTERVAL 轮扫描行为数据 → 注册新盲区
        # 信号：查询弱命中 / 被拒路径重复 / 知识稀疏 / 信息差停滞（scan_blindspots）
        scan_result = {"scanned": 0, "registered": 0}
        if self.cycle_count % self.SCAN_INTERVAL == 0:
            try:
                from scan_blindspots import BlindspotScanner
                scanner = BlindspotScanner(self.engine)
                sr = scanner.scan(limit=2, dry_run=False)
                scan_result = {"scanned": sr.get("scanned", 0),
                               "registered": len(sr.get("registered", []))}
                if sr.get("registered"):
                    self.engine.add_perception(
                        f"[自主盲区发现] 注册 {len(sr['registered'])} 个新盲区："
                        + "、".join(r["code"] for r in sr["registered"]),
                        importance=0.6, tags=["观测层", "blindspot_scan", "self_discovery"])
            except Exception:
                pass
        report["blindspot_scan"] = scan_result

        # 2. curiosity：好奇（开放盲区高优先 or 预测缺口）
        target = self._curiosity()
        report["curiosity"] = {"target": target["code"] if target else None,
                               "has_target": target is not None}

        # 3. reduce_gap：缩小信息差（预测×盲区深度联动）
        gap_result = self._reduce_gap(target)
        report["reduce_gap"] = gap_result

        # 信任评估（2.9 节 T_total 复核 · 降级路径）
        trust = self.engine.self_model.trust_state.get("t_total", 0.0)
        report["trust_assessment"] = {"t_total": trust}

        # 4. consolidate：巩固
        try:
            report["consolidate"] = self.engine.consolidate_cycle()
        except Exception:
            report["consolidate"] = {}

        # 4.5 睡眠巩固·记忆衰减（v1.16）：每 MAINT_INTERVAL 轮执行一次
        # 「短期记忆自动减少权重」——CONTEXT 情境层 importance 指数衰减 +
        # 未验证边置信度衰减（decay_cycle），锚点/结构层不可遗忘。
        # 与 consolidate 同属「睡眠巩固」语义（P1-4：衰减+巩固+归纳）。
        decay_result = {"decayed": 0, "note": "未到期"}
        if self.cycle_count % self.MAINT_INTERVAL == 0:
            try:
                self.engine.decay_cycle(factor=0.02, min_confidence=0.1)
                # 主动遗忘决策器（v1.16 · J 维进化）：未被使用的记忆归档
                try:
                    fa = self.engine.forget_advisor()
                    decay_result = {"decayed": 1,
                                    "forget_advisor": fa,
                                    "note": "记忆衰减周期：CONTEXT 短期记忆降权 + 主动遗忘归档"}
                except Exception as _fa_e:
                    decay_result = {"decayed": 1,
                                    "note": f"记忆衰减周期（forget_advisor 异常: {_fa_e}）"}
            except Exception:
                decay_result = {"decayed": 0, "note": "衰减执行异常"}
            # 因果候选发现 + 验证（v1.16 · R 维进化：条件论对自身）
            # 发现：被拒路径/预测未命中 → 因果候选（存观测层）
            # 验证：候选对应被拒路径 consumed → 因果确认（物理基底校准）
            try:
                from causal_discover import CausalDiscoverer
                cd = CausalDiscoverer(self.engine)
                disc = cd.discover(limit=3, persist=True)
                ver = cd.verify_candidates()
                decay_result["causal_discover"] = {
                    "new_candidates": len(disc.get("candidates", [])),
                    "verify": ver}
            except Exception as _cd_e:
                decay_result["causal_discover"] = {"error": str(_cd_e)[:60]}
        report["memory_decay"] = decay_result

        # 5. standby 判定（终裁检查点2：暂停提交复核）
        if self._should_standby():
            self.state = "standby_pending"
            report["checkpoint"] = "standby_pending_review"
            report["note"] = "收敛判定：提交验证单元复核 + 维生系统确认（防假收敛 盲区28）"

        self.cycle_count += 1
        self.cycle_log.append(report)
        return report

    # ==================== 阶段实现 ====================

    def _perceive(self) -> Dict:
        """存在威胁感知（1.10 第一相）→ 需求确认 → 生存评估"""
        trend = {"current": 0.0, "trend": "insufficient"}
        try:
            trend = self.engine.get_gap_trend(window=10)
        except Exception:
            pass
        d_norm = trend.get("current") or 0.0
        level = "normal"
        if d_norm > self.P0_CRISIS_THRESHOLD:
            level = "P0"
        elif d_norm > 0.7:
            level = "P1"
        elif d_norm > 0.5:
            level = "P2"
        escalations = 0
        try:
            escalations = len(self.engine.check_escalation("deviation", d_norm))
        except Exception:
            pass
        return {"level": level, "d_norm": round(d_norm, 3),
                "trend": trend.get("trend"), "escalations": escalations}

    def _curiosity(self) -> Optional[Dict]:
        """好奇：开放盲区（高优先）"""
        if self.learning_loop is None:
            return None
        try:
            return self.learning_loop.get_next_candidate()
        except Exception:
            return None

    def _reduce_gap(self, target: Optional[Dict]) -> Dict:
        """缩小信息差：预测×盲区深度联动（learn_next(use_prediction=True)）"""
        if target is None or self.learning_loop is None:
            return {"action": "none", "reason": "no_target"}
        try:
            lr = self.learning_loop.learn_next(use_prediction=True)
            return {"action": "learn_next", "status": lr.get("status"),
                    "predicted_routes": lr.get("predicted_routes", 0)}
        except Exception as e:
            return {"action": "failed", "error": str(e)[:60]}

    def _should_standby(self) -> bool:
        """收敛判定（盲区28 可操作条件：D_norm 收敛 + 无高优先盲区持续 N 轮）"""
        try:
            trend = self.engine.get_gap_trend(window=10)
            if trend.get("trend") in ("narrowing", "stable"):
                self.standby_rounds += 1
            else:
                self.standby_rounds = 0
        except Exception:
            self.standby_rounds = 0
        high = 0
        try:
            high = len([b for b in self.engine.list_blindspots(status="open")
                        if b.get("severity") == "high"])
        except Exception:
            pass
        return self.standby_rounds >= self.STANDBY_REQUIRED_ROUNDS and high == 0

    # ==================== 终裁检查点（DEVIATION-002） ====================

    def resolve_crisis(self, directive: str) -> Dict:
        """终裁检查点1：维生系统 P0 终裁指令"""
        if directive in ("protect", "freeze", "rollback"):
            self.state = "paused"
        elif directive in ("continue", "normal"):
            self.state = "active"
        elif directive == "emergency_sleep":
            self.state = "standby"
        return {"state": self.state, "directive": directive}

    def confirm_standby(self, approved: bool) -> Dict:
        """终裁检查点2：验证单元复核 + 维生系统确认后进入 standby"""
        if approved:
            self.state = "standby"
            self.standby_rounds = 0
            return {"status": "standby", "engine": "low_power"}
        self.state = "active"
        self.standby_rounds = 0
        return {"status": "active", "note": "standby 被否决（防假收敛 盲区28）"}

    # ==================== 状态控制（DEVIATION-004 概念分离） ====================

    def enter_standby(self) -> Dict:
        """工程低功耗待机（不等同于 4.10 节协议休眠）"""
        if self._protocol_dormant:
            self.stop_lifecycle(source="protocol_dormant")
            return {"status": "protocol_dormant_priority", "engine": "stopped"}
        self.state = "standby"
        return {"status": "standby"}

    def wake(self) -> Dict:
        """唤醒：危机信号/外部指令/新盲区"""
        self.state = "active"
        self.standby_rounds = 0
        try:
            self.engine.add_perception("[lifecycle] 唤醒事件", importance=0.4,
                                       tags=["lifecycle", "wake"])
        except Exception:
            pass
        return {"status": "active"}

    # ==================== 自发运行（DEVIATION-002 中断权） ====================

    def start_lifecycle(self, interval: float = 60.0) -> Dict:
        """启动后台自发循环（终裁检查点内运行；paused/standby 时跳过）"""
        if self._running:
            return {"status": "already_running"}
        self._running = True

        def loop():
            while self._running:
                time.sleep(interval)
                if self.state in ("paused", "standby", "standby_pending"):
                    continue
                try:
                    self.cycle()
                except Exception:
                    pass

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        return {"status": "running", "interval": interval}

    def stop_lifecycle(self, source: str) -> Dict:
        """中断自发循环。中断权优先级：维生系统 > 验证单元 > 用户 > 实例自身。
        外部中断须立即生效，不等待当前 cycle 完成。"""
        self._running = False
        if source == "protocol_dormant":
            self._protocol_dormant = True
        return {"status": "stopped", "source": source}

    def set_protocol_dormant(self, dormant: bool):
        """4.10 节协议休眠状态标记（协议休眠优先于工程待机）"""
        self._protocol_dormant = dormant
        if dormant:
            self.stop_lifecycle(source="protocol_dormant")
