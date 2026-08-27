# -*- coding: utf-8 -*-
"""test_multilang_code.py · 多语言代码生成测试（第四阶段·代码深学）
验证：①语言识别（rust/js/python）②Rust 排序/求和/最大（结构+逻辑校验）
③JavaScript 排序/求和/反转 ④Python 回归 ⑤逻辑错误自校验（py_ref 样例）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import code_compose as cc

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 语言识别
check('①a rust 识别', cc.detect_language("用rust写排序") == "rust")
check('①b js 识别', cc.detect_language("用js写求和") == "javascript")
check('①c python 默认', cc.detect_language("写一个函数排序") == "python")

# ② Rust 生成+校验
r = cc.code_route("用rust写一个函数把数组从小到大排序")
ok = r.get("ok") and r.get("lang") == "rust" and "fn " in r.get("code", "")
check('②a Rust 排序生成+结构校验', ok, r.get("code", "")[:30].replace(chr(10), " "))
r2 = cc.code_route("用rust写一个函数把数组加起来求和")
check('②b Rust 求和', r2.get("ok") and "iter().sum()" in r2.get("code", ""))
r3 = cc.code_route("用rust写一个函数找最大值")
check('②c Rust 最大值', r3.get("ok") and "max()" in r3.get("code", ""))

# ③ JavaScript
r4 = cc.code_route("用js写一个函数把数组从小到大排序")
check('③a JS 排序', r4.get("ok") and "function " in r4.get("code", "")
      and "sort" in r4.get("code", ""))
r5 = cc.code_route("用javascript写一个函数求和")
check('③b JS 求和', r5.get("ok") and "reduce" in r5.get("code", ""))
r6 = cc.code_route("用js写一个函数把列表反转")
check('③c JS 反转', r6.get("ok") and "reverse" in r6.get("code", ""))

# ④ Python 回归
r7 = cc.code_route("写一个函数把数组从小到大排序")
check('④ Python 排序回归', r7.get("ok") and r7.get("lang") == "python")

# ⑤ 逻辑错误自校验（py_ref 样例抓住）
bad_unit = {
    "task": "求和", "lang": "rust",
    "pattern": "fn solve(arr: &[i32]) -> i32 {\n    arr.iter().sum::<i32>() + 1\n}\n",
    "cases": [([1, 2, 3], 6), ([], 0)],
    "py_ref": "def solve(arr): return sum(arr) + 1\n",  # 逻辑错（+1）
}
ok5, checks5 = cc.verify_code(bad_unit["pattern"], bad_unit, "rust")
check('⑤ Rust 逻辑错误被 py_ref 样例抓住', not ok5, checks5[0][:40])

print(f'\n=== 多语言代码生成测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
