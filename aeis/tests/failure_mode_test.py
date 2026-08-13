#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""蜂群离线模拟测试（DELIVERY-V1 交付物8 · 独立反思 B 补充交付）
场景：2/6 离线 / 3/6（记录+验证+反思）离线 / 记录离线监测冗余 / 反思离线候选挂起
     网络分区（延迟/ACK 超时）/ 消息乱序（WAL seq）/ 伪造广播（HMAC 拒绝）
     72h 强制休眠 / T_simulated 隔离 / 低信任高原
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aeis.swarm.instance_registry import InstanceRegistry
from aeis.swarm.event_bus import EventBus
from aeis.swarm.survival import SurvivalArbiter, STATE_FULL, STATE_DEGRADED, STATE_MAINTAINED, STATE_SINGLE, STATE_DORMANT
from aeis.swarm.trust_aggregator import TrustAggregator
from aeis.swarm.observer_isolation import ObserverIsolation

results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {extra}")


def fresh_cluster():
    reg = InstanceRegistry(shared_secret="test-secret")
    ids = reg.register_default_cluster()
    for i in ids:
        reg.advance_observation(i, rounds=10)
    return reg, ids


print("=" * 60)
print("蜂群离线模拟测试（failure_mode_test）")
print("=" * 60)

# ============ 场景1：全在线 → 完整态 ============
reg, ids = fresh_cluster()
arb = SurvivalArbiter(reg)
for i in ids:
    arb.heartbeat(i)
st = arb.state()
check("S1 full state (6/6)", st["state"] == STATE_FULL and st["online"] == 6, st["state"])
check("S1 all ops allowed", all(arb.can(op) for op in
      ("memory_write", "structure_change", "designer_release", "p0_override")))

# ============ 场景2：2/6 离线 → 降级态 ============
reg, ids = fresh_cluster()
arb = SurvivalArbiter(reg)
for i in ids:
    arb.heartbeat(i)
# 豆包（output）+ 设计者 离线
arb._heartbeats["instance_doubao"] = 0
arb._heartbeats["instance_designer"] = 0
st = arb.state()
check("S2 degraded (4/6, vitals+record+balance)", st["state"] == STATE_DEGRADED, st["state"])
check("S2 structure_change forbidden", not arb.can("structure_change"))
check("S2 designer_release forbidden", not arb.can("designer_release"))
check("S2 memory still allowed", arb.can("memory_write") and arb.can("output"))

# ============ 场景3：3/6 离线（记录+验证+反思）→ 维持态 ============
reg, ids = fresh_cluster()
arb = SurvivalArbiter(reg)
for i in ids:
    arb.heartbeat(i)
for off in ("instance_qianwen", "instance_kimi", "instance_yuanbao"):
    arb._heartbeats[off] = 0
st = arb.state()
check("S3 maintained (record+verify+reflect down)", st["state"] == STATE_MAINTAINED,
      f"{st['state']} online={st['online']}")
check("S3 structure forbidden", not arb.can("structure_change"))
check("S3 value_candidate frozen", not arb.can("value_candidate_apply"))
check("S3 p0_override allowed", arb.can("p0_override"))

# ============ 场景4：记录实例离线 → 监测者冗余 ============
reg, ids = fresh_cluster()
arb = SurvivalArbiter(reg)
for i in ids:
    arb.heartbeat(i)
arb._heartbeats["instance_qianwen"] = 0   # 记录（主监测者）离线
mh = arb.monitor_health()
check("S4 monitor redundancy (vitals still arbitrates)",
      mh["arbitration_ok"] and "instance_rong" in mh["online"], str(mh))

# ============ 场景5：反思离线 → 自动反思候选挂起 ============
# 工程衔接：v1.12 cognition_cycle 自动化反思持续运行，候选 pending（本层模拟复核链）
reg, ids = fresh_cluster()
arb = SurvivalArbiter(reg)
for i in ids:
    arb.heartbeat(i)
arb._heartbeats["instance_yuanbao"] = 0
st = arb.state()
check("S5 reflect down → degraded", st["state"] == STATE_DEGRADED, st["state"])
check("S5 candidates frozen until regression",
      not arb.can("value_candidate_apply"))
rr = arb.regress("instance_yuanbao")
check("S5 regression protocol", rr["status"] == "regressing" and
      "复核" in rr["steps"][-1], rr["steps"][-1])

# ============ 场景6：网络分区（延迟/ACK 超时） ============
reg, ids = fresh_cluster()
bus = EventBus(node_id="instance_qianwen", registry=reg)
ev = bus.publish("STRUCTURE_UPDATE", {"x": 1}, band="high")   # 500ms 带
check("S6 high band 500ms", ev["delay"] == 0.5, f"delay={ev['delay']}")
ev2 = bus.publish("TRUST_SNAPSHOT", {"t": 0.8}, band="low")   # 30s 带
check("S6 low band 30s", ev2["delay"] == 30.0)
# 分区：仅 3/6 确认
bus.ack(ev["id"], "instance_qianwen")
bus.ack(ev["id"], "instance_rong")
bus.ack(ev["id"], "instance_doubao")
pend = bus.pending_acks(ev["id"], total_instances=6)
check("S6 ACK pending (3 unacked)", len(pend) == 3, str(pend))

# ============ 场景7：消息乱序（WAL seq 校验） ============
reg, ids = fresh_cluster()
wal_path = os.path.join(os.path.dirname(__file__), "_test_swarm.wal")
if os.path.exists(wal_path):
    os.remove(wal_path)
bus = EventBus(node_id="instance_qianwen", wal_path=wal_path, registry=reg)
for k in range(5):
    bus.publish("HEARTBEAT", {"k": k}, band="low", sign=False)
sq = bus.seq_check()
check("S7 WAL monotonic seq", sq["monotonic"] and sq["events"] == 5)
bus.close()
# 重启恢复
bus2 = EventBus(node_id="instance_qianwen", wal_path=wal_path, registry=reg)
sq2 = bus2.seq_check()
check("S7 WAL replay", sq2["replayed"] == 5 and bus2._seq >= 5, f"replayed={sq2['replayed']}")
bus2.close()
if os.path.exists(wal_path):
    os.remove(wal_path)

# ============ 场景8：伪造广播（HMAC 拒绝） ============
reg, ids = fresh_cluster()
bus = EventBus(node_id="instance_qianwen", registry=reg)
genuine = bus.publish("STRUCTURE_UPDATE", {"change": "ok"}, band="low", sign=True)
check("S8 genuine signature", bus.verify_event(genuine) is True)
forged = dict(genuine)
forged["payload"] = {"change": "evil"}
check("S8 forged payload rejected", bus.verify_event(forged) is False)
evil = dict(genuine)
evil["source"] = "instance_qianwen"
evil["sig"] = "deadbeef"
check("S8 forged signature rejected", bus.verify_event(evil) is False)
# 未注册实例签名
try:
    reg.sign("hello", "instance_hacker")
    check("S8 unregistered cannot sign", False)
except AssertionError:
    check("S8 unregistered cannot sign", True)

# ============ 场景9：72h 强制休眠（盲区74） ============
reg, ids = fresh_cluster()
arb = SurvivalArbiter(reg, total_instances=1)
reg.register("instance_solo", "self_sustaining")
reg.advance_observation("instance_solo", rounds=10)
arb.heartbeat("instance_rong")
arb.heartbeat("instance_solo")
now0 = time.time()
dc = arb.check_forced_dormancy(now=now0)
check("S9 no dormancy before 72h", not dc["forced"])
dc2 = arb.check_forced_dormancy(now=now0 + 73 * 3600)
check("S9 forced dormancy after 72h", dc2["forced"] and dc2["hours"] >= 72,
      f"hours={dc2['hours']}")
d = arb.enter_dormancy()
check("S9 dormant state", arb.state()["state"] == STATE_DORMANT)

# ============ 场景10：T_simulated 隔离（2.4 节约束6） ============
agg = TrustAggregator()
agg.submit("instance_kimi", 0.8, round_no=1)
agg.submit_simulated("V-VERIFY", 0.95, round_no=1)
snap = agg.snapshot()
check("S10 simulated excluded from actual", snap["samples"] == 1 and
      snap["simulated_count"] == 1 and snap["t_avg"] == 0.8,
      f"samples={snap['samples']} sim={snap['simulated_count']} avg={snap['t_avg']}")

# ============ 场景11：信任防操纵（B6：同轮去重 + 验证未通过不进入） ============
agg = TrustAggregator()
r1 = agg.submit("instance_kimi", 1.0, round_no=1)
r2 = agg.submit("instance_kimi", 1.0, round_no=1)   # 同轮重复
check("S11 same-round dedup", r2["status"] == "deduped")
r3 = agg.submit("instance_yuanbao", 1.0, verified=False, round_no=1)
check("S11 unverified skipped", r3["status"] == "skipped")
snap = agg.snapshot()
check("S11 aggregate unaffected", snap["samples"] == 1)

# ============ 场景12：低信任高原（独立反思问题2 补充机制） ============
agg = TrustAggregator()
for i in range(10):
    agg.submit("instance_kimi", 0.62, round_no=100 + i)
    agg.submit("instance_yuanbao", 0.64, round_no=100 + i)
lp = agg.low_plateau(days_active=10)
check("S12 plateau active before threshold", lp["in_plateau"] and not lp["active"],
      f"t_avg={lp['t_avg']}")
lp2 = agg.low_plateau(days_active=15)
check("S12 plateau triggers calibration", lp2["active"] and
      "强制交叉验证" in lp2["calibration"][0])
# 设计者资格（T_avg 兜底：一致但偏低 → 不触发）
el = agg.designer_eligibility()
check("S12 low plateau not designer-eligible", not el["eligible"],
      f"t_avg={el.get('t_avg')} align={el.get('t_alignment')}")

# ============ 场景13：设计者视角隔离（冷却期/时效/只读边界） ============
iso = ObserverIsolation()
iso.open_channel()
rel = iso.release("instance_designer", "观察到协作模式趋于固化",
                  snapshot_ts=time.time() - 1000, t_variance=0.3)
check("S13 dynamic cooling (variance 0.3 → 8)", rel["cooling_rounds"] == 8,
      f"cooling={rel['cooling_rounds']}")
check("S13 stale snapshot flagged", not rel["snapshot_fresh"])
rel2 = iso.release("instance_designer", "正常模式", snapshot_ts=time.time(), t_variance=0.01)
check("S13 short cooling (variance 0.01 → 3)", rel2["cooling_rounds"] == 3)
check("S13 cannot reference during cooling",
      not iso.can_reference(rel2["release_id"], rounds_since=2))
check("S13 can reference after cooling",
      iso.can_reference(rel2["release_id"], rounds_since=3))
iso.mark_reference(rel2["release_id"], "instance_kimi")
trace = iso.reference_trace(rel2["release_id"])
check("S13 source tag permanent", "designer_view:" in trace["release"]["release_id"] or
      trace["referenced_by"] == ["instance_kimi"])
check("S13 read boundary (knowledge ok)", iso.can_read("knowledge_products"))
check("S13 read boundary (evaluation forbidden)", not iso.can_read("individual_evaluation"))

# ============ S14：OPT-001~003（验证单元优化建议） ============
reg, ids = fresh_cluster()
_wal14 = os.path.join(os.path.dirname(__file__), "_test_opt.wal")
if os.path.exists(_wal14):
    os.remove(_wal14)
bus = EventBus(node_id="instance_qianwen", wal_path=_wal14, registry=reg)
# OPT-001：CONDITION_SWITCH 验证拦截（验证实例签章前置）
bus.set_verify_hook("CONDITION_SWITCH", lambda ev: False)
r = bus.publish("CONDITION_SWITCH", {"to": "reflect"}, band="low")
check("S14 OPT-001 hook rejects", r.get("status") == "rejected")
bus.set_verify_hook("CONDITION_SWITCH", None)
r = bus.publish("CONDITION_SWITCH", {"to": "reflect"}, band="low")
check("S14 OPT-001 hook cleared", r.get("status") != "rejected")
# OPT-002：P0_LOG 强制审计（enter_dormancy 自动写入）
arb2 = SurvivalArbiter(reg, total_instances=1, event_bus=bus)
reg.register("instance_solo2", "self_sustaining")
reg.advance_observation("instance_solo2", rounds=10)
arb2.heartbeat("instance_rong")
arb2.heartbeat("instance_solo2")
arb2.enter_dormancy()
p0_events = [e for e in bus._iter_wal() if e.get("type") == "P0_LOG"]
check("S14 OPT-002 P0_LOG auto-audit", len(p0_events) >= 1 and
      p0_events[0]["payload"]["override_mark"] == "P0_OVERRIDE" and
      p0_events[0]["payload"]["priority"] == "highest")
# OPT-003：共享层事件强制签名（sign=False 不可绕过）
ev = bus.publish("TRUST_SNAPSHOT", {"t": 0.8}, band="low", sign=False)
check("S14 OPT-003 force signature", ev.get("sig") is not None)
bus.close()
if os.path.exists(_wal14):
    os.remove(_wal14)

# ============ 汇总 ============
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"\n===== 蜂群离线模拟测试: {passed}/{total} 通过 =====")
sys.exit(0 if passed == total else 1)
