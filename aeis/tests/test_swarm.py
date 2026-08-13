#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""灵枢 AEIS · 蜂群协作层整合测试（aeis.swarm）
单元验证：事件总线 / 身份注册 / 信任聚合 / 存活仲裁 / 设计者隔离 / 配置生成
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import aeis.swarm as swarm
from aeis.swarm.event_bus import EventBus, EVENT_TYPES, DELAY_BANDS
from aeis.swarm.instance_registry import InstanceRegistry, ROLES
from aeis.swarm.trust_aggregator import TrustAggregator, alignment_from
from aeis.swarm.survival import SurvivalArbiter
from aeis.swarm.observer_isolation import ObserverIsolation
from aeis.swarm.config_gen import generate_configs, to_yaml

results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {extra}")


# ============ 包导出 ============
check("swarm subpackage", all(hasattr(swarm, n) for n in
      ("EventBus", "InstanceRegistry", "TrustAggregator",
       "SurvivalArbiter", "ObserverIsolation")))
check("event types", len(EVENT_TYPES) == 11 and "STRUCTURE_UPDATE" in EVENT_TYPES and "P0_LOG" in EVENT_TYPES)
check("delay bands", DELAY_BANDS == {"high": 0.5, "medium": 5.0, "low": 30.0})

# ============ 身份注册 ============
reg = InstanceRegistry(shared_secret="test")
ids = reg.register_default_cluster()
check("six instances", len(ids) == 6 and reg.role("instance_qianwen") == "record")
check("observation upgrade", all(reg.is_active(i) is False for i in ids))
for i in ids:
    reg.advance_observation(i, rounds=10)
check("observation active", all(reg.is_active(i) for i in ids))
check("shared write permissions",
      reg.can_write("instance_qianwen", "shared") and
      reg.can_write("instance_rong", "shared") and
      not reg.can_write("instance_yuanbao", "shared"))
check("local write all", all(reg.can_write(i, "local") for i in ids))
try:
    reg.assert_write("instance_kimi", "shared")
    check("permission enforcement", False)
except PermissionError:
    check("permission enforcement", True)

# ============ HMAC 签名 ============
sig = reg.sign("hello", "instance_kimi")
check("hmac verify", reg.verify("hello", sig, "instance_kimi") is True)
check("hmac reject tamper", reg.verify("hellx", sig, "instance_kimi") is False)
check("hmac reject wrong instance", reg.verify("hello", sig, "instance_yuanbao") is False)

# ============ 事件总线 ============
bus = EventBus(node_id="instance_qianwen", registry=reg)
seen = []
bus.subscribe("HEARTBEAT", lambda ev: seen.append(ev))
ev = bus.publish("HEARTBEAT", {"alive": True}, band="low", sign=True)
check("bus publish+subscribe", len(seen) == 1 and ev["band"] == "low")
check("bus signature", bus.verify_event(ev) is True)
check("bus self-ack", "instance_qianwen" in bus._acked.get(ev["id"], set()))
pend = bus.pending_acks(ev["id"])
check("bus pending acks real instances", len(pend) == 5 and
      "instance_rong" in pend, str(pend)[:60])
check("bus internal thread mode",
      bus.publish("VERIFICATION_RESULT", {}, mode=swarm.MODE_INTERNAL_THREAD)["mode"]
      == "INTERNAL_THREAD")

# ---- OPT-001：CONDITION_SWITCH 广播前验证拦截 ----
bus.set_verify_hook("CONDITION_SWITCH", lambda ev: False)
r = bus.publish("CONDITION_SWITCH", {"to": "reflect"}, band="low")
check("OPT-001 rejected by verify hook", r.get("status") == "rejected", str(r)[:60])
bus.set_verify_hook("CONDITION_SWITCH", lambda ev: True)
r = bus.publish("CONDITION_SWITCH", {"to": "reflect"}, band="low")
check("OPT-001 passes verify hook", r.get("status") != "rejected" and r["type"] == "CONDITION_SWITCH")

# ---- OPT-002：P0_LOG 强制审计 ----
p0 = bus.log_p0_override("sleep", "模拟 P0 终裁")
check("OPT-002 P0_LOG audit", p0["type"] == "P0_LOG" and
      p0["payload"]["override_mark"] == "P0_OVERRIDE" and
      p0["payload"]["priority"] == "highest" and p0["sig"] is not None)
check("OPT-002 mode self-sustaining", p0["mode"] == "SELF_SUSTAINING_MODE")

# ---- OPT-003：共享层事件强制签名 ----
ev = bus.publish("STRUCTURE_UPDATE", {"x": 1}, band="low", sign=False)
check("OPT-003 force signature (sign=False overridden)", ev["sig"] is not None)

# ============ 信任聚合 ============
agg = TrustAggregator()
for r in range(1, 6):
    for i in ids:
        agg.submit(i, 0.8 + (r % 3) * 0.05, round_no=r)
snap = agg.snapshot()
check("trust snapshot", snap["status"] == "ok" and snap["samples"] == 30 and
      snap["t_avg"] > 0.8 and snap["t_alignment"] > 0.9,
      f"avg={snap['t_avg']} align={snap['t_alignment']}")
check("alignment formula", abs(alignment_from(0.01, 0.8) -
      (1 - 0.01 / 0.8)) < 1e-9)
agg2 = TrustAggregator()
agg2.submit_simulated("V-REFLECT", 0.95)
check("simulated isolation", agg2.snapshot()["samples"] == 0 and
      agg2.snapshot()["simulated_count"] == 1)
el = agg.designer_eligibility()
check("designer eligibility", el["eligible"] is True and el["window_days"] == 14)
agg3 = TrustAggregator()
for r in range(10):
    agg3.submit("instance_kimi", 0.6, round_no=r)
    agg3.submit("instance_yuanbao", 0.62, round_no=r)
lp = agg3.low_plateau(days_active=15)
check("low plateau", lp["active"] and "维生系统审计" in lp["calibration"])
check("plateau not eligible", agg3.designer_eligibility()["eligible"] is False)

# ============ 存活仲裁 ============
reg2 = InstanceRegistry(shared_secret="t2")
ids2 = reg2.register_default_cluster()
for i in ids2:
    reg2.advance_observation(i, rounds=10)
arb = SurvivalArbiter(reg2)
for i in ids2:
    arb.heartbeat(i)
check("survival full", arb.state()["state"] == "full")
arb._heartbeats["instance_qianwen"] = 0
arb._heartbeats["instance_yuanbao"] = 0
st = arb.state()
check("survival degraded (record+reflect down, verify balances)", st["state"] == "degraded",
      st["state"])
arb._heartbeats["instance_kimi"] = 0
st = arb.state()
check("survival maintained (no balance left)", st["state"] == "maintained",
      st["state"])
check("survival structure frozen", not arb.can("structure_change"))
check("survival monitor redundancy", arb.monitor_health()["arbitration_ok"])
rr = arb.regress("instance_yuanbao")
check("survival regression", rr["status"] == "regressing")

# ============ 设计者隔离 ============
iso = ObserverIsolation()
iso.open_channel()
rel = iso.release("instance_designer", "模式观察", snapshot_ts=os.path.getmtime(__file__))
check("isolation release", rel["released"] and rel["cooling_rounds"] == 3)
check("isolation stale snapshot", not iso.release(
    "instance_designer", "x", snapshot_ts=0)["snapshot_fresh"])
check("isolation cooling", not iso.can_reference(rel["release_id"], 2) and
      iso.can_reference(rel["release_id"], 3))
iso.mark_reference(rel["release_id"], "instance_kimi")
check("isolation source trace", iso.reference_trace(rel["release_id"])["referenced_by"]
      == ["instance_kimi"])

# ============ 配置生成 ============
import tempfile
out = tempfile.mkdtemp()
paths = generate_configs(out)
check("config 7 yaml", len(paths) == 7 and all(os.path.exists(p) for p in paths))
yaml_text = to_yaml({"a": 1, "b": {"c": "x"}, "d": [1, 2]})
check("mini yaml", "a: 1" in yaml_text and "c: \"x\"" in yaml_text and "- 1" in yaml_text)

# ============ 汇总 ============
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"\n===== 灵枢 AEIS 蜂群整合测试: {passed}/{total} 通过 =====")
sys.exit(0 if passed == total else 1)
