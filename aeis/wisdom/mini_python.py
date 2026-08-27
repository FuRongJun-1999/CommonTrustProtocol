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
    ("STR", r"'[^']*'|\"[^\"]*\""),
    ("NUMBER", r"\d+\.\d+|\d+"),
    ("OP", r"\*\*|//|==|!=|<=|>=|[+\-*/%<>()=,\[\]{}:]"),
    ("KEY", r"and|or|not|True|False|None|if|elif|else|while|def|return"),
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
                if kind == "STR":
                    tokens.append(("STRING", text[1:-1]))
                elif kind == "KEY":
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
        """解析器初始化：持有词元流与位置指针。"""
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        """前瞻：返回当前 token 类型但不消费。"""
        return self.tokens[self.pos]

    def advance(self):
        """前进：消费并返回当前 token。"""
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def match(self, *texts):
        """尝试匹配：类型相符即消费返回 True，否则 False。"""
        t = self.peek()
        if t[1] in texts:
            return self.advance()
        return None

    def _maybe_index(self, node):
        """索引后缀：obj[key] → ("index", obj, key)（P5 数据结构）"""
        while self.peek()[1] == "[":
            self.advance()
            key = self.or_expr()
            self.expect("]")
            node = ("index", node, key)
        return node

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
        """or 链：短路求值（左真返左，否则续右）——对照 CPython 语义。"""
        node = self.and_expr()
        while self.match("or"):
            node = ("or", node, self.and_expr())
        return node

    def and_expr(self):
        """and 链：短路求值（左假返假，否则续右）。"""
        node = self.not_expr()
        while self.match("and"):
            node = ("and", node, self.not_expr())
        return node

    def not_expr(self):
        """not 一元表达式求值。"""
        if self.match("not"):
            return ("not", self.not_expr())
        return self.comparison()

    def comparison(self):
        """比较链：== != < <= > >= 双目比较。"""
        node = self.arith()
        while True:
            t = self.peek()
            if t[1] in ("==", "!=", "<", ">", "<=", ">="):
                self.advance()
                node = (t[1], node, self.arith())
            else:
                return node

    def arith(self):
        """加减项：+ - 左结合。"""
        node = self.term()
        while True:
            t = self.peek()
            if t[1] in ("+", "-"):
                self.advance()
                node = (t[1], node, self.term())
            else:
                return node

    def term(self):
        """乘除项：* / // % 左结合。"""
        node = self.factor()
        while True:
            t = self.peek()
            if t[1] in ("*", "/", "//", "%"):
                self.advance()
                node = (t[1], node, self.factor())
            else:
                return node

    def factor(self):
        """一元因子：- 负号 / not 前缀。"""
        if self.peek()[1] in ("-", "+"):
            op = self.advance()[1]
            return (op, self.factor())  # 一元负号在外层：-2**2 = -(2**2)
        return self.power()

    def power(self):
        """幂运算：** 右结合。"""
        node = self.atom()
        if self.match("**"):
            return ("**", node, self.factor())  # 右结合
        return node

    def atom(self):
        """原子项：数字/字符串/名称/括号表达式/[列表]/字典字面量。"""
        t = self.peek()
        if t[0] == "NUMBER":
            self.advance()
            return ("num", t[1])
        if t[0] == "STRING":  # P5：字符串字面量
            self.advance()
            return ("str", t[1])
        if t[0] == "NAME":  # 变量/函数调用（P3）
            self.advance()
            if self.peek()[1] == "(":
                self.advance()
                args = []
                if self.peek()[1] != ")":
                    args.append(self.or_expr())
                    while self.match(","):
                        args.append(self.or_expr())
                self.expect(")")
                node = ("call", t[1], args)
            else:
                node = ("name", t[1])
            return self._maybe_index(node)
        if t[1] == "[":
            self.advance()
            items = []
            if self.peek()[1] != "]":
                items.append(self.or_expr())
                while self.match(","):
                    items.append(self.or_expr())
            self.expect("]")
            return self._maybe_index(("list", items))
        if t[1] == "{":
            self.advance()
            pairs = []
            if self.peek()[1] != "}":
                k = self.or_expr()
                self.expect(":")
                v = self.or_expr()
                pairs.append((k, v))
                while self.match(","):
                    k = self.or_expr()
                    self.expect(":")
                    v = self.or_expr()
                    pairs.append((k, v))
            self.expect("}")
            return self._maybe_index(("dict", pairs))
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
    """真值判定：对照 CPython 规则（None/0/空容器为假）。"""
    return v is not None and v is not False and v != 0


def eval_node(node, env=None):
    """AST 求值（P2：env 提供变量环境；name 节点从环境取值）"""
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "str":
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
    if kind == "call":  # 函数调用（P3：局部作用域 + 参数绑定 + return 捕获）
        f = env.get(node[1])
        if not (isinstance(f, tuple) and f[0] == "func"):
            raise MiniPyError(f"'{node[1]}' is not a function")
        _, params, body, def_env = f
        local = Env(def_env)
        args = [eval_node(a, env) for a in node[2]]
        if len(args) != len(params):
            raise MiniPyError(f"参数数量不符：{node[1]} 需要 {len(params)}，给了 {len(args)}")
        for p, a in zip(params, args):
            local.set(p, a)
        try:
            for s in body:
                exec_stmt(s, local)
        except ReturnSignal as rs:
            return rs.value
        return None
    if kind == "list":  # P5：list 字面量
        return [eval_node(e, env) for e in node[1]]
    if kind == "dict":  # P5：dict 字面量
        return {eval_node(k, env): eval_node(v, env) for k, v in node[1]}
    if kind == "index":  # P5：obj[key]
        obj = eval_node(node[1], env)
        key = eval_node(node[2], env)
        try:
            return obj[key]
        except (TypeError, IndexError, KeyError):
            raise MiniPyError(f"索引错误：{obj!r}[{key!r}]")
    raise MiniPyError(f"未知节点: {node}")


def _compare(op, a, b):
    """比较运算统一求值：==·!=·<·> 四路分派（对照 CPython 类型提升）。"""
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
    """变量环境（P3：作用域链——局部 → 父环境）"""
    def __init__(self, parent=None):
        """作用域帧构造：本地变量表 + 父链指向外层（链式查找）。"""
        self.vars = {}
        self.parent = parent

    def get(self, name):
        """变量读取：沿父作用域链向上查找，未定义抛 NameError。"""
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise MiniPyError(f"NameError: name '{name}' is not defined")

    def set(self, name, value):
        """变量赋值绑定到当前作用域。"""
        self.vars[name] = value


class ReturnSignal(Exception):
    """return 语句信号（P3）"""
    def __init__(self, value):
        """常量值包装（字面量求值结果载体）。"""
        self.value = value


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
        if code.startswith("def "):
            import re as _re
            m = _re.match(r"def\s+(\w+)\s*\(([^)]*)\)\s*:", code)
            name = m.group(1)
            params = [p.strip() for p in m.group(2).split(",") if p.strip()]
            body = build(idx, lines[idx[0]][0] if idx[0] < len(lines) else 0)
            return ("funcdef", name, params, body)
        if code.startswith("return "):
            return ("return", Parser(tokenize(code[7:])).parse())
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
    """执行单条语句（if/while/funcdef 递归执行块）"""
    kind = stmt[0]
    if kind == "assign":
        env.set(stmt[1], eval_node(stmt[2], env))
    elif kind == "funcdef":
        # 函数对象 = 参数 + body + 定义环境（P4 闭包基础）
        env.set(stmt[1], ("func", stmt[2], stmt[3], env))
    elif kind == "return":
        raise ReturnSignal(eval_node(stmt[1], env))
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


# ============ P5：字节码 VM 雏形（栈机——机制供 C 线原生后端复用） ============
# 表达式 → 字节码指令 → 栈机执行（对照 eval_node 结果）
# 指令：PUSH_CONST/PUSH_LIST/PUSH_DICT/LOAD_NAME/ADD/SUB/MUL/DIV/FLOOR/MOD/POW/
#       NEG/AND_OR/CMP_*/JUMP_IF_FALSE/JUMP（逻辑短路用跳转）

def compile_expr(node):
    """AST 表达式 → 字节码指令列表（栈机）"""
    kind = node[0]
    if kind == "num":
        return [("PUSH_CONST", node[1])]
    if kind == "str":
        return [("PUSH_CONST", node[1])]
    if kind == "bool":
        return [("PUSH_CONST", node[1])]
    if kind == "none":
        return [("PUSH_CONST", None)]
    if kind == "name":
        return [("LOAD_NAME", node[1])]
    if kind == "list":
        code = []
        for e in node[1]:
            code.extend(compile_expr(e))
        code.append(("PUSH_LIST", len(node[1])))
        return code
    if kind == "dict":
        code = []
        for k, v in node[1]:
            code.extend(compile_expr(k))
            code.extend(compile_expr(v))
        code.append(("PUSH_DICT", len(node[1])))
        return code
    if kind == "index":
        code = compile_expr(node[1]) + compile_expr(node[2])
        code.append(("INDEX", None))
        return code
    if kind in ("-", "+") and len(node) == 2:  # 一元
        code = compile_expr(node[1])
        if kind == "-":
            code.append(("NEG", None))
        return code
    if kind in ("+", "-", "*", "/", "//", "%", "**"):
        code = compile_expr(node[1]) + compile_expr(node[2])
        code.append((_ARITH_VM[kind], None))
        return code
    if kind in ("==", "!=", "<", ">", "<=", ">="):
        code = compile_expr(node[1]) + compile_expr(node[2])
        code.append((_CMP_VM[kind], None))
        return code
    if kind == "not":
        return compile_expr(node[1]) + [("NOT", None)]
    if kind == "or" or kind == "and":
        # 短路：左值 → 真保留左值（or）/假保留左值（and）→ 否则求右值
        right = compile_expr(node[2])
        code = compile_expr(node[1])
        jmp = "JUMP_IF_TRUE" if kind == "or" else "JUMP_IF_FALSE"
        jmp_idx = len(code)
        code.append((jmp, 0))       # 回填
        code.append(("POP", None))  # 丢弃左值（不短路时）
        code.extend(right)
        code[jmp_idx] = (jmp, len(code))  # 短路目标 = 程序末尾（栈顶左值保留）
        return code
    if kind == "call":
        code = [("LOAD_NAME", node[1])]
        for a in node[2]:
            code.extend(compile_expr(a))
        code.append(("CALL", len(node[2])))
        return code
    raise MiniPyError(f"无法编译节点: {node}")


_ARITH_VM = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV",
             "//": "FLOOR", "%": "MOD", "**": "POW"}
_CMP_VM = {"==": "CMP_EQ", "!=": "CMP_NE", "<": "CMP_LT", ">": "CMP_GT",
           "<=": "CMP_LE", ">=": "CMP_GE"}


class VM:
    """栈机执行（P5 雏形：算术/比较/逻辑短路/数据结构/调用）"""
    def __init__(self, env):
        """VM 执行上下文：环境引用·操作数栈·调用帧序列。"""
        self.env = env
        self.stack = []
        self.frames = []  # 调用帧（P5 简化：函数调用直接执行 body）

    def run(self, code, max_steps=100000):
        """字节码 VM 执行主循环：取指分派，max_steps 上限防死循环。"""
        ip = 0
        while ip < len(code) and max_steps > 0:
            op, arg = code[ip]
            ip += 1
            max_steps -= 1
            if op == "PUSH_CONST":
                self.stack.append(arg)
            elif op == "LOAD_NAME":
                self.stack.append(self.env.get(arg))
            elif op == "PUSH_LIST":
                items = self.stack[-arg:]
                self.stack = self.stack[:-arg]
                self.stack.append(items)
            elif op == "PUSH_DICT":
                pairs = self.stack[-arg * 2:]
                self.stack = self.stack[:-arg * 2]
                self.stack.append({pairs[i]: pairs[i + 1] for i in range(0, len(pairs), 2)})
            elif op == "INDEX":
                key, obj = self.stack.pop(), self.stack.pop()
                self.stack.append(obj[key])
            elif op == "ADD":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
            elif op == "SUB":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)
            elif op == "MUL":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)
            elif op == "DIV":
                b, a = self.stack.pop(), self.stack.pop()
                if b == 0:
                    raise MiniPyError("ZeroDivisionError")
                self.stack.append(a / b)
            elif op == "FLOOR":
                b, a = self.stack.pop(), self.stack.pop()
                if b == 0:
                    raise MiniPyError("ZeroDivisionError")
                self.stack.append(int(a // b))
            elif op == "MOD":
                b, a = self.stack.pop(), self.stack.pop()
                if b == 0:
                    raise MiniPyError("ZeroDivisionError")
                self.stack.append(a % b)
            elif op == "POW":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a ** b)
            elif op == "NOT":
                self.stack.append(not is_truthy(self.stack.pop()))
            elif op == "NEG":
                self.stack.append(-self.stack.pop())
            elif op.startswith("CMP_"):
                b, a = self.stack.pop(), self.stack.pop()
                _cmp_map = {"EQ": "==", "NE": "!=", "LT": "<", "GT": ">",
                            "LE": "<=", "GE": ">="}
                self.stack.append(_compare(_cmp_map[op[4:]], a, b))
            elif op == "JUMP_IF_TRUE":
                if is_truthy(self.stack[-1]):
                    ip = arg
            elif op == "JUMP_IF_FALSE":
                if not is_truthy(self.stack[-1]):
                    ip = arg
            elif op == "POP":
                self.stack.pop()
            elif op == "CALL":
                args = self.stack[-arg:]
                self.stack = self.stack[:-arg]
                f = self.stack.pop()  # 函数在参数之下（先压函数后压参数）
                _, params, body, def_env = f
                local = Env(def_env)
                for p, a in zip(params, args):
                    local.set(p, a)
                try:
                    for s in body:
                        exec_stmt(s, local)
                    self.stack.append(None)
                except ReturnSignal as rs:
                    self.stack.append(rs.value)
            else:
                raise MiniPyError(f"未知指令: {op}")
        return self.stack[-1] if self.stack else None


def eval_expr_vm(src, env=None):
    """字节码 VM 求值入口（P5：对照 eval_expr/eval_node）"""
    env = env or Env()
    ast = Parser(tokenize(src)).parse()
    code = compile_expr(ast)
    return VM(env).run(code)


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
