# -*- coding: utf-8 -*-
"""test_file_memory.py · 文件树↔记忆图双向映射测试（充分测试·荣指令 2026-09-03）"""
import os
import sys
import json
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aeis import Agent  # noqa: E402
from aeis.file_memory import FileMemory, _path_anchor  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + (f" | {detail}" if detail else ""))


def main():
    tmp = tempfile.mkdtemp(prefix="fm_src_")
    out = tempfile.mkdtemp(prefix="fm_out_")
    db = os.path.join(tempfile.mkdtemp(prefix="fm_db_"), "fm.db")
    a = Agent(db_path=db)
    fm = FileMemory(a)

    # ---- 构造源树：多级目录+文本+大文件+二进制 ----
    os.makedirs(os.path.join(tmp, "docs", "sub"))
    open(os.path.join(tmp, "README.md"), "w", encoding="utf-8").write("# 项目说明\n文件记忆化测试")
    open(os.path.join(tmp, "docs", "design.md"), "w", encoding="utf-8").write("## 设计\n内容A" * 10)
    open(os.path.join(tmp, "docs", "sub", "detail.txt"), "w", encoding="utf-8").write("细节内容" * 50)
    big = os.path.join(tmp, "data.bin")
    open(big, "wb").write(os.urandom(200 * 1024))  # 200KB > 64KB → 引用型

    # ---- 1. 摄入 ----
    r1 = fm.ingest_tree(tmp)
    anchor = _path_anchor(".")
    imm = a.engine.store.conn.execute(
        "SELECT id, tags FROM nodes WHERE tags LIKE ?",
        (f'%"{anchor}"%',)).fetchall()
    print(f"  [立即查] anchor={anchor!r} 命中={len(imm)}")
    check("1.1 摄入成功", r1["created"] > 0, str({k: r1[k] for k in ("dirs", "files", "refs", "created")}))
    check("1.2 大文件走引用", r1["refs"] >= 1, f"refs={r1['refs']}")
    root_node = _find_root(a, tmp)
    check("1.3 根节点建立", root_node is not None)

    # ---- 2. 幂等：重复摄入不重复建 ----
    r2 = fm.ingest_tree(tmp)
    check("2.1 重复摄入更新而非新建", r2["created"] == 0 and r2["updated"] > 0,
          f"created={r2['created']} updated={r2['updated']}")

    # ---- 3. 层级边验证 ----
    raw = a.engine.store.conn.execute(
        "SELECT source_id, target_id, relation_type FROM edges").fetchall()
    print(f"  [诊断] 全库边数={len(raw)} 根id={root_node.id} 根tag={root_node.tags[0] if root_node and root_node.tags else None}")
    for r in raw:
        print("   边:", tuple(r))
    all_tags = a.engine.store.conn.execute("SELECT id, tags FROM nodes").fetchall()
    for i, t in all_tags:
        print("   节点:", i, (t or "")[:50])
    children = fm._children_of(root_node.id)
    check("3.1 根有层级子边", len(children) >= 2, f"children={len(children)}")

    # ---- 4. 条件空间验证（按名字 tag 找 design.md 节点）----
    docs_node = None
    for (i,) in a.engine.store.conn.execute("SELECT id FROM nodes").fetchall():
        n = a.engine.store.get_node(i)
        if n and n.tags and "file_mem_name:design.md" in n.tags:
            docs_node = n
            break
    cs_raw = getattr(docs_node, "condition_space", None) if docs_node else None
    if isinstance(cs_raw, str):
        cs_pos = cs_raw
    elif hasattr(cs_raw, "to_json"):
        cs_pos = cs_raw.to_json()
    elif isinstance(cs_raw, dict):
        cs_pos = str(cs_raw.get("observation_position", ""))
    else:
        cs_pos = str(cs_raw)
    check("4.1 文件节点条件空间带路径", docs_node is not None and "docs" in cs_pos, cs_pos[:90])

    # ---- 5. 投影 roundtrip ----
    r5 = fm.export_tree(root_node.id, out)
    same = _tree_equal(tmp, out)
    check("5.1 投影 roundtrip 内容一致", same, f"files={r5['files']} dirs={r5['dirs']}")
    check("5.2 引用文件还原", r5["refs_restored"] >= 1, f"restored={r5['refs_restored']} missing={r5['refs_missing']}")

    # ---- 6. 变更检测 ----
    open(os.path.join(tmp, "docs", "design.md"), "a", encoding="utf-8").write("\n追加修改行")
    r6 = fm.diff_tree(tmp, root_node.id)
    check("6.1 diff 检测到修改", len(r6["changed"]) >= 1, str(r6["changed"])[:80])

    # ---- 7. dry_run 不写库 ----
    before = _count_nodes(a)
    r7 = fm.ingest_tree(tmp, dry_run=True)
    check("7.1 dry_run 不写库", _count_nodes(a) == before, f"前后节点数 {before}/{_count_nodes(a)}")

    # ---- 8. 拒绝路径 ----
    r8 = fm.ingest_tree(os.path.join(tmp, "不存在的目录XYZ"))
    check("8.1 不存在目录 REJECT", r8.get("status") == "REJECT")

    a.close()
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(out, ignore_errors=True)

    ok = sum(1 for _, s, _ in RESULTS if s)
    print(f"\n===== 文件记忆化测试: {ok}/{len(RESULTS)} 通过 =====")
    return 0 if ok == len(RESULTS) else 1


def _find_root(a, tmp):
    from aeis.file_memory import _path_anchor
    from aeis.file_memory import _find_by_anchor
    return _find_by_anchor(a.engine.store, _path_anchor(".")) or \
        _find_by_anchor(a.engine.store, _path_anchor(os.path.basename(tmp)))


def _find_by_name(a, fm, root_id, name_part):
    stack = [root_id]
    while stack:
        cur = stack.pop()
        n = a.engine.store.get_node(cur)
        if n is None:
            continue
        if name_part in (n.content or ""):
            return n
        stack.extend(fm._children_of(cur))
    return None


def _count_nodes(a):
    return a.engine.store.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]


def _tree_equal(src, dst):
    """roundtrip 一致性：文本文件内容一致（引用型比大小）。"""
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        rel = os.path.relpath(dirpath, src)
        ddst = os.path.join(dst, rel) if rel != "." else dst
        for f in filenames:
            s = os.path.join(dirpath, f)
            d = os.path.join(ddst, f)
            if not os.path.exists(d):
                return False
            if os.path.getsize(s) > 64 * 1024:
                if os.path.getsize(d) != os.path.getsize(s):
                    return False
            else:
                if open(s, encoding="utf-8", errors="replace").read() != \
                   open(d, encoding="utf-8", errors="replace").read():
                    return False
    return True


if __name__ == "__main__":
    sys.exit(main())
