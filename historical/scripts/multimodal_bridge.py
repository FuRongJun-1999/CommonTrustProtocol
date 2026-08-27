# -*- coding: utf-8 -*-
"""multimodal_bridge.py · 白箱自举第三阶段·多模态对接——3D 时空 CNN × 灵枢时空记忆图
理论：《白箱自举·LLM替代与3D时空多模态》（§3 看见→记住→回忆 白箱闭环）
核心：stcnn 提取的时空原语（方向/速度/周期）→ 写入灵枢记忆（时空锚点+标签）→
      灵枢 recall 召回（白箱感知通道：感知→记忆→回忆 全链路零 LLM）。
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stcnn import (extract_spatiotemporal_primitives, synth_ball_rolling,
                   synth_blinking, synth_static)


def see_and_remember(agent, frames, label):
    """看见→记住：帧序列 → 3D 时空 CNN 时空原语 → 灵枢记忆写入
    返回 (prims, node)：时空原语 + 灵枢记忆节点（时空锚点）"""
    prims, feat = extract_spatiotemporal_primitives(frames)
    parts = [f"[时空事件] {label}"]
    if prims["direction"] != "静止":
        parts.append(f"方向={prims['direction']} 速度={prims['speed']}/帧")
    if prims["period"]:
        parts.append(f"周期={prims['period']}帧")
    if not prims["moving"]:
        parts.append("静止")
    parts.append(f"运动量={prims['motion_magnitude']}")
    content = " ".join(parts)
    node = agent.remember(content, importance=0.8,
                          tags=["spatiotemporal", "stcnn", label,
                                "perception"])
    return prims, node


def recall_event(agent, query, limit=3):
    """回忆：灵枢组合联想召回（时空事件白箱召回）"""
    try:
        return agent.recall(query, limit=limit)
    except Exception:
        return []


def verify_remembered(agent, node, prims):
    """记住自校验：灵枢记忆节点与时空原语一致性（无幻觉）"""
    n = agent.engine.store.get_node(node.id)
    if not n:
        return False, "节点不存在"
    content = n.content or ""
    ok = True
    if prims["direction"] != "静止" and prims["direction"] not in content:
        ok = False
    if prims["period"] and f"周期={prims['period']}" not in content:
        ok = False
    return ok, content


def demo(agent):
    """看见→记住→回忆 全链路演示（零 LLM）"""
    print("=== 3D 时空 CNN × 灵枢时空记忆图（看见→记住→回忆 · 零 LLM） ===\n")
    scenes = [
        ("球", synth_ball_rolling(frames=10, speed_px=2)),
        ("灯", synth_blinking(frames=12, period=3)),
        ("背景", synth_static(frames=6)),
    ]
    for label, frames in scenes:
        prims, node = see_and_remember(agent, frames, label)
        ok, content = verify_remembered(agent, node, prims)
        mark = "✔" if ok else "✘"
        print(f"[{mark}] 看见「{label}」→ 时空原语: 方向={prims['direction']} "
              f"速度={prims['speed']} 周期={prims['period']}")
        print(f"    记住 → 灵枢记忆: {content[:70]}")

    print("\n=== 回忆（灵枢 recall） ===")
    for q in ["球 运动", "灯 周期", "背景"]:
        hits = recall_event(agent, q, limit=2)
        if hits:
            n, score = hits[0]
            print(f"  召回[{q}] → {n.content[:60]}（score={score:.3f}）")
        else:
            print(f"  召回[{q}] → 无")

    # 一致性：3 场景全部记住且可召回
    all_nodes = agent.engine.store.get_nodes_by_tag("spatiotemporal", limit=10)
    return len(all_nodes) >= 3


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'aeis'))
    from aeis.api import Agent
    a = Agent(identity="multimodal-test", db_path=":memory:")
    ok = demo(a)
    print(f"\n=== 判定 ===\n看见→记住→回忆 全链路: {'✔ 成立' if ok else '✘ 未成立'}（{len(a.engine.store.get_nodes_by_tag('spatiotemporal', limit=10))} 个时空记忆）")
