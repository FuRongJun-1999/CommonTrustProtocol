---
name: pylang-7ca54f0e
description: >-
  默认参数 / 语法-默认参数 / Python 默认参数 / 参数绑定（缺省用默认。用户提到这些词时使用本技能。
  场景：对照：Python 默认参数（缺省用默认值绑定）。
  【不适用】Not for 以下场景：条件不满足即不适用（负路由：输入不满足生效条件时返回 None/不执行）
license: MIT
compatibility: >-
  参数 params/defaults/call_args 合法
allowed-tools: Read Write Bash
metadata:
  version: "1.0"
  skill-author: 灵枢（AEIS）
  last-reviewed: "2026-08-29"
  kccs:
    trigger_words: ["默认参数", "语法-默认参数", "Python 默认参数", "参数绑定（缺省用默认"]
    when: "参数 params/defaults/call_args 合法"
    sub: ["① 调用 enumerate；② 调用 len"]
    execute: "循环迭代；顺序调用"
    not_applicable: ["条件不满足即不适用（负路由：输入不满足生效条件时返回 None/不执行）"]
  calibration: "对照：Python 默认参数（缺省用默认值绑定）"
---

# 语法-默认参数（pylang-7ca54f0e）

## When to use

任务「默认参数」；对照：Python 默认参数（缺省用默认值绑定）。

## 克制条款（不适用条件）

条件不满足即不适用（负路由：输入不满足生效条件时返回 None/不执行）

## How to execute

循环迭代；顺序调用

## Verification

- 单元样例 3 条（cases 断言）
- 物理基底：按 calibration 对照（编译/运行/断言裁决）

## References

- 单元库：compiler_code_units.py「语法-默认参数」
