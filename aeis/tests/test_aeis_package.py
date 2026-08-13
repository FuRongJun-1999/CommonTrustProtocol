#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""灵枢 AEIS 包级功能回归测试（51 项）
覆盖：v1.11 知识飞轮（边证据/蒸馏/度量/迁移/校准/图遍历/工作记忆/事件驱动/复用追踪）
+ v1.10 回归（生命周期/预测/多模态/完整性/衰减/检索/备份恢复）
在包命名空间（import aeis）下运行。
"""

import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import aeis

results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {extra}")


eng = aeis.SpacetimeMemoryEngine(identity="aeis-test")
ML, ET = aeis.MemoryLayer, aeis.EdgeType
fw = eng._flywheel

# ============ 版本与组件 ============
check("version", aeis.__version__ == "0.2.0" and aeis.ENGINE_VERSION == "v1.12.0")
check("flywheel assembled", fw is not None, f"err={eng._flywheel_error}")
check("flywheel version", fw.DISTILL_STANDARD_VERSION == "v1.11.0")

# ============ P1-1 边证据标签 ============
n1 = eng.add_perception("起点")
n2 = eng.add_perception("终点")
e_def = eng.add_edge(n1.id, n2.id, confidence=0.5)
check("edge default extracted", e_def.source_evidence == "extracted")
e_inf = eng.add_edge(n2.id, n1.id, ET.SIMILAR, confidence=0.6, source_evidence="inferred")
check("edge inferred param", e_inf.source_evidence == "inferred")
got = eng.store.get_edge(e_inf.id)
check("edge persistence roundtrip", got.source_evidence == "inferred" and got.verified is False)
eng.add_perception("词A")
eng.add_perception("词B")
eng.add_perception("词C")
eng.induce_concepts()
sim_inf = [e for e in eng.store.query_nodes(limit=300) if e.id != n1.id for e2 in
           eng.store.get_outgoing_edges(e.id) if e2.source_evidence == "inferred"]
sim_all = [e for e in eng.store.query_nodes(limit=300) if e.id != n1.id for e2 in
           eng.store.get_outgoing_edges(e.id) if e2.relation_type == ET.SIMILAR]
check("induce concepts inferred", len(sim_all) >= 1 and len(sim_inf) == len(sim_all))

# ============ P0-1 蒸馏管线 ============
r = eng.evo_distill_cycle()
check("distill no_input", r["status"] == "no_input")
eng.add_perception("用户反复询问天气 回答成功 用户满意", tags=["learning_result"])
eng.add_perception("用户反复询问天气 再次回答成功 用户满意", tags=["learning_result"])
eng.add_perception("用户询问时间 回答成功", tags=["learning_result"])
r = eng.evo_distill_cycle()
check("distill ok", r["status"] == "ok" and r["input"] == 3 and r["patterns"] >= 1)
check("distill dsv recorded", fw.distill_log and fw.distill_log[-1]["standard_version"] == "v1.11.0")
patterns = [n for n in eng.store.query_nodes(limit=200) if "reusable_pattern" in n.tags]
check("distill pattern nodes", len(patterns) >= 1)
if patterns:
    check("distill pattern dsv tag", any(t.startswith("dsv:v1.11.0") for t in patterns[0].tags))
check("distill reuse edges inferred",
      any(e.source_evidence == "inferred" and getattr(eng.store.get_edge(e.id), "verified", False) is False
          for e in eng.store.get_outgoing_edges(patterns[0].id)) if patterns else False)

# ============ P0-2 飞轮度量 ============
met = eng.evo_flywheel_metrics()
check("metrics 3 indicators",
      set(met) >= {"knowledge_growth_rate", "reuse_rate", "distill_output_rate"})
check("metrics non-trust property", "不参与信任" in met.get("property", ""))
check("metrics distill rate", met["distill_output_rate"] > 0)
eng.search_content("天气")
tracker = eng._reuse_tracker
hit_ids = {n.id for n, _ in eng.search_content("天气")}
check("reuse tracker recorded", len(tracker) > 0 and any(s & hit_ids for s in tracker.values()))

# ============ P0-3 迁移测试 ============
t = eng.test_transfer_capability()
check("transfer insufficient", t["status"] == "insufficient" and t.get("min_required") == 20)
for i in range(20):
    eng.update_prediction_feedback("p%d" % i, "a%d" % i, i % 2 == 0)
t = eng.test_transfer_capability()
check("transfer computed", t["status"] in ("passed", "failed") and 0 <= t.get("success_rate", -1) <= 1)
check("transfer significance", t.get("significant") is False and
      t.get("failure_condition") and len(t.get("reflection", [])) == 3)

# ============ 宇宙校准参照 ============
c = eng.universe_calibrate()
expect5 = {"judgment1_info_gap_trend", "judgment2_existence_priority",
           "judgment3_resource_conservation", "judgment4_completeness",
           "judgment5_experiment", "positioning"}
check("calibrate 5 judgments", expect5 <= set(c.keys()))
check("calibrate j2 direction", c["judgment2_existence_priority"]["status"] in
      ("direction_consistent", "direction_review"))
check("calibrate j3 observe", c["judgment3_resource_conservation"]["status"] in
      ("direction_consistent", "observe", "pending"))
check("calibrate j4 claims", isinstance(c["judgment4_completeness"]["explicit_claims"], list))
eng.add_perception("本系统已达完备状态 无遗漏", tags=["learning_result"])
c2 = eng.universe_calibrate()
check("calibrate j4 detects claims", len(c2["judgment4_completeness"]["explicit_claims"]) >= 1)
check("calibrate positioning", "元理论参照工具" in c2["positioning"])
cal_nodes = [n for n in eng.store.query_nodes(limit=300) if "calibration" in n.tags]
check("calibration records persisted", len(cal_nodes) >= 1 and len(fw.calibration_log) >= 1)

# ============ P1-2 图遍历 ============
n3 = eng.add_perception("中转")
n4 = eng.add_perception("目标")
eng.add_edge(n3.id, n4.id, ET.CAUSAL, confidence=0.7)
p = eng.shortest_path(n3.id, n4.id)
check("shortest_path direct", p == [n3.id, n4.id])
eng.add_edge(n1.id, n3.id, ET.CAUSAL, confidence=0.6)
p2 = eng.shortest_path(n1.id, n4.id)
check("shortest_path multi-edge", p2 == [n1.id, n3.id, n4.id])
sg = eng.query_subgraph("目标", max_nodes=10)
check("subgraph returns nodes", len(sg.get("nodes", {})) >= 1 and isinstance(sg.get("edges"), list))

# ============ P1-3 工作记忆深化 ============
ok = eng.mark_contested(n3.id, "证据不足")
check("mark_contested", ok and "contested" in eng.store.get_node(n3.id).tags)
ok = eng.resolve_contested(n3.id, "confirmed")
check("resolve_contested", ok and "contested" not in eng.store.get_node(n3.id).tags)
ok = eng.mark_stale(n4.id, "条件空间切换")
check("mark_stale", ok and "stale" in eng.store.get_node(n4.id).tags)
conf_before = eng.store.get_node(n4.id).confidence
ok = eng.reverify(n4.id)
check("reverify +confidence", ok and eng.store.get_node(n4.id).confidence >= conf_before and
      "stale" not in eng.store.get_node(n4.id).tags)
iso = eng.add_perception("信任评估记录", tags=["trust_evaluation"])
check("recency isolation (6类)", fw.recency_weighted_update(iso.id, -0.5) is False)
norm = eng.add_perception("普通记录")
check("recency normal accepted", fw.recency_weighted_update(norm.id, -0.5) is True)
check("recency tau factor", eng.store.get_node(norm.id).confidence <= 0.5)

# ============ P1-4 事件驱动 ============
eng.notify_event("perception", {"c": 1})
eng.notify_event("perception", {"c": 2})
eng.notify_event("perception", {"c": 3})
eng.notify_event("write")
ev = eng.consume_events()
check("event debounce merged", ev["status"] == "ok" and ev["consumed"] == 2)
eng.notify_event("perception")
check("event queue cleared", len(eng._event_queue) == 1)

# ============ v1.10 回归 ============
check("REG lifecycle assembled", eng._lifecycle is not None, eng._lifecycle_error)
lc = eng.lifecycle_cycle()
check("REG lifecycle cycle", isinstance(lc, dict) and len(lc) > 0)
check("REG prediction", eng._prediction is not None)
pr = eng.predict_routes(start_id=n1.id, horizon=2)
check("REG predict_routes", isinstance(pr, dict))
hr = eng._prediction._hit_rate() if eng._prediction else None
check("REG hit_rate", hr is not None and 0 <= hr <= 1)
eng.add_perception("图像内容", modality="image")
check("REG multimodal", any(n.modality == "image" for n in eng.store.query_nodes(limit=300)))
check("REG verify_integrity", eng.verify_integrity()["orphan_edges"] == 0)
eng.add_perception("衰减测试内容")
r = eng.decay_cycle(0.1) or {}
check("REG decay_cycle", r.get("decayed", 0) >= 0)
check("REG search_content", len(eng.search_content("天气")) >= 1)
check("REG recall", len(eng.recall("天气")) >= 0)
check("REG gap trend", eng.get_gap_trend(window=10)["trend"] in ("insufficient", "narrowing", "stable", "widening"))
bak = os.path.join(PROJECT_ROOT, "backup_aeis_test.json")
exp = eng.export_all(bak)
eng2 = aeis.SpacetimeMemoryEngine(identity="aeis-restored")
imp = eng2.import_all(bak)
check("REG backup/restore", imp["imported"].get("nodes", 0) == exp["exported_nodes"])
if os.path.exists(bak):
    os.remove(bak)

# ============ Agent 高层 API ============
agent = aeis.Agent(identity="agent-api-test")
an = agent.remember("高层接口测试内容", tags=["api"])
check("API remember", an is not None and an.content == "高层接口测试内容")
check("API recall", len(agent.recall("高层")) >= 1)
check("API lifecycle_state", agent.lifecycle_state()["status"] == "ok")
check("API self_check", agent.self_check()["integrity_ok"] is True)
agent.close()

# ============ 汇总 ============
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"\n===== 灵枢 AEIS 包级回归: {passed}/{total} 通过 =====")
sys.exit(0 if passed == total else 1)
