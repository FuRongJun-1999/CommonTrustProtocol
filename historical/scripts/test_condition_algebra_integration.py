# -*- coding: utf-8 -*-
"""test_condition_algebra_integration.py · 条件代数集成测试（第五阶段）
验证：①compose_parallel 并行分组（独立域同组/共享域串行）
②coverage_report 核心常识域覆盖率（判定④ ≥80%）
③并行分组结果与串行一致（不破坏生成）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import compose_engine as ce

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 并行分组（独立域可并行）
qs = [
    "为什么高原上煮饭不容易熟？",   # 气压域
    "为什么植物要放在有阳光的地方？", # 光照域
    "为什么保温杯里的热水放很久还是热的？",  # 隔热域
]
r = ce.compose_parallel(qs)
groups = r["groups"]
check('①a 独立域查询（气压/光照/隔热）→ 同组可并行',
      len(groups) == 1 and len(groups[0]) == 3, f'分组 {groups}')
check('①b 并行组合结果全部生成',
      all(x["result"].get("ok") for x in r["results"]))

# 共享条件域（温度 相关）→ 分组
qs2 = [
    "为什么夏天晾衣服干得快？",     # 蒸发-条件（温度/通风）
    "为什么有风的时候衣服干得更快？", # 蒸发-条件（通风）
    "为什么金属勺放进热汤会烫手？",   # 导热（温度）
]
r2 = ce.compose_parallel(qs2)
# 温度/通风共享蒸发-条件 → 前两个相关；导热也涉及温度
check('①c 共享条件域 → 分组数 > 1（相关需串行）',
      len(r2["groups"]) >= 2, f'分组 {r2["groups"]}')

# ② 覆盖率判定
cov = ce.coverage_report()
check('②a 核心常识域覆盖率 ≥80%（判定④）',
      cov["rate"] >= 80.0, f"{cov['rate']}% ({cov['covered']}/{cov['total']})")
check('②b 覆盖率报告结构', "missing" in cov and cov["units"] >= 30,
      f"{cov['units']} 单元 {cov['domains']} 域")
if cov["missing"]:
    print(f'   未覆盖: {cov["missing"]}')

# ③ 并行不破坏生成（与串行一致）
for x in r["results"]:
    q = x["query"]
    serial = ce.route_compose(q)
    check(f'③ 并行结果=串行结果: {q[:12]}…',
          x["result"].get("answer") == serial.get("answer"))

print(f'\n=== 条件代数集成测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
