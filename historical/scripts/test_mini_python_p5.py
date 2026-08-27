# -*- coding: utf-8 -*-
"""test_mini_python_p5.py · Mini-Python P5 测试（第六阶段·数据结构 + 字节码 VM 雏形）
验证：①list 字面量+索引 ②dict 字面量+索引 ③字节码 VM 求值对照 eval_node
④逻辑短路 VM ⑤调用 VM ⑥CPython 对照"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from mini_python import (run_program, eval_expr, eval_expr_vm, Env,
                         MiniPyError, compile_expr, VM)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① list 字面量 + 索引
env = run_program("a = [1, 2, 3]\nr = a[1]\n")
check('①a list 字面量+索引', env.get("r") == 2 and env.get("a") == [1, 2, 3],
      f'r={env.get("r")} a={env.get("a")}')
env = run_program("a = [1, 2, 3]\nr = a[-1]\n")
check('①b 负索引', env.get("r") == 3, f'r={env.get("r")}')

# ② dict 字面量 + 索引
env = run_program("d = {'甲': 1, '乙': 2}\nr = d['乙']\n")
check('② dict 字面量+索引', env.get("r") == 2 and env.get("d") == {"甲": 1, "乙": 2},
      f'r={env.get("r")}')

# ③ 字节码 VM 对照 eval_node（算术/比较/变量/数据结构）
PAIRS = [
    ("2+3*4", None), ("(2+3)*4", None), ("-2**2", None), ("10//3", None),
    ("-7%2", None), ("3>2", None), ("not 1>2", None),
]
all_ok = True
for src, _ in PAIRS:
    try:
        m = eval_expr(src)
        v = eval_expr_vm(src)
        if m != v or type(m) is not type(v):
            all_ok = False
            print(f"    VM 不符: {src} eval={m!r} vm={v!r}")
    except Exception as e:
        all_ok = False
        print(f"    {src} 异常: {e}")
check('③ 字节码VM对照eval_node', all_ok, f'{len(PAIRS)} 表达式')

# ③b 变量环境 VM
env = Env()
env.set("x", 5)
check('③b VM 变量读取', eval_expr_vm("x + 2", env) == 7,
      f'vm={eval_expr_vm("x + 2", env)}')

# ④ 逻辑短路 VM
check('④a VM 短路 or', eval_expr_vm("1 or 2") == 1, '')
check('④b VM 短路 and', eval_expr_vm("0 and 5") == 0, '')
try:
    eval_expr_vm("True or 1/0")
    check('④c VM or 短路不除零', True, '')
except MiniPyError:
    check('④c VM or 短路不除零', False, '除零了')

# ⑤ VM 调用
env = run_program("def square(x):\n    return x * x\nr = square(6)\n")
import mini_python as mp
code = mp.compile_expr(mp.Parser(mp.tokenize("square(6)")).parse())
vm = VM(env)
check('⑤ VM 函数调用', vm.run(code) == 36, f'vm={vm.run(code)}')

# ⑥ CPython 对照（list/dict 程序）
def cpython_run(src):
    ns = {}
    exec(src, ns)
    return ns
prog6 = "a = [1, 2, 3]\nr = a[1]\n"
mine = run_program(prog6)
ref = cpython_run(prog6)
check('⑥ CPython 对照(list)', mine.get("r") == ref["r"], f'r={mine.get("r")}')

print(f'\n=== Mini-Python P5 测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
