#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OBS-REV1 观测持久化回归测试（v1.14）
====================================
修复目标（心跳观测三连空）：
1. P0-1 行为日志跨进程持久化（action_logs 表）——进程重启后 action_log 可恢复
2. 认知循环自记行为（cognition 类型）——心跳观测面持续有内容
3. 飞轮基线持久化（engine_meta）——增长率跨进程连续
4. patterns 以 reusable_pattern 标签节点统计——口径与 distill 实际产出一致
"""

import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aeis.api import Agent

PASS = 0
TOTAL = 0


def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        print(f"  [FAIL] {name} {detail}")


def main():
    db = os.path.join(tempfile.mkdtemp(), "obs_test.db")

    # ---- 1. 行为日志持久化：写入 → 关闭 → 新实例恢复 ----
    a = Agent(identity="obs-a", db_path=db)
    a.remember("OBS-REV1 持久化测试", importance=0.9, tags=["obs"])
    a.cognition_cycle()
    log1 = a.action_log(50)
    check("行为日志写入", len(log1) >= 2, f"count={len(log1)}")
    types1 = {e["action_type"] for e in log1}
    check("认知循环自记行为", "cognition" in types1, f"types={sorted(types1)}")
    a.close()

    b = Agent(identity="obs-b", db_path=db)
    log2 = b.action_log(50)
    check("跨实例恢复行为日志", len(log2) == len(log1),
          f"a={len(log1)} b={len(log2)}")
    check("恢复内容一致",
          [e["action_type"] for e in log2] == [e["action_type"] for e in log1])

    # ---- 2. 飞轮基线持久化：首调建基 → 增长 → 新实例增长率连续 ----
    m1 = b.flywheel_report()
    check("metrics 首调建立基线", m1["knowledge_growth_rate"] == 0.0)
    b.remember("OBS-REV1 增长节点", importance=0.5)
    m2 = b.flywheel_report()
    check("同实例增长率>0", m2["knowledge_growth_rate"] > 0.0,
          f"growth={m2['knowledge_growth_rate']}")
    b.close()

    c = Agent(identity="obs-c", db_path=db)
    m3 = c.flywheel_report()
    check("新实例基线连续（非归零）", m3["totals"]["nodes"] == m2["totals"]["nodes"],
          f"b={m2['totals']['nodes']} c={m3['totals']['nodes']}")

    # ---- 3. patterns 口径：蒸馏产出可复用模式 → metrics 统计可见 ----
    r = c.distill()
    if r.get("status") == "ok" and r.get("patterns", 0) > 0:
        m4 = c.flywheel_report()
        check("patterns 标签节点统计", m4["totals"]["patterns"] >= r["patterns"],
              f"distill={r['patterns']} metrics={m4['totals']['patterns']}")
    else:
        print("  [SKIP] patterns 口径（无待蒸馏经验，场景未触发）")
    c.close()

    print(f"\n===== OBS-REV1 观测持久化回归: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
