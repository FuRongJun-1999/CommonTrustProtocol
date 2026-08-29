# -*- coding: utf-8 -*-
"""test_dual_agent_nodes.py · 双智能体蜂群化验证（2026-08-29）

- 反思/验证分置两节点（经总线异步），闭环 accepted
- fail 路径：错误候选被裁决 → 证据回反思 → 修正后通过
- 双节点 ADOPTED 登记
"""
import sys, os, shutil, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dual_agent_nodes import run_dual_node_session

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


tmp = tempfile.mkdtemp(prefix="dan_")
try:
    task = {"arr": [4, 2, 3, 1]}
    truth = sorted(task["arr"])

    # 正路：反思直接产出正确候选
    r1 = run_dual_node_session(os.path.join(tmp, "s1"), task,
                               propose=lambda t, rnd, fail: sorted(t["arr"]),
                               judge=lambda c: (c == truth, f"重算 {truth} vs {c}"))
    check("双节点闭环 accepted", r1["status"] == "accepted" and r1["answer"] == truth, str(r1)[:80])
    check("双节点 ADOPTED 事件", any(e["stage"] == "adopted" for e in r1["events"]))

    # fail 路径：首轮错候选 → 裁决 fail → 次轮修正
    calls = {"n": 0}
    def propose_then_fix(t, rnd, fail):
        calls["n"] += 1
        return [99, 1] if rnd == 1 else truth
    r2 = run_dual_node_session(os.path.join(tmp, "s2"), task,
                               propose=propose_then_fix,
                               judge=lambda c: (c == truth, f"重算 {truth} vs {c}"))
    check("fail 后修正通过", r2["status"] == "accepted" and r2["rounds"] == 2, str(r2)[:80])
    check("fail 证据回传反思节点", any(e["stage"] == "verdict" and not e["pass"]
                                    for e in r2["events"]))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"双智能体蜂群化验证: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
