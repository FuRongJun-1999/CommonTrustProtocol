# -*- coding: utf-8 -*-
"""mini_python.py · Mini-Python 解释器（第六阶段 P1·机制训练场）
P1：词法 + 语法 + 表达式求值（对照 CPython 行为，P 线校准参考实现）
  - or/and 返回操作数 + 短路；/ 返回 float；// % floor；** 右结合高优先级
  - 除零抛 MiniPyError；链式比较；一元负号；-2**2 = -4
机制训练场：词法/AST/求值 机制供 C 线原生后端复用（语义不照抄——中文编译器走智能论语义）。
"""
import sys
import re
sys.stdout.reconfigure(encoding='utf-8')


class MiniPyError(Exception):
    """运行时错误（除零等）"""


# ============ 一、词法分析 ============
_TOKEN_RE = [
    ("NUMBER", r"\d+\.\d+|\d+"),
    ("OP", r"\*\*|//|==|!=|<=|>=|[+\-*/%<>()=]"),
    ("KEY", r"and|or|not|True|False|None|if|elif|else|while"),
    ("NAME", r"[A-Za-z_]\w*"),
    ("WS", r"\s+"),
]


def tokenize(src):
    """字符流 → token 列表（数字/运算符/关键字/括号）"""
    tokens, i = [], 0
    while i < len(src):
        for kind, pat in _TOKEN_RE:
            m = re.match(pat, src[i:])
            if m:
                text = m.group(0)
                i += len(text)
                if kind == "WS":
                    break
                if kind == "KEY":
                    tokens.append((text.upper(), text))
                elif kind == "NUMBER":
                    tokens.append(("NUMBER", float(text) if "." in text else int(text)))
                elif kind == "NAME":
                    tokens.append(("NAME", text))
                else:
                    tokens.append(("OP", text))
                break
        else:
            raise SyntaxError(f"词法错误：未知字符 '{src[i]}'（位置 {i}）")
    tokens.append(("EOF", ""))
    return tokens


# ============ 二、语法分析（递归下降，Python 优先级） ============
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def match(self, *texts):
        t = self.peek()
        if t[1] in texts:
            return self.advance()
        return None

    def expect(self, text):
        t = self.peek()
        if t[1] != text:
            raise SyntaxError(f"语法错误：期望 '{text}'，得到 '{t[1]}'")
        return self.advance()

    def parse(self):
        node = self.or_expr()
        if self.peek()[0] != "EOF":
            raise SyntaxError(f"语法错误：意外的 token '{self.peek()[1]}'")
        return node

    def or_expr(self):
        node = self.and_expr()
        while self.match("or"):
            node = ("or", node, self.and_expr())
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.match("and"):
            node = ("and", node, self.not_expr())
        return node

    def not_expr(self):
        if self.match("not"):
            return ("not", self.not_expr())
        return self.comparison()

    def comparison(self):
        node = self.arith()
        while True:
            t = self.peek()
            if t[1] in ("==", "!=", "<", ">", "<=", ">="):
                self.advance()
                node = (t[1], node, self.arith())
            else:
                return node

    def arith(self):
        node = self.term()
        while True:
            t = self.peek()
            if t[1] in ("+", "-"):
                self.advance()
                node = (t[1], node, self.term())
            else:
                return node

    def term(self):
        node = self.factor()
        while True:
            t = self.peek()
            if t[1] in ("*", "/", "//", "%"):
                self.advance()
                node = (t[1], node, self.factor())
            else:
                return node

    def factor(self):
        if self.peek()[1] in ("-", "+"):
            op = self.advance()[1]
            return (op, self.factor())  # 一元负号在外层：-2**2 = -(2**2)
        return self.power()

    def power(self):
        node = self.atom()
        if self.match("**"):
            return ("**", node, self.factor())  # 右结合
        return node

    def atom(self):
        t = self.peek()
        if t[0] == "NUMBER":
            self.advance()
            return ("num", t[1])
        if t[0] == "NAME":  # 变量名（P2：从环境取值）
            self.advance()
            return ("name", t[1])
        if t[1] == "True":
            self.advance()
            return ("bool", True)
        if t[1] == "False":
            self.advance()
            return ("bool", False)
        if t[1] == "None":
            self.advance()
            return ("none", None)
        if t[1] == "(":
            self.advance()
            node = self.or_expr()
            self.expect(")")
            return node
        raise SyntaxError(f"语法错误：意外的 token '{t[1]}'")


# ============ 三、求值（对照 CPython 行为） ============
def is_truthy(v):
    return v is not None and v is not False and v != 0


def eval_node(node, env=None):
    """AST 求值（P2：env 提供变量环境；name 节点从环境取值）"""
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "bool":
        return node[1]
    if kind == "none":
        return None
    if kind == "name":
        if env is None:
            raise MiniPyError(f"NameError: name '{node[1]}' is not defined")
        return env.get(node[1])
    if kind == "or":
        a = eval_node(node[1], env)
        return a if is_truthy(a) else eval_node(node[2], env)
    if kind == "and":
        a = eval_node(node[1], env)
        return eval_node(node[2], env) if is_truthy(a) else a
    if kind == "not":
        return not is_truthy(eval_node(node[1], env))
    if kind in ("==", "!=", "<", ">", "<=", ">="):
        return _compare(kind, eval_node(node[1], env), eval_node(node[2], env))
    if kind in ("-", "+") and len(node) == 2:  # 一元（先于二元判断）
        v = eval_node(node[1], env)
        return -v if kind == "-" else +v
    if kind == "+":
        return eval_node(node[1], env) + eval_node(node[2], env)
    if kind == "-":
        return eval_node(node[1], env) - eval_node(node[2], env)
    if kind == "*":
        return eval_node(node[1], env) * eval_node(node[2], env)
    if kind == "/":
        b = eval_node(node[2], env)
        if b == 0:
            raise MiniPyError("ZeroDivisionError: division by zero")
        return eval_node(node[1], env) / b
    if kind == "//":
        b = eval_node(node[2], env)
        if b == 0:
            raise MiniPyError("ZeroDivisionError: integer division by zero")
        a = eval_node(node[1], env)
        return int(a // b)  # floor（Python 语义）
    if kind == "%":
        b = eval_node(node[2], env)
        if b == 0:
            raise MiniPyError("ZeroDivisionError: modulo by zero")
        return eval_node(node[1], env) % b
    if kind == "**":
        return eval_node(node[1], env) ** eval_node(node[2], env)
    raise MiniPyError(f"未知节点: {node}")


def _compare(op, a, b):
    return {"==": a == b, "!=": a != b, "<": a < b, ">": a > b,
            "<=": a <= b, ">=": a >= b}[op]


def eval_expr(src):
    """表达式求值入口：源码 → 值（P1）"""
    tokens = tokenize(src)
    ast = Parser(tokens).parse()
    return eval_node(ast)


# ============ P2：变量环境 + 控制流（赋值/if/while，缩进块） ============
# 语句树：("assign", name, expr) / ("if", cond, then[], else[]) /
#         ("while", cond, body[]) / ("expr", expr)
# 缩进块解析：行 → (缩进, 语句) → 嵌套树

class Env:
    """变量环境（名实对应：变量名 → 值）"""
    def __init__(self):
        self.vars = {}

    def get(self, name):
        if name not in self.vars:
            raise MiniPyError(f"NameError: name '{name}' is not defined")
        return self.vars[name]

    def set(self, name, value):
        self.vars[name] = value


def parse_program(src):
    """源码 → 语句树（缩进决定嵌套）"""
    lines = []
    for raw in src.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw.strip()))
    # 缩进栈构建嵌套
    def build(idx, indent):
        stmts = []
        while idx[0] < len(lines):
            cur_indent, code = lines[idx[0]]
            if cur_indent < indent:
                break
            if cur_indent > indent:
                raise SyntaxError(f"意外的缩进：{code}")
            idx[0] += 1
            stmts.append(_parse_line(code, build, idx))
        return stmts

    def _parse_line(code, build, idx):
        # 赋值
        if "=" in code and not code.startswith(("if ", "while ", "elif ", "else")):
            name, expr = code.split("=", 1)
            return ("assign", name.strip(),
                    Parser(tokenize(expr)).parse())
        # if/elif/else
        if code.startswith("if "):
            cond = Parser(tokenize(code[3:].rstrip(":"))).parse()
            then_indent = lines[idx[0]][0] if idx[0] < len(lines) else 0
            then = build(idx, then_indent)
            else_stmts = []
            # else 配对：同缩进 else 行 → else 块
            if idx[0] < len(lines) and lines[idx[0]][1].startswith("else"):
                idx[0] += 1  # 消费 else 行
                else_indent = lines[idx[0]][0] if idx[0] < len(lines) else 0
                else_stmts = build(idx, else_indent)
            return ("if", cond, then, else_stmts)
        if code.startswith("while "):
            cond = Parser(tokenize(code[6:].rstrip(":"))).parse()
            body = build(idx, lines[idx[0]][0] if idx[0] < len(lines) else 0)
            return ("while", cond, body)
        if code.startswith(("else", "elif ")):
            raise SyntaxError("else/elif 未与 if 配对（意外的 else 行）")
        # 表达式语句
        return ("expr", Parser(tokenize(code)).parse())

    idx = [0]
    return build(idx, 0)


def exec_stmt(stmt, env):
    """执行单条语句（if/while 递归执行块）"""
    kind = stmt[0]
    if kind == "assign":
        env.set(stmt[1], eval_node(stmt[2], env))
    elif kind == "if":
        if is_truthy(eval_node(stmt[1], env)):
            for s in stmt[2]:
                exec_stmt(s, env)
        elif stmt[3]:
            for s in stmt[3]:
                exec_stmt(s, env)
    elif kind == "while":
        guard = 0
        while is_truthy(eval_node(stmt[1], env)) and guard < 10000:
            for s in stmt[2]:
                exec_stmt(s, env)
            guard += 1
    elif kind == "expr":
        eval_node(stmt[1], env)
    else:
        raise MiniPyError(f"未知语句: {stmt}")


def run_program(src):
    """程序执行：源码 → Env（P2：变量/if/while）"""
    env = Env()
    for stmt in parse_program(src):
        exec_stmt(stmt, env)
    return env


if __name__ == "__main__":
    print("=== Mini-Python P2：变量环境 + 控制流（对照 CPython）===\n")
    prog = """
x = 0
while x < 5:
    x = x + 1
if x == 5:
    y = 10
else:
    y = 0
"""
    env = run_program(prog)
    print(f"① 程序执行后: x={env.get('x')} y={env.get('y')}")
    ok = env.get("x") == 5 and env.get("y") == 10
    print(f"\n=== 判定 ===\n变量+控制流: {'✔ 循环/条件/赋值成立（对照 CPython）' if ok else '✘'}")


if __name__ == "__main__":
    print("=== Mini-Python P1：表达式求值（对照 CPython）===\n")
    cases = [
        ("2+3*4", 14), ("2**3**2", 512), ("-2**2", -4), ("4/2", 2.0),
        ("10//3", 3), ("-7//2", -4), ("-7%2", 1), ("3>2", True),
        ("not 1>2", True), ("0 or 5", 5), ("2 and 3", 3),
        ("True or 1/0", True), ("0 and 1/0", 0), ("2**-1", 0.5),
        ("1<2<3", True), ("(2+3)*4", 20), ("-5+3", -2),
    ]
    ok_n = 0
    for src, expect in cases:
        try:
            got = eval_expr(src)
            ok = got == expect and type(got) is type(expect)
            if ok:
                ok_n += 1
            print(f"[{'✔' if ok else '✘'}] {src} = {got!r} (期望 {expect!r})")
        except Exception as e:
            print(f"[✘] {src} → 异常 {e}")
    print(f"\n=== 判定 ===\n表达式求值: {ok_n}/{len(cases)}（对照 CPython 行为）")
