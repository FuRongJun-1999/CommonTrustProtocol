# -*- coding: utf-8 -*-
"""cognition_render.py · 认知图渲染器 v0（灵枢 × archify）

《条件路由图_单源与可溯源规范》配套：把一次检索的认知过程渲染为
可溯源交互图（CognitionTrace v0 → archify workflow IR → HTML）。

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
ARCHIFY_BIN = os.path.join(os.path.dirname(ROOT), "archify-ref", "archify", "bin", "archify.mjs")


def build_cognition(question: str, routes: list, db_path: str | None):
    """graph_retrieve 返回 → CognitionTrace v0 + archify workflow IR。"""

    # ---- 判定四态 ----
    hits = [r for r in routes if r.get("_card_hit")]
    top = routes[0] if routes else None
    if top and top.get("_card_hit") and top.get("score", 0) >= 5:
        verdict = "ACCEPT"
    elif top:
        verdict = "DEFER"      # 有候选但置信不足
    else:
        verdict = "BLINDSPOT"  # 无候选

    # ---- archify workflow IR ----
    q_short = question if len(question) <= 6 else question[:6]
    lanes = [
        {"id": "intake", "label": "问题入口"},
        {"id": "route", "label": "条件识别与收敛"},
        {"id": "kp", "label": "知识点卡"},
        {"id": "gap", "label": "认知边界", "variant": "exception"},
    ]
    lanes.insert(1, {"id": "route2", "label": "收敛判定"})
    nodes = [
        {"id": "q", "lane": "intake", "col": 0, "type": "external", "label": q_short},
        {"id": "cond", "lane": "route2", "col": 0, "type": "backend",
         "label": "条件识别", "sublabel": f"二元组×{len((top or {}).get('evidence', {}).get('condition_matches', []))}"},
        {"id": "conv", "lane": "route", "col": 0, "type": "backend",
         "label": "两阶段收敛",
         "sublabel": f"域={(top or {}).get('domain_group', '-')} 候选={len(routes)}"},
    ]
    edges = [
        {"from": "q", "to": "cond", "role": "main"},
        {"from": "cond", "to": "conv", "role": "main"},
    ]
    col = 3
    seen_lanes = {"kp"}
    for i, h in enumerate(hits[:3]):
        lane_id = f"kp{i}"
        seen_lanes.add(lane_id)
        label_lane = next((l["label"] for l in lanes), "")
        lanes.append({"id": lane_id, "label": (h.get("edu_level") or "KP") + " 卡"})
        nodes.append({"id": f"k{i}", "lane": lane_id, "col": 3,
                      "type": "database", "label": (h.get("name") or "").split("（")[0][:6],
                      "sublabel": f"{h.get('matched', [''])[0] or 'KCCS'} {round(h.get('score', 0), 2)}"})
        edges.append({"from": "conv", "to": f"k{i}",
                      "role": "main" if i == 0 else "branch"})
    gap_note = []
    if verdict == "ACCEPT":
        gap_node_label = "资格满足"
        gap_sub = "条件核对通过"
        g_type = "backend"
        edges.append({"from": f"k0", "to": "ans", "role": "main"})
    elif verdict == "DEFER":
        gap_node_label = "条件不足 DEFER"
        gap_sub = "条件不闭合·递归"
        g_type = "security"   # 守门语义（枚举内无 decision）
    else:
        gap_node_label = "BLINDSPOT"
        gap_sub = "声明未知"
        g_type = "external"   # 盲区=局部不可知外域
    lanes.append({"id": "verdict", "label": "四态判定"})
    lanes.append({"id": "answer", "label": "直答输出"})
    nodes.append({"id": "ans", "lane": "verdict", "col": 4, "type": g_type,
                  "label": gap_node_label, "sublabel": gap_sub})
    direct = (top or {}).get("direct_answer")
    if direct:
        nodes.append({"id": "a_text", "lane": "answer", "col": 0, "type": "database",
                      "label": "直答",
                      "sublabel": direct[:10]})
        edges.append({"from": "conv", "to": "k0", "role": "main"}) if not any(
            e.get("to") == "k0" for e in edges) else None

    doc = {
        "schema_version": 1,
        "diagram_type": "workflow",
        "meta": {
            "title": f"灵枢认知路由 · 「{q_short}」· 判定={verdict}",
            "quality_profile": "showcase",
            "views": [
                {"id": "ops", "label": "操作图层",
                 "focus": ["q", "cond", "conv", "ans"]},
                {"id": "know", "label": "知识图层",
                 "focus": ["k0"]},
            ],
            "viewBox": [1000, max(720, 340 + 130 * len(lanes))],
        },
        "lanes": lanes,
        "nodes": nodes,
        "edges": edges,
        "mainPath": ["q", "cond", "conv"] + ([f"k0", "ans"] if verdict == "ACCEPT" else []),
    }
    trace = {"question": question, "verdict": verdict,
             "schema": "cognition-v0",
             "ops": [n.get("label") for n in nodes if n.get("lane") == "route"],
             "hits": [(h.get("name"), round(h.get("score", 0), 2)) for h in hits[:3]],
             "rejected_visible_at": "execution_trace 增强（挂账）"}
    return doc, trace


def deliver(doc: dict, trace: dict, out_html: str) -> bool:
    workdir = os.path.dirname(os.path.abspath(out_html)) or "."
    cand = os.path.join(workdir, "_cognition.candidate.json")
    json.dump(doc, open(cand, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    binp = ARCHIFY_BIN
    node = shutil.which("node") or "node"
    r = subprocess.run([node, binp,
                        "deliver", "workflow", cand, out_html,
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
