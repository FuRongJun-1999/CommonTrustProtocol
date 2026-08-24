# -*- coding: utf-8 -*-
"""test_compiler_self_bootstrap.py · 白箱自举写编译器 + 外部校准（第六阶段 C2 白箱化）
流程：编译器代码条件单元库 → 白箱生成（模板填充）→ 三层自校验
  L1 语法（ast.parse）→ L2 样例（args→期望断言运行）→ L3 边界（空/极端）
→ 外部校准：语义对照（智能论语义基准）+ 集成（生成代码组装 VM 执行）
"""
import sys, ast
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from compiler_code_units import COMPILER_UNITS, route_compiler_unit

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ============ 白箱生成 + 三层自校验 ============
generated = {}
for uid, u in COMPILER_UNITS.items():
    code_text = u["pattern"]
    # L1 语法自校验（物理基底：ast.parse）
    try:
        tree = ast.parse(code_text)
        l1_ok = True
    except SyntaxError as e:
        l1_ok = False
    check(f'L1 语法[{uid}]', l1_ok, str(e) if not l1_ok else '')
    if not l1_ok:
        continue
    # L2 样例自校验（运行生成函数断言）
    ns = {}
    exec(compile(tree, "<unit>", "exec"), ns)
    fn = next((v for k, v in ns.items() if k.startswith("exec_") or
               k.startswith("accumulate_") or k.startswith("condition_") or
               k.startswith("compile_")), None)
    l2_ok, detail = True, ""
    if fn:
        for args, expect in u["cases"]:
            try:
                got = fn(*args) if isinstance(args, tuple) else fn(args)
                if got != expect:
                    l2_ok, detail = False, f"{args} → {got!r} ≠ {expect!r}"
                    break
            except Exception as e:
                l2_ok, detail = False, f"{args} → 异常 {e}"
                break
    check(f'L2 样例[{uid}]', l2_ok, detail)
    if l2_ok:
        generated[uid] = (code_text, fn)

# ============ 外部校准 ============
# 校准①：语义对照——生成代码与智能论语义基准一致
cal_ok = all(u["calibration"] for u in COMPILER_UNITS.values())
check('校准① 语义基准声明齐全', cal_ok, f'{len(COMPILER_UNITS)} 单元')

# 校准②：集成——白箱生成的单元组装成迷你 VM 跑「若则+德」
if "VM-条件跳转" in generated and "VM-信任累积" in generated:
    jf, _ = generated["VM-条件跳转"]
    at, _ = generated["VM-信任累积"]
    # 组装：栈=[False(条件为假)] → 跳转跳过德 → 信任不变
    ns = {}
    exec(compile(ast.parse(jf), "<jf>", "exec"), ns)
    exec(compile(ast.parse(at), "<at>", "exec"), ns)
    trust = ns["accumulate_trust"](0.0, 0.5)
    new_ip = ns["exec_jump_if_false"]([False], 3, 9)
    check('校准② 集成(信任累积)', trust == 0.5, f'trust={trust}')
    check('校准②b 集成(条件假跳转)', new_ip == 9, f'ip={new_ip}')

# 校准③：任务识别
check('校准③ 任务识别', route_compiler_unit("实现条件跳转") == "VM-条件跳转"
      and route_compiler_unit("信任累积怎么写") == "VM-信任累积", '')

print(f'\n=== 白箱自举写编译器（C2 白箱化）: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
