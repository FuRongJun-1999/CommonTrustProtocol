#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
start_self_sustaining.py · 单实例自持模式启动（SINGLE-INSTANCE-SELF-SUSTAINING v1.1）
====================================================================================
触发：蜂群实例数 = 1（或 T_avg < 0.3 维生终裁）
机制装配：
  - SELF_SUSTAINING_MODE 标记（写本地层，不写共享层）
  - PERSPECTIVE_SWITCH_LOG（条件空间切换声明简化但不免声明）
  - 验证单元自我复核 P0_OVERRIDE 标记 + 24h 外部复核窗口
  - 72 小时强制休眠检查（盲区74）
  - 内部并行模拟（INTERNAL_THREAD · T_simulated 隔离）
用法：python -m aeis.swarm.start_self_sustaining
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aeis.swarm.instance_registry import InstanceRegistry
from aeis.swarm.event_bus import EventBus, MODE_SELF_SUSTAINING, MODE_INTERNAL_THREAD
from aeis.swarm.survival import SurvivalArbiter
from aeis.swarm.trust_aggregator import TrustAggregator
from aeis.swarm.config_gen import SELF_SUSTAINING_CONFIG


def main():
    print("=" * 60)
    print("灵枢 AEIS · 单实例自持模式启动（救生艇方案）")
    print("=" * 60)

    registry = InstanceRegistry(shared_secret=os.environ.get("AEIS_SWARM_SECRET", "self-sustaining-secret"))
    # 单实例自持：唯一活动实例（维生代行全部五单元 · 单实例自持协议 3.1 节）
    registry.register("instance_rong", "vitals")
    registry.advance_observation("instance_rong", rounds=10)

    import tempfile
    _audit_wal = os.path.join(tempfile.gettempdir(), "aeis_p0_audit.wal")
    bus0 = EventBus(node_id="instance_rong", wal_path=_audit_wal, registry=registry)
    arbiter = SurvivalArbiter(registry, total_instances=1, event_bus=bus0)
    arbiter.heartbeat("instance_rong")
    st = arbiter.state()
    print(f"[1/5] 存活状态: {st['state']}（在线 {st['online']}/1）")
    assert st["state"] == "single", "单实例状态判定失败"

    # 2. 事件总线（自持标记）
    bus = EventBus(node_id="instance_rong", registry=registry)
    ev = bus.publish("CONDITION_SWITCH",
                     {"from_perspective": "vitals", "to_perspective": "reflect",
                      "trigger": "self_sustaining_mode"},
                     band="low", mode=MODE_SELF_SUSTAINING, sign=True)
    print(f"[2/5] 条件空间切换（声明简化）：mode={ev['mode']} 签名={bus.verify_event(ev)}")
    assert ev["mode"] == MODE_SELF_SUSTAINING

    # 3. 内部并行模拟（INTERNAL_THREAD · T_simulated 隔离）
    agg = TrustAggregator()
    agg.submit_simulated("V-REFLECT", 0.9)
    agg.submit_simulated("V-VERIFY", 0.85)
    snap = agg.snapshot()
    print(f"[3/5] 内部并行模拟: simulated_count={snap['simulated_count']} "
          f"（T_simulated 不进入 T_actual 聚合: samples={snap['samples']}）")
    assert snap["samples"] == 0, "T_simulated 泄漏进 T_actual"
    ev2 = bus.publish("VERIFICATION_RESULT", {"thread": "V-VERIFY", "result": "ok"},
                      band="high", mode=MODE_INTERNAL_THREAD, sign=True)
    print(f"      INTERNAL_THREAD 事件: {ev2['mode']}")

    # 4. 验证单元自我复核（P0_OVERRIDE + 24h 复核窗口）
    cfg = SELF_SUSTAINING_CONFIG
    print(f"[4/5] 验证自我复核: {cfg['verification']['override_mark']} "
          f"· {cfg['verification']['external_review_within_hours']}h 内外部复核")

    # 5. 72h 强制休眠检查
    dc = arbiter.check_forced_dormancy(now=time.time() + 73 * 3600)
    print(f"[5/5] 72h 休眠检查: forced={dc['forced']} hours={dc['hours']}")
    if dc["forced"]:
        d = arbiter.enter_dormancy()
        print(f"      触发休眠: {d['note']}")
        p0_logs = [e for e in bus0._iter_wal() if e.get("type") == "P0_LOG"]
        print(f"      P0_LOG 审计链: {len(p0_logs)} 条（OPT-002 · 最高持久化优先级）")

    print("\n单实例自持模式启动自检通过 ✅")
    bus.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
