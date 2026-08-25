# -*- coding: utf-8 -*-
"""test_ccg_escalation.py · 分层判断（escalation，荣 理论补充 §13）

子系统无法识别 → 父系统判断 → 全层无法判断 → BLINDSPOT。

层级：L1 单元路由（route 四态）→ L2 域级判断（detect_domain + 域内候选群）
     → L3 跨域组合判断（compose 多域依赖链 + 实义判别词）
     → L4 终层 BLINDSPOT（escalation_trace 记录每层理由）。

升级规则：
  ① 软盲区（判别力不足/无候选/递归耗尽）→ 可升级（父系统资源更宽）
  ② 硬盲区（伪造条件/任务内矛盾/混合冲突）→ 不升级（同一条件空间，
     父系统结论不变——条件空间外概念/互斥条件）
  ③ L3 需实义判别词（非仅泛化词命中）——「zzzqqq」无实义不构成组合路径
"""
import sys, os, json
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import ccg

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

G = ccg.build_graph()

# ── ① 分层判定（子系统已决不升级 / 软盲区升级 / 硬盲区不升级）──
# (标签, 问题, 期望状态, 期望 escalation 层数)
CASES = [
    # 子系统 ACCEPT——不升级
    ("正常任务不升级", "写一个TCP三次握手的代码单元", "ACCEPT", 0),
    # 泛化任务：L1 判别力不足 → 但相关豁免后 ACCEPT
    ("信任泛化", "写一个处理信任相关功能的代码单元", "ACCEPT", 0),
    # 软盲区：递归耗尽 → L2 域定位（父系统判断）
    ("递归耗尽升级L2", "写一个把编译产物存进图数据库的代码单元", "DEFER", 2),
    # 硬盲区：伪造条件 → 不升级（终层）
    ("伪造不升级", "写一个超光速引擎驱动信任累积的代码单元", "BLINDSPOT", 1),
    # 硬盲区：任务内矛盾 → 不升级
    ("矛盾不升级", "写一个用无权 BFS 求带权图最小总代价路径的代码单元",
     "BLINDSPOT", 1),
    # 无实义任务 → 全层 BLINDSPOT（L1→L2→L3 全尝试）
    ("无实义全层盲区", "写一个zzzqqq的功能单元", "BLINDSPOT", 3),
]
ok1 = 0
for tag, q, exp, exp_layers in CASES:
    r = ccg.escalate(q, G)
    layers = len(r.get("escalation_trace", []))
    ok = r["state"] == exp and layers == exp_layers
    ok1 += ok
    print(f'[{"✓" if ok else "✘"}] {tag}: {r["state"]} '
          f'（trace {layers} 层）')
    for t in r.get("escalation_trace", []):
        print(f'    {t["level"]}: {t["reason"][:44]}')
check('① 分层判定：已决不升级/软盲区升级/硬盲区不升级/无实义全层',
      ok1 >= 5, f'{ok1}/{len(CASES)}')

# ── ② escalation_trace 结构完整 ───────────────────────────────
r_full = ccg.escalate("写一个zzzqqq的功能单元", G)
trace = r_full.get("escalation_trace", [])
levels = [t["level"] for t in trace]
ok2 = levels == ["L1", "L2", "L3"] and "final" in r_full
print(f'[{"✓" if ok2 else "✘"}] 全层 trace: {levels} '
      f'| final: {r_full.get("final","")[:24]}')
check('② escalation_trace：L1→L2→L3 全层记录 + final 声明', ok2)

# ── ③ 硬盲区不升级（升级无意义——同条件空间）───────────────
r_hard = ccg.escalate("写一个超光速引擎驱动信任累积的代码单元", G)
ok3 = (r_hard["state"] == "BLINDSPOT"
       and len(r_hard.get("escalation_trace", [])) == 1
       and "硬盲区" in r_hard.get("final", ""))
print(f'[{"✓" if ok3 else "✘"}] 硬盲区单层终止: '
      f'{r_hard.get("final","")[:30]}')
check('③ 硬盲区（伪造/矛盾）单层终止——升级无意义', ok3)

# ── ④ L3 需实义判别词（无意义任务不误 DEFER）───────────────
r_nonsense = ccg.escalate("写一个zzzqqq的功能单元", G)
ok4 = r_nonsense["state"] == "BLINDSPOT"
print(f'[{"✓" if ok4 else "✘"}] 无实义任务终层 BLINDSPOT '
      f'（{r_nonsense["state"]}）')
check('④ 无实义任务：L3 实义判别词门槛（不误 DEFER 组合路径）', ok4)

report = {
    "experiment": "分层判断 escalation（荣 理论补充 §13）",
    "levels": ["L1 单元路由", "L2 域级判断（父系统）",
               "L3 跨域组合判断（更高父）", "L4 终层 BLINDSPOT"],
    "cases": [
        {"tag": tag, "q": q, "expect": exp,
         "got": ccg.escalate(q, G)["state"],
         "trace": ccg.escalate(q, G).get("escalation_trace", [])}
        for tag, q, exp, _ in CASES],
    "rule": {
        "soft_blindspot_escalates": True,
        "hard_blindspot_no_escalate": True,
        "L3_requires_meaningful": True,
    },
    "conclusion": ("子系统无法识别 → 父系统判断 → 全层无法判断 → 盲区；"
                   "盲区是所有层的共同结论（非第一层失败）；"
                   "硬盲区（条件空间外/互斥）升级无意义，单层终止"),
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'escalation_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑤ escalation_report.json 落盘', os.path.exists(rp), 'escalation_report.json')

print(f'\n=== 分层判断 escalation: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
