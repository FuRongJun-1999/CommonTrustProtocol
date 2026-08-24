#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_condition_nodes.py · 条件节点化验证（GPT 审查·第二优先级 v1）
① declare_condition：条件成为独立节点（可检索）
② apply_condition：条件→知识 applies_to 边（条件路由到知识）
③ promote_condition：预测误差 condition_candidate → 正式条件节点
④ 全链路：误差→candidate→提升→适用（条件可学习的认知对象）"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aeis'))
from aeis.api import Agent
from aeis.core import EdgeType, ConditionSpace

PASS = 0
TOTAL = 0

def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    print(f'[{"✓" if cond else "✘"}] {name}{" — " + detail if detail else ""}')

agent = Agent(identity="cond-node", db_path=":memory:")

# ① 声明条件节点
try:
    c1 = agent.declare_condition("气压低", existence_constraint="海拔高（如高原）时")
    conds = agent.conditions()
    check("① 条件成为独立节点（declare_condition + conditions 检索）",
          len(conds) >= 1 and any("气压低" in (n.content or "") for n in conds),
          f"{len(conds)} 个条件节点")
    # 条件节点携带条件空间（存在约束）
    n = agent.engine.store.get_node(c1.id)
    cs_ok = n is not None and n.condition_space is not None \
        and "海拔高" in (n.condition_space.existence_constraint or "")
    check("①b 条件节点携带存在约束（条件空间）", cs_ok)
except Exception as e:
    check("① 声明条件节点", False, f"异常: {e}")

# ② 条件→知识 applies_to 边
try:
    k = agent.remember("沸点随气压变化：气压低沸点低", importance=0.8)
    e = agent.apply_condition(c1.id, k.id)
    edges = agent.engine.store.get_outgoing_edges(c1.id)
    ok = any(ed.relation_type == EdgeType.APPLIES_TO and ed.target_id == k.id
             for ed in edges)
    check("② 条件→知识 applies_to 边（条件路由到适用知识）", ok,
          f"{len(edges)} 条出边")
except Exception as e:
    check("② applies_to 边", False, f"异常: {e}")

# ③ 预测误差 candidate → 正式条件节点
try:
    n_pred = agent.remember("高原水沸点预测为100°C", importance=0.8)
    n_actual = agent.remember(
        "高原水沸点实际约88°C", importance=0.8,
        condition_space=ConditionSpace(
            observation_position="高原观测位", observation_tool="温度计",
            time_window=(0.0, 0.0), existence_constraint="气压低时"))
    agent.prediction_feedback(predicted_node_id=n_pred.id,
                              actual_node_id=n_actual.id, hit=False)
    cands = agent.engine.store.get_nodes_by_tag("condition_candidate", limit=10)
    check("③a 误差→条件候选节点", len(cands) >= 1, f"{len(cands)} 个")
    if cands:
        promoted = agent.promote_condition(cands[0].id)
        tags = promoted.tags or []
        check("③b 候选提升为正式条件（condition_verified）",
              "condition_verified" in tags and "condition" in tags,
              str(tags[:5]))
except Exception as e:
    check("③ 候选提升", False, f"异常: {e}")

# ④ 全链路：误差→candidate→提升→适用
try:
    total_conds = len(agent.conditions())
    check("④ 条件成为可学习的认知对象（误差→提升→可检索）",
          total_conds >= 2, f"{total_conds} 个条件节点")
except Exception as e:
    check("④ 全链路", False, f"异常: {e}")

print(f"\n=== 条件节点化验证: {PASS}/{TOTAL} 通过 ===")
sys.exit(0 if PASS == TOTAL else 1)
