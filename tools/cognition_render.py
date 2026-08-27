# -*- coding: utf-8 -*-
"""cognition_render.py · 认知图渲染器 v0（灵枢 × archify）

《条件路由图_单源与可溯源规范》配套：把一次检索的认知过程渲染为
可溯源交互图（CognitionTrace → archify cognition 原生类型 → HTML）。

四态即图例：
  ACCEPT   main    主命中边
  branch   branch  低分相关边
  REJECT   error   负路由排除边（v1 将随 execution_trace 增强可见）
  DEFER/BLINDSPOT  终态节点（条件不足递归 / 声明未知）

用法：
  python tools/cognition_render.py "三角形内角和是多少" --out out.html
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CMAP = os.path.join(HERE, "cognition_map")
ARCHIFY_BIN = os.path.join(os.path.dirname(ROOT), "archify-ref", "archify", "bin", "archify.mjs")

# 上游 cognition 原生类型（archify PR #150）落地后，IR 构造单源收敛到
# build_cognition_ir.routes_to_cognition_ir——本文件保留 CLI 入口、四态判定
# 与 CognitionTrace（path_fingerprint 溯源侧车）。
sys.path.insert(0, CMAP)
from build_cognition_ir import routes_to_cognition_ir  # noqa: E402


def build_cognition(question: str, routes: list, db_path: str | None):
    """graph_retrieve 返回 → archify cognition 原生 IR + CognitionTrace 侧车。"""

    # ---- 判定四态（侧车口径，与 IR 内 meta.verdict 对应）----
    hits = [r for r in routes if r.get("_card_hit")]
    top = routes[0] if routes else None
    if top and top.get("_card_hit") and top.get("score", 0) >= 5:
        verdict = "ACCEPT"
    elif top:
        verdict = "DEFER"      # 有候选但置信不足
    else:
        verdict = "BLINDSPOT"  # 无候选

    doc = routes_to_cognition_ir(question, routes)

    trace = {"question": question, "verdict": verdict,
             "schema": "cognition-v1-native",
             "diagram_type": "cognition",
             "ops": ["question-banner", "conditional-narrowing", "verdict"],
             "hits": [(h.get("name"), round(h.get("score", 0), 2)) for h in hits[:3]],
             "rejected_visible_at": "cognition 原生类型（reject verdict/role 天然可见）"}
    return doc, trace


def deliver(doc: dict, trace: dict, out_html: str) -> bool:
    workdir = os.path.dirname(os.path.abspath(out_html)) or "."
    cand = os.path.join(workdir, "_cognition.candidate.json")
    json.dump(doc, open(cand, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    binp = ARCHIFY_BIN
    node = shutil.which("node") or "node"
    r = subprocess.run([node, binp,
                        "deliver", "cognition", cand, out_html,
                        "--quality", "showcase", "--json"],
                       capture_output=True, text=True)
    try:
        res = json.loads(r.stdout)
    except Exception:
        print("[deliver] 非法输出:", r.stdout[-300:], r.stderr[-200:], file=sys.stderr)
        return False
    if not res.get("ok"):
        print("[deliver 诊断]", (res.get("error") or "")[:300], file=sys.stderr)
    return bool(res.get("ok"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from knowledge_fingerprint import path_fingerprint, graph_fingerprint
    sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))
    from wisdom_book import ConditionDex
    from semantic_translate import graph_retrieve

    db = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")
    dex = ConditionDex(db_path=db, fresh=False)
    try:
        routes = graph_retrieve(dex, args.question)
    finally:
        dex.close()

    doc, trace = build_cognition(args.question, routes, db)
    route_names = [r.get("name", "") for r in hits if True] if (hits := [
        x for x in routes]) else []
    rank_order = [r.get("name", "") for r in routes[:5]]
    top_direct = (routes[0] or {}).get("direct_answer", "") if routes else ""
    pfp = path_fingerprint(args.question,
                           [r.get("name", "") for r in routes],
                           [],
                           top_direct,
                           [r.get("name", "") for r in routes[:5]])
    gfp = graph_fingerprint(db)
    trace["path_fingerprint"] = pfp
    trace["graph_snapshot"] = {"fingerprint": gfp["graph_fingerprint"][:16],
                               "nodes": gfp["nodes"], "edges": gfp["edges"]}
    out = args.out or os.path.join(ROOT, "tools", "cognition_map", "latest_cognition.html")
    json.dump(trace, open(os.path.join(os.path.dirname(os.path.abspath(out)), "_cognition.trace.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok = deliver(doc, trace, out)

    print(f"verdict 判定 : {trace['verdict']}")
    print(f"渲染交付     : {'✅ ' + out if ok else '❌ 失败（见诊断）'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
