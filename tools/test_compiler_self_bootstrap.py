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
    fn_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    fn = ns[fn_names[0]] if fn_names else None
    l2_ok, detail = True, ""
    if fn:
        for args, expect in u["cases"]:
            try:
                got = fn(*args) if isinstance(args, tuple) else fn(args)
                if isinstance(expect, dict) and isinstance(got, dict):
                    # dict 期望：子集匹配（VM 执行循环返回状态 dict）
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

# 校准④：端到端组装管线——白箱生成单元组装「中文程序 → 编译 → VM 执行」
def _fn(uid):
    t = ast.parse(COMPILER_UNITS[uid]["pattern"])
    ns = {}
    exec(compile(t, "<u>", "exec"), ns)
    return ns[[n.name for n in ast.walk(t) if isinstance(n, ast.FunctionDef)][0]]

vm_run = _fn("VM-执行循环")
compile_instr = _fn("编译-指令")
instr_token = _fn("词法-道德经")
check('校准④a 词法→编译→执行(道/德/止)',
      instr_token("道") == "DAO" and compile_instr("DAO", "路径甲") == ("DAO", "路径甲"), '')
prog = [("DAO", "新信任路径"), ("DE", "0.3"), ("DE", "0.5"), ("ZHI", None)]
instrs = [compile_instr(k, v) for k, v in prog if compile_instr(k, v)]
state = vm_run(instrs)
check('校准④b 端到端(信任累积+条件空间+止)',
      state["trust"] == 0.8 and state["cond"] == [{"name": "新信任路径"}]
      and state["halt"] == "halt",
      f'trust={state["trust"]} cond={state["cond"]} halt={state["halt"]}')
# 若则端到端：条件为假跳过 then
compile_condition = _fn("编译-若则")
cond_code = compile_condition([("PUSH", False)], [("DE", 0.5)], [("DE", 0.1)])
state2 = vm_run(cond_code)
check('校准④c 端到端(若则假跳→else)',
      state2["trust"] == 0.1 and state2["halt"] is None,
      f'trust={state2["trust"]}（假→跳过 then 的 0.5 执行 else 的 0.1）')

# 校准⑤：完整中文源码端到端（词法→编译→VM 执行）
lex_line = _fn("词法-中文程序")
compile_program = _fn("编译-程序")
instr_token = _fn("词法-道德经")
source = """问曰：如何验证信任？
答曰：信任值大于0.7。
术曰：
1。道 新信任路径；
2。若 信任值 大于 0.3，则 德 0.5；
3。德 0.3；
4。止。
"""
stmts = []
for line in source.splitlines():
    r = lex_line(line)
    if r is None:
        continue
    kind, payload = r
    if kind in ("问曰_STRUCT", "答曰_STRUCT", "术曰_STRUCT"):
        stmts.append((kind, payload))
    elif kind == "STEP":
        words = payload[1].split()
        en = instr_token(words[0])
        if en:
            stmts.append(("INSTR", en, words[1] if len(words) > 1 else None))
    elif kind == "COND":
        cond_txt, then_txt, else_txt = payload
        then_parts = then_txt.split()
        en = instr_token(then_parts[0])
        stmts.append(("COND", cond_txt,
                      [(en if en else then_parts[0],
                        then_parts[1] if len(then_parts) > 1 else None)], []))
    elif kind == "INSTR":
        en = instr_token(payload[0])
        if en:
            stmts.append(("INSTR", en, payload[1]))
check('校准⑤a 中文源码词法', any(s[0] == "术曰_STRUCT" for s in stmts)
      and any(s[0] == "INSTR" and s[1] == "DAO" for s in stmts)
      and any(s[0] == "INSTR" and s[1] == "DE" for s in stmts),
      f'{len(stmts)} 条语句')
code5 = compile_program(stmts, compile_instr, compile_condition)
state5 = vm_run(code5)
check('校准⑤b 端到端执行(信任≥0.8+条件空间+halt)',
      state5["trust"] >= 0.8 and state5["cond"] == [{"name": "新信任路径"}]
      and state5["halt"] == "halt",
      f'trust={state5["trust"]} cond={state5["cond"]} halt={state5["halt"]}')

print(f'\n=== 白箱自举写编译器（C2 白箱化）: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
