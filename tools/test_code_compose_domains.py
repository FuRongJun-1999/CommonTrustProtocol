# -*- coding: utf-8 -*-
"""test_code_compose_domains.py · 白箱自举正式管线接管（第六阶段·方案A）
四套域单元库（编译器/语言机制/图数据库/操作系统）接入 code_compose 正式管线：
  域识别 → 单元匹配 → 模板填充 → verify_code 三层自校验 → 固化 JSON → 固化直出
验证：①四域组合生成+自校验 ②域识别 ③固化 ④固化直出 ⑤未识别诚实回落"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from code_compose import (domain_route, domain_solidify, detect_domain,
                          compose_domain_code, CODE_SOLIDIFIED, _SOL_FILE)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 四域组合生成 + 自校验（verify_code 三层）
QS = {
    "compiler": "写一个道德经指令编译单元（DAO→创建路径）",
    "pylang": "写一个闭包机制单元（捕获自由变量）",
    "graph": "写一个图遍历单元（BFS 可达节点）",
    "os": "写一个进程调度单元（FCFS 完成时间）",
}
ok_domains = 0
for domain, q in QS.items():
    d = detect_domain(q)
    r = domain_route(q)
    if d == domain and r.get("ok") and r.get("code"):
        ok_domains += 1
    check(f'① {domain} 域生成+自校验', d == domain and r.get("ok"),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:20]}')
check('① 四域全部生成', ok_domains == 4, f'{ok_domains}/4')

# ② 域识别
check('②a 域识别(编译器)', detect_domain("写个类型推断单元") == "compiler", '')
check('②b 域识别(操作系统)', detect_domain("写个内存分页分配") == "os", '')
check('②c 域识别(图)', detect_domain("写个条件路由图查询") == "graph", '')

# ③ 固化（自举纪律：验证通过才固化）
before = {k for k in CODE_SOLIDIFIED if k.startswith("domain:")}
e = domain_solidify("写一个闭包机制单元（捕获自由变量）")
check('③ 域固化', e is not None and e.get("source") == "domain_solidified",
      str(e.get("unit") if e else None))
after = {k for k in CODE_SOLIDIFIED if k.startswith("domain:")}
check('③b 固化写入JSON', len(after) > len(before), f'{len(after)} 域固化条目')

# ④ 固化直出
r2 = domain_route("写一个闭包机制单元（捕获自由变量）")
check('④ 固化直出', r2.get("solidified") is True
      and r2.get("unit") == e.get("unit"), f'unit={r2.get("unit")}')

# ⑤ 未识别诚实回落
r3 = domain_route("什么是碳中和？")
check('⑤ 域未识别回落', not r3.get("ok") and "域未识别" in r3.get("reason", ""),
      r3.get("reason", "")[:20])

# ⑥ 旧管线回归（基础 CODE_UNITS 不受影响）
from code_compose import code_route
r4 = code_route("写一个函数把数组从小到大排序")
check('⑥ 旧管线回归', r4.get("ok") and "def " in r4.get("code", ""), '')

print(f'\n=== 白箱自举正式管线（域接管）: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
