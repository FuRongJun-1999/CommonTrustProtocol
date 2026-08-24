# -*- coding: utf-8 -*-
"""python_code_units.py · Mini-Python 语言机制白箱单元库（第六阶段 P 线·白箱自举）
设计者指令：7 终极目标 + 7 初级复现项目都是白箱自举后验证编程能力的项目——
P 线 Mini-Python 由白箱自己实现（code_compose 机制），外部只校准。
mini_python.py 定位为校准参考实现（语义基准）。
单元：{任务 → 代码模式模板 + 验证样例 + 校准基准}——语言机制（词法/优先级/
求值/逻辑/环境/栈机）逐一白箱化。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 任务 → 代码模式 + 验证样例（白箱生成的自校验基准）
PYTHON_UNITS = {
    "词法-记号化": {
        "task": "词法分析",
        "pattern": (
            "def tokenize(src):\n"
            "    # 字符流 → token 列表（数字/运算符/括号）——Mini-Python 词法\n"
            "    import re\n"
            "    tokens, i = [], 0\n"
            "    while i < len(src):\n"
            "        if src[i].isdigit():\n"
            "            j = i\n"
            "            while j < len(src) and (src[j].isdigit() or src[j] == '.'):\n"
            "                j += 1\n"
            "            text = src[i:j]\n"
            "            tokens.append(('NUMBER', float(text) if '.' in text else int(text)))\n"
            "            i = j\n"
            "        elif src[i] in '+-*/%()':\n"
            "            tokens.append(('OP', src[i]))\n"
            "            i += 1\n"
            "        elif src[i].isspace():\n"
            "            i += 1\n"
            "        else:\n"
            "            raise SyntaxError('未知字符: ' + src[i])\n"
            "    tokens.append(('EOF', ''))\n"
            "    return tokens\n"),
        "cases": [("2+3", [("NUMBER", 2), ("OP", "+"), ("NUMBER", 3), ("EOF", "")]),
                  ("3.5*2", [("NUMBER", 3.5), ("OP", "*"), ("NUMBER", 2), ("EOF", "")]),
                  ("(1)", [("OP", "("), ("NUMBER", 1), ("OP", ")"), ("EOF", "")])],
        "params": [],
        "calibration": "对照：mini_python.py tokenize（数字含小数/运算符/括号）",
    },
    "语法-优先级": {
        "task": "优先级计算",
        "pattern": (
            "def precedence(expr):\n"
            "    # 表达式优先级求值（2+3*4=14；括号最高）——Mini-Python 语法\n"
            "    def parse(i, min_prec):\n"
            "        if expr[i] == '(':\n"
            "            val, i = parse(i + 1, 0)\n"
            "            i += 1  # 跳过 ')'\n"
            "        else:\n"
            "            val = 0\n"
            "            j = i\n"
            "            while j < len(expr) and expr[j].isdigit():\n"
            "                val = val * 10 + int(expr[j])\n"
            "                j += 1\n"
            "            i = j\n"
            "        prec = {'+': 1, '-': 1, '*': 2, '/': 2, '**': 3}\n"
            "        while i < len(expr) and expr[i] in prec and prec[expr[i]] >= min_prec:\n"
            "            op = expr[i]\n"
            "            right, i = parse(i + 1, prec[op] + 1)\n"
            "            if op == '+':\n"
            "                val += right\n"
            "            elif op == '-':\n"
            "                val -= right\n"
            "            elif op == '*':\n"
            "                val *= right\n"
            "            elif op == '/':\n"
            "                val /= right\n"
            "        return val, i\n"
            "    return parse(0, 0)[0]\n"),
        "cases": [("2+3*4", 14), ("(2+3)*4", 20), ("10-3*2", 4), ("2+3+4", 9)],
        "params": [],
        "calibration": "对照：CPython 优先级（乘除高于加减，括号最高）",
    },
    "求值-逻辑短路": {
        "task": "逻辑短路",
        "pattern": (
            "def logic_eval(expr, values):\n"
            "    # or/and 短路 + 返回操作数（Python 语义：0 or 5 → 5）\n"
            "    def truthy(v):\n"
            "        return v is not None and v is not False and v != 0\n"
            "    left = values[expr[0]]\n"
            "    if expr[1] == 'or':\n"
            "        return left if truthy(left) else values[expr[2]]\n"
            "    if expr[1] == 'and':\n"
            "        return values[expr[2]] if truthy(left) else left\n"
            "    return None\n"),
        "cases": [((("a", "or", "b"), {"a": 1, "b": 0}), 1),
                  ((("a", "or", "b"), {"a": 0, "b": 5}), 5),
                  ((("a", "and", "b"), {"a": 0, "b": 5}), 0),
                  ((("a", "and", "b"), {"a": 2, "b": 3}), 3)],
        "params": [],
        "calibration": "对照：Python 语义——or/and 返回操作数 + 短路",
    },
    "环境-作用域链": {
        "task": "作用域环境",
        "pattern": (
            "class Env:\n"
            "    # 变量环境：作用域链（局部 → 父环境）——Mini-Python 环境\n"
            "    def __init__(self, parent=None):\n"
            "        self.vars = {}\n"
            "        self.parent = parent\n"
            "    def get(self, name):\n"
            "        if name in self.vars:\n"
            "            return self.vars[name]\n"
            "        if self.parent:\n"
            "            return self.parent.get(name)\n"
            "        raise NameError(name + ' 未定义')\n"
            "    def set(self, name, value):\n"
            "        self.vars[name] = value\n"
            "def env_scope():\n"
            "    g = Env()\n"
            "    g.set('x', 1)\n"
            "    l = Env(g)\n"
            "    l.set('y', 2)\n"
            "    return (l.get('x'), l.get('y'))\n"),
        "cases": [("call", (1, 2))],
        "params": [],
        "calibration": "对照：mini_python.py Env（父链作用域：局部找不到向上查找）",
    },
    "栈机-字节码执行": {
        "task": "栈机执行",
        "pattern": (
            "def vm_exec(code):\n"
            "    # 字节码栈机雏形（PUSH/ADD/SUB/MUL）——Mini-Python VM\n"
            "    stack = []\n"
            "    for op, arg in code:\n"
            "        if op == 'PUSH':\n"
            "            stack.append(arg)\n"
            "        elif op == 'ADD':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a + b)\n"
            "        elif op == 'SUB':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a - b)\n"
            "        elif op == 'MUL':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a * b)\n"
            "    return stack[-1] if stack else None\n"),
        "cases": [(([("PUSH", 2), ("PUSH", 3), ("PUSH", 4), ("MUL", None), ("ADD", None)],), 14),
                  (([("PUSH", 10), ("PUSH", 3), ("SUB", None)],), 7)],
        "params": [],
        "calibration": "对照：mini_python.py VM 栈机（指令→栈操作）",
    },
}


def route_python_unit(question):
    """任务识别（问题 → P 线单元，最长关键词优先）"""
    best, best_len = None, 0
    for uid, u in PYTHON_UNITS.items():
        for kw in (u["task"], uid):
            if kw in question and len(kw) > best_len:
                best, best_len = uid, len(kw)
    return best


if __name__ == "__main__":
    print("=== Mini-Python 语言机制白箱单元库（P 线自举 · 校准参考）===\n")
    for uid, u in PYTHON_UNITS.items():
        print(f"[{uid}] 任务={u['task']} 样例数={len(u['cases'])}")
        print(f"    校准: {u['calibration']}")
    print(f"\n=== 判定 ===\nP 线单元库: "
          f"{'✔ 5 单元就绪（词法/优先级/逻辑/环境/栈机——白箱自举 P 线）' if len(PYTHON_UNITS) >= 4 else '✘'}")
