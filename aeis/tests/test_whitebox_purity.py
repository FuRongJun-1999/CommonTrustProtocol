#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_whitebox_purity.py · GPT 审查点修改验证
① 蒸馏推导 trace：模式节点 content 内嵌「证据:」摘要（可回滚性）
② predict_routes 门槛收紧：semantic_induced 弱门 0.5→0.8 不破坏主路径
③ 盲区结构性判定 ④ 预测未命中 → 被拒路径（误差→结构）
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aeis'))
from aeis.api import Agent

PASS = 0
TOTAL = 0

def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    print(f'[{"✓" if cond else "✘"}] {name}{" — " + detail if detail else ""}')

agent = Agent(identity="purity-test", db_path=":memory:")

# ============ ① 蒸馏推导 trace ============
# 造学习结果（distill 输入：learning_result 标签节点）
try:
    agent.remember("预测未命中：高原水沸点预测为100°C（实际88°C）",
                   importance=0.8, tags=["learning_result", "prediction"])
    agent.remember("预测未命中：高压锅水沸点预测为100°C（实际120°C）",
                   importance=0.8, tags=["learning_result", "prediction"])
    r = agent.distill()
    created = r.get("created", [])
    trace_ok = False
    for nid in created:
        n = agent.engine.store.get_node(nid)
        if n and "证据:" in (n.content or ""):
            trace_ok = True
            print(f'  模式节点: {n.content[:90]}')
            break
    check("① 蒸馏模式节点内嵌证据 trace（可回滚）", trace_ok,
          f"patterns={r.get('patterns', 0)}")
except Exception as e:
    check("① 蒸馏模式节点内嵌证据 trace", False, f"distill 异常: {e}")

# ============ ② predict_routes 门槛收紧不破坏 ============
try:
    n_a = agent.remember("信息差缩小驱动智能增长", importance=0.8)
    n_b = agent.remember("预测误差触发反思", importance=0.8)
    n_c = agent.remember("被拒路径进入候选验证", importance=0.8)
    from aeis.core import EdgeType
    agent.relate(n_a.id, n_b.id, relation="causal", confidence=0.9)
    agent.relate(n_b.id, n_c.id, relation="causal", confidence=0.9)
    pr = agent.predict_routes(start_id=n_a.id, horizon=3)
    routes = pr.get("routes", [])
    ok = len(routes) >= 1 and any(n_b.id in r["path"] for r in routes)
    check("② predict_routes 因果主路径不受门槛影响", ok, f"{len(routes)} 路线")
    cond_ok = all(r.get("conditions") for r in routes[:3])
    check("②b 路线携带条件空间序列（条件驱动）", cond_ok)
except Exception as e:
    check("② predict_routes 主路径", False, f"异常: {e}")

# ============ ③ 盲区结构性判定 ============
try:
    bs = agent.blindspots()
    check("③ 盲区接口可用（结构性盲区机制）", bs is not None,
          f"{len(bs) if isinstance(bs, list) else bs} 条")
except Exception as e:
    check("③ 盲区接口", False, f"异常: {e}")

# ============ ④ 预测未命中 → 被拒路径（误差→结构） ============
try:
    before = len(agent.engine.store.list_rejected_paths(status="open") or [])
    agent.prediction_feedback(predicted_node_id=n_b.id,
                              actual_node_id=n_c.id, hit=False)
    after = len(agent.engine.store.list_rejected_paths(status="open") or [])
    check("④ 预测未命中 → 被拒路径登记（误差进入结构）", after > before,
          f"{before}→{after}")
except Exception as e:
    check("④ 误差→被拒路径", False, f"异常: {e}")

print(f"\n=== 白箱纯度核查: {PASS}/{TOTAL} 通过 ===")
sys.exit(0 if PASS == TOTAL else 1)
