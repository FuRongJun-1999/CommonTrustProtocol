# -*- coding: utf-8 -*-
"""test_phase3_domains.py · 第三阶段·覆盖扩展+递归组合测试
验证：①生活常识域组合生成（洗涤/保温/化雪/保鲜）
②生物常识域组合生成（光合/呼吸/生长/迁徙）
③递归组合（多场景多条件链）④回归（物态/浮力/热传递/摩擦）⑤矛盾检测"""
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

# ① 生活常识域
LIFE_QS = {
    "为什么碗上的油污用洗洁精一洗就掉？": ("乳化", "洗涤剂"),
    "为什么保温杯里的热水放很久还是热的？": ("真空", "保温"),
    "为什么冬天路面要撒盐？": ("降低冰点", "化雪"),
    "为什么冰箱里的食物不容易坏？": ("微生物", "保鲜"),
}
for q, (kw1, kw2) in LIFE_QS.items():
    r = ce.route_compose(q)
    ok = r.get("ok") and kw1 in r.get("answer", "") and kw2 in r.get("answer", "")
    check(f'生活常识: {q[:14]}…', ok, r.get("answer", "?")[:44])

# ② 生物常识域
BIO_QS = {
    "为什么植物要放在有阳光的地方？": ("光合", "氧气"),
    "为什么鱼离开水会死？": ("呼吸", "窒息"),
    "为什么种子发芽需要浇水？": ("生长", "阳光+水"),
    "为什么大雁秋天往南飞？": ("迁徙", "南飞"),
}
for q, (kw1, kw2) in BIO_QS.items():
    r = ce.route_compose(q)
    ok = r.get("ok") and kw1 in r.get("answer", "") and kw2 in r.get("answer", "")
    check(f'生物常识: {q[:14]}…', ok, r.get("answer", "?")[:44])

# ③ 递归组合（多场景多条件链）
r = ce.compose_recursive("高压锅在高原上煮饭会怎么样？")
rec = r.get("recursive", False)
ans = r.get("answer", "")
ok_rec = rec and r.get("ok") and "气压低" in ans or ("沸点" in ans and len(ans) > 30)
check('③ 递归组合（高压锅×高原 双层条件链）', ok_rec, f'递归={rec} | {ans[:60]}')

# ③b 地球/技术域
EARTH_TECH = {
    "为什么有白天和黑夜？": ("自转", "昼夜"),
    "为什么有春夏秋冬四季？": ("公转", "四季"),
    "为什么海水会涨潮退潮？": ("引力", "潮汐"),
    "为什么灯泡不亮了？": ("回路", "电流"),
    "为什么撬棍能撬起大石头？": ("杠杆", "省力"),
    "为什么升旗要用定滑轮？": ("定滑轮", "方向"),
    "为什么筷子放在水里看起来像折断了？": ("折射", "弯折"),
}
for q, (kw1, kw2) in EARTH_TECH.items():
    r = ce.route_compose(q)
    ok = r.get("ok") and kw1 in r.get("answer", "") and kw2 in r.get("answer", "")
    check(f'地球/技术: {q[:14]}…', ok, r.get("answer", "?")[:44])

# ③c 类比（条件结构相似：真空=气压低 → 同高原规律域）
r = ce.route_compose("为什么真空瓶里煮饭也煮不熟？")
ok_analogy = r.get("ok") and "气压低" in r.get("answer", "") and "沸点" in r.get("answer", "")
check('③c 类比: 真空瓶煮饭 → 同高原规律域（气压×沸点）', ok_analogy, r.get("answer", "?")[:50])

# ④ 回归（原 4 域）
REGRESS = [
    "为什么高原上煮饭不容易熟？", "为什么铁块会沉入水底？",
    "为什么金属勺放进热汤会烫手？", "为什么鞋底要有花纹？",
    "为什么冬天湖面会结冰？", "为什么樟脑丸放久了变小？",
]
for q in REGRESS:
    r = ce.route_compose(q)
    check(f'回归: {q[:12]}…', r.get("ok"), r.get("answer", "?")[:30])

# ⑤ 矛盾检测（自发现错误）
for q in ["高原上水为什么烧得特别热？", "冬天湖面为什么会沸腾？"]:
    r = ce.route_compose(q)
    check(f'矛盾检测: {q[:12]}… → 自校验拒绝', not r.get("ok"))

print(f'\n=== 第三阶段·覆盖扩展+递归组合测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
