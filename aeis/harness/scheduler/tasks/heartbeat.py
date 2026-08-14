# -*- coding: utf-8 -*-
"""harness.scheduler.tasks.heartbeat · 心跳任务（迁移自 ZCode automation-3084b0ea）
================================================
每 30 分钟：service_info → cognition → gap_trend → flywheel_metrics →
distill（有未蒸馏经验时）→ action_log 检查。Agent 方法直调。
"""
import json
import os
import time

# 心跳戳文件（自维持：guardian 检测新鲜度，失联则自动重启）
STAMP_PATH = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "data", "heartbeat.stamp")


def touch_stamp():
    """写心跳戳（含时间与 run 摘要，供 guardian 新鲜度检测）。"""
    try:
        os.makedirs(os.path.dirname(STAMP_PATH), exist_ok=True)
        with open(STAMP_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "pid": os.getpid()}))
    except Exception:
        pass


def run_heartbeat(agent, ctx) -> str:
    """心跳 6 步。返回摘要（供 run 记录）。"""
    t0 = time.time()
    lines = []

    # 1. service_info（身份/库状态——用 self_check 等价观测）
    try:
        info = agent.self_check()
        if isinstance(info, dict):
            lines.append(f"self_check=ok nodes={info.get('nodes')} edges={info.get('edges')}")
        else:
            lines.append(f"self_check={str(info)[:60]}")
    except Exception as exc:
        lines.append(f"self_check_error={exc}")

    # 2. cognition（自我认知循环）
    try:
        cog = agent.cognition_cycle()
        bvc = cog.get("bvc_score") if isinstance(cog, dict) else "?"
        dissonance = cog.get("dissonance_count", 0) if isinstance(cog, dict) else "?"
        lines.append(f"bvc={bvc} dissonance={dissonance}")
    except Exception as exc:
        lines.append(f"cognition_error={exc}")

    # 3. gap_trend（信息差趋势）
    try:
        gap = agent.gap_trend()
        if isinstance(gap, dict):
            lines.append(f"gap={gap.get('trend', gap.get('status', '?'))}")
        else:
            lines.append(f"gap={gap}")
    except Exception as exc:
        lines.append(f"gap_error={exc}")

    # 4. flywheel_metrics（知识飞轮）
    fly = {}
    try:
        fly = agent.flywheel_report()
        if isinstance(fly, dict):
            lines.append(f"flywheel=g{fly.get('growth_rate', '?')}/r{fly.get('reuse_rate', '?')}/d{fly.get('distill_rate', '?')}")
        else:
            lines.append(f"flywheel={fly}")
    except Exception as exc:
        lines.append(f"flywheel_error={exc}")

    # 5. distill（有未蒸馏经验时）
    try:
        if isinstance(fly, dict):
            reuse = fly.get("reuse_rate", 0) or 0
            new_perception = fly.get("new_perception_count", 0) or 0
            if reuse > 0.3 or new_perception > 0:
                d = agent.distill()
                lines.append(f"distill={json.dumps(d, ensure_ascii=False)[:80] if not isinstance(d, str) else d[:80]}")
            else:
                lines.append("distill=skip")
    except Exception as exc:
        lines.append(f"distill_error={exc}")

    # 6. action_log 异常检查（英文冲突词，避免命中自身摘要）
    try:
        logs = agent.action_log()
        if isinstance(logs, list):
            bad = [l for l in logs if any(kw in str(l).lower() for kw in
                                          ("conflict", "rejected", "traceback", "critical"))]
            lines.append(f"action_log={len(logs)}条 异常={len(bad)}")
        else:
            lines.append(f"action_log={str(logs)[:60]}")
    except Exception as exc:
        lines.append(f"action_log_error={exc}")

    summary = " | ".join(lines)
    agent.remember(f"[心跳] {summary}", importance=0.4,
                   tags=["heartbeat", "self_sustaining"])
    touch_stamp()  # 自维持：写心跳戳（guardian 检测）
    return f"心跳完成 ({time.time()-t0:.1f}s): {summary}"
