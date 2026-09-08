# -*- coding: utf-8 -*-
"""export_ccg_dump.py · 解析 MD 目录生成 CCG 路由索引（card_route 消费）

数据源（唯一权威）：aeis/knowledge/*.md —— 知识正本，人读 / git / 审计
产物（可重建派生物）：aeis/knowledge/_ccg_dump.json —— 路由索引

md 中每个知识点的格式：
    ### 知识点名

    - **生效条件**: 问X | 问Y          ← 路由正索引（必需，缺失则不生成路由记录）
    - **不适用条件**: 问A | 问B        ← 路由负索引（可选，≥2 命中排除）

    正文…                              ← 执行内容 / direct_answer

新增知识点流程：直接在学科 .md 里写 ### 块（含 生效条件）→ 重跑本脚本 → qbank_eval_md。

用法：
    python tools/export_ccg_dump.py                # 写出 _ccg_dump.json
    python tools/export_ccg_dump.py --dry-run      # 只统计不写
    python tools/export_ccg_dump.py --derive-missing   # 缺生效条件的块按名称派生（默认跳过并告警）
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KNOWLEDGE = os.path.join(ROOT, "aeis", "knowledge")
OUT = os.path.join(KNOWLEDGE, "_ccg_dump.json")


def _split_cond(raw: str):
    return [t.strip() for t in re.split(r"[|｜]", raw) if t.strip()]


def parse_md(path: str):
    """解析一个学科 md → (领域, 教育层级, [(name, body, 生效条件|None, 不适用条件|None)])"""
    s = open(path, encoding="utf-8").read()

    def meta(key):
        m = re.search(rf"-\s*\*\*{key}\*\*[:：]\s*(.+)", s)
        return m.group(1).strip() if m else ""

    domain, edu = meta("领域"), meta("教育层级")
    blocks = []
    for part in re.split(r"^### ", s, flags=re.M)[1:]:
        lines = part.split("\n")
        name = lines[0].strip()
        cond = neg = None
        body_lines = []
        for ln in lines[1:]:
            m1 = re.match(r"-\s*\*\*生效条件\*\*[:：]\s*(.+)", ln)
            m2 = re.match(r"-\s*\*\*不适用条件\*\*[:：]\s*(.+)", ln)
            if m1:
                cond = _split_cond(m1.group(1))
            elif m2:
                neg = _split_cond(m2.group(1))
            else:
                body_lines.append(ln)
        blocks.append((name, "\n".join(body_lines).strip(), cond, neg))
    return domain, edu, blocks


def _derive_cond(name: str):
    cond = [f"问{name}"]
    core = re.split(r"[（(：:·]", name)[0].strip()
    if core and core != name and len(core) >= 2:
        cond.append(f"问{core}")
    return cond


def _subfunc(body: str, limit: int = 3):
    return [p for p in re.split(r"[。；;]", body) if p.strip()][:limit]


def build(derive_missing: bool = False):
    entries = []
    files = sorted(f for f in os.listdir(KNOWLEDGE) if f.endswith(".md"))
    no_cond = []
    for f in files:
        domain, edu, blocks = parse_md(os.path.join(KNOWLEDGE, f))
        for name, body, cond, neg in blocks:
            if not name:
                continue
            if not cond:
                if derive_missing:
                    cond = _derive_cond(name)
                else:
                    no_cond.append(f"{f}::{name}")
                    continue
            nid = "md_" + hashlib.sha1((f + "\x00" + name).encode("utf-8")).hexdigest()[:16]
            sa = {
                "name": name,
                "kind": "knowledge_point",
                "domain": domain,
                "edu_level": edu,
                "source_file": f,
                "comment": {
                    "name": f"{name}（{domain}）" if domain else name,
                    "生效条件": cond,
                    "子功能": _subfunc(body),
                    "执行": body,
                    "不适用条件": neg or [],
                },
            }
            entries.append({
                "id": nid,
                "sa_json": json.dumps(sa, ensure_ascii=False),
                "content": body,
            })
    return entries, files, no_cond


def main(write=True, derive_missing=False):
    entries, files, no_cond = build(derive_missing=derive_missing)
    print(f"解析 md: {len(files)} 个学科文件")
    print(f"生成 CCG 路由记录: {len(entries)} 条")
    if no_cond:
        print(f"⚠️ 缺 生效条件 的知识点（未生成路由记录）: {len(no_cond)}")
        for x in no_cond[:10]:
            print(f"    {x}")
    if write:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as fp:
            json.dump(entries, fp, ensure_ascii=False)
        print(f"已写出: {OUT}")
    return entries


if __name__ == "__main__":
    main(write="--dry-run" not in sys.argv,
         derive_missing="--derive-missing" in sys.argv)
