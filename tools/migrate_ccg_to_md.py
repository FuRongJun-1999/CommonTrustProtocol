# -*- coding: utf-8 -*-
"""migrate_ccg_to_md.py · 一次性迁移：把 sqlite/dump 中的 CCG 条件注入 MD 正本

背景：md 是知识正本，但 生效条件/不适用条件 是历史手工撰写的（在 seed 脚本→sqlite）。
本脚本按知识点名把条件注入 md，使 md 成为自包含的唯一权威。

注入格式（### 标题 之后）：
    - **生效条件**: 问X | 问Y
    - **不适用条件**: 问A | 问B

幂等：已有 生效条件 注释的块跳过。
用法：
    python tools/migrate_ccg_to_md.py --dry-run
    python tools/migrate_ccg_to_md.py --from <历史 dump 路径>

注：条件源是**历史（sqlite 导出）的 _ccg_dump.json**（本次迁移前的快照，可从
   git 历史 commit f8487f59 取回）。当前 _ccg_dump.json 已由 md 派生，对其重跑
   本脚本是幂等 no-op。
"""
from __future__ import annotations
import io
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KNOWLEDGE = os.path.join(ROOT, "aeis", "knowledge")
DUMP = os.path.join(KNOWLEDGE, "_ccg_dump.json")


def merged_conditions():
    """name -> (生效条件, 不适用条件)：同名条目条件取并集（保序去重）。

    键取 sa['name']（md 标题通常等于它）；为空时回退 comment['name'] 去掉「（…）」后缀。
    不过滤 kind —— knowledge / knowledge_point / None 都可能带 comment。
    """
    d = json.load(open(DUMP, encoding="utf-8"))
    by = defaultdict(lambda: {"cond": [], "neg": []})
    for r in d:
        try:
            sa = json.loads(r["sa_json"])
        except Exception:
            continue
        cm = sa.get("comment") or {}
        if not cm:
            continue
        keys = []
        nm = (sa.get("name") or "").strip()
        if nm:
            keys.append(nm)
        cn = (cm.get("name") or "").strip()
        if cn:
            keys.append(cn)
            core = re.split(r"[（(：:·]", cn)[0].strip()
            if core and core not in keys:
                keys.append(core)
        for k in keys:
            for key, ckey in (("cond", "生效条件"), ("neg", "不适用条件")):
                for x in cm.get(ckey, []) or []:
                    if x and x not in by[k][key]:
                        by[k][key].append(x)
    return {n: (v["cond"], v["neg"]) for n, v in by.items()}


def inject(path, cond_map, dry=False):
    """向一个 md 注入条件。返回 (注入块数, 跳过已有数, 无条件数)。"""
    s = open(path, encoding="utf-8").read()
    parts = re.split(r"^### ", s, flags=re.M)
    if len(parts) <= 1:
        return 0, 0, 0
    head = parts[0]
    injected = skipped = nocond = 0
    new_parts = [head]
    for part in parts[1:]:
        lines = part.split("\n")
        name = lines[0].strip()
        rest = lines[1:]
        # 已有显式条件 → 跳过（幂等）
        if any(re.match(r"-\s*\*\*生效条件\*\*", ln) for ln in rest):
            skipped += 1
            new_parts.append(part)
            continue
        cond, neg = cond_map.get(name, ([], []))
        if not cond:
            nocond += 1
            new_parts.append(part)
            continue
        # 去掉标题后的前导空行，统一插入
        body = "\n".join(rest)
        lead = ""
        while body.startswith("\n"):
            lead += "\n"
            body = body[1:]
        block = [lines[0], ""]
        block.append("- **生效条件**: " + " | ".join(cond))
        if neg:
            block.append("- **不适用条件**: " + " | ".join(neg))
        block.append("")
        block.append(body)
        new_parts.append("\n".join(block))
        injected += 1
    if injected and not dry:
        with open(path, "w", encoding="utf-8") as f:
            f.write("### ".join(new_parts))
    return injected, skipped, nocond


def main(dry=False):
    cmap = merged_conditions()
    print(f"dump 知识点名: {len(cmap)}")
    ti = ts = tn = 0
    for f in sorted(os.listdir(KNOWLEDGE)):
        if not f.endswith(".md"):
            continue
        p = os.path.join(KNOWLEDGE, f)
        i, s, n = inject(p, cmap, dry=dry)
        ti += i; ts += s; tn += n
    print(f"{'[dry-run] ' if dry else ''}注入块: {ti} | 已有跳过: {ts} | 无条件: {tn}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if "--from" in sys.argv:
        DUMP = sys.argv[sys.argv.index("--from") + 1]
    main(dry="--dry-run" in sys.argv)
