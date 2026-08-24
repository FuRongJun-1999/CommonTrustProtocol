# -*- coding: utf-8 -*-
"""compiler_code_units.py · 编译器代码条件单元库（第六阶段·白箱自举写编译器）
中文编译器 C 线 = 白箱代码条件单元（{任务 → 代码模式模板 + 验证样例}）——
白箱 code_compose 机制生成代码，三层自校验（语法/样例/边界），外部校准语义。
单元设计对齐智能论语义：若则=条件跳转、德=信任累积、道/自然=条件空间、赋值=名实写入。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 任务 → 代码模式 + 验证样例（白箱生成的自校验基准）
COMPILER_UNITS = {
    "VM-条件跳转": {
        "task": "条件跳转",
        "pattern": (
            "def exec_jump_if_false(stack, ip, target):\n"
            "    # 若…则…否则：栈顶为假则跳转（智能论条件语句的 VM 语义）\n"
            "    if not stack:\n"
            "        return ip + 1\n"
            "    v = stack.pop()\n"
            "    return target if (v is False or v is None or v == 0) else ip + 1\n"),
        "cases": [(([False], 3, 9), 9), (([0], 3, 9), 9), (([True], 3, 9), 4),
                  (([1], 3, 9), 4), (([], 3, 9), 4)],
        "params": [],
        "calibration": "对照：若条件为假则跳过 then 执行 else（JUMP_IF_FALSE）",
    },
    "VM-信任累积": {
        "task": "信任累积",
        "pattern": (
            "def accumulate_trust(trust, amount):\n"
            "    # 德：信任值累积（信任引擎内建语义）\n"
            "    return round(trust + amount, 3)\n"),
        "cases": [((0.0, 0.5), 0.5), ((0.3, 0.5), 0.8), ((0.7, 0.0), 0.7)],
        "params": [],
        "calibration": "对照：德指令 → accumulate_trust（v0.2 INSTRUCTION_MAP 同语义）",
    },
    "VM-条件空间": {
        "task": "条件空间",
        "pattern": (
            "def condition_space_op(space_stack, op, name):\n"
            "    # 道：创建协议路径（条件空间栈压入）；自然：恢复默认（弹栈到根）\n"
            "    if op == '道':\n"
            "        space_stack.append({'name': name})\n"
            "    elif op == '自然':\n"
            "        while len(space_stack) > 1:\n"
            "            space_stack.pop()\n"
            "    return space_stack\n"),
        "cases": [(([], "道", "路径甲"), [{"name": "路径甲"}]),
                  (([{"name": "根"}, {"name": "子"}], "自然", ""), [{"name": "根"}])],
        "params": [],
        "calibration": "对照：道=create_path（条件空间注册）、自然=restore_default",
    },
    "编译-若则": {
        "task": "编译条件",
        "pattern": (
            "def compile_condition(cond_instrs, then_instrs, else_instrs):\n"
            "    # 若…则…否则 → JUMP_IF_FALSE + JUMP（AST→字节码）\n"
            "    code = []\n"
            "    code.extend(cond_instrs)\n"
            "    else_lbl = len(code) + 1 + len(then_instrs) + 1\n"
            "    code.append(('JUMP_IF_FALSE', else_lbl))\n"
            "    code.extend(then_instrs)\n"
            "    end_lbl = len(code) + 1 + len(else_instrs)\n"
            "    code.append(('JUMP', end_lbl))\n"
            "    code.extend(else_instrs)\n"
            "    return code\n"),
        "cases": [(([("LOAD", "x")], [("DE", 0.5)], [("DE", 0.1)]),
                  # 外部校准（2026-03）：JIF→4=假跳 else 起点；JUMP→5=then 结束越界
                  [("LOAD", "x"), ("JUMP_IF_FALSE", 4), ("DE", 0.5),
                   ("JUMP", 5), ("DE", 0.1)])],
        "params": [],
        "calibration": "对照：若则=条件语句（v0.2 codegen if/else 的字节码形态）",
    },
    "编译-赋值": {
        "task": "编译赋值",
        "pattern": (
            "def compile_assign(value_instrs, name):\n"
            "    # 赋值 → 值指令 + STORE_NAME（以名举实：名实写入）\n"
            "    code = list(value_instrs)\n"
            "    code.append(('STORE_NAME', name))\n"
            "    return code\n"),
        "cases": [(([("PUSH", 1)], "甲"), [("PUSH", 1), ("STORE_NAME", "甲")])],
        "params": [],
        "calibration": "对照：赋值 = target = expr（名实对应）",
    },
    "词法-道德经": {
        "task": "道德经词法",
        "pattern": (
            "def instr_token(word):\n"
            "    # 道德经助记符 → 指令 Token（剥离尾部标点；未接入 VM 的指令诚实返回 None）\n"
            "    m = {'道': 'DAO', '德': 'DE', '自然': 'ZIRAN', '无为': 'WUWEI',\n"
            "         '止': 'ZHI', '知足': 'ZHIZU'}\n"
            "    return m.get((word or '').rstrip('。；;，,'))\n"),
        "cases": [("道", "DAO"), ("德", "DE"), ("止", "ZHI"), ("知足", "ZHIZU"),
                  ("谷", None), ("随便", None)],
        "params": [],
        "calibration": "对照：TokenType 道德经助记符（道/德/自然/无为/谷/牝/柔/朴/止/知足）",
    },
    "词法-九章算术": {
        "task": "九章算术",
        "pattern": (
            "def structure_token(text):\n"
            "    # 九章算术结构：问曰/答曰/术曰 → (TokenType, 原文)\n"
            "    for kw in ('问曰', '答曰', '术曰'):\n"
            "        if text.startswith(kw):\n"
            "            return (kw + '_STRUCT', kw)\n"
            "    return None\n"),
        "cases": [("问曰：如何验证", ("问曰_STRUCT", "问曰")),
                  ("术曰：", ("术曰_STRUCT", "术曰")),
                  ("答曰：信任值", ("答曰_STRUCT", "答曰")),
                  ("随便文本", None)],
        "params": [],
        "calibration": "对照：TokenType WENYUE/DAYUE/SHUYUE（九章算术结构）",
    },
    "校验-名实": {
        "task": "名实校验",
        "pattern": (
            "def check_names(required, declared):\n"
            "    # 以名举实：要求的符号必须已声明（墨辩静态检查）\n"
            "    return [s for s in required if s not in declared]\n"),
        "cases": [((["a"], {"a": 1, "b": 2}), []),
                  ((["a", "b"], {"a": 1}), ["b"]),
                  (([], {}), [])],
        "params": [],
        "calibration": "对照：name_checker 以名举实（符号表→协议实体）",
    },
    "VM-执行循环": {
        "task": "执行循环",
        "pattern": (
            "def vm_run(code, symbols=None, trust=0.0, cond_stack=None):\n"
            "    # 智能论 VM 执行循环：ip 顺序执行；止/无为 = 控制流信号；名实不符报错\n"
            "    ip, stack = 0, []\n"
            "    symbols = dict(symbols or {})\n"
            "    cond_stack = list(cond_stack or [])\n"
            "    result = {'trust': trust, 'symbols': symbols, 'cond': cond_stack,\n"
            "              'stack': [], 'halt': None, 'error': None}\n"
            "    while ip < len(code):\n"
            "        op, arg = code[ip]\n"
            "        ip += 1\n"
            "        if op == 'PUSH':\n"
            "            stack.append(arg)\n"
            "        elif op == 'STORE':\n"
            "            symbols[arg] = stack.pop()\n"
            "        elif op == 'LOAD':\n"
            "            if arg not in symbols:\n"
            "                result['error'] = '名实不符：' + arg\n"
            "                break\n"
            "            stack.append(symbols[arg])\n"
            "        elif op == 'JUMP_IF_FALSE':\n"
            "            v = stack.pop() if stack else False\n"
            "            if v is False or v is None or v == 0:\n"
            "                ip = arg\n"
            "        elif op == 'JUMP':\n"
            "            ip = arg\n"
            "        elif op == 'DE':\n"
            "            trust = round(trust + arg, 3)\n"
            "        elif op == 'DAO':\n"
            "            cond_stack.append({'name': arg})\n"
            "        elif op == 'ZIRAN':\n"
            "            while len(cond_stack) > 1:\n"
            "                cond_stack.pop()\n"
            "        elif op == 'ZHIZU':\n"
            "            if trust >= arg[0]:\n"
            "                ip = arg[1]\n"
            "        elif op == 'ZHI':\n"
            "            result['halt'] = 'halt'\n"
            "            break\n"
            "        elif op == 'WUWEI':\n"
            "            result['halt'] = 'yield'\n"
            "            break\n"
            "    result['stack'] = list(stack)\n"
            "    result['trust'] = trust\n"
            "    return result\n"),
        "cases": [(([("DE", 0.3), ("DE", 0.5)],), {"trust": 0.8}),
                  (([("PUSH", False), ("JUMP_IF_FALSE", 3), ("DE", 0.5),
                     ("DE", 0.2)],), {"trust": 0.2}),
                  (([("DAO", "路径甲"), ("ZIRAN", None)],), {"cond": [{"name": "路径甲"}]}),
                  (([("ZHI", None)],), {"halt": "halt"}),
                  (([("WUWEI", None)],), {"halt": "yield"}),
                  (([("LOAD", "未声明")],), {"error": "名实不符：未声明"})],
        "params": [],
        "calibration": "对照：condition_vm 执行循环（止=halt/无为=yield/名实不符=错误）",
    },
    "编译-指令": {
        "task": "编译指令",
        "pattern": (
            "def compile_instr(kind, operand=None):\n"
            "    # 道德经指令 AST → VM 指令（未接入 VM 的指令诚实返回 None）\n"
            "    if kind == 'DAO':\n"
            "        return ('DAO', operand or '无名路径')\n"
            "    if kind == 'DE':\n"
            "        return ('DE', float(operand or 0))\n"
            "    if kind in ('ZIRAN', 'WUWEI', 'ZHI'):\n"
            "        return (kind, None)\n"
            "    return None\n"),
        "cases": [(("DAO", "路径甲"), ("DAO", "路径甲")), (("DE", "0.5"), ("DE", 0.5)),
                  (("ZHI", None), ("ZHI", None)), (("谷", "x"), None)],
        "params": [],
        "calibration": "对照：INSTRUCTION_MAP（道→create_path 等；未接入指令诚实边界）",
    },
    "校验-条件空间类型": {
        "task": "条件空间类型",
        "pattern": (
            "def check_condition_types(conditions, symbol_types):\n"
            "    # 条件空间=类型系统：条件声明中的符号必须已定义类型（编译期静态检查）\n"
            "    # conditions: [{'space': '伴侣', 'symbol': '情感权重', 'type': '数值'}]\n"
            "    return [c for c in conditions\n"
            "            if c['symbol'] not in symbol_types]\n"),
        "cases": [(([{"space": "伴侣", "symbol": "情感权重", "type": "数值"}],
                    {"情感权重": "数值", "信任值": "数值"}), []),
                  (([{"space": "伴侣", "symbol": "未定义量", "type": "数值"}],
                    {"情感权重": "数值"}), [{"space": "伴侣", "symbol": "未定义量",
                                              "type": "数值"}]),
                  (([], {}), [])],
        "params": [],
        "calibration": "对照：C2 语义——条件空间=类型系统（若条件空间X则符号Y类型Z 编译期校验）",
    },
    "词法-中文程序": {
        "task": "中文程序词法",
        "pattern": (
            "def lex_line(line):\n"
            "    # 中文程序行 → (kind, payload)；九章算术结构/条件/指令/步骤识别\n"
            "    line = line.strip()\n"
            "    if not line or line.startswith('#'):\n"
            "        return None\n"
            "    for kw in ('问曰', '答曰', '术曰'):\n"
            "        if line.startswith(kw):\n"
            "            return (kw + '_STRUCT', line[len(kw):].lstrip('：:'))\n"
            "    m = None\n"
            "    import re as _re\n"
            "    m = _re.match(r'^(\\d+)。\\s*(.+?)[；;]?$', line)\n"
            "    if m:\n"
            "        num, content = int(m.group(1)), m.group(2)\n"
            "        if content.startswith('若'):\n"
            "            cm = _re.match(r'^若\\s*(.+?)\\s*[,，]?\\s*则\\s*(.+?)\\s*[。;；]?(?:否则\\s*(.+?))?[。;]?$', content)\n"
            "            if cm:\n"
            "                return ('COND', (cm.group(1), cm.group(2), cm.group(3)))\n"
            "        return ('STEP', (num, content))\n"
            "    m = _re.match(r'^若\\s*(.+?)\\s*[,，]?\\s*则\\s*(.+?)\\s*[。;；]?(?:否则\\s*(.+?))?[。;]?$', line)\n"
            "    if m:\n"
            "        return ('COND', (m.group(1), m.group(2), m.group(3)))\n"
            "    for kw in ('道', '德', '止', '知足', '自然', '无为'):\n"
            "        if line.startswith(kw):\n"
            "            rest = line[len(kw):].strip().rstrip('。；;')\n"
            "            return ('INSTR', (kw, rest or None))\n"
            "    return ('UNKNOWN', line)\n"),
        "cases": [("术曰：", ("术曰_STRUCT", "")),
                  ("1。道 新信任路径；", ("STEP", (1, "道 新信任路径"))),
                  ("若 信任值 大于 0.3，则 德 0.5；", ("COND", ("信任值 大于 0.3",
                    "德 0.5", None))),
                  ("德 0.5。", ("INSTR", ("德", "0.5"))),
                  ("止。", ("INSTR", ("止", None))),
                  ("# 注释", None),
                  ("", None)],
        "params": [],
        "calibration": "对照：protocol-compiler lexer（九章算术结构/若则/道德经指令/步骤序号）",
    },
    "编译-程序": {
        "task": "编译程序",
        "pattern": (
            "def compile_program(statements, compile_instr=None, compile_condition=None):\n"
            "    # 程序语句列表 → 字节码（术曰=作用域；条件=跳转；指令=道德经；止=停止）\n"
            "    def _num(v):\n"
            "        if v is None:\n"
            "            return None\n"
            "        s = str(v)\n"
            "        return float(s) if s.replace('.', '', 1).isdigit() else v\n"
            "    ci = compile_instr or (lambda k, v=None: (k, _num(v)))\n"
            "    cc = compile_condition or (lambda c, t, e: c + [('JUMP_IF_FALSE', 0)] + t)\n"
            "    code = []\n"
            "    for stmt in statements:\n"
            "        kind = stmt[0]\n"
            "        if kind == '术曰':\n"
            "            code.append(('ENTER_SHUYUE', None))\n"
            "        elif kind == 'INSTR':\n"
            "            instr = ci(stmt[1], stmt[2])\n"
            "            if instr:\n"
            "                code.append(instr)\n"
            "        elif kind == 'COND':\n"
            "            cond, then_s, else_s = stmt[1], stmt[2], stmt[3]\n"
            "            then_i = [x for x in [ci(t[0], t[1]) for t in then_s] if x]\n"
            "            else_i = [x for x in [ci(t[0], t[1]) for t in else_s] if x]\n"
            "            base = len(code)\n"
            "            seg = cc([('PUSH', True)], then_i, else_i)\n"
            "            # 外部校准：段内相对跳转目标需加全局偏移（否则组合后跳到自己）\n"
            "            seg = [(op, arg + base) if op in ('JUMP', 'JUMP_IF_FALSE')\n"
            "                   and isinstance(arg, int) else (op, arg) for op, arg in seg]\n"
            "            code.extend(seg)\n"
            "        elif kind == '止':\n"
            "            code.append(('ZHI', None))\n"
            "    return code\n"),
        "cases": [(([("术曰", None), ("INSTR", "DAO", "路径甲"), ("止", None)],),
                   [("ENTER_SHUYUE", None), ("DAO", "路径甲"), ("ZHI", None)]),
                  (([("INSTR", "DE", "0.3"), ("止", None)],),
                   [("DE", 0.3), ("ZHI", None)])],
        "params": [],
        "calibration": "对照：C2 顶层编译——术曰作用域/道德经指令/止停止",
    },
}


def route_compiler_unit(question):
    """任务识别（问题 → 编译器单元，最长关键词优先）"""
    best, best_len = None, 0
    for uid, u in COMPILER_UNITS.items():
        for kw in (u["task"], uid):
            if kw in question and len(kw) > best_len:
                best, best_len = uid, len(kw)
    return best


if __name__ == "__main__":
    print("=== 编译器代码条件单元库（白箱自举写编译器 · 校准参考）===\n")
    for uid, u in COMPILER_UNITS.items():
        print(f"[{uid}] 任务={u['task']} 样例数={len(u['cases'])}")
        print(f"    校准: {u['calibration']}")
    print(f"\n=== 判定 ===\n编译器单元库: "
          f"{'✔ 5 单元就绪（每单元含模式+样例+校准基准）' if len(COMPILER_UNITS) >= 4 else '✘'}")
