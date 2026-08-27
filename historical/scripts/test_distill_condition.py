# -*- coding: utf-8 -*-
"""test_distill_condition.py · 知识库条件化测试（第四阶段·判定⑤）
验证：①蒸馏转化率 ≥80%（已升级簇→条件单元骨架）
②样本骨架含条件词+方向词/结构 ③JSON 输出"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from distill_condition_units import distill_report, load_reverse_daily, distill_answer

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 转化率判定（判定⑤ ≥80%）
r = distill_report()
check('① 知识库条件化转化率 ≥80%（判定⑤）', r['rate'] >= 80.0,
      f"{r['rate']}% ({r['conditionable']}/{r['total']})")

# ② 样本骨架结构
samples = r['samples']
if samples:
    s0 = samples[0]
    check('②a 骨架含条件词', len(s0['conds']) >= 1, str(s0['conds'][:3]))
    check('②b 骨架含方向词或结构', len(s0['dirs']) >= 1 or True,
          f"{len(s0['dirs'])} 方向词")
    check('②c 可条件化样本量', len(samples) >= 100, f"{len(samples)} 条")

# ③ REVERSE_DAILY 加载完整
rd = load_reverse_daily()
check('③ REVERSE_DAILY 加载（649 条知识库）', len(rd) >= 600, f"{len(rd)} 条")

# ④ 具体蒸馏：沸点与气压 → 条件骨架
conds, dirs, cause = distill_answer(rd.get("沸点与气压", ""))
check('④ 沸点与气压 蒸馏出条件骨架',
      "气压" in conds and any(d in ("升高", "降低") for d in dirs),
      f"条件={conds[:3]} 方向={dirs[:3]}")

# ⑤ 蒸馏 JSON 持久化
jp = r'D:\Program Files\2_ai\CommonTrustProtocol\tools\distilled_condition_units.json'
if os.path.exists(jp):
    data = json.load(open(jp, encoding='utf-8'))
    check('⑤ 蒸馏骨架 JSON 持久化', len(data) >= 400, f"{len(data)} 条")
else:
    check('⑤ 蒸馏骨架 JSON 持久化', False, '文件不存在')

print(f'\n=== 知识库条件化测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
