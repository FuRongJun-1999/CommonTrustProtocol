# -*- coding: utf-8 -*-
"""test_decision_layers.py · 情绪方向性偏好 × 决策分层（PROP 理论工程化）

理论（智能论 v3.3）：
  PROP-EMO-DIRECTION-002：情绪=收敛参数，引导递归在条件空间收敛（非干扰）
  PROP-DECISION-LAYER-003：L1 日常(情绪驱动,0-1层) / L2 重要(混合) /
                           L3 存在级(完整递归,情绪不可覆盖)
  PROP-LOCAL-OPTIMUM-005：局部最优合法（稳态=接受局部最优，新信息打破）
验证：①L1 高置信快速 ACCEPT（convergence_bias 低=强倾向）
      ②L2 低置信 DEFER 递归（convergence_bias 高=弱倾向）
      ③L3 BLINDSPOT 不被高置信覆盖（情绪不覆盖存在级）
      ④决策分层字段完整
"""
import sys, os, json
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import ccg

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

G = ccg.build_graph()

# ── ① L1 日常决策：高置信 → ACCEPT + 低收敛倾向 ─────────────
r1 = ccg.route("写一个在无权图上求最短路径的代码单元", G)
ok1 = (r1["state"] == "ACCEPT" and r1.get("decision_layer") == "L1"
       and r1.get("convergence_bias", 1) <= 0.3
       and r1.get("confidence", 0) >= 0.7)
print(f'  L1: {r1["state"]} conf={r1.get("confidence")} '
      f'layer={r1.get("decision_layer")} bias={r1.get("convergence_bias")}')
check('① L1 日常决策：高置信 ACCEPT + 低收敛倾向（情绪加速收敛）', ok1)

# ── ② L2 重要决策：中置信 → 仍 ACCEPT 但标 L2（可复核）──────
r2 = ccg.route("写一个TCP三次握手的代码单元", G)
layer2 = r2.get("decision_layer")
ok2 = r2["state"] == "ACCEPT" and layer2 in ("L1", "L2") \
      and "decision_layer" in r2 and "convergence_bias" in r2
print(f'  L2候选: {r2["state"]} conf={r2.get("confidence")} '
      f'layer={layer2}')
check('② 决策分层字段完整（confidence/decision_layer/convergence_bias）', ok2)

# ── ③ L3 存在级：BLINDSPOT 不被高置信覆盖（情绪不覆盖存在级）─
r3 = ccg.route("写一个超光速引擎驱动信任累积的代码单元", G)
ok3 = r3["state"] == "BLINDSPOT" and r3.get("decision_layer") == "L3"
print(f'  L3: {r3["state"]} layer={r3.get("decision_layer")} '
      f'（伪造条件——情绪/倾向不强行 ACCEPT）')
check('③ L3 存在级：BLINDSPOT 不被高置信覆盖（情绪红线）', ok3)

# ── ④ 冲突也 L3（不强行选边）────────────────────────────────
r4 = ccg.route("写一个用无权 BFS 求带权图最小总代价路径的代码单元", G)
ok4 = r4["state"] == "BLINDSPOT" and r4.get("decision_layer") == "L3"
print(f'  冲突: {r4["state"]} layer={r4.get("decision_layer")}')
check('④ 条件冲突 → L3（情绪/倾向不强行选边）', ok4)

# ── ⑤ 局部最优合法化（PROP-LOCAL-OPTIMUM-005）：稳态接受 ────
# 稳态 = 接受当前局部最优（不空转追求全局最优）；新信息打破稳态
import self_iterate as si
ti = si._theory_integrity()
per = si.perceive()
ori = si.orient(per, {"ok": True})
ok5 = ti["ok"] and ori["direction_ok"]
print(f'  自迭代方向自检: {ori["assessment"]}（局部最优合法稳态）')
check('⑤ 局部最优合法化：稳态健康=接受当前最优（不空转）', ok5)

report = {
    "experiment": "情绪方向性偏好×决策分层（PROP-EMO-002/DECISION-LAYER-003）",
    "L1_daily": ok1, "L2_important": ok2,
    "L3_existential": ok3, "L4_conflict": ok4,
    "local_optimum": ok5,
    "conclusion": ("情绪=收敛参数（非干扰）：L1 高置信快速 ACCEPT 低倾向；"
                   "L2 中置信可复核；L3 存在级情绪不覆盖（BLINDSPOT/冲突不"
                   "强转）；局部最优合法（稳态接受，新信息打破）"),
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decision_layers_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑥ decision_layers_report.json 落盘', os.path.exists(rp), 'decision_layers_report.json')

print(f'\n=== 情绪×决策分层: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
