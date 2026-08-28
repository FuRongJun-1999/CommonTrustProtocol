---
name: os-485833fa
description: >-
  页缓存/内存-页缓存。用户提到与「页缓存」相关的能力时使用本技能。
  场景：对照：页缓存——文件页缓存命中/写入/命中率。
  【不适用】Not for 以下场景：op 非 {get, put, stats} 时
license: MIT
compatibility: >-
  op ∈ {get, put, stats}
allowed-tools: Read Write Bash
metadata:
  version: "1.0"
  skill-author: 灵枢（AEIS）
  last-reviewed: "2026-08-29"
  kccs:
    when: "op ∈ {get, put, stats}"
    sub: ["① op 分支处理"]
    execute: "按 op 分派；顺序调用"
    not_applicable: ["op 非 {get, put, stats} 时"]
  calibration: "对照：页缓存——文件页缓存命中/写入/命中率"
---

# 内存-页缓存（os-485833fa）

## When to use

任务「页缓存」；对照：页缓存——文件页缓存命中/写入/命中率。

## 克制条款（不适用条件）

op 非 {get, put, stats} 时

## How to execute

按 op 分派；顺序调用

## Verification

- 单元样例 4 条（cases 断言）
- 物理基底：按 calibration 对照（编译/运行/断言裁决）

## References

- 单元库：compiler_code_units.py「内存-页缓存」
