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
