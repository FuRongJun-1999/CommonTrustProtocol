---
name: vm-closure-create
description: >-
  闭包创建/VM-闭包创建。用户提到与「闭包创建」相关的能力时使用本技能。
  场景：对照：闭包对象=函数体+捕获环境（MAKE_CLOSURE 指令语义；未捕获名字不入环境）。
  【不适用】Not for 以下场景：条件不满足即不适用（负路由：输入不满足生效条件时返回 None/不执行）
license: MIT
compatibility: >-
  参数 func_body/free_names/captured_values 合法
allowed-tools: Read Write Bash
metadata:
  version: "1.0"
  skill-author: 灵枢（AEIS）
  last-reviewed: "2026-08-29"
  kccs:
    when: "参数 func_body/free_names/captured_values 合法"
    sub: ["① 调用 list"]
    execute: "顺序调用"
    not_applicable: ["条件不满足即不适用（负路由：输入不满足生效条件时返回 None/不执行）"]
  calibration: "对照：闭包对象=函数体+捕获环境（MAKE_CLOSURE 指令语义；未捕获名字不入环境）"
---

# VM-闭包创建（vm-closure-create）

## When to use

任务「闭包创建」；对照：闭包对象=函数体+捕获环境（MAKE_CLOSURE 指令语义；未捕获名字不入环境）。

## 克制条款（不适用条件）

条件不满足即不适用（负路由：输入不满足生效条件时返回 None/不执行）

## How to execute

顺序调用

## Verification

- 单元样例 3 条（cases 断言）
- 物理基底：按 calibration 对照（编译/运行/断言裁决）

## References

- 单元库：compiler_code_units.py「VM-闭包创建」
