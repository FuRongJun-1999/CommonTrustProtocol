#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""migrate_memory.py · 会话记忆 md 迁移入库（资产归灵枢，脱离 ZCode 依赖）
================================================
把 ZCode 会话记忆（C:\\Users\\FuRongJun\\.zcode\\cli\\memories\\...\\memory\\*.md）
摄取到灵枢库知识层（data/aeis_memory.db），标签标记 source:<file>。

用法：python migrate_memory.py [--dir 记忆目录] [--dry-run]
"""
import glob
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

DEFAULT_DIR = os.path.join(
    os.path.expanduser("~"), ".zcode", "cli", "memories",
    "projects", "default-1204b567a16a0fa4", "memory")


def strip_frontmatter(text: str) -> str:
    """去掉 md frontmatter（--- 之间的元数据），只保留正文。"""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].strip()
    return text.strip()


def split_by_heading(text: str, min_len: int = 40) -> list:
    """按 markdown 标题分块（##/### 章节独立成块，块级检索精准）。
    无标题或块过短时按段落合并。"""
    lines = text.splitlines()
    blocks, cur_title, cur = [], "", []
    heading_re = re.compile(r"^#{1,3}\s+(.*)$")

    def flush():
        nonlocal cur
        body = "\n".join(cur).strip()
        if body:
            blocks.append((f"## {cur_title}" if cur_title else "") + "\n" + body
                          if cur_title else body)
        cur = []

    for ln in lines:
        m = heading_re.match(ln)
        if m:
            flush()
            cur_title = m.group(1).strip()
        else:
            cur.append(ln)
    flush()
    # 过短的块并入相邻（防碎片）
    merged = []
    for b in blocks:
        if merged and len(b) < min_len:
            merged[-1] = merged[-1] + "\n" + b
        else:
            merged.append(b)
    return merged


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mem_dir = args[0] if args else DEFAULT_DIR
    dry_run = "--dry-run" in sys.argv

    os.environ["AEIS_DB"] = r"D:\Program Files\2_ai\AEIS\data\aeis_memory.db"
    from aeis.api import Agent
    agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])

    files = sorted(glob.glob(os.path.join(mem_dir, "*.md")))
    print(f"待迁移记忆文件 {len(files)} 个（{mem_dir}）")
    total_nodes = 0
    for fp in files:
        name = os.path.basename(fp)
        with open(fp, "r", encoding="utf-8") as f:
            raw = f.read()
        content = strip_frontmatter(raw)
        if not content:
            print(f"  - {name}: 空内容，跳过")
            continue
        blocks = split_by_heading(content)
        if dry_run:
            print(f"  - {name}: {len(blocks)} 块（{len(content)} 字符）")
            continue
        try:
            for i, block in enumerate(blocks):
                r = agent.ingest_text(
                    block, source=f"migrated:{name}",
                    tags=["project_memory", "migrated",
                          f"source:{name}", f"chunk:{i}"],
                    importance=0.7)
                total_nodes += r.get("nodes", 0) or 1
            print(f"  ✅ {name}: +{len(blocks)} 块")
        except Exception as exc:
            print(f"  ❌ {name}: {exc}")
    if not dry_run:
        print(f"迁移完成：新增 {total_nodes} 节点（标签 migrated/source:*）")
    agent.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
