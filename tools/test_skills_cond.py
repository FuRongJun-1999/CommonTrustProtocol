# -*- coding: utf-8 -*-
"""test_skills_cond.py · 技能条件路由加载（anthropics/skills 吸纳）

技能 = 目录化 + 元数据（适用条件/不适用条件）→ 条件路由加载：
  任务词命中适用条件 → 加载；命中不适用条件 → 排除（不盲目加载）。
"""
import sys, os, json
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import self_iterate as si

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 技能含条件元数据（适用/不适用）
db = json.load(open(si.SKILLS_PATH, encoding='utf-8'))
has_meta = all("适用条件" in s and "不适用条件" in s
               for g in db.values() for s in g.get("skills", []))
print(f'  技能条目含条件元数据: {"✓" if has_meta else "✗"}')
check('① 技能条件化：适用条件/不适用条件 元数据已声明', has_meta)

# ② 条件路由加载：命中适用条件 → 加载
q_ok = "负面测试发现空输入返回默认值需要标注盲区"
r_ok = si.skills_cond(q_ok)
ok2 = len(r_ok) >= 1 and any("空/非法" in m["skill"] for m in r_ok)
print(f'  加载 [{q_ok[:14]}…] → {len(r_ok)} 条: '
      f'{", ".join(m["skill"][:18] for m in r_ok[:2])}')
check('② 适用条件命中 → 技能加载', ok2)

# ③ 不适用条件命中 → 排除（抛异常是强拒绝非盲区）
q_not = "输入超范围抛异常强拒绝不是盲区"
r_not = si.skills_cond(q_not)
ok3 = all("隐式盲区" not in m["skill"] for m in r_not)
print(f'  排除 [{q_not[:14]}…] → {len(r_not)} 条'
      f'（应 0——异常=强拒绝非盲区技能）')
check('③ 不适用条件命中 → 技能排除（条件路由）', ok3)

# ④ 无匹配 → 空（不盲目加载）
q_none = "写一个 TCP 握手"
r_none = si.skills_cond(q_none)
ok4 = len(r_none) == 0
print(f'  无关任务 → {len(r_none)} 条（应 0——不盲目加载）')
check('④ 无关任务 → 不加载（技能路由白箱化）', ok4)

report = {
    "experiment": "技能条件路由加载（GitHub 吸纳：anthropics/skills）",
    "skills_with_meta": has_meta,
    "condition_hit": ok2, "not_condition_exclude": ok3,
    "no_match": ok4,
    "conclusion": ("技能=目录化+元数据（适用/不适用条件）→ 条件路由加载；"
                   "外部工程实践（anthropics/skills）已吸纳进白箱体系"),
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skills_cond_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑤ skills_cond_report.json 落盘', os.path.exists(rp), 'skills_cond_report.json')

print(f'\n=== 技能条件路由: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
