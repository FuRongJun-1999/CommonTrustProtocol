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

# 六域单元库（域 → 模块/变量名）
DOMAINS = {
    "compiler": ("compiler_code_units", "COMPILER_UNITS"),
    "pylang": ("python_code_units", "PYTHON_UNITS"),
    "graph": ("graph_db_units", "GRAPH_UNITS"),
    "os": ("os_units", "OS_UNITS"),
    "browser": ("browser_units", "BROWSER_UNITS"),
    "net": ("net_units", "NET_UNITS"),
}

# 中文 uid → 英文 slug（SKILL name 要求 slug；未映射的统一哈希尾保证唯一）
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
    "VM-循环执行": "vm-loop-run",
    "VM-执行循环": "vm-run-loop",
    "VM-闭包创建": "vm-closure-create",
    "VM-闭包调用": "vm-closure-call",
    "VM-栈操作": "vm-stack-ops",
    "VM-比较执行": "vm-compare",
    "VM-引用计数": "vm-refcount",
    "VM-指令剖析": "vm-profiling",
    "VM-栈保护": "vm-stack-guard",
    "VM-数组操作": "vm-array-ops",
    "VM-异常处理": "vm-exception",
    "VM-短路求值": "vm-short-circuit",
}

def slugify(uid, domain="unit"):
    """uid → 英文 slug：映射表优先；未映射统一哈希尾（保证唯一合法，不冲突）。"""
    if uid in NAME_MAP:
        return NAME_MAP[uid]
    import hashlib
    return f"{domain}-" + hashlib.md5(uid.encode()).hexdigest()[:8]

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

def _clean_trigger(part):
    """清洗触发词片段：去括号内容/尾标点；混合拉丁段砍到中文边界；纯 API 标识符保留。"""
    p = (part or "").strip()
    if not p:
        return None
    # 去括号及括号内
    p = re.sub(r"[（(].*?[)）]", "", p)
    p = p.rstrip("。；;，,：:—")
    if not p:
        return None
    # 含拉丁字符：若整体是合法标识符（API 触发）保留；否则砍到中文边界前
    if re.search(r"[A-Za-z]", p):
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", p):
            return p  # 纯 API 名（compile_recursive）
        m = re.match(r"^(.*?[\u4e00-\u9fff])", p)
        if m:
            p = m.group(1)
        else:
            return None
    return p[:12]

def extract_triggers(task, uid, calib, specific):
    """提取触发词（KCCS v0.2 五要素）：task/uid/calibration 核心短语/特有注释语义词。"""
    triggers = []
    seen = set()
    def add(w, full=False):
        if full:
            w = re.sub(r"[（(].*?[)）]", "", (w or "").strip()).rstrip("。；;，,：:—")
        else:
            w = _clean_trigger(w)
        if w and w not in seen and len(w) >= 2:
            seen.add(w)
            triggers.append(w)
    add(task, full=True)
    add(uid, full=True)
    # calibration 核心短语（「对照：X（Y…）」→ 取 X 前段 + Y 前段）
    if calib:
        m = re.search(r"对照：(.+?)（", calib)
        if m:
            core = m.group(1).strip()
            for part in re.split(r"[，、/]", core):
                add(part)
    # 特有注释语义词（递归函数/阶乘 等）
    for s in (specific or [])[:3]:
        for part in re.split(r"[；：，]", s)[:2]:
            add(part)
    return triggers[:8]

def render_skill(uid, unit, slug, domain="unit"):
    """渲染 SKILL.md（KCCS v0.2 五要素：触发词 + 四要素）。"""
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

    triggers = extract_triggers(task, uid, calib, specific)
    trig_text = " / ".join(triggers)

    desc_trigger = f"{trig_text}。用户提到这些词时使用本技能。"
    desc_not = ""
    if not_app:
        desc_not = f"【不适用】Not for 以下场景：{not_app[:120]}"

    md = f"""---
name: {slug}
description: >-
  {trig_text}。用户提到这些词时使用本技能。
  场景：{calib[:120] if calib else '白箱条件单元（KCCS 五要素）'}。
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
    trigger_words: {json.dumps(triggers, ensure_ascii=False)}
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

def render_plugin(units_out, domains):
    """渲染 plugin.json（agent-plugins.org 1.0.0 + extensions.condition-route 六域）。"""
    return {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": "lingshu-skills",
        "version": "0.1.0",
        "description": "灵枢（AEIS）自我认知技能包——白箱条件化知识（Agent Skills 兼容导出）。本质是灵枢了解自身的工具：每个技能描述灵枢在什么条件下能做什么、怎么执行、克制什么（KCCS 四要素），由条件路由图精确路由，由灵枢 MCP 工具执行验证（物理基底）。",
        "author": {"name": "灵枢（AEIS）· CommonTrustProtocol"},
        "license": "MIT",
        "keywords": ["agent-skills", "whitebox", "condition-route", "kccs", "self-cognition", "lingshu"],
        "extensions": {
            "lingshu": {
                "self-cognition": {
                    "essence": "灵枢自我认知技能包——用灵枢自己构建的条件单元，描述灵枢自己如何认知（白箱自举的对外投影）",
                    "source-of-truth": "CTP 主仓库 aeis/wisdom/*_code_units.py（真源）；本 skills/ 为生成投影"
                },
                "condition-route": {
                    "domains": domains,
                    "unit-count": len(units_out),
                    "kccs-version": "四要素（生效条件/子功能/执行/不适用条件）",
                    "negative-route": True,
                    "condition-space": "观测位置/观测工具/时间窗口/存在约束（D(C)）"
                },
                "mcp": {
                    "relation": "技能为说明书（何时用/怎么用/克制什么），灵枢 MCP 77 工具为执行（物理基底）——技能 Verification 由 MCP 工具（编译/运行/断言）裁决",
                    "entry": "aeis-mcp（MCP stdio server）· dsh-memory 插件挂载"
                }
            }
        },
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="", help="逗号分隔指定单元；空=全部")
    ap.add_argument("--domains", default="", help="逗号分隔指定域（compiler/pylang/graph/os/browser/net）；空=全部六域")
    ap.add_argument("--out", default=os.path.join(HERE, "skill-export"))
    ap.add_argument("--limit", type=int, default=0, help="每域最多导出单元数（0=不限）")
    args = ap.parse_args()

    sys.path.insert(0, WISDOM)
    domains_cfg = [d.strip() for d in args.domains.split(",") if d.strip()] or list(DOMAINS.keys())
    selected = [u.strip() for u in args.units.split(",") if u.strip()] if args.units else None

    out_dir = args.out
    os.makedirs(os.path.join(out_dir, "skills"), exist_ok=True)

    exported = []
    exported_domains = {}
    for dom in domains_cfg:
        if dom not in DOMAINS:
            print(f"  ✘ 未知域: {dom}")
            continue
        mod_name, var_name = DOMAINS[dom]
        try:
            mod = __import__(mod_name)
            units = getattr(mod, var_name)
        except Exception as e:
            print(f"  ✘ 域 {dom} 加载失败: {e}")
            continue
        unit_ids = list(units.keys()) if selected is None else [u for u in selected if u in units]
        if args.limit:
            unit_ids = unit_ids[: args.limit]
        n = 0
        for uid in unit_ids:
            slug = slugify(uid, dom)
            md = render_skill(uid, units[uid], slug)
            path = os.path.join(out_dir, "skills", slug, "SKILL.md")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(md)
            exported.append(uid)
            n += 1
        exported_domains[dom] = n
        print(f"  ✓ {dom} 域: {n} 单元 → skills/")

    plugin = render_plugin(exported, exported_domains)
    with open(os.path.join(out_dir, "plugin.json"), "w", encoding="utf-8") as f:
        json.dump(plugin, f, ensure_ascii=False, indent=2)
    print(f"\nplugin.json 已生成（domains={exported_domains} 合计={len(exported)}）")
    print(f"输出目录: {out_dir}")

if __name__ == "__main__":
    main()
