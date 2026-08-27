# -*- coding: utf-8 -*-
"""knowledge_fingerprint.py · 索引指纹化四层实现（《灵枢确定性有效化_索引指纹化方案_v0.1》）

层级：
  L1 节点   sha256(canonical(kp 内容 + KCCS 四要素 + edu_level + domain))
  L2 边     sha256(canonical(源节点fp + 生效条件 + 目标节点fp))
  L3 路径   sha256(canonical(查询归一化 + 节点fp序列 + 负路由排除集 + topk + 直答))
  L4 整图   sha256(canonical(全部节点fp ∥ 全部边fp 排序 + 代码版本))

诚实边界（照方案 §六）：指纹证明的是「检索路径确定性」，不验证答案正确性；
跨环境一致性要求代码版本相同（版本变更 → 指纹预期变化）。

用法：
  python tools/knowledge_fingerprint.py --graph            # 整图指纹
  python tools/knowledge_fingerprint.py --path "问题"      # 单次检索路径证据
  python tools/knowledge_fingerprint.py --write-nodes      # 幂等写入节点指纹到库
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_DB = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")

# 检索端同款符号归一（对齐 semantic_translate._q_norm 口径）
_SYM_NORM = [("+", "加"), ("＋", "加"), ("-", "减"), ("－", "减"),
             ("×", "乘"), ("÷", "除")]


def canonical(obj) -> str:
    """RFC 8785 风格确定性序列化：键排序·NFC 归一·紧凑分隔符·数组排序可选。"""
    def _norm(x):
        if isinstance(x, str):
            return unicodedata.normalize("NFC", x)
        if isinstance(x, dict):
            return {k: _norm(v) for k, v in sorted(x.items())}
        if isinstance(x, list):
            items = [_norm(i) for i in x]
            # 语义无关的集合类数组做排序以稳定指纹；调用方若需保序请传 tuple 包装标记
            try:
                items.sort(key=lambda i: (i if isinstance(i, str) else json.dumps(
                    i, ensure_ascii=False, sort_keys=True)))
            except Exception:
                pass
            return items
        return x
    return json.dumps(_norm(obj), ensure_ascii=False, separators=(",", ":"))


def fp(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def short(fp_hex: str, n: int = 12) -> str:
    return fp_hex[:n]


def norm_question(q: str) -> str:
    q = unicodedata.normalize("NFC", (q or "").strip())
    for a, b in _SYM_NORM:
        q = q.replace(a, b)
    return q


# ---------------- L1 节点 ----------------
def node_fingerprint(content: str, state_attributes_json: str | None,
                     comment_override: dict | None = None) -> dict:
    """L1 节点指纹：kp 内容 + KCCS 四要素 + edu_level + domain。

    返回 {fingerprint, comment_kind}；comment_kind 记录来源形态供审计。
    """
    sa = {}
    kind = "absent"
    if isinstance(state_attributes_json, str) and state_attributes_json.strip():
        try:
            sa = json.loads(state_attributes_json)
        except Exception:
            sa = {}
        cm_raw = sa.get("comment")
        cm = cm_override if comment_override is not None else cm_raw
        if isinstance(cm, dict):
            kind = "dict"
        elif isinstance(cm, list):
            kind = "list"
    obj = {
        "content": content or "",
        "edu_level": sa.get("edu_level", "") if isinstance(sa, dict) else "",
        "domain": sa.get("domain", "") if isinstance(sa, dict) else "",
        "kccs": (comment_override if comment_override is not None else
                 (sa.get("comment") if isinstance(sa, dict) else {})),
    }
    return {"fingerprint": fp(canonical(obj)), "comment_kind": kind}


# ---------------- L2 边 ----------------
def edge_fingerprint(src_fp: str, effective_condition: str, dst_fp: str) -> str:
    return fp(canonical({"src": src_fp, "cond": effective_condition, "dst": dst_fp}))


# ---------------- L3 路径 ----------------
def path_fingerprint(question: str, route_names: list[str],
                     negative_routes: list[str], direct_answer: str,
                     rank_order: list[str]) -> str:
    """路径指纹：走过节点的名称序列（保序）+ 负路由排除集（排序）+ topk + 直答。

    注：v0 以「卡名序列」作为节点身份代理；节点 fp 化（阶段 1 写库后）
    升级为 fp 序列。
    """
    payload = {
        "q_norm": norm_question(question),
        "route_seq": [unicodedata.normalize("NFC", n) for n in route_names],
        "neg_routes": sorted(negative_routes),
        "topk": [unicodedata.normalize("NFC", r) for r in rank_order],
        "answer": (direct_answer or "").strip(),
    }
    return fp(canonical(payload))


# ---------------- L4 整图 ----------------
def code_version() -> str:
    try:
        h = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True)
        if h.returncode == 0 and h.stdout.strip():
            return "git:" + h.stdout.strip()[:10]
    except Exception:
        pass
    return "unknown"


def graph_fingerprint(db_path: str = DEFAULT_DB, include_code_version: bool = True) -> dict:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT id, content, state_attributes FROM nodes").fetchall()
        node_fps = []
        for nid, c, sa in rows:
            f = node_fingerprint(c, sa)
            node_fps.append(f"{nid}:{f['fingerprint']}")
        edges = []
        if True:
            ecols = [c[1] for c in conn.execute("PRAGMA table_info(edges)").fetchall()]
            src_col = "source_id" if "source_id" in ecols else "src"
            dst_col = "target_id" if "target_id" in ecols else "tgt"
            for sid, tid in conn.execute(f"SELECT {src_col}, {dst_col} FROM edges"):
                edges.append(f"{sid}->{tid}")
        payload = {
            "nodes_sorted": sorted(node_fps),
            "edges_sorted": sorted(edges),
            "code_version": code_version() if include_code_version else "",
        }
        return {"graph_fingerprint": fp(canonical(payload)),
                "nodes": len(node_fps), "edges": len(edges)}
    finally:
        conn.close()


# ---------------- 阶段1 · 幂等写库 ----------------
def attach_node_fingerprints(db_path: str = DEFAULT_DB) -> int:
    """把节点指纹幂等写入 state_attributes.fingerprint（已是最新则跳过）。"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    rows = cur.execute("SELECT id, content, state_attributes FROM nodes").fetchall()
    changed = 0
    for nid, c, sa in rows:
        res = node_fingerprint(c, sa)
        try:
            obj = json.loads(sa) if isinstance(sa, str) else {}
        except Exception:
            continue
        if obj.get("fingerprint") == res["fingerprint"]:
            continue
        obj["fingerprint"] = res["fingerprint"]
        cur.execute("UPDATE nodes SET state_attributes=? WHERE id=?",
                    (json.dumps(obj, ensure_ascii=False), nid))
        changed += 1
    conn.commit()
    conn.close()
    return changed


# ---------------- CLI ----------------
def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="灵枢索引指纹化（四层有效化）")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--graph", action="store_true", help="计算整图指纹（L4）")
    ap.add_argument("--write-nodes", action="store_true", help="幂等写入节点指纹（L1）")
    args = ap.parse_args()

    if args.write_nodes:
        n = attach_node_fingerprints(args.db)
        print(f"L1 节点指纹写入: {n} 条更新")
    if args.graph:
        g = graph_fingerprint(args.db)
        print(json.dumps(g, ensure_ascii=False))
        return 0
    if not (args.graph or args.write_nodes):
        g = graph_fingerprint(args.db)
        print(json.dumps(g, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
