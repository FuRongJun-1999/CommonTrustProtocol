# -*- coding: utf-8 -*-
"""test_se_compose.py · 软件工程概念测试（第四阶段·代码深学）
验证：①六概念组合生成 ②概念核心词自校验 ③非软件问题回落"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from se_compose import se_route, identify_se_direction

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 六概念组合生成
QS = {
    "为什么大型程序要模块化？": ("模块", "独立"),
    "什么是接口？": ("接口", "隔离"),
    "为什么要写单元测试？": ("测试", "回归"),
    "什么是重构？": ("重构", "行为"),
    "为什么代码要封装？": ("封装", "隐藏"),
    "为什么要用版本控制？": ("版本", "回滚"),
}
for q, (kw1, kw2) in QS.items():
    r = se_route(q)
    ans = r.get("answer", "")
    ok = r.get("ok") and kw1 in ans and kw2 in ans
    check(f'① 概念生成: {q[:12]}…', ok, ans[:36])

# ② 方向识别
check('②a 模块识别', identify_se_direction("为什么程序要模块化") == "模块")
check('②b 测试识别', identify_se_direction("单元测试有什么用") == "测试")

# ③ 非软件问题回落
r = se_route("什么是碳中和？")
check('③ 非软件工程问题回落', not r.get("ok") and "落回" in r.get("reason", ""))

print(f'\n=== 软件工程概念测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
