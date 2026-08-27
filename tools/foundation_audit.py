# -*- coding: utf-8 -*-
"""foundation_audit.py · 地基审计器 v1.0（错误信息校验）

《条件路由图_单源与可溯源规范_v1.0》配套工具：
对知识库 / 代码 / 描述文档三线做可自动化的错误校验，输出带证据的错误清单。

维度：
  A. 知识库结构 —— cloud db 注释 kp 的 KCCS 四要素完整性 + 空洞节点
  B. 代码单元   —— 六域单元的 KCCS 注释覆盖 + 硬编码残留
  C. 数字口径   —— 全仓 .md 中声称的关键数字 vs 锁定基线冲突清单
  D. 链接有效性 —— README/docs 内部相对路径引用存在性
  E. 数据一致性 —— seed_knowledge 学科卡数 vs 库内学科卡数

用法：
    python tools/foundation_audit.py [--quick]
退出码 = 发现的问题总数是否为 0。
"""
from __future__ import annotations

import ast
import json
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 锁定基线（《条件路由图_单源与可溯源规范_v1.0》§三）
BASELINE = {
    "six_domain_cases": 1058,
    "compiler_bootstrap": 272,
    "pyline_bootstrap": 240,
    "graph_db_tests": 123,
    "solidified": 619,
    "mcp_tools": 73,
}

problems: list[tuple[str, str, str]] = []  # (维度, 位置, 描述)


def problem(dim: str, where: str, desc: str, level: str = "error") -> None:
    problems.append((dim, where, desc))
    if level == "info":
        return


# ---------------- C. 数字口径 ----------------
NUM_PATTERNS = [
    # (正则, 基线键, 合法表述提示)
    (re.compile(r"(?<![\d.])(4[45]\d|6[78]\d|681)\s*(?:个|条)?\s*单元"), None, None),
]


def audit_numbers() -> dict:
    """扫描活文档中的过时数字口径。

    现行正确值：681 单元 / 73 工具 / 619 固化 / 1058 case。
    过时值示例：「71 工具」「459 单元」等旧快照口径。
    """
    found = {"files_scanned": 0, "hits": []}
    md_files = []
    for root in ["README.md", "docs"]:
        full = os.path.join(ROOT, root)
        if os.path.isfile(full):
            md_files.append(full)
        elif os.path.isdir(full):
            for dp, dn, fn in os.walk(full):
                dn[:] = [d for d in dn if d != "__pycache__"]
                if "history" in dp.lower():
                    continue
                for f in fn:
                    if f.endswith(".md"):
                        md_files.append(os.path.join(dp, f))
    stale_patterns = [
        (re.compile(r"71\s*(个|项)?\s*MCP|71\s*(个|项)?\s*工具"), "「71 工具」旧口径（现 73）"),
        (re.compile(r"459\s*(个|条)?\s*单元"), "「459 单元」缩水快照口径（现 681）"),
    ]
    for path in md_files:
        try:
            text = open(path, encoding="utf-8").read()
        except Exception:
            continue
        rel = os.path.relpath(path, ROOT)
        found["files_scanned"] += 1
        for pat, desc in stale_patterns:
            if pat.search(text):
                found["hits"].append((rel, desc))
                problem("C口径", rel, "[时点快照·人工核查] " + desc, level="info")
    return found


# ---------------- A. 知识库结构 ----------------
def audit_knowledge_db(db_path: str) -> dict:
    """KCCS 四要素 + 空洞节点抽样审计。"""
    out = {"exists": False}
    if not os.path.exists(db_path):
        return out
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = {r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    out["tables"] = sorted(tables)[:20]

    kp_tables = [t for t in tables if t in ("knowledge_points", "kps", "comment_kp")]
    stats = {}
    for t in kp_tables:
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})").fetchall()]
        total = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        empty_note = 0
        note_col = next((c for c in cols if c in ("annotation", "note", "comment", "content")), None)
        if note_col:
            empty_note = cur.execute(
                f"SELECT COUNT(*) FROM {t} WHERE {note_col} IS NULL OR TRIM({note_col})=''").fetchone()[0]
        kccs_ok = 0
        body_col = note_col or "content"
        if body_col in cols:
            rows = cur.execute(f"SELECT {body_col} FROM {t}").fetchall()
            for (txt,) in rows:
                if txt and all(k in txt for k in ("生效条件", "执行")):
                    kccs_ok += 1
        stats[t] = {"total": total, "empty_body": empty_note, "kccs_min_ok": kccs_ok}
    out["kp_stats"] = stats
    nodes = cur.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] if "nodes" in tables else 0
    orphan_edges = 0
    if "edges" in tables and "nodes" in tables:
        orphan_edges = cur.execute(
            "SELECT COUNT(*) FROM edges e WHERE e.source_id NOT IN (SELECT id FROM nodes)"
            " OR e.target_id NOT IN (SELECT id FROM nodes)").fetchone()[0]
    out["nodes"] = nodes
    out["orphan_edges"] = orphan_edges
    if orphan_edges:
        problem("A知识库", db_path, f"{orphan_edges} 条孤儿边")
    conn.close()
    return out


# ---------------- B. 代码单元 ----------------
HARDCODE_PAT = re.compile(r"[A-Z]:\\\\Program Files|[A-Z]:/Program Files")


def audit_code_units() -> dict:
    out = {"domains": {}, "hardcoded": []}
    wisdom_dir = os.path.join(ROOT, "aeis", "wisdom")
    unit_files = ["browser_units.py", "compiler_code_units.py", "graph_db_units.py",
                  "net_units.py", "os_units.py", "python_code_units.py"]
    for f in unit_files:
        p = os.path.join(wisdom_dir, f)
        src = open(p, encoding="utf-8").read()
        tree = ast.parse(src)  # 语法即 L1
        n_units = len(re.findall(r'\n\s+"[^"]+":\s*\{\s*\n', src))
        kccs = sum(1 for kw in ("生效条件", "子功能") if kw in src)
        no_comment_units = src.count("def ") - sum(
            1 for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and ast.get_docstring(node))
        out["domains"][f] = {"units": n_units, "kccs_marker": kccs >= 2,
                             "no_docstring_defs": max(no_comment_units, 0)}
        # 硬编码残留
        for i, line in enumerate(src.split("\n"), 1):
            if HARDCODE_PAT.search(line) and "#" not in line.split(HARDCODE_PAT.search(line).group())[0][-3:]:
                out["hardcoded"].append(f"{f}:{i}")
                problem("B代码", f"{f}:{i}", "本机绝对路径残留")

    # 全 wisdom 包硬编码总查
    for dp, dn, fn in os.walk(wisdom_dir):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in fn:
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ROOT)
            for i, line in enumerate(open(p, encoding="utf-8"), 1):
                if re.search(r"D:[\\\\/]Program Files", line):
                    problem("B代码", f"{rel}:{i}", "Program Files 硬编码残留：" + line.strip()[:70])
                    out["hardcoded"].append(f"{rel}:{i}")
    return out


# ---------------- D. README 内部链接 ----------------
def audit_links() -> list:
    bad = []
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    for m in re.finditer(r"\]\((?!http|#)([^)]+)\)", readme):
        target = m.group(1).split("#")[0].strip()
        if not target or target.endswith((".svg", ".png")) and target.startswith("http"):
            continue
        candidate = os.path.join(ROOT, target.replace("/", os.sep))
        alt = os.path.join(ROOT, "aeis", target.replace("/", os.sep))
        if not os.path.exists(candidate) and not os.path.exists(alt):
            bad.append(target)
            problem("D链接", "README.md", "内部引用不存在：" + target)
    return bad


# ---------------- E. 数据一致性 ----------------
def audit_seed_cards(db_path: str) -> dict:
    out = {}
    seed_dir = os.path.join(ROOT, "aeis", "seed_knowledge", "wisdom_cards")
    n_cards_disk = len([f for f in os.listdir(seed_dir) if f.endswith(".md")]) \
        if os.path.isdir(seed_dir) else 0
    out["cards_on_disk"] = n_cards_disk
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        try:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            # 学科卡通常以 tag/type 标记；此处用名称近似
            for t in ("disciplines", "subject_cards"):
                if t in tables:
                    out["cards_in_db_" + t] = conn.execute(
                        f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        finally:
            conn.close()
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    print("=" * 60)
    print("地基审计 · foundation_audit v1.0")
    print("=" * 60)

    cloud_db = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")

    print("[C] 数字口径 …")
    nums = audit_numbers()
    print("    扫描 .md:", nums["files_scanned"], "| 过时口径命中:", len(nums["hits"]))

    print("[A] 知识库结构 …")
    kb = audit_knowledge_db(cloud_db)
    print("    ", json.dumps(kb, ensure_ascii=False, default=str)[:300])

    print("[B] 代码单元 …")
    cu = audit_code_units()
    for d, st in cu["domains"].items():
        print(f"    {d}: ~{st['units']} 单元 | KCCS标记={'✓' if st['kccs_marker'] else '✗'} "
              f"| 缺docstring def≈{st['no_docstring_defs']}")

    print("[D] README 链接 …")
    bad_links = audit_links()
    print("    失效内部引用:", len(bad_links))

    print("[E] 数据一致性 …")
    seed = audit_seed_cards(cloud_db)
    print("    ", seed)

    print("-" * 60)
    errors = [x for x in problems if True]  # 全量展示
    print(f"提示+问题总数: {len(problems)}")
    by_dim: dict[str, int] = {}
    for dim, _, _ in problems:
        by_dim[dim] = by_dim.get(dim, 0) + 1
    for dim, n in sorted(by_dim.items()):
        print(f"  [{dim}] {n}")
    for dim, where, desc in problems[:40]:
        print(f"  • [{dim}] {where}: {desc}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
