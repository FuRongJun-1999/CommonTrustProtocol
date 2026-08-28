---
name: unit-64c4224b
description: >-
  中间表示/编译-中间表示。用户提到与「中间表示」相关的能力时使用本技能。
  场景：对照：三地址码——IR 中间表示（赋值/二元运算）。
  【不适用】Not for 以下场景：op 非 {assign, binary} 时
license: MIT
compatibility: >-
  op ∈ {assign, binary}
allowed-tools: Read Write Bash
metadata:
  version: "1.0"
  skill-author: 灵枢（AEIS）
  last-reviewed: "2026-08-29"
  kccs:
    when: "op ∈ {assign, binary}"
    sub: ["① op 分支处理"]
    execute: "按 op 分派"
    not_applicable: ["op 非 {assign, binary} 时"]
  calibration: "对照：三地址码——IR 中间表示（赋值/二元运算）"
---

# 编译-中间表示（unit-64c4224b）

## When to use

任务「中间表示」；对照：三地址码——IR 中间表示（赋值/二元运算）。

## 克制条款（不适用条件）

op 非 {assign, binary} 时

## How to execute

按 op 分派

## Verification

- 单元样例 3 条（cases 断言）
- 物理基底：按 calibration 对照（编译/运行/断言裁决）

## References

- 单元库：compiler_code_units.py「编译-中间表示」
