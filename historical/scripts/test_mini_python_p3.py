# -*- coding: utf-8 -*-
"""test_mini_python_p3.py · Mini-Python P3 测试（第六阶段·函数+作用域+递归）
验证：①函数定义+调用 ②参数绑定 ③return 值 ④递归（阶乘/斐波那契）⑤作用域隔离
⑥参数数量错误 ⑦CPython 对照"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from mini_python import run_program, MiniPyError

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 函数定义+调用
env = run_program("""
def add(a, b):
    return a + b
r = add(2, 3)
""")
check('① 函数调用', env.get("r") == 5, f'r={env.get("r")}')

# ② 参数绑定 + 多参数
env = run_program("""
def mul3(a, b, c):
    return a * b * c
r = mul3(2, 3, 4)
""")
check('② 多参数', env.get("r") == 24, f'r={env.get("r")}')

# ③ return 值（含表达式）
env = run_program("""
def square(x):
    return x * x
r = square(7)
""")
check('③ return 表达式', env.get("r") == 49, f'r={env.get("r")}')

# ④ 递归：阶乘 + 斐波那契
env = run_program("""
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)
r = fact(5)
""")
check('④a 递归阶乘', env.get("r") == 120, f'r={env.get("r")}')
env = run_program("""
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
r = fib(7)
""")
check('④b 递归斐波那契', env.get("r") == 13, f'r={env.get("r")}')

# ⑤ 作用域隔离：函数内变量不泄漏
env = run_program("""
def f():
    tmp = 99
    return tmp
r = f()
""")
check('⑤a 函数内变量', env.get("r") == 99, f'r={env.get("r")}')
try:
    env.get("tmp")
    check('⑤b 变量不泄漏', False, 'tmp 泄漏到全局')
except MiniPyError:
    check('⑤b 变量不泄漏', True, '')

# ⑥ 参数数量错误
try:
    run_program("def f(a):\n    return a\nr = f()\n")
    check('⑥ 参数数量错误', False, '未报错')
except MiniPyError as e:
    check('⑥ 参数数量错误', "参数数量不符" in str(e), str(e))

# ⑦ CPython 对照（固定小程序）
def cpython_run(src):
    ns = {}
    exec(src, ns)
    return ns

PROGS = [
    ("def add(a, b):\n    return a + b\nr = add(2, 3)\n", ["r"]),
    ("def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\nr = fact(5)\n", ["r"]),
    ("def fib(n):\n    if n <= 1:\n        return n\n    return fib(n - 1) + fib(n - 2)\nr = fib(7)\n", ["r"]),
]
all_match = True
for src, keys in PROGS:
    mine = run_program(src)
    ref = cpython_run(src)
    for k in keys:
        if mine.get(k) != ref[k]:
            all_match = False
            print(f"    对照不符: {k} mine={mine.get(k)!r} cp={ref[k]!r}")
check('⑦ CPython 对照 3 程序', all_match, f'{len(PROGS)} 程序')

print(f'\n=== Mini-Python P3 测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
