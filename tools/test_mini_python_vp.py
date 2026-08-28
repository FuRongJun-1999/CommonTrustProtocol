# -*- coding: utf-8 -*-
"""test_mini_python_vp.py · 编程语言完整版条件卡 V-P1~P3 验证用例（2026-08-28）

对照 docs/T11_完整版条件卡_其余六目标.md 目标 1 验证缺口清单：
- V-P1 错误处理语义：除零（/、//、%）/ 未定义变量 / 白名单外方法的报错形态统一
- V-P2 列表字典嵌套组合：排序+去重+统计一条龙（F6/F7 复合）
- V-P3 字符串方法族全覆盖：upper/split/startswith/endswith/strip/join（F5）
验证口径：对照 CPython 行为（外部校准），AST 与字节码 VM 双路对照。
注：P 线 Mini-Python 标识符为英文（CPython 对齐；中文语法属 C 线编译器域）。
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mini_python import run_program, eval_expr, eval_expr_vm, MiniPyError

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


def expect_error(name, src, prefix):
    """错误形态统一断言：MiniPyError 且消息以指定前缀开头。"""
    try:
        run_program(src)
        check(name, False, "未抛异常")
    except MiniPyError as e:
        check(name, str(e).startswith(prefix), f"got {e!r}")


# ============ V-P1 错误处理语义（报错形态统一） ============
expect_error("V-P1 真除零 /", "x = 1 / 0", "ZeroDivisionError: division by zero")
expect_error("V-P1 整除零 //", "x = 1 // 0", "ZeroDivisionError: integer division by zero")
expect_error("V-P1 取模零 %", "x = 1 % 0", "ZeroDivisionError: modulo by zero")
expect_error("V-P1 复合赋值 /= 零", "x = 5\nx /= 0", "ZeroDivisionError: division by zero")
expect_error("V-P1 函数内除零", "def f(n):\n    return n / 0\nr = f(3)",
             "ZeroDivisionError")
expect_error("V-P1 未定义变量读取", "x = y + 1", "NameError: name 'y' is not defined")
expect_error("V-P1 函数内未定义变量", "def f():\n    return missing\nr = f()",
             "NameError: name 'missing' is not defined")
expect_error("V-P1 白名单外方法", "s = 'a'\ns.contains('b')", "方法不在白名单")
expect_error("V-P1 非字符串调方法", "n = 3\nn.upper()", "不可调用")

# 除零消息形态统一：三路全为 ZeroDivisionError 前缀（错误可定位=显式报错形态）
forms = []
for src in ("x = 1 / 0", "x = 1 // 0", "x = 1 % 0"):
    try:
        run_program(src)
        forms.append("no-raise")
    except MiniPyError as e:
        forms.append(str(e).split(":")[0])
check("V-P1 三路除零错误形态统一", forms == ["ZeroDivisionError"] * 3, f"got {forms}")

# ============ V-P2 列表字典嵌套组合（排序+去重+统计一条龙） ============
env = run_program(
    "data = [3, 1, 2, 3, 1]\n"
    "uniq = []\n"
    "for x in sorted(data):\n"
    "    if not uniq or uniq[len(uniq) - 1] != x:\n"
    "        uniq.append(x)\n"
    "result = uniq")
check("V-P2 排序+去重", env.get("result") == [1, 2, 3], f"got {env.get('result')!r}")

env = run_program(
    "data = ['b', 'a', 'b']\n"
    "count = {}\n"
    "for x in data:\n"
    "    count[x] = count.get(x, 0) + 1\n"
    "result = count['b']")
check("V-P2 字典计数统计", env.get("result") == 2, f"got {env.get('result')!r}")

env = run_program(
    "scores = [88, 72, 95]\n"
    "ranked = sorted(scores)\n"
    "result = ranked[len(ranked) - 1]")
check("V-P2 嵌套索引取最大", env.get("result") == 95, f"got {env.get('result')!r}")
# V-P4 kwargs 已落地（2026-08-28 第二批）：原挂账实证用例翻转为正向断言
check("V-P4 kwargs 原缺口已闭合", eval_expr("sorted([2, 1], reverse=True)") == [2, 1])

env = run_program(
    "freq = {'a': 3, 'b': 1}\n"
    "freq['c'] = 2\n"
    "total = 0\n"
    "for k in freq:\n"
    "    total = total + freq[k]\n"
    "result = total")
check("V-P2 字典遍历求和", env.get("result") == 6, f"got {env.get('result')!r}")

# 双路对照（AST / VM 同值）
expr = "[3, 1, 2][1] + len([9, 9])"
check("V-P2 双路对照 AST/VM", eval_expr(expr) == eval_expr_vm(expr) == 3,
      f"AST={eval_expr(expr)} VM={eval_expr_vm(expr)}")

# ============ V-P3 字符串方法族全覆盖（F5：upper/split/startswith/endswith/strip/join） ============
check("V-P3 upper", eval_expr("'abc'.upper()") == "ABC")
check("V-P3 split 默认", eval_expr("'a b c'.split()") == ["a", "b", "c"])
check("V-P3 split 分隔符", eval_expr("'a,b,c'.split(',')") == ["a", "b", "c"])
check("V-P3 startswith 真", eval_expr("'hello'.startswith('he')") is True)
check("V-P3 startswith 假", eval_expr("'hello'.startswith('lo')") is False)
check("V-P3 endswith 真", eval_expr("'hello'.endswith('lo')") is True)
check("V-P3 endswith 假", eval_expr("'hello'.endswith('he')") is False)
check("V-P3 strip 两端", eval_expr("'  hi  '.strip()") == "hi")
check("V-P3 strip 指定字符", eval_expr("'xxhixx'.strip('x')") == "hi")
check("V-P3 join 列表", eval_expr("','.join(['a', 'b', 'c'])") == "a,b,c")

# 程序级（run_program 路径）+ VM 双路
env = run_program("s = ' Hello World '\nresult = s.strip().upper()")
check("V-P3 方法链（程序级）", env.get("result") == "HELLO WORLD", f"got {env.get('result')!r}")
check("V-P3 双路对照 startswith",
      eval_expr("'白箱'.startswith('白')") == eval_expr_vm("'白箱'.startswith('白')") is True)

try:
    eval_expr("','.join([1, 2])")
    check("V-P3 join 非字符串元素报错", False, "未抛异常")
except (MiniPyError, TypeError):
    check("V-P3 join 非字符串元素报错", True)

# ============ V-P4（部分落地 2026-08-28）：in / not in 成员运算符 ============
check("V-P4 in str", eval_expr("'ell' in 'hello'") is True)
check("V-P4 in list", eval_expr("2 in [1, 2, 3]") is True)
check("V-P4 not in", eval_expr("9 not in [1, 2, 3]") is True)
check("V-P4 in dict 键", eval_expr("'a' in {'a': 1}") is True)
check("V-P4 VM 双路", eval_expr_vm("9 not in [1, 2, 3]") is True)
env = run_program("words = ['ab', 'cd']\ncount = 0\nfor w in words:\n    if 'a' in w:\n        count += 1\nresult = count")
check("V-P4 程序级成员判断", env.get("result") == 1, f"got {env.get('result')!r}")

# ============ V-P4（第二批 2026-08-28）：关键字参数 kwargs ============
check("V-P4 kwargs sorted reverse", eval_expr("sorted([3, 1, 2], reverse=True)") == [3, 2, 1])
check("V-P4 VM kwargs", eval_expr_vm("sorted([3, 1, 2], reverse=True)") == [3, 2, 1])
check("V-P4 内置函数作值 key=len",
      eval_expr("sorted(['bb', 'a', 'ccc'], key=len)") == ["a", "bb", "ccc"])
env = run_program("data = [3, 1, 2]\nresult = sorted(data, reverse=True)[0]")
check("V-P4 程序级 kwargs", env.get("result") == 3, f"got {env.get('result')!r}")
try:
    eval_expr("len(x=1)")
    check("V-P4 非法 kwarg 显式报错", False, "未抛异常")
except (MiniPyError, TypeError):
    check("V-P4 非法 kwarg 显式报错", True)

# ============ V-P4（第三批 2026-08-29）：def 默认参数 + 自定义函数关键字调用 ============
env = run_program("def f(a, b=10):\n    return a + b\nr1 = f(1)\nr2 = f(1, 2)\nr3 = f(1, b=5)")
check("V-P4 默认参数省略", env.get("r1") == 11, f"got {env.get('r1')!r}")
check("V-P4 位置覆盖默认", env.get("r2") == 3)
check("V-P4 关键字覆盖默认", env.get("r3") == 6)
env = run_program("def area(w, h=2):\n    return w * h\nresult = area(3, h=4)")
check("V-P4 位置+关键字混合", env.get("result") == 12)
env = run_program("def rec(n, acc=1):\n    if n <= 1:\n        return acc\n    return rec(n - 1, acc * n)\nresult = rec(5)")
check("V-P4 递归+默认累加器", env.get("result") == 120)
try:
    run_program("def f(a):\n    return a\nr = f()")
    check("V-P4 缺参显式报错", False, "未抛异常")
except MiniPyError:
    check("V-P4 缺参显式报错", True)

# 白名单边界显式：contains 确认不可用（str 无 .contains，须走 in 运算符）
try:
    eval_expr("'a'.contains('a')")
    check("V-P3 白名单边界（contains 拒绝）", False, "未抛异常")
except MiniPyError:
    check("V-P3 白名单边界（contains 拒绝）", True)

# ============ 判定 ============
print("\n=== 判定 ===")
print(f"V-P1~P3 验证用例: {pass_n}/{pass_n + fail_n}（对照 CPython 行为）")
sys.exit(0 if fail_n == 0 else 1)
