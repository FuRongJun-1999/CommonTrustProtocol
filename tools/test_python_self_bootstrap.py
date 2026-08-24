# -*- coding: utf-8 -*-
"""test_python_self_bootstrap.py · P 线白箱自举测试（第六阶段·Mini-Python 机制白箱化）
流程：语言机制单元库 → 白箱生成（模板填充）→ 三层自校验（L1 语法/L2 样例）
→ 外部校准（对照 CPython 行为 + 校准参考 mini_python.py）
"""
import sys, ast
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from python_code_units import PYTHON_UNITS, route_python_unit

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ============ 白箱生成 + 三层自校验 ============
generated = {}
for uid, u in PYTHON_UNITS.items():
    tree = ast.parse(u["pattern"])
    check(f'L1 语法[{uid}]', True, '')
    ns = {}
    exec(compile(tree, "<unit>", "exec"), ns)
    fn_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    fn = ns[fn_names[0]] if fn_names else None
    cls_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    l2_ok, detail = True, ""
    if fn:
        for args, expect in u["cases"]:
            try:
                if args == "call":  # 特殊：环境单元调用 env_scope()
                    got = ns["env_scope"]()
                else:
                    got = fn(*args) if isinstance(args, tuple) else fn(args)
                if isinstance(expect, dict) and isinstance(got, dict):
                    if not all(got.get(k) == v for k, v in expect.items()):
                        l2_ok, detail = False, f"{args} → {got} ⊉ {expect}"
                        break
                elif got != expect:
                    l2_ok, detail = False, f"{args} → {got!r} ≠ {expect!r}"
                    break
            except Exception as e:
                l2_ok, detail = False, f"{args} → 异常 {e}"
                break
    check(f'L2 样例[{uid}]', l2_ok, detail)
    if l2_ok:
        generated[uid] = (ns, fn_names)

# ============ 外部校准 ============
# 校准①：对照 CPython（优先级/逻辑）
ns_prec, _ = generated.get("语法-优先级", ({}, []))
if ns_prec:
    fn = ns_prec["precedence"]
    ok = fn("2+3*4") == 14 and fn("(2+3)*4") == 20 and fn("10-3*2") == 4
    check('校准① 优先级对照CPython', ok, '')
ns_logic, _ = generated.get("求值-逻辑短路", ({}, []))
if ns_logic:
    fn = ns_logic["logic_eval"]
    ok = fn(("a", "or", "b"), {"a": 1, "b": 0}) == 1 and fn(("a", "or", "b"), {"a": 0, "b": 5}) == 5
    check('校准② 逻辑短路对照Python', ok, '')

# 校准③：对照校准参考 mini_python.py（栈机结果一致）
ns_vm, _ = generated.get("栈机-字节码执行", ({}, []))
if ns_vm:
    fn = ns_vm["vm_exec"]
    r1 = fn([("PUSH", 2), ("PUSH", 3), ("PUSH", 4), ("MUL", None), ("ADD", None)])
    from mini_python import eval_expr
    check('校准③ 栈机对照eval_expr(2+3*4)', r1 == eval_expr("2+3*4") == 14,
          f'vm={r1} eval={eval_expr("2+3*4")}')

# 校准④：任务识别
check('校准④ 任务识别', route_python_unit("词法分析怎么做") == "词法-记号化"
      and route_python_unit("栈机执行") == "栈机-字节码执行", '')

print(f'\n=== P 线白箱自举（Mini-Python 机制）: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
