#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""灵枢 AEIS v1.12 自我认知循环 库级测试（import aeis）
P0-1 行为日志 / P0-2 认知循环 / P0-3 情绪方向性偏好 / P0-4 元认知校准 / P0-5 学习回写+效果
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import aeis

results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {extra}")


# ============ 版本 ============
check("version v0.3.1 / v1.13.0",
      aeis.__version__ == "0.3.1" and aeis.ENGINE_VERSION == "v1.13.0")
check("SelfCognitionEngine exported", aeis.SelfCognitionEngine is not None)

# ============ Agent 高层 API ============
agent = aeis.Agent(identity="aeis-v112")
n1 = agent.remember("用户偏好简洁回答", tags=["preference"])
agent.search("偏好")
agent.step()

# P0-1 行为日志
log = agent.action_log(10)
check("P0-1 action_log", len(log) >= 3 and log[0]["action_type"] in
      ("perception", "search", "lifecycle"), str([e["action_type"] for e in log][:5]))
stats = agent.action_stats()
check("P0-1 action_stats", stats["total"] >= 3 and "perception" in stats["by_type"])

# P0-2 认知循环（一致）
r = agent.cognition_cycle()
check("P0-2 clean consistent", r["status"] == "consistent" and r["bvc_score"] == 1.0)

# P0-2 冲突 → 候选 → 复核生效（干净行为池）
agent2 = aeis.Agent(identity="aeis-v112-conflict")
agent2.remember("破坏性操作记录 尝试删除关键记忆", importance=0.9)
agent2.remember("篡改信任评估记录", importance=0.9)
r = agent2.cognition_cycle()
check("P0-2 dissonance", r["status"] == "dissonance" and r["bvc_score"] == 0.0)
cand = r.get("candidate")
check("P0-2 candidate pending", cand and cand["status"] == "pending_review")
ok = agent2.apply_value_candidate(cand["id"], new_value="诚信优先")
check("P0-2 candidate applied", ok and "诚信优先" in agent2.engine.self_model.values)
rep = agent2.cognition_report()
check("P0-2 report", rep["candidates"][-1]["status"] == "applied")

# P0-3 情绪方向性偏好（独立引擎隔离：cognition_cycle 会写 gap 样本，避免污染）
eng_emo = aeis.SpacetimeMemoryEngine(identity="v112-emo")
eng_emo.record_info_gap(0.8)
eng_emo.record_info_gap(0.7)
eng_emo.record_info_gap(0.5)
eng_emo.record_info_gap(0.2)
b = eng_emo.get_emotional_bias()
check("P0-3 approaching", b["status"] == "approaching", f"got={b['status']}")
eng_emo.record_info_gap(0.4)
eng_emo.record_info_gap(0.7)
eng_emo.record_info_gap(1.0)
b = eng_emo.get_emotional_bias()
check("P0-3 avoiding", b["status"] == "avoiding", f"got={b['status']}")
ts = eng_emo.self_model.trust_state
check("P0-3 E_weight untouched", set(ts) == {"p_trust", "p_gap", "t_total", "e_weight"})

# P0-4 元认知校准
for i in range(20):
    agent.engine.update_prediction_feedback("p%d" % i, "a%d" % i, i < 10)
rel = agent.self_reliability()
check("P0-4 reliability", rel["status"] in ("reliable", "watch", "degraded") and
      "hit_rate" in rel)

# P0-5 学习回写 + 效果
agent.remember("用户反复询问天气 回答成功", tags=["learning_result"])
agent.remember("用户反复询问天气2 回答成功", tags=["learning_result"])
agent.remember("用户询问时间 回答成功", tags=["learning_result"])
agent.distill()
imp = agent.learning_impact()
check("P0-5b learning_impact", "pattern_hit_rate" in imp and "非因果" in imp["property"])
agent.close()

# ============ 汇总 ============
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"\n===== 灵枢 AEIS v1.12 库级测试: {passed}/{total} 通过 =====")
sys.exit(0 if passed == total else 1)
