---
name: compile-recursive
description: >-
  compile_recursive / 递归调用 / 递归函数 / 阶乘 / 斐波那契 / 终止条件 / 基例。
  用户提到这些词时使用本技能：把「定义函数 + 函数体内自调用 + 终止条件」编译为字节码。
  场景：中文协议编译器（protocol-compiler）中需要编译递归函数（若则体内 RETURN 的递归形态）。
  触发：代码引用 compile_recursive / Compiler.funcs / CALL 回填入口。
  【不适用】Not for 非递归函数（顺序/分支即可）；not applicable when 循环结构
  （当…执行——循环是 LOOP_STMT，与递归不同字节码形态）；无终止条件的递归会死循环，
  不适用本单元（应拒绝）。
license: MIT
compatibility: >-
  Python 3.10+，protocol-compiler core 模块可导入（compile_source / Compiler）。
  前置：词法/语法已解析出 FUNC_DEF AST；函数名与参数列表已登记。
allowed-tools: Read Write Bash
metadata:
  version: "1.0"
  skill-author: 灵枢（AEIS）
  last-reviewed: "2026-08-28"
  kccs:
    when: 参数 name/params/cond_instrs/then_ret/else_expr_instrs 合法；AST 为 FUNC_DEF 且函数体含自身调用
    sub:
      - 组装函数体字节码（条件跳转 + RETURN）
      - 登记函数入口与参数（CALL 由调用方回填入口）
      - 校验终止条件存在（基例）
    execute: "若 基条件 则 返回 基值，否则 返回 表达式（含自身调用）→ 若则体内 RETURN；入口=函数体起点，体末 RETURN"
    not_applicable:
      - 非递归函数（无自身调用）
      - 循环结构（当…执行 LOOP_STMT——字节码形态不同）
      - 无终止条件的递归（死循环风险，应拒绝）
  calibration: "对照：protocol-compiler 递归函数（若则体内 RETURN，对齐阶乘 da997ef 语义）"
---

# 编译-递归（Compile Recursive）

## When to use

用户要求编译**递归函数**：函数体内调用自身 + 必须有终止条件（基例）。
典型：阶乘（n<2 返回 1）、斐波那契（n<2 返回 n）、递归累加。

## 克制条款（不适用条件）

- **不是**所有函数都是递归——顺序/分支函数用普通编译路径。
- **循环 ≠ 递归**：「当…执行」是 LOOP_STMT（条件跳转回环），本单元是 CALL/RETURN 调用栈帧——字节码形态不同。
- **无终止条件**的「递归」不适用本单元——它会导致死循环（VM 步数上限拦截），应拒绝而非编译。
- 混用上述场景 = 条件空间错配（把递归的条件套到循环上），结果产生哪个都不满足的字节码。

## How to execute

1. 校验：AST 是 FUNC_DEF 且函数体含自身调用（编译-递归生效条件）
2. 组装函数体：条件跳转（JUMP_IF_FALSE）+ then 分支 RETURN + else 分支表达式 RETURN
3. 登记 `{name, params, body}`——函数入口 = 函数体起点，体末 RETURN
4. 调用方（CALL 指令）回填函数入口标签

## Verification

- 编译产物含 `CALL` 与 `RETURN` 指令（自验）
- 物理基底：`compile_source(中文递归程序)` + `ConditionVM().run` → 结果断言
  （阶乘(5)=120.0 / 斐波那契(6)=8.0，±0.01）

## References

- protocol-compiler: `core/compiler.py` · `core/condition_vm.py`（Opcode.CALL/RETURN）
- 单元库: `compiler_code_units.py`「编译-递归」（cases: 阶乘→body 字节码对照）
