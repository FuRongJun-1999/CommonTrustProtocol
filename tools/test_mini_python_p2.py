# -*- coding: utf-8 -*-
"""test_mini_python_p2.py · Mini-Python P2 测试（第六阶段·变量环境+控制流）
验证：①赋值+变量读取 ②while 循环 ③if/else ④嵌套 ⑤未定义变量错误 ⑥CPython 对照"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from mini_python import run_program, Env, MiniPyError

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 赋值 + 变量读取
env = run_program("x = 3\ny = x + 2\n")
check('① 赋值+读取', env.get("x") == 3 and env.get("y") == 5,
      f'x={env.get("x")} y={env.get("y")}')

# ② while 循环（求和 0..4）
env = run_program("""
s = 0
i = 0
while i < 5:
    s = s + i
    i = i + 1
""")
check('② while 求和', env.get("s") == 10 and env.get("i") == 5,
      f's={env.get("s")} i={env.get("i")}')

# ③ if/else
env = run_program("""
a = 7
if a > 5:
    r = 1
else:
    r = 0
""")
check('③a if 真分支', env.get("r") == 1, f'r={env.get("r")}')
env = run_program("""
a = 3
if a > 5:
    r = 1
else:
    r = 0
""")
check('③b if else 分支', env.get("r") == 0, f'r={env.get("r")}')

# ④ 嵌套（while 内 if）
env = run_program("""
n = 0
c = 0
while n < 6:
    if n % 2 == 0:
        c = c + 1
    n = n + 1
""")
check('④ 嵌套(偶数计数)', env.get("c") == 3, f'c={env.get("c")}')

# ⑤ 未定义变量错误
try:
    run_program("x = y\n")
    check('⑤ 未定义变量', False, '未报错')
except MiniPyError as e:
    check('⑤ 未定义变量', "not defined" in str(e), str(e))

# ⑥ CPython 对照（固定小程序 exec 后变量对照）
def cpython_run(src):
    ns = {}
    exec(src, ns)
    return ns

PROGS = [
    ("x = 0\nwhile x < 5:\n    x = x + 1\n", ["x"]),
    ("a = 7\nif a > 5:\n    r = 1\nelse:\n    r = 0\n", ["r"]),
    ("s = 0\ni = 0\nwhile i < 5:\n    s = s + i\n    i = i + 1\n", ["s", "i"]),
    ("n = 0\nc = 0\nwhile n < 6:\n    if n % 2 == 0:\n        c = c + 1\n    n = n + 1\n", ["c"]),
]
all_match = True
for src, keys in PROGS:
    mine = run_program(src)
    ref = cpython_run(src)
    for k in keys:
        if mine.get(k) != ref[k] or type(mine.get(k)) is not type(ref[k]):
            all_match = False
            print(f"    对照不符: {k} mine={mine.get(k)!r} cp={ref[k]!r}")
check('⑥ CPython 对照 4 程序', all_match, f'{len(PROGS)} 程序')

print(f'\n=== Mini-Python P2 测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
