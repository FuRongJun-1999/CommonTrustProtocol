# -*- coding: utf-8 -*-
"""test_common_domains.py · 常识域扩充测试（第四阶段·目标①：光声/天文/经济/化学）
验证：①新域 13 单元生成（核心词≥2 自校验）②旧域回归 ③跨域不串扰"""
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

# ① 新域 13 单元生成（问题 → 组合生成含核心词）
QS = {
    "影子是怎么来的？": ("直线传播", "影子"),
    "为什么照镜子能看到自己？": ("反射-光", "镜面"),
    "彩虹怎么形成的？": ("色散", "彩虹"),
    "声音是怎么产生的？": ("发声", "振动"),
    "为什么山谷里有回声？": ("回声", "反射"),
    "为什么女声比男声尖？": ("音调", "频率"),
    "为什么月亮形状会变？": ("月相", "公转"),
    "为什么会有日食？": ("食", "日食"),
    "为什么口罩会涨价？": ("价格", "需求"),
    "为什么钱会贬值？": ("通胀", "货币"),
    "为什么水能灭火？": ("燃烧", "要素"),
    "为什么铁会生锈？": ("氧化", "生锈"),
    "为什么糖在热水里化得快？": ("溶解", "温度"),
}
new_domains = set()
for q, (dir_kw, kw) in QS.items():
    r = ce.route_compose(q)
    ans = r.get("answer", "")
    ok = r.get("ok") and kw in ans and r.get("direction") == dir_kw
    check(f'① 新域生成: {q[:12]}…', ok,
          f'{r.get("direction")} | {ans[:30] if ok else (r.get("reason") or (r.get("checks") or [""])[0])[:40]}')
    if ok:
        u = r.get("units", [""])[0]
        if u in ce.CONDITION_UNITS:
            new_domains.add(ce.CONDITION_UNITS[u].get("domain", ""))

# ② 旧域回归（9 域代表性问法）
OLD_QS = [
    "为什么高原上煮饭不容易熟？", "为什么铁块会沉到水底？", "为什么金属勺摸起来烫手？",
    "为什么洗洁精能去油？", "为什么冬天湖面会结冰？", "为什么植物需要光照？",
    "为什么有白天黑夜？", "为什么灯泡不亮？", "为什么饿了要吃饭？",
]
old_ok = 0
for q in OLD_QS:
    r = ce.route_compose(q)
    if r.get("ok"):
        old_ok += 1
check('② 旧域回归 9/9', old_ok == len(OLD_QS), f'{old_ok}/{len(OLD_QS)}')

# ③ 跨域不串扰：经济问题不命中物理/生物域
r = ce.route_compose("为什么口罩会涨价？")
check('③a 经济问题命中经济域', r.get("units", [""])[0] == "价格-供需", str(r.get("units")))
r = ce.route_compose("为什么铁会生锈？")
check('③b 化学问题命中化学域', r.get("units", [""])[0] == "生锈-氧化", str(r.get("units")))
# 人体反射不被光学劫持
r = ce.route_compose("为什么烫手会缩手？")
check('③c 人体反射不被光学劫持', r.get("direction") == "反射" and "缩手" in r.get("answer", ""),
      f'{r.get("direction")}')

# ④ 域数统计
domains = sorted({u.get("domain", "-") for u in ce.CONDITION_UNITS.values()})
check('④ 新域已纳入（≥14 域）', len(domains) >= 14, f'{len(domains)} 域: {domains}')

print(f'\n=== 常识域扩充测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
