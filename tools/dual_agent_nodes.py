# -*- coding: utf-8 -*-
"""dual_agent_nodes.py · 最小双智能体蜂群化——反思/验证分置两节点（2026-08-29）

双智能体架构（dual_agent.py）与蜂群协议（M1 总线）合体：
- nodeR（反思节点）：接收任务 → 产出候选 → RESULT 发出
- nodeV（验证节点）：接收候选 → 独立裁决 → VERDICT 回发
- ADOPTED 双方登记（经 memory_hook 可固化知识库）

这是六实例蜂群架构的最小真实运行：两节点各持一认知角色（反思/验证），
经总线完成「任务→候选→裁决→固化」全流程。
"""
from __future__ import annotations

import json
import os
import time


def run_dual_node_session(bus_root: str, task, propose, judge,
                          node_r: str = "nodeR", node_v: str = "nodeV",
                          max_rounds: int = 3, poll_s: float = 0.4,
                          timeout_s: float = 10.0) -> dict:
    """反思/验证双节点会话（经目录总线异步交互）。

    propose(task, round, failing) → 候选（nodeR 认知）
    judge(candidate) → (pass, evidence)（nodeV 独立基底）
    返回：{status, answer/evidence, rounds, events}
    """
    import tempfile
    from swarm_m1 import Bus, Node, make_msg
    bus = Bus(bus_root)
    R = Node(node_r, bus, ["出码"])
    V = Node(node_v, bus, ["裁决"])
    def _judge_handler(candidate):
        ok, ev = judge(candidate)          # V 侧独立基底裁决
        return {"output": candidate, "pass": ok, "evidence": ev}
    V.register_handler("裁决", _judge_handler)
    V.capabilities = ["裁决"]           # 资格白名单同步（handle_bus TASK 检查用）

    events = []
    failing = None
    answer = None
    for rnd in range(1, max_rounds + 1):
        # --- 反思节点：产出候选 → TASK 消息发给验证节点 ---
        candidate = propose(task, rnd, failing)
        events.append({"round": rnd, "stage": "propose", "node": node_r})
        t = make_msg("TASK", node_r, node_v, {"capability": "裁决",
                                              "input": candidate})
        bus.send(t)
        # --- 验证节点：收 TASK → 独立裁决（judge 基底）→ RESULT 回发 ---
        deadline = time.time() + timeout_s
        result = None
        while time.time() < deadline and result is None:
            V.handle_bus()
            for m in bus.recv(node_r):
                if m["type"] == "RESULT" and m.get("reply_to") == t["id"]:
                    result = m["payload"]
            time.sleep(poll_s)
        if result is None:
            return {"status": "timeout", "rounds": rnd, "events": events}
        # --- R 侧裁决收口：采信 V 基底裁决（R 不复裁——自验证不采信的对偶） ---
        out = result.get("output") or {}
        passed = bool(out.get("pass"))
        evidence = out.get("evidence", "")
        vd = make_msg("VERDICT", node_r, node_v,
                      {"pass": passed, "evidence": evidence}, reply_to=t["id"])
        bus.send(vd)
        V.handle_bus()   # V 登记 ADOPTED
        events.append({"round": rnd, "stage": "verdict", "node": node_v,
                       "pass": passed})
        if passed:
            answer = candidate
            R.adopted.append({"verdict_id": vd["id"], "peer": node_v})
            events.append({"round": rnd, "stage": "adopted"})
            return {"status": "accepted", "answer": answer, "rounds": rnd,
                    "evidence": evidence, "events": events}
        failing = evidence   # 失败证据回反思节点
    return {"status": "exhausted", "rounds": max_rounds, "events": events}


def verdict_id_of(verdict_payload):
    return f"vd_{hash(str(verdict_payload)) % 100000:05d}"


if __name__ == "__main__":
    import sys, tempfile
    sys.stdout.reconfigure(encoding="utf-8")
    root = tempfile.mkdtemp(prefix="dual_nodes_")
    task = {"arr": [3, 1, 2]}
    truth = sorted(task["arr"])
    r = run_dual_node_session(
        root, task,
        propose=lambda t, rnd, fail: sorted(t["arr"]),
        judge=lambda c: (c == truth, f"独立重算 {truth} vs 候选 {c}"))
    print(json.dumps(r, ensure_ascii=False)[:250])
    print("双节点会话:", "PASS ✅" if r["status"] == "accepted" else "FAIL")
