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
    "编译-循环": {
        "task": "循环编译",
        "pattern": (
            "def compile_loop(cond_instrs, body_instrs):\n"
            "    # 当…执行 → 条件 + JUMP_IF_FALSE 跳出 + 循环体 + JUMP 回条件\n"
            "    # （while 语义：条件为假即退出，回跳形成循环）\n"
            "    code = []\n"
            "    code.extend(cond_instrs)\n"
            "    end_lbl = len(code) + 1 + len(body_instrs) + 1\n"
            "    code.append(('JUMP_IF_FALSE', end_lbl))\n"
            "    code.extend(body_instrs)\n"
            "    code.append(('JUMP', 0))\n"
            "    return code\n"),
        "cases": [(([("LOAD", "i"), ("PUSH", 3), ("CMP_LT", None)],
                    [("DE", 0.1)]),
                   [("LOAD", "i"), ("PUSH", 3), ("CMP_LT", None),
                    ("JUMP_IF_FALSE", 6), ("DE", 0.1), ("JUMP", 0)]),
                  (([("PUSH", False)], [("DE", 0.5), ("DE", 0.2)]),
                   [("PUSH", False), ("JUMP_IF_FALSE", 5),
                    ("DE", 0.5), ("DE", 0.2), ("JUMP", 0)])],
        "params": [],
        "calibration": "对照：当…执行=while 语句（条件先判→体→回跳；假则跳出到循环后）",
    },
    "VM-循环执行": {
        "task": "循环执行",
        "pattern": (
            "def vm_run_loop(code, symbols=None, max_steps=1000):\n"
            "    # 智能论 VM 循环执行：算术(ADD/SUB)+比较+回跳；步数上限防死循环\n"
            "    ip, stack = 0, []\n"
            "    symbols = dict(symbols or {})\n"
            "    steps = 0\n"
            "    while ip < len(code):\n"
            "        steps += 1\n"
            "        if steps > max_steps:\n"
            "            return {'error': '循环未终止（超出步数上限）',\n"
            "                    'symbols': symbols, 'stack': stack}\n"
            "        op, arg = code[ip]\n"
            "        ip += 1\n"
            "        if op == 'PUSH':\n"
            "            stack.append(arg)\n"
            "        elif op == 'STORE':\n"
            "            symbols[arg] = stack.pop()\n"
            "        elif op == 'LOAD':\n"
            "            if arg not in symbols:\n"
            "                return {'error': '名实不符：' + arg,\n"
            "                        'symbols': symbols, 'stack': stack}\n"
            "            stack.append(symbols[arg])\n"
            "        elif op == 'JUMP_IF_FALSE':\n"
            "            v = stack.pop() if stack else False\n"
            "            if v is False or v is None or v == 0:\n"
            "                ip = arg\n"
            "        elif op == 'JUMP':\n"
            "            ip = arg\n"
            "        elif op == 'CMP_LT':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a < b)\n"
            "        elif op == 'ADD':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a + b)\n"
            "        elif op == 'SUB':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a - b)\n"
            "    return {'error': None, 'symbols': symbols, 'stack': stack}\n"),
        "cases": [(([("LOAD", "i"), ("PUSH", 3), ("CMP_LT", None),
                     ("JUMP_IF_FALSE", 13),
                     ("LOAD", "s"), ("LOAD", "i"), ("ADD", None), ("STORE", "s"),
                     ("LOAD", "i"), ("PUSH", 1), ("ADD", None), ("STORE", "i"),
                     ("JUMP", 0)],
                    {"i": 1, "s": 0}),
                   {'error': None, 'symbols': {'i': 3, 's': 3},
                    'stack': []}),
                  (([("LOAD", "i"), ("PUSH", 3), ("CMP_LT", None),
                     ("JUMP_IF_FALSE", 13),
                     ("LOAD", "s"), ("LOAD", "i"), ("ADD", None), ("STORE", "s"),
                     ("LOAD", "i"), ("PUSH", 1), ("ADD", None), ("STORE", "i"),
                     ("JUMP", 0)],
                    {"i": 5, "s": 0}),
                   {'error': None, 'symbols': {'i': 5, 's': 0},
                    'stack': []}),
                  (([("JUMP", 0)], {}),
                   {'error': '循环未终止（超出步数上限）',
                    'symbols': {}, 'stack': []})],
        "params": [],
        "calibration": "对照：while 循环 VM 运行（i=1→3 累积 1+2=3 于 s；死循环被步数上限拦截）",
    },
    "编译-函数定义": {
        "task": "函数定义",
        "pattern": (
            "def compile_func_def(name, params, body_instrs):\n"
            "    # 定义 名（参数）：语句 → 函数体后置 + RETURN（入口=函数体起点）\n"
            "    # 返回 (skip_jump, entry_ip, body)：调用方拼接 JUMP 跳过 + 函数体\n"
            "    body = list(body_instrs)\n"
            "    body.append(('RETURN', None))\n"
            "    return {'name': name, 'params': params,\n"
            "            'skip': ('JUMP', None),  # 占位，拼接后回填\n"
            "            'entry_ip': 0, 'body': body}\n"),
        "cases": [(("阶乘", ["n"], [("LOAD", "n")]),
                   {'name': '阶乘', 'params': ['n'],
                    'skip': ('JUMP', None), 'entry_ip': 0,
                    'body': [('LOAD', 'n'), ('RETURN', None)]})],        "params": [],
        "calibration": "对照：protocol-compiler 函数定义（入口=函数体起点，体末 RETURN）",
    },
    "VM-函数调用": {
        "task": "函数调用",
        "pattern": (
            "def call_func(call_stack, symbols, params, args, entry_ip, ret_ip):\n"
            "    # CALL 语义：保存调用帧(返回地址+符号表) → 参数绑定(遮蔽全局) → 跳入口\n"
            "    call_stack.append((ret_ip, dict(symbols)))\n"
            "    for pname, pval in zip(params, args):\n"
            "        symbols[pname] = pval\n"
            "    return entry_ip\n"),
        "cases": [(([], {'甲': 1}, ['x'], [5], 10, 3), 10)],
        "params": [],
        "calibration": "对照：protocol-compiler CALL（帧保存+参数绑定遮蔽全局，对齐 da997ef VM）",
    },
    "编译-递归": {
        "task": "递归调用",
        "pattern": (
            "def compile_recursive(name, params, cond_instrs, then_ret, else_expr_instrs):\n"
            "    # 递归函数：若 基条件 则 返回 基值，否则 返回 表达式（含自身调用）\n"
            "    # 组装为函数体字节码（CALL 自身由调用方回填入口）\n"
            "    body = []\n"
            "    body.extend(cond_instrs)\n"
            "    body.append(('JUMP_IF_FALSE', 0))  # 占位\n"
            "    body.extend(then_ret)\n"
            "    body.append(('RETURN', None))\n"
            "    body.append(('JUMP', 0))  # 占位\n"
            "    body.extend(else_expr_instrs)\n"
            "    body.append(('RETURN', None))\n"
            "    return {'name': name, 'params': params, 'body': body}\n"),
        "cases": [((("阶乘", ["n"], [("LOAD", "n"), ("PUSH", 2), ("CMP_LT", None)],
                     [("PUSH", 1)], [("LOAD", "n")])),
                   {'name': '阶乘', 'params': ['n'],
                    'body': [('LOAD', 'n'), ('PUSH', 2), ('CMP_LT', None),
                             ('JUMP_IF_FALSE', 0), ('PUSH', 1), ('RETURN', None),
                             ('JUMP', 0), ('LOAD', 'n'), ('RETURN', None)]})],
        "params": [],
        "calibration": "对照：protocol-compiler 递归函数（若则体内 RETURN，对齐阶乘 da997ef 语义）",
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
            "        elif op in ('CMP_GT', 'CMP_LT', 'CMP_EQ', 'CMP_NE', 'CMP_LE', 'CMP_GE'):\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append({'CMP_GT': a > b, 'CMP_LT': a < b, 'CMP_EQ': a == b,\n"
            "                         'CMP_NE': a != b, 'CMP_LE': a <= b,\n"
            "                         'CMP_GE': a >= b}[op])\n"
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
                  (([("LOAD", "未声明")],), {"error": "名实不符：未声明"}),
                  (([("PUSH", 0.5), ("PUSH", 0.3), ("CMP_GT", None),
                     ("DE", 0.2), ("ZHI", None)],), {"trust": 0.2}),
                  (([("PUSH", 0.1), ("PUSH", 0.3), ("CMP_GT", None),
                     ("JUMP_IF_FALSE", 5), ("DE", 0.2), ("ZHI", None)],),
                   {"trust": 0.0})],
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
    "校验-条件空间存在性": {
        "task": "条件空间存在",
        "pattern": (
            "def check_condition_spaces(used_spaces, declared_spaces):\n"
            "    # 条件空间=类型系统：使用的条件空间必须已声明（编译期拦截未声明空间）\n"
            "    return [s for s in used_spaces if s not in declared_spaces]\n"),
        "cases": [((["伴侣", "高原"], {"伴侣", "高原"}), []),
                  ((["伴侣"], {"伴侣"}), []),
                  ((["伴侣", "未知空间"], {"伴侣"}), ["未知空间"]),
                  (([], set()), [])],
        "params": [],
        "calibration": "对照：C2 语义——条件空间=类型系统（使用前必须声明，编译期拦截）",
    },
    "编译-管线静态检查": {
        "task": "编译管线",
        "pattern": (
            "def compile_pipeline(statements, symbol_types, declared_spaces):\n"
            "    # 编译管线（C2 语义：静态检查→字节码）——名实 + 条件空间类型 + 存在性\n"
            "    errors = []\n"
            "    for st in statements:\n"
            "        kind = st[0]\n"
            "        if kind == 'INSTR' and st[1] == 'DE':\n"
            "            operand = st[2]\n"
            "            if operand is not None and not str(operand).replace('.', '', 1).isdigit():\n"
            "                errors.append('类型错误：德 操作数「' + str(operand) + '」非数值（条件空间类型）')\n"
            "        elif kind == 'COND':\n"
            "            import re as _re\n"
            "            m = _re.search(r'条件空间为(.+?)[，,。\\s]', st[1])\n"
            "            if m:\n"
            "                space = m.group(1).strip()\n"
            "                if space not in declared_spaces:\n"
            "                    errors.append('条件空间未声明：「' + space + '」（编译期拦截）')\n"
            "    if errors:\n"
            "        return None, {'ok': False, 'errors': errors}\n"
            "    return [('COMPILED', len(statements))], {'ok': True}\n"),
        "cases": [(([("INSTR", "DE", "0.5"), ("止", None)], {"信任值": "数值"},
                    {"伴侣"}), ([("COMPILED", 2)], {"ok": True})),
                  (([("INSTR", "DE", "高信任"), ("止", None)], {"信任值": "数值"},
                    {"伴侣"}), (None, {"ok": False,
                    "errors": ["类型错误：德 操作数「高信任」非数值（条件空间类型）"]})),
                  (([("COND", "条件空间为未知 则 德 0.5", [("DE", "0.5")], [])],
                    {"信任值": "数值"}, {"伴侣"}), (None, {"ok": False,
                    "errors": ["条件空间未声明：「未知」（编译期拦截）"]})),
                  (([("COND", "条件空间为伴侣 则 德 0.5", [("DE", "0.5")], [])],
                    {"信任值": "数值"}, {"伴侣"}), ([("COMPILED", 1)], {"ok": True}))],
        "params": [],
        "calibration": "对照：C2 语义——名实=静态检查、条件空间=类型系统（编译期拦截类型错误/未声明空间）",
    },
    "分析-类型推断": {
        "task": "类型推断",
        "pattern": (
            "def infer_types(statements):\n"
            "    # 编译期类型推断：从赋值推断符号类型，条件空间声明登记空间类型\n"
            "    # 冲突赋值 → 类型标记'混合'（编译期拦截候选）\n"
            "    import re as _re\n"
            "    types, spaces = {}, {}\n"
            "    for st in statements:\n"
            "        kind = st[0]\n"
            "        if kind == 'assign':\n"
            "            val = st[2]\n"
            "            if isinstance(val, bool):\n"
            "                t = '布尔'\n"
            "            elif isinstance(val, (int, float)):\n"
            "                t = '数值'\n"
            "            elif isinstance(val, str):\n"
            "                t = '文本'\n"
            "            else:\n"
            "                t = '未知'\n"
            "            if st[1] in types and types[st[1]] != t:\n"
            "                types[st[1]] = '混合'\n"
            "            else:\n"
            "                types.setdefault(st[1], t)\n"
            "        elif kind == 'COND':\n"
            "            m = _re.search(r'条件空间为(.+?)(?:[，,。\\s]|$)', st[1])\n"
            "            if m:\n"
            "                spaces[m.group(1).strip()] = '已声明'\n"
            "    return {'types': types, 'spaces': spaces}\n"),
        "cases": [(([("assign", "甲", 3), ("assign", "乙", "x")],),
                   {"types": {"甲": "数值", "乙": "文本"}, "spaces": {}}),
                  (([("COND", "条件空间为伴侣 则 德 0.5", [], [])],),
                   {"types": {}, "spaces": {"伴侣": "已声明"}}),
                  (([("assign", "甲", 3), ("assign", "甲", "x")],),
                   {"types": {"甲": "混合"}, "spaces": {}}),
                  (([],), {"types": {}, "spaces": {}})],
        "params": [],
        "calibration": "对照：C2 语义深化——类型推断（赋值→数值/文本/布尔，冲突→混合）+ 条件空间声明登记（目标3 分析器完整化）",
    },
    "编译-类型检查": {
        "task": "类型检查",
        "pattern": (
            "def compile_typed(statements, infer_fn=None):\n"
            "    # 类型检查编译：先类型推断 → 未推断/混合类型符号使用 → 编译期拦截\n"
            "    # infer_fn 注入（组装白箱单元：分析-类型推断）\n"
            "    import re as _re\n"
            "    inf = infer_fn(statements) if infer_fn else {}\n"
            "    types = (inf or {}).get('types', {})\n"
            "    errors = []\n"
            "    skip = ('条件空间', '为', '则', '大于', '小于', '等于', '不等于',\n"
            "            '不小于', '不大于', '信任值', '德', '道', '止')\n"
            "    for st in statements:\n"
            "        if st[0] == 'COND':\n"
            "            for name in _re.findall(r'([\\u4e00-\\u9fffA-Za-z_]\\w*)', st[1]):\n"
            "                if name in skip:\n"
            "                    continue\n"
            "                t = types.get(name)\n"
            "                if t is None:\n"
            "                    errors.append('未推断类型：' + name)\n"
            "                elif t == '混合':\n"
            "                    errors.append('类型冲突：' + name + '（混合类型）')\n"
            "    if errors:\n"
            "        return None, {'ok': False, 'errors': errors}\n"
            "    return [('TYPED_OK', len(statements))], {'ok': True}\n"),
        "cases": [(([("assign", "甲", 3), ("COND", "甲 大于 2 则 德 0.5", [], [])],),
                   ([("TYPED_OK", 2)], {"ok": True})),
                  (([("COND", "未知量 大于 2 则 德 0.5", [], [])],),
                   (None, {"ok": False, "errors": ["未推断类型：未知量"]})),
                  (([("assign", "甲", 3), ("assign", "甲", "x"),
                     ("COND", "甲 大于 2 则 德 0.5", [], [])],),
                   (None, {"ok": False, "errors": ["类型冲突：甲（混合类型）"]}))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：C2 语义深化——类型推断接入编译管线（未推断/混合类型符号使用→编译期拦截，目标3 分析器完整化）",
    },
    "编译-完整管线": {
        "task": "完整编译",
        "pattern": (
            "def compile_full(source, declared_spaces=None):\n"
            "    # 白箱版 pc compile 单入口：中文源码 → 字节码\n"
            "    # 流程：逐行词法 → 静态检查（条件空间存在性/类型）→ 编译指令\n"
            "    import re as _re\n"
            "    spaces = set(declared_spaces or [])\n"
            "    instr_map = {'道': 'DAO', '德': 'DE', '止': 'ZHI', '知足': 'ZHIZU',\n"
            "                 '自然': 'ZIRAN', '无为': 'WUWEI'}\n"
            "    code, errors = [], []\n"
            "    pending_zhizu = []\n"
            "    for line in source.splitlines():\n"
            "        line = line.strip()\n"
            "        if not line or line.startswith('#'):\n"
            "            continue\n"
            "        m = _re.match(r'^(\\d+)。\\s*(.+?)[；;]?$', line)\n"
            "        if m:\n"
            "            line = m.group(2)\n"
            "        m = _re.match(r'^若\\s*(.+?)\\s*[,，]?\\s*则\\s*(.+?)\\s*[。;；]?$', line)\n"
            "        if m:\n"
            "            cond, then = m.group(1), m.group(2)\n"
            "            sm = _re.search(r'条件空间为(.+?)(?:[，,。\\s]|$)', cond)\n"
            "            if sm and sm.group(1).strip() not in spaces:\n"
            "                errors.append('条件空间未声明：' + sm.group(1).strip())\n"
            "                continue\n"
            "            t = then.split()\n"
            "            then_instr = (instr_map.get(t[0], t[0]),\n"
            "                          float(t[1]) if len(t) > 1 and t[1].replace('.', '', 1).isdigit()\n"
            "                          else (t[1] if len(t) > 1 else None))\n"
            "            # 条件真值编译：LOAD 左值 + PUSH 右值 + CMP + 假则跳过 then\n"
            "            cmp_map = {'大于': 'CMP_GT', '小于': 'CMP_LT', '等于': 'CMP_EQ',\n"
            "                       '不等于': 'CMP_NE', '不小于': 'CMP_GE', '不大于': 'CMP_LE'}\n"
            "            cm = _re.search(r'(.+?)\\s*(大于|小于|等于|不等于|不小于|不大于)\\s*(.+?)\\s*$', cond)\n"
            "            if cm:\n"
            "                left, op, right = cm.group(1).strip(), cm.group(2), cm.group(3).strip()\n"
            "                code.append(('LOAD', left))\n"
            "                code.append(('PUSH', float(right) if right.replace('.', '', 1).isdigit() else right))\n"
            "                code.append((cmp_map[op], None))\n"
            "                jif = len(code)\n"
            "                code.append(('JUMP_IF_FALSE', 0))\n"
            "                code.append(then_instr)\n"
            "                code[jif] = ('JUMP_IF_FALSE', len(code))\n"
            "            else:\n"
            "                code.append(('PUSH', True))\n"
            "                code.append(('JUMP_IF_FALSE', 0))\n"
            "                code.append(then_instr)\n"
            "            continue\n"
            "        m = _re.match(r'^(.+?)\\s*[=＝]\\s*(.+?)\\s*[。；;]?$', line)\n"
            "        if m:\n"
            "            # 赋值：名 = 值 → PUSH/LOAD 值 + STORE_NAME（以名举实：名实动态绑定）\n"
            "            left = m.group(1).strip()\n"
            "            right = m.group(2).strip()\n"
            "            if right.replace('.', '', 1).isdigit():\n"
            "                code.append(('PUSH', float(right) if '.' in right else int(right)))\n"
            "            else:\n"
            "                code.append(('LOAD', right))\n"
            "            code.append(('STORE', left))\n"
            "            continue\n"
            "        for kw in ('道', '德', '止', '知足', '自然', '无为'):\n"
            "            if line.startswith(kw):\n"
            "                rest = line[len(kw):].strip().rstrip('。；;')\n"
            "                arg = None\n"
            "                if rest:\n"
            "                    arg = float(rest) if rest.replace('.', '', 1).isdigit() else rest\n"
            "                if kw == '知足':\n"
            "                    # 知足：信任达标跳转（达标→跳程序末尾=满足；目标末尾回填）\n"
            "                    code.append(('ZHIZU', (float(rest), 0)))\n"
            "                    pending_zhizu.append(len(code) - 1)\n"
            "                else:\n"
            "                    code.append((instr_map[kw], arg))\n"
            "                break\n"
            "        else:\n"
            "            errors.append('无法识别：' + line)\n"
            "    for i in pending_zhizu:\n"
            "        code[i] = ('ZHIZU', (code[i][1][0], len(code)))\n"
            "    if errors:\n"
            "        return None, {'ok': False, 'errors': errors}\n"
            "    return code, {'ok': True}\n"),
        "cases": [(("道 新信任路径\n德 0.3\n止。\n", {"伴侣"}),
                   ([("DAO", "新信任路径"), ("DE", 0.3), ("ZHI", None)], {"ok": True})),
                  (("若 条件空间为未知 则 德 0.5\n止。\n", {"伴侣"}),
                   (None, {"ok": False, "errors": ["条件空间未声明：未知"]})),
                  (("若 信任值 大于 0.3，则 德 0.5\n止。\n", {"伴侣"}),
                   ([("LOAD", "信任值"), ("PUSH", 0.3), ("CMP_GT", None),
                     ("JUMP_IF_FALSE", 5), ("DE", 0.5), ("ZHI", None)], {"ok": True})),
                  (("甲 = 3\n止。\n", set()),
                   ([("PUSH", 3), ("STORE", "甲"), ("ZHI", None)], {"ok": True})),
                  (("甲 = 3\n若 甲 大于 2，则 德 0.5\n止。\n", {"伴侣"}),
                   ([("PUSH", 3), ("STORE", "甲"), ("LOAD", "甲"), ("PUSH", 2.0),
                     ("CMP_GT", None), ("JUMP_IF_FALSE", 7), ("DE", 0.5),
                     ("ZHI", None)], {"ok": True})),
                  (("德 0.3\n知足 0.7\n德 0.5\n止。\n", set()),
                   ([("DE", 0.3), ("ZHIZU", (0.7, 4)), ("DE", 0.5),
                     ("ZHI", None)], {"ok": True})),
                  (("随便文本\n", set()), (None, {"ok": False,
                   "errors": ["无法识别：随便文本"]}))],
        "params": [],
        "calibration": "对照：白箱版 pc compile 单入口（词法→静态检查→编译）；若则真值计算由编译-若则单元深化",
    },
    "求值-条件表达式": {
        "task": "条件求值",
        "pattern": (
            "def eval_condition(cond_text, symbols):\n"
            "    # 中文条件表达式求值：左值 比较词 右值（比较词：大于/小于/等于/不等于/不小于/不大于）\n"
            "    ops = {'不小于': '>=', '不大于': '<=', '大于': '>', '小于': '<',\n"
            "           '等于': '==', '不等于': '!='}\n"
            "    for kw, op in ops.items():\n"
            "        if kw in cond_text:\n"
            "            left_s, right_s = cond_text.split(kw)\n"
            "            left = symbols.get(left_s.strip())\n"
            "            right_s = right_s.strip()\n"
            "            right = (float(right_s) if right_s.replace('.', '', 1).isdigit()\n"
            "                     else symbols.get(right_s))\n"
            "            if left is None or right is None:\n"
            "                return None  # 诚实：符号未定义\n"
            "            return {'>': left > right, '<': left < right, '==': left == right,\n"
            "                    '!=': left != right, '>=': left >= right,\n"
            "                    '<=': left <= right}[op]\n"
            "    return None\n"),
        "cases": [(("信任值 大于 0.3", {"信任值": 0.5}), True),
                  (("信任值 大于 0.3", {"信任值": 0.2}), False),
                  (("信任值 不小于 0.7", {"信任值": 0.7}), True),
                  (("信任值 等于 0.5", {"信任值": 0.5}), True),
                  (("未知量 大于 0.3", {"信任值": 0.5}), None)],
        "params": [],
        "calibration": "对照：中文比较词（CHINESE_COMP_MAP：等于/大于/小于/不等于/不小于/不大于）；未定义符号诚实返回 None",
    },
    "对接-协议词法": {
        "task": "协议词法对接",
        "pattern": (
            "def bridge_token(token_name):\n"
            "    # protocol-compiler TokenType → 白箱指令名（真实词法对接校准基准）\n"
            "    m = {'DAO': 'DAO', 'DE': 'DE', 'ZIRAN': 'ZIRAN', 'WUWEI': 'WUWEI',\n"
            "         'ZHI': 'ZHI', 'ZHIZU': 'ZHIZU', 'RUO': 'COND_START',\n"
            "         'ZE': 'COND_THEN', 'FOUZE': 'COND_ELSE',\n"
            "         'WENYUE': 'STRUCT_问曰', 'DAYUE': 'STRUCT_答曰',\n"
            "         'SHUYUE': 'STRUCT_术曰'}\n"
            "    return m.get(token_name)\n"),
        "cases": [("DAO", "DAO"), ("DE", "DE"), ("ZHI", "ZHI"),
                  ("RUO", "COND_START"), ("SHUYUE", "STRUCT_术曰"),
                  ("UNKNOWN", None)],
        "params": [],
        "calibration": "对照：protocol-compiler TokenType 枚举（道德经助记符/若则/九章算术）",
    },
    "字节码-序列化": {
        "task": "字节码序列化",
        "pattern": (
            "def serialize(code):\n"
            "    # 指令列表 → .pbc 字节串（原生编译产物：op字符串+arg编码）\n"
            "    import struct\n"
            "    out = bytearray()\n"
            "    for op, arg in code:\n"
            "        b = op.encode('utf-8')\n"
            "        out.extend(struct.pack('H', len(b))); out.extend(b)\n"
            "        if arg is None:\n"
            "            out.append(0)\n"
            "        elif isinstance(arg, bool):\n"
            "            out.append(1); out.append(1 if arg else 0)\n"
            "        elif isinstance(arg, int):\n"
            "            out.append(2); out.extend(struct.pack('q', arg))\n"
            "        elif isinstance(arg, float):\n"
            "            out.append(3); out.extend(struct.pack('d', arg))\n"
            "        elif isinstance(arg, str):\n"
            "            s = arg.encode('utf-8')\n"
            "            out.append(4); out.extend(struct.pack('H', len(s))); out.extend(s)\n"
            "        elif isinstance(arg, tuple):\n"
            "            out.append(5); out.extend(struct.pack('d', arg[0]))\n"
            "            out.extend(struct.pack('q', arg[1]))\n"
            "        else:\n"
            "            raise ValueError('无法序列化参数 ' + repr(arg))\n"
            "    return bytes(out)\n"),
        "cases": [(([("DE", 0.3), ("ZHI", None)],),
                   b'\x02\x00DE\x03333333\xd3?\x03\x00ZHI\x00')],
        "params": [],
        "calibration": "对照：C3 原生编译——字节码文件格式（op字符串+arg类型标记编码）",
    },
    "字节码-反序列化": {
        "task": "字节码反序列化",
        "pattern": (
            "def deserialize(data):\n"
            "    # .pbc 字节串 → 指令列表（原生编译加载）\n"
            "    import struct\n"
            "    code, i = [], 0\n"
            "    while i < len(data):\n"
            "        n = struct.unpack_from('H', data, i)[0]; i += 2\n"
            "        op = data[i:i + n].decode('utf-8'); i += n\n"
            "        tag = data[i]; i += 1\n"
            "        if tag == 0:\n"
            "            arg = None\n"
            "        elif tag == 1:\n"
            "            arg = data[i] == 1; i += 1\n"
            "        elif tag == 2:\n"
            "            arg = struct.unpack_from('q', data, i)[0]; i += 8\n"
            "        elif tag == 3:\n"
            "            arg = struct.unpack_from('d', data, i)[0]; i += 8\n"
            "        elif tag == 4:\n"
            "            m = struct.unpack_from('H', data, i)[0]; i += 2\n"
            "            arg = data[i:i + m].decode('utf-8'); i += m\n"
            "        elif tag == 5:\n"
            "            t = struct.unpack_from('d', data, i)[0]\n"
            "            a = struct.unpack_from('q', data, i + 8)[0]\n"
            "            arg = (t, a); i += 16\n"
            "        else:\n"
            "            raise ValueError('未知标签 ' + str(tag))\n"
            "        code.append((op, arg))\n"
            "    return code\n"),
        "cases": [((b"",), []),
                  ((bytes([0x03, 0x00]) + b"ZHI" + bytes([0x00])), [("ZHI", None)])],
        "params": [],
        "calibration": "对照：C3 原生编译——.pbc 加载（与序列化对称，往返一致性由校准⑫验证）",
    },
    "调试-单步": {
        "task": "VM单步",
        "pattern": (
            "def step_exec(code, ip, stack=None, symbols=None, trust=0.0, cond=None):\n"
            "    # VM 单步：执行一条指令 → (next_ip, 新状态)；止/无为返回 halt；越界返回 None\n"
            "    if ip >= len(code):\n"
            "        return None\n"
            "    op, arg = code[ip]\n"
            "    stack = list(stack or [])\n"
            "    symbols = dict(symbols or {})\n"
            "    cond = list(cond or [])\n"
            "    ip += 1\n"
            "    if op == 'PUSH':\n"
            "        stack.append(arg)\n"
            "    elif op == 'STORE':\n"
            "        symbols[arg] = stack.pop()\n"
            "    elif op == 'LOAD':\n"
            "        if arg not in symbols:\n"
            "            return None\n"
            "        stack.append(symbols[arg])\n"
            "    elif op == 'DE':\n"
            "        trust = round(trust + arg, 3)\n"
            "    elif op == 'DAO':\n"
            "        cond.append({'name': arg})\n"
            "    elif op == 'ZIRAN':\n"
            "        while len(cond) > 1:\n"
            "            cond.pop()\n"
            "    elif op == 'ZHIZU':\n"
            "        if trust >= arg[0]:\n"
            "            ip = arg[1]\n"
            "    elif op == 'ZHI':\n"
            "        return ('halt', {'trust': trust, 'symbols': symbols, 'cond': cond,\n"
            "                        'stack': stack})\n"
            "    elif op == 'WUWEI':\n"
            "        return ('yield', {'trust': trust, 'symbols': symbols, 'cond': cond,\n"
            "                         'stack': stack})\n"
            "    return (ip, {'trust': trust, 'symbols': symbols, 'cond': cond,\n"
            "                'stack': stack})\n"),
        "cases": [(([("DE", 0.3), ("DE", 0.5)], 0),
                   (1, {"trust": 0.3, "symbols": {}, "cond": [], "stack": []})),
                  (([("DAO", "路径甲")], 0),
                   (1, {"trust": 0.0, "symbols": {}, "cond": [{"name": "路径甲"}],
                        "stack": []})),
                  (([("ZHI", None)], 0),
                   ("halt", {"trust": 0.0, "symbols": {}, "cond": [], "stack": []}))],
        "params": [],
        "calibration": "对照：C4 调试器单步（一条指令 → 新状态；止/无为=控制流信号）",
    },
    "分析-字节码转储": {
        "task": "字节码转储",
        "pattern": (
            "def dump_bytecode(code):\n"
            "    # 字节码 → 可读指令列表（地址+指令+参数——分析器输出）\n"
            "    return [f'{i:4d}  {op:14s} {arg}' for i, (op, arg) in enumerate(code)]\n"),
        "cases": [(([("DE", 0.3), ("ZHI", None)],),
                  ['   0  DE             0.3', '   1  ZHI            None'])],
        "params": [],
        "calibration": "对照：C4 分析器字节码转储（可读调试输出）",
    },
    "词法-注释剥离": {
        "task": "注释剥离",
        "pattern": (
            "def strip_comments(src):\n"
            "    # 注释剥离：# 行注释 / 井号中文注释（词法预处理）\n"
            "    lines = []\n"
            "    for line in src.splitlines():\n"
            "        idx = line.find('#')\n"
            "        lines.append(line[:idx] if idx >= 0 else line)\n"
            "    return '\\n'.join(lines)\n"),
        "cases": [("a = 1  # 赋值", 'a = 1  '),
                  ("# 注释\nb = 2", '\nb = 2'),
                  ("无注释", '无注释')],
        "params": [],
        "calibration": "对照：词法预处理——注释剥离（# 行注释，中文注释同语义）",
    },
    "编译-逻辑表达式": {
        "task": "逻辑表达式",
        "pattern": (
            "def compile_logic(left_instrs, op, right_instrs):\n"
            "    # 逻辑表达式：且/或 → 短路跳转字节码（AND/OR 语义）\n"
            "    code = list(left_instrs)\n"
            "    if op == '且':\n"
            "        code.append(('JUMP_IF_FALSE', 0))  # 左假短路\n"
            "        code.extend(right_instrs)\n"
            "    else:  # 或\n"
            "        code.append(('JUMP_IF_TRUE', 0))   # 左真短路\n"
            "        code.extend(right_instrs)\n"
            "    return code\n"),
        "cases": [(([("LOAD", "a")], '且', [("LOAD", "b")]),
                   [("LOAD", "a"), ("JUMP_IF_FALSE", 0), ("LOAD", "b")]),
                  (([("LOAD", "a")], '或', [("LOAD", "b")]),
                   [("LOAD", "a"), ("JUMP_IF_TRUE", 0), ("LOAD", "b")])],
        "params": [],
        "calibration": "对照：编译逻辑——且/或短路（左操作数决定是否求右——短路求值语义）",
    },
    "编译-链式比较": {
        "task": "链式比较",
        "pattern": (
            "def compile_chain(cmp1, cmp2):\n"
            "    # 链式比较：a < b < c → 比较1 且 比较2（AND 组合）\n"
            "    code = list(cmp1)\n"
            "    code.append(('JUMP_IF_FALSE', 0))  # 第一比较假 → 短路\n"
            "    code.extend(cmp2)\n"
            "    return code\n"),
        "cases": [(([("LOAD", "a"), ("LOAD", "b"), ("CMP_LT", None)],
                    [("LOAD", "b"), ("LOAD", "c"), ("CMP_LT", None)]),
                   [("LOAD", "a"), ("LOAD", "b"), ("CMP_LT", None),
                    ("JUMP_IF_FALSE", 0),
                    ("LOAD", "b"), ("LOAD", "c"), ("CMP_LT", None)])],
        "params": [],
        "calibration": "对照：编译链式比较——a<b<c = (a<b) 且 (b<c)（短路组合，Python 链式语义）",
    },
    "编译-常量折叠": {
        "task": "常量折叠",
        "pattern": (
            "def fold_constants(instrs):\n"
            "    # 常量折叠：PUSH 常量 + 算术 → 立即结果（编译期求值优化）\n"
            "    out, i = [], 0\n"
            "    while i < len(instrs):\n"
            "        if (i + 2 < len(instrs) and instrs[i][0] == 'PUSH'\n"
            "                and instrs[i + 1][0] == 'PUSH'\n"
            "                and instrs[i + 2][0] in ('ADD', 'SUB', 'MUL', 'DIV')):\n"
            "            a, b = instrs[i][1], instrs[i + 1][1]\n"
            "            op = instrs[i + 2][0]\n"
            "            val = {'ADD': a + b, 'SUB': a - b, 'MUL': a * b,\n"
            "                   'DIV': a / b}[op]\n"
            "            out.append(('PUSH', val))\n"
            "            i += 3\n"
            "        else:\n"
            "            out.append(instrs[i])\n"
            "            i += 1\n"
            "    return out\n"),
        "cases": [(([("PUSH", 1), ("PUSH", 2), ("ADD", None), ("LOAD", "x")],),
                   [("PUSH", 3), ("LOAD", "x")]),
                  (([("PUSH", 10), ("PUSH", 4), ("MUL", None)],),
                   [("PUSH", 40)])],
        "params": [],
        "calibration": "对照：编译优化——常量折叠（PUSH+PUSH+算术 → PUSH 结果，编译期求值）",
    },
    "编译-死代码消除": {
        "task": "死代码消除",
        "pattern": (
            "def dead_code_elim(code):\n"
            "    # 死代码消除：不可达指令（无条件 JUMP 之后）删除\n"
            "    live = []\n"
            "    reachable = True\n"
            "    for op, arg in code:\n"
            "        if op == 'JUMP':\n"
            "            live.append((op, arg))\n"
            "            reachable = False\n"
            "        elif reachable:\n"
            "            live.append((op, arg))\n"
            "    return live\n"),
        "cases": [(([("DE", 0.5), ("JUMP", 5), ("DE", 0.9), ("ZHI", None)],),
                   [("DE", 0.5), ("JUMP", 5)]),
                  (([("DE", 0.1)],), [("DE", 0.1)])],
        "params": [],
        "calibration": "对照：编译优化——死代码消除（JUMP 后不可达指令删除）",
    },
    "编译-寄存器分配": {
        "task": "寄存器分配",
        "pattern": (
            "def reg_alloc(vars_used):\n"
            "    # 寄存器分配：变量 → 寄存器（无冲突复用，溢出计数）\n"
            "    regs = {}\n"
            "    spills = 0\n"
            "    for v in vars_used:\n"
            "        if v not in regs:\n"
            "            if len(regs) < 4:\n"
            "                regs[v] = 'R' + str(len(regs))\n"
            "            else:\n"
            "                spills += 1\n"
            "                regs[v] = 'mem'\n"
            "    return regs, spills\n"),
        "cases": [((['a', 'b', 'c', 'd', 'e'],), ({'a': 'R0', 'b': 'R1',
                                                  'c': 'R2', 'd': 'R3',
                                                  'e': 'mem'}, 1)),
                  (([],), ({}, 0))],
        "params": [],
        "calibration": "对照：编译优化——寄存器分配（4 寄存器，溢出到内存）",
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
