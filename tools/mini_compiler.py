# -*- coding: utf-8 -*-
"""mini_compiler.py · 编译原理白箱管线（第四阶段·代码深学）
完整编译管线（零 LLM 确定性）：
  词法分析（字符流→token）→ 语法分析（递归下降→AST）→
  解释执行（AST 求值）→ 代码生成（AST→JS/Rust 代码）
演示「3 + 4 * 2」→ token → AST → 11（优先级）→ JS/Rust 代码
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')


# ============ 一、词法分析（字符流 → token） ============
def tokenize(src):
    """词法分析：数字/运算符/括号 → token 列表；未知字符报错"""
    tokens = []
    i = 0
    while i < len(src):
        c = src[i]
        if c.isdigit():
            j = i
            while j < len(src) and src[j].isdigit():
                j += 1
            tokens.append(("NUMBER", int(src[i:j])))
            i = j
        elif c in "+-*/()":
            tokens.append((c, c))
            i += 1
        elif c.isspace():
            i += 1
        else:
            raise SyntaxError(f"词法错误：未知字符 '{c}'（位置 {i}）")
    tokens.append(("EOF", ""))
    return tokens


# ============ 二、语法分析（递归下降 → AST） ============
# 文法：expr → term (('+'|'-') term)*
#       term → factor (('*'|'/') factor)*
#       factor → NUMBER | '(' expr ')'
def parse(tokens):
    """语法分析：递归下降 → AST（优先级：* / 高于 + -，括号最高）"""
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else ("EOF", "")

    def advance():
        nonlocal pos
        t = tokens[pos]
        pos += 1
        return t

    def parse_expr():
        node = parse_term()
        while peek()[0] in ("+", "-"):
            op = advance()[0]
            node = ("binop", op, node, parse_term())
        return node

    def parse_term():
        node = parse_factor()
        while peek()[0] in ("*", "/"):
            op = advance()[0]
            node = ("binop", op, node, parse_factor())
        return node

    def parse_factor():
        t = peek()
        if t[0] == "NUMBER":
            advance()
            return ("num", t[1])
        if t[0] == "(":
            advance()
            node = parse_expr()
            if peek()[0] != ")":
                raise SyntaxError("语法错误：缺 ')'")
            advance()
            return node
        raise SyntaxError(f"语法错误：意外 token {t}")

    ast = parse_expr()
    if pos < len(tokens) - 1:  # 剩 EOF
        raise SyntaxError(f"语法错误：多余 token {tokens[pos]}")
    return ast


# ============ 三、解释执行（AST 求值） ============
def eval_ast(node):
    """解释执行：AST 递归求值"""
    if node[0] == "num":
        return node[1]
    op = node[1]
    l, r = eval_ast(node[2]), eval_ast(node[3])
    if op == "+":
        return l + r
    if op == "-":
        return l - r
    if op == "*":
        return l * r
    if op == "/":
        if r == 0:
            raise ZeroDivisionError("除零错误")
        return l // r
    raise ValueError(f"未知运算符 {op}")


# ============ 四、代码生成（AST → JS / Rust） ============
def codegen_js(node):
    """AST → JavaScript 表达式"""
    if node[0] == "num":
        return str(node[1])
    return f"({codegen_js(node[2])} {node[1]} {codegen_js(node[3])})"


def codegen_rust(node):
    """AST → Rust 表达式"""
    if node[0] == "num":
        return str(node[1])
    return f"({codegen_rust(node[2])} {node[1]} {codegen_rust(node[3])})"


# ============ 五、完整编译管线 ============
def compile_expression(src):
    """编译完整管线：词法 → 语法 → 求值 → 双语言代码"""
    tokens = tokenize(src)
    ast = parse(tokens)
    value = eval_ast(ast)
    return {"source": src, "tokens": tokens[:-1], "ast": ast,
            "value": value, "js": codegen_js(ast), "rust": codegen_rust(ast)}


if __name__ == "__main__":
    print("=== 编译原理白箱管线（词法→语法→求值→代码生成 · 零 LLM）===\n")
    for expr in ["3 + 4 * 2", "(3 + 4) * 2", "10 - 3 + 2", "8 / 2 * 3"]:
        r = compile_expression(expr)
        print(f"① 表达式: {expr}")
        print(f"   token: {[t[0] for t in r['tokens']]}")
        print(f"   AST:   {r['ast']}")
        print(f"   求值:  {r['value']}")
        print(f"   JS:    {r['js']}")
        print(f"   Rust:  {r['rust']}")
        print()

    # 错误检测
    print("② 错误检测（编译管线自发现）")
    for bad in ["3 +", "4 * (2", "x + 1", "5 / 0"]:
        try:
            compile_expression(bad)
            print(f"   ✘ {bad} 未报错")
        except (SyntaxError, ZeroDivisionError) as e:
            print(f"   ✔ {bad} → {e}")

    print("\n=== 判定 ===\n编译管线（词法/语法/求值/代码生成 + 错误检测）:")
    ok = (compile_expression("3 + 4 * 2")["value"] == 11
          and compile_expression("(3 + 4) * 2")["value"] == 14)
    print(f"  {'✔ 成立（优先级/括号/代码生成正确）' if ok else '✘'}")
