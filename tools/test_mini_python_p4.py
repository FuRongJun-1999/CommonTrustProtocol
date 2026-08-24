# -*- coding: utf-8 -*-
"""test_mini_python_p4.py · Mini-Python P4 测试（第六阶段·闭包+高阶函数）
验证：①闭包捕获自由变量 ②独立捕获（多实例）③函数作参数 ④嵌套闭包
⑤函数返回值调用 ⑥CPython 对照
诚实边界：call 的 func 为名字（不支持链式 make_adder(3)(4)，需变量中转）"""
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

# ① 闭包捕获自由变量（make_adder）
env = run_program("""
def make_adder(n):
    def add(x):
        return x + n
    return add
a = make_adder(3)
r = a(4)
""")
check('① 闭包捕获自由变量', env.get("r") == 7, f'r={env.get("r")}')

# ② 独立捕获（多实例互不干扰）
env = run_program("""
def make_adder(n):
    def add(x):
        return x + n
    return add
a = make_adder(3)
b = make_adder(10)
r1 = a(1)
r2 = b(1)
""")
check('② 独立捕获', env.get("r1") == 4 and env.get("r2") == 11,
      f'r1={env.get("r1")} r2={env.get("r2")}')

# ③ 函数作参数（apply）
env = run_program("""
def square(x):
    return x * x
def apply(f, x):
    return f(x)
r = apply(square, 6)
""")
check('③ 函数作参数', env.get("r") == 36, f'r={env.get("r")}')

# ④ 嵌套闭包（两层捕获，变量中转——链式 make_mul(2)(3) 是诚实边界不支持）
env = run_program("""
def make_mul(a):
    def inner(b):
        def innermost(c):
            return a * b * c
        return innermost
    return inner
i = make_mul(2)
m = i(3)
r = m(4)
""")
check('④ 嵌套闭包(变量中转)', env.get("r") == 24, f'r={env.get("r")}')

# ⑤ 闭包返回值再调用（变量中转，诚实边界）
env = run_program("""
def make_counter():
    def inc():
        return 1
    return inc
f = make_counter()
r = f()
""")
check('⑤ 闭包返回值调用', env.get("r") == 1, f'r={env.get("r")}')

# ⑥ CPython 对照
def cpython_run(src):
    ns = {}
    exec(src, ns)
    return ns

PROGS = [
    ("def make_adder(n):\n    def add(x):\n        return x + n\n    return add\na = make_adder(3)\nr = a(4)\n", ["r"]),
    ("def square(x):\n    return x * x\ndef apply(f, x):\n    return f(x)\nr = apply(square, 6)\n", ["r"]),
    ("def make_adder(n):\n    def add(x):\n        return x + n\n    return add\na = make_adder(3)\nb = make_adder(10)\nr1 = a(1)\nr2 = b(1)\n", ["r1", "r2"]),
]
all_match = True
for src, keys in PROGS:
    mine = run_program(src)
    ref = cpython_run(src)
    for k in keys:
        if mine.get(k) != ref[k]:
            all_match = False
            print(f"    对照不符: {k} mine={mine.get(k)!r} cp={ref[k]!r}")
check('⑥ CPython 对照 3 程序', all_match, f'{len(PROGS)} 程序')

print(f'\n=== Mini-Python P4 测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
