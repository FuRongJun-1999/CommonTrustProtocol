# -*- coding: utf-8 -*-
"""skill_export.py · 条件单元库 → Agent Skills 兼容导出（v1.0 设计落地）

原则：兼容是形式（agentskills.io + agent-plugins.org），条件是要求（KCCS 四要素不放弃）。
- 从单元 pattern 注释解析四要素（生效条件/子功能/执行/不适用条件）
- 渲染 SKILL.md（含克制条款章节 + metadata.kccs）+ plugin.json（extensions.condition-route）

用法：
  python tools/skill_export.py                     # 导出全部单元（默认前 N 个可限）
  python tools/skill_export.py --units 编译-递归,编译-赋值   # 指定单元
  python tools/skill_export.py --out tools/skill-export
"""
import os, re, sys, json, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WISDOM = os.path.join(ROOT, "aeis", "wisdom")

# 中文 uid → 英文 slug（SKILL name 要求 slug；未映射的回退 domain-拼音化简化）
NAME_MAP = {
    "编译-递归": "compile-recursive",
    "编译-赋值": "compile-assign",
    "编译-若则": "compile-if-then",
    "编译-函数定义": "compile-func-def",
    "编译-循环": "compile-while",
    "VM-条件跳转": "vm-cond-jump",
    "VM-算术执行": "vm-arithmetic",
    "VM-函数调用": "vm-func-call",
    "VM-信任累积": "vm-trust-accum",
    "VM-条件空间": "vm-cond-space",
    "词法-道德经": "lex-dao-de-jing",
    "词法-九章算术": "lex-nine-chapters",
    "校验-名实": "check-name-real",
    "编译-类型检查": "compile-type-check",
    "编译-表达式树": "compile-expr-tree",
    "编译-逻辑表达式": "compile-logic-expr",
    "分析-类型推断": "analyze-type-infer",
    "编译-作用域分析": "compile-scope",
    "词法-中文程序": "lex-chinese-program",
    "编译-完整管线": "compile-full-pipeline",
}

def slugify(uid):
    """uid → 英文 slug：映射表优先，否则去符号取拼音不可行则用 domain-unit 编号。"""
    if uid in NAME_MAP:
        return NAME_MAP[uid]
    # 回退：非中文部分 + 哈希尾（保证唯一合法 slug）
    m = re.sub(r"[^a-zA-Z0-9]+", "-", uid).strip("-").lower()
    if m:
        return m[:40]
    import hashlib
    return "unit-" + hashlib.md5(uid.encode()).hexdigest()[:8]

# 通用模板注释（code_compose 占位，非单元特有语义）——过滤
TEMPLATE_MARKS = [
    "主体逻辑执行", "顺序执行", "返回 None/不执行",
    "name/params/cond_instrs", "value_instrs", "输入不满足生效条件",
]

def parse_four_elements(pattern):
    """从 pattern 注释解析 KCCS 四要素。
    策略：过滤 code_compose 通用模板注释；剩余注释行=单元特有语义；未标注则回退 calibration。"""
    when = sub = execute = not_app = None
    specific = []  # 单元特有语义注释行（非模板）
    for line in (pattern or "").splitlines():
        raw = line.strip()
        if not raw.startswith("#"):
            continue  # 只处理注释行（跳过代码行）
        ls = raw.lstrip("#").strip()
        if not ls:
            continue
        if any(t in ls for t in TEMPLATE_MARKS):
            # 模板行：仅保留「不适用条件」的通用负路由语义（条件不满足=不适用）
            if ls.startswith("不适用条件") and not_app is None:
                not_app = "条件不满足即不适用（负路由：输入不满足生效条件时返回 None/不执行）"
            continue
        if ls.startswith("生效条件"):
            when = ls.split("：", 1)[-1].strip() if "：" in ls else ls
        elif ls.startswith("子功能"):
            sub = ls.split("：", 1)[-1].strip() if "：" in ls else ls
        elif ls.startswith("执行"):
            execute = ls.split("：", 1)[-1].strip() if "：" in ls else ls
        elif ls.startswith("不适用条件"):
            not_app = ls.split("：", 1)[-1].strip() if "：" in ls else ls
        else:
            specific.append(ls)  # 单元特有注释（如「递归函数：若 基条件…」）
    return when, sub, execute, not_app, specific

def render_skill(uid, unit, slug):
    """渲染 SKILL.md。"""
    task = unit.get("task", "")
    calib = unit.get("calibration", "")
    when, sub, execute, not_app, specific = parse_four_elements(unit.get("pattern", ""))
    cases_n = len(unit.get("cases", []))
    today = datetime.date.today().isoformat()

    # 特有语义优先级：pattern 特有注释 > calibration > 通用
    if not execute and specific:
        execute = "；".join(specific[:3])
    if not when and calib:
        when = calib

    desc_trigger = f"{task}/{uid}。用户提到与「{task}」相关的能力时使用本技能。"
    desc_not = ""
    if not_app:
        desc_not = f"【不适用】Not for 以下场景：{not_app[:120]}"

    md = f"""---
name: {slug}
description: >-
  {desc_trigger}
  场景：{calib[:120] if calib else '白箱条件单元（KCCS 四要素）'}。
  {desc_not}
license: MIT
compatibility: >-
  {when or '环境以单元校准为准（Python 3.10+）'}
allowed-tools: Read Write Bash
metadata:
  version: "1.0"
  skill-author: 灵枢（AEIS）
  last-reviewed: "{today}"
  kccs:
    when: {json.dumps(when or '', ensure_ascii=False)}
    sub: {json.dumps([sub] if sub else [], ensure_ascii=False)}
    execute: {json.dumps(execute or '', ensure_ascii=False)}
    not_applicable: {json.dumps([not_app] if not_app else [], ensure_ascii=False)}
  calibration: {json.dumps(calib or '', ensure_ascii=False)}
---

# {uid}（{slug}）

## When to use

任务「{task}」；{calib or '按单元校准基准对照'}。

## 克制条款（不适用条件）

{not_app or '（未标注——按条件路由图负路由规则处理：条件不满足即拒绝）'}

## How to execute

{execute or '（执行机制见单元 pattern）'}

## Verification

- 单元样例 {cases_n} 条（cases 断言）
- 物理基底：按 calibration 对照（编译/运行/断言裁决）

## References

- 单元库：compiler_code_units.py「{uid}」
"""
    return md

def render_plugin(units_out):
    """渲染 plugin.json（agent-plugins.org 1.0.0 + extensions.condition-route）。"""
    return {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": "lingshu-condition-units",
        "version": "0.1.0",
        "description": "灵枢条件单元库（Agent Skills 兼容导出）——白箱条件化知识，KCCS 四要素不放弃",
        "author": {"name": "灵枢（AEIS）"},
        "license": "MIT",
        "keywords": ["agent-skills", "whitebox", "condition-route", "kccs", "protocol-compiler"],
        "extensions": {
            "lingshu": {
                "condition-route": {
                    "domain": "compiler",
                    "unit-count": len(units_out),
                    "kccs-version": "四要素（生效条件/子功能/执行/不适用条件）",
                    "negative-route": True,
                    "condition-space": "观测位置/观测工具/时间窗口/存在约束（D(C)）",
                }
            }
        },
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="", help="逗号分隔指定单元；空=全部（建议先小批量验证）")
    ap.add_argument("--out", default=os.path.join(HERE, "skill-export"))
    ap.add_argument("--limit", type=int, default=0, help="最多导出单元数（0=不限）")
    args = ap.parse_args()

    sys.path.insert(0, WISDOM)
    import compiler_code_units as ccu
    units = ccu.COMPILER_UNITS

    selected = [u.strip() for u in args.units.split(",") if u.strip()] if args.units else list(units.keys())
    if args.limit:
        selected = selected[: args.limit]

    out_dir = args.out
    os.makedirs(os.path.join(out_dir, "skills"), exist_ok=True)

    exported = []
    for uid in selected:
        if uid not in units:
            print(f"  ✘ 跳过未知单元: {uid}")
            continue
        slug = slugify(uid)
        md = render_skill(uid, units[uid], slug)
        path = os.path.join(out_dir, "skills", slug, "SKILL.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        exported.append(uid)
        print(f"  ✓ {uid} → skills/{slug}/SKILL.md")

    plugin = render_plugin(exported)
    with open(os.path.join(out_dir, "plugin.json"), "w", encoding="utf-8") as f:
        json.dump(plugin, f, ensure_ascii=False, indent=2)
    print(f"\nplugin.json 已生成（units={len(exported)}）")
    print(f"输出目录: {out_dir}")

if __name__ == "__main__":
    main()
