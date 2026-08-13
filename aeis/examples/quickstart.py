#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""灵枢 AEIS 快速开始：完整可运行示例"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aeis


def main():
    print(f"灵枢 AEIS v{aeis.__version__} · 引擎 {aeis.ENGINE_VERSION} · 协议 {aeis.PROTOCOL}\n")

    agent = aeis.Agent(identity="示例智能体")  # :memory: 临时库

    # ---- 记忆 ----
    n1 = agent.remember("用户偏好简洁回答", importance=0.8, tags=["preference"])
    n2 = agent.remember("用户反复询问天气 回答成功 用户满意", tags=["learning_result"])
    agent.remember("用户反复询问天气 再次回答成功 用户满意", tags=["learning_result"])
    agent.remember("用户询问时间 回答成功", tags=["learning_result"])
    print(f"记忆写入: {n1.content} / {n2.content}")

    hits = agent.recall("偏好", limit=3)
    print(f"召回: {len(hits)} 条")

    # ---- 关系 ----
    agent.relate(n1.id, hits[0][0].id, relation="similar", source_evidence="inferred")
    print("关系边已建立（similar · inferred）")

    # ---- 知识飞轮 ----
    r = agent.distill()
    print(f"蒸馏: {r['patterns']} 个模式（标准 {r['distillation_standard_version']}）")
    report = agent.flywheel_report()
    print(f"飞轮度量: 增长 {report['knowledge_growth_rate']} · 复用 {report['reuse_rate']} · 蒸馏 {report['distill_output_rate']}")

    # ---- 宇宙校准 ----
    c = agent.calibrate()
    print(f"宇宙校准: {len(c) - 1} 判据 + 定位")
    for k in ("judgment1_info_gap_trend", "judgment2_existence_priority",
              "judgment4_completeness", "judgment5_experiment"):
        print(f"  {k}: {c[k].get('status', c[k].get('explicit_claims', '-'))}")

    # ---- 生命周期 ----
    s = agent.step()
    print(f"生命周期: state={s.get('state')}")

    # ---- 元认知 ----
    print(f"完整性自检: {agent.self_check()['integrity_ok']}")
    agent.close()
    print("\n灵枢 AEIS 快速开始完成 ✅")


if __name__ == "__main__":
    main()
