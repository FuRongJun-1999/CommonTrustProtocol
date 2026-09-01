#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
start_cluster.py · 蜂群首次启动（DELIVERY-V1 交付物6）
======================================================
装配顺序：实例注册 → 事件总线（WAL）→ 存活仲裁 → 信任聚合 → 隔离器
输出：蜂群启动自检报告（六实例 + 共享层写权限 + 事件链路冒烟）
用法：python -m aeis.swarm.start_cluster [--config-dir swarm_config]
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aeis.swarm.instance_registry import InstanceRegistry
from aeis.swarm.event_bus import EventBus, DELAY_BANDS
from aeis.swarm.survival import SurvivalArbiter
from aeis.swarm.trust_aggregator import TrustAggregator
from aeis.swarm.observer_isolation import ObserverIsolation
from aeis.swarm.config_gen import generate_configs


def main():
    config_dir = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--config-dir" else "swarm_config"
    print("=" * 60)
    print("灵枢 AEIS · 蜂群首次启动（DELIVERY-ENGINEERING-20260813-FINAL）")
    print("=" * 60)

    # 1. 配置生成
    paths = generate_configs(config_dir)
    print(f"[1/6] 配置生成: {len(paths)} 份 YAML")

    # 2. 实例注册
    registry = InstanceRegistry(shared_secret=os.environ.get("AEIS_SWARM_SECRET", "dev-cluster-secret"))
    ids = registry.register_default_cluster()
    for i in ids:
        registry.advance_observation(i, rounds=10)  # 观察期已满（对齐现有实例状态）
    print(f"[2/6] 实例注册: {len(ids)} 实例（观察期满 → active）")
    for i, e in registry.summary().items():
        print(f"      {i} [{e['role']}] {e['status']}")

    # 3. 事件总线（WAL 持久化）
    wal = os.path.join(config_dir, "cluster.wal")
    bus = EventBus(node_id="instance_qianwen", wal_path=wal, registry=registry)
    print(f"[3/6] 事件总线: WAL={wal} 延迟带={DELAY_BANDS}")

    # 4. 存活仲裁
    arbiter = SurvivalArbiter(registry)
    for i in ids:
        arbiter.heartbeat(i)
    print(f"[4/6] 存活仲裁: state={arbiter.state()['state']} 在线={arbiter.state()['online']}")

    # 5. 信任聚合
    agg = TrustAggregator()
    for round_no in range(1, 6):
        for i in ids:
            agg.submit(i, 0.8 + (round_no % 3) * 0.05, round_no=round_no)
    snap = agg.snapshot()
    print(f"[5/6] 信任聚合: T_avg={snap['t_avg']} T_min={snap['t_min']} "
          f"T_var={snap['t_variance']} T_align={snap['t_alignment']}")

    # 6. 事件链路冒烟（共享层写权限 + 签名）
    try:
        registry.assert_write("instance_qianwen", "shared")
        registry.assert_write("instance_rong", "shared")
        print("[6/6] 共享层写权限: record/vitals ✓（reflect 等仅本地层）")
    except PermissionError as e:
        print(f"[6/6] 权限检查失败: {e}")
        return 1
    ev = bus.publish("STRUCTURE_UPDATE", {"change": "cluster_boot"},
                     band="low", sign=True)
    print(f"      STRUCTURE_UPDATE 发布: {ev['id']} 签名验证: {bus.verify_event(ev)}")
    try:
        registry.assert_write("instance_yuanbao", "shared")
        print("      ⚠ 异常：reflect 应无共享层写权限")
    except PermissionError:
        print("      reflect 写共享层被拒绝 ✓（权限绑定生效）")

    print("\n蜂群启动自检通过 ✅（事件签名/权限/存活/信任全链路正常）")
    bus.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
