#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_jacobian_agent.py · Agent 影响雅可比接入测试（条件代数工程化）
① influence_jacobian：语义时空图 → 雅可比矩阵（因果边=∂y/∂x）
② jacobian_chain：链式法则传播（A→B→C = 0.9×0.85 = 0.765）
③ 与 predict_routes 一致性（图路径传播）"""
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

agent = Agent(identity="jacobian-test", db_path=":memory:")

# 构造因果链：A → B(0.9) → C(0.85)（信息差→反思→候选）
n_a = agent.remember("信息差缩小驱动智能增长", importance=0.8)
n_b = agent.remember("预测误差触发反思", importance=0.8)
n_c = agent.remember("被拒路径进入候选验证", importance=0.8)
agent.relate(n_a.id, n_b.id, relation="causal", confidence=0.9)
agent.relate(n_b.id, n_c.id, relation="causal", confidence=0.85)

# ① 影响雅可比
try:
    J, ids = agent.influence_jacobian()
    check("① influence_jacobian 构建", J is not None and len(ids) >= 3,
          f"节点 {len(ids)}")
    # A→B 边 = ∂B/∂A = 0.9
    if J is not None:
        val = float(J[ids.index(n_b.id), ids.index(n_a.id)])
        check("①b 雅可比 ∂B/∂A = 0.9（因果边置信=偏导）",
              abs(val - 0.9) < 1e-4, str(val))
except Exception as e:
    check("① influence_jacobian", False, f"异常: {e}")

# ② 链式法则传播
try:
    chain = agent.jacobian_chain(n_a.id, n_c.id, steps=2)
    check("② 链式法则 jacobian_chain(A→C, 2步) = 0.765",
          abs(chain - 0.765) < 1e-3, f"{chain:.4f}")
except Exception as e:
    check("② 链式法则", False, f"异常: {e}")

# ③ 与 predict_routes 一致（条件路由 = 雅可比路径）
try:
    pr = agent.predict_routes(start_id=n_a.id, horizon=3)
    routes = pr.get("routes", [])
    path_c = [r for r in routes if n_c.id in r["path"]]
    # 雅可比链 0.765 应对应 A→B→C 路径的置信度乘积
    jac = agent.jacobian_chain(n_a.id, n_c.id, steps=2)
    check("③ 雅可比链 = 预测路径传播（条件路由一致性）",
          len(path_c) >= 1 and jac > 0.7,
          f"雅可比={jac:.3f} 路径数={len(routes)}")
except Exception as e:
    check("③ 与 predict_routes 一致", False, f"异常: {e}")

print(f"\n=== 影响雅可比接入测试: {PASS}/{TOTAL} 通过 ===")
sys.exit(0 if PASS == TOTAL else 1)
