# -*- coding: utf-8 -*-
"""test_mini_python_t4.py · T4 Mini-Python 增强族单元测试
任务书 T4 规范：+= 复合赋值 / print 多参 / str 方法（upper/split）。
验证口径：对照 CPython 行为（外部校准），AST 与字节码 VM 双路对照。
"""
import sys, os, io, contextlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mini_python import run_program, eval_expr, eval_expr_vm, MiniPyError

pass_n = fail_n = 0
def check(name, ok, detail=''):
    """断言登记：通过/失败计数并打印结果行。"""
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


# ============ 一、+= 复合赋值 ============
env = run_program("x = 1\nx += 2")
check("aug += 整数", env.get("x") == 3, f"got {env.get('x')!r}")

env = run_program("s = 'a'\ns += 'b'")
check("aug += 字符串拼接", env.get("s") == "ab", f"got {env.get('s')!r}")

env = run_program("x = 10\nx -= 4\nx *= 3")
check("aug -= 与 *= 链", env.get("x") == 18, f"got {env.get('x')!r}")

env = run_program("x = 10\nx /= 4")
check("aug /= 真除(float)", env.get("x") == 2.5 and isinstance(env.get("x"), float),
      f"got {env.get('x')!r}")

try:
    run_program("x = 1\nx /= 0")
    check("aug /= 除零抛错", False, "未抛异常")
except MiniPyError as e:
    check("aug /= 除零抛错", "ZeroDivisionError" in str(e), str(e))

env = run_program("def inc(n):\n    n += 1\n    return n\nr = inc(5)")
check("aug 函数内局部作用域", env.get("r") == 6, f"got {env.get('r')!r}")

env = run_program("total = 0\nfor i in range(5):\n    total += i")
check("aug for 内累加（典型用例）", env.get("total") == 10, f"got {env.get('total')!r}")

env = run_program("x = 5\nx += 2 * 3")
check("aug 右侧完整表达式", env.get("x") == 11, f"got {env.get('x')!r}")

# ============ 二、print 多参 ============
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    run_program('print("a", 1, 2)')
check("print 多参空格分隔（CPython sep 默认）", buf.getvalue() == "a 1 2\n",
      f"got {buf.getvalue()!r}")

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    run_program('x = 7\nprint("x =", x)')
check("print 标签+变量", buf.getvalue() == "x = 7\n", f"got {buf.getvalue()!r}")

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    run_program('print()')
check("print 零参（空行）", buf.getvalue() == "\n", f"got {buf.getvalue()!r}")

# ============ 三、str 方法（upper/split） ============
env = run_program("s = 'hello'\nu = s.upper()")
check("str.upper()", env.get("u") == "HELLO", f"got {env.get('u')!r}")

env = run_program("parts = 'a,b,c'.split(',')" if False else
                  "s = 'a,b,c'\nparts = s.split(',')")
check("str.split(',')", env.get("parts") == ["a", "b", "c"], f"got {env.get('parts')!r}")

env = run_program("s = 'a,b,c'\nfirst = s.split(',')[0]")
check("split 后索引链 [0]", env.get("first") == "a", f"got {env.get('first')!r}")

env = run_program("def shout(w):\n    return w.upper()\nr = shout('ok')")
check("方法在函数体内调用", env.get("r") == "OK", f"got {env.get('r')!r}")

try:
    run_program("s = 'x'\ns.foo()")
    check("方法白名单外拒绝", False, "未抛异常")
except MiniPyError as e:
    check("方法白名单外拒绝", "白名单" in str(e), str(e))

# ============ 四、AST 与字节码 VM 双路对照 ============
for src, expect in [
    ("1 + 2 + 3", 6),
    ("(1 + 2) * 3", 9),
]:
    a = eval_expr(src)
    b = eval_expr_vm(src)
    check(f"双路对照 {src!r}", a == b == expect, f"ast={a!r} vm={b!r}")

# 方法调用 VM 路径
import mini_python as mp
_env = mp.Env()
_env.set("s", "hello")
ast_n = mp.Parser(mp.tokenize("s.upper()")).parse()
vm_code = mp.compile_expr(ast_n)
vm_val = mp.VM(_env).run(vm_code)
check("VM CALL_METHOD upper()", vm_val == "HELLO", f"got {vm_val!r}")

print(f"\n=== 判定 ===\nT4 增强族: {pass_n}/{pass_n + fail_n}"
      f"（对照 CPython 行为）")
sys.exit(0 if fail_n == 0 else 1)
