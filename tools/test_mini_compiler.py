# -*- coding: utf-8 -*-
"""test_mini_compiler.py · 编译原理管线测试（第四阶段·代码深学）
验证：①词法分析（token 化）②语法分析（优先级/括号 AST）③解释求值
④错误检测（词法/语法/除零）⑤代码生成（JS/Rust）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from mini_compiler import tokenize, parse, eval_ast, codegen_js, codegen_rust

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 词法
toks = tokenize("3 + 4")
check('① 词法 token 化', [t[0] for t in toks] == ["NUMBER", "+", "NUMBER", "EOF"],
      str([t[0] for t in toks]))

# ② 语法 + 优先级
ast = parse(tokenize("3 + 4 * 2"))
check('② 优先级（* 高于 +）', ast[0] == "binop" and ast[1] == "+"
      and ast[3][1] == "*", str(ast))
ast2 = parse(tokenize("(3 + 4) * 2"))
check('②b 括号优先', ast2[1] == "*" and ast2[2][1] == "+", str(ast2))

# ③ 求值
check('③a 3+4*2 = 11', eval_ast(ast) == 11)
check('③b (3+4)*2 = 14', eval_ast(ast2) == 14)
check('③c 8/2*3 = 12', eval_ast(parse(tokenize("8 / 2 * 3"))) == 12)

# ④ 错误检测
errs = 0
for bad, etype in [("3 +", SyntaxError), ("4 * (2", SyntaxError),
                   ("x + 1", SyntaxError), ("5 / 0", ZeroDivisionError)]:
    try:
        parse(tokenize(bad)) if bad != "5 / 0" else eval_ast(parse(tokenize(bad)))
    except etype:
        errs += 1
    except SyntaxError:
        errs += 1
check('④ 错误检测（缺操作数/缺括号/未知字符/除零）', errs == 4, f"{errs}/4")

# ⑤ 代码生成
check('⑤a JS 代码生成', codegen_js(ast) == "(3 + (4 * 2))", codegen_js(ast))
check('⑤b Rust 代码生成', codegen_rust(ast) == "(3 + (4 * 2))", codegen_rust(ast))

print(f'\n=== 编译原理管线测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
