# -*- coding: utf-8 -*-
"""build_cognition_ir.py · 灵枢 graph_retrieve → archify cognition 原生类型

上游 PR（tt-a1i/archify feat/cognition-diagram-type）的实证链路：
graph_retrieve 的返回**天然符合** cognition IR——verdict 四态、card_hit
确定性证据、confidence 置信度链、edu_level 条件空间声明、direct_answer
直答，全部一等公民字段，不再需要 workflow 类型硬塞 + trace 侧车。

用法：
  python tools/cognition_map/build_cognition_ir.py "三角形内角和是多少" --out out.html
"""
from __future__ import annotations

import argparse
import json
import re
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ARCHIFY_BIN = os.path.join(os.path.dirname(ROOT), "archify-ref", "archify", "bin", "archify.mjs")


def _verdict_of(route: dict, is_top: bool) -> str:
    if is_top and route.get("_card_hit") and route.get("score", 0) >= 5:
        return "accept"
    if is_top:
        return "defer"
    if route.get("_card_hit"):
        return "branch"
    return "reject"


def routes_to_cognition_ir(question: str, routes: list) -> dict:
    """graph_retrieve 返回 → archify cognition IR（认知语义一等公民）。"""
    top = routes[0] if routes else None
    accepted = bool(top and top.get("_card_hit") and top.get("score", 0) >= 5)
    overall = "resolved" if accepted else ("deferred" if routes else "blindspot")

    lanes = [{"id": "subjectLane", "label": "问题入口"}]
    nodes = [{
        "id": "q", "lane": "subjectLane", "col": 0,
        "kind": "subject", "verdict": "accept" if routes else "blindspot",
        "label": question if len(question) <= 6 else question[:6],
        "confidence": 1,
    }]
    edges = []
    main_path = ["q"]
    seen_lanes = {"subjectLane"}

    max_score = max((r.get("score", 0) for r in routes), default=1) or 1
    for i, r in enumerate(routes[:4]):
        verdict = _verdict_of(r, i == 0)
        if verdict == "reject" and overall == "blindspot":
            continue
        domain = r.get("domain_group") or "候选"
        lane_id = f"lane{i}"
        lanes.append({"id": lane_id, "label": domain[:12],
                      "variant": "exception" if verdict in ("reject", "blindspot") else "normal"})
        seen_lanes.add(lane_id)
        conf = round(min(1.0, r.get("score", 0) / max_score), 2)
        name = (r.get("name") or f"卡{i}").split("（")[0][:6]
        node = {
            "id": f"c{i}", "lane": lane_id, "col": 1,
            "kind": "atomic", "verdict": verdict,
            "label": name,
            "sublabel": f"score {round(r.get('score', 0), 2)}",
            "card_hit": bool(r.get("_card_hit")),
            "confidence": conf,
        }
        if r.get("edu_level"):
            node["tag"] = r["edu_level"]
            # schema 契约：edu_level 仅接受 E1-E5；库内其他口径（如「通用」）
            # 只作 tag 展示，不进条件空间声明字段
            if re.fullmatch(r"E[1-5]", str(r["edu_level"])):
                node["edu_level"] = r["edu_level"]
        if i == 0 and r.get("direct_answer"):
            node["direct_answer"] = r["direct_answer"][:200]
        nodes.append(node)
        # 标签沿各自边的竖直段显式错位（q 出口共线，自动标签会挤在同一点）
        q_cy, lane_h = 119, 124
        cy_i = q_cy + (i + 1) * lane_h
        label_y = round(q_cy + (cy_i - q_cy) * (0.3 + 0.06 * i))
        label_x = 156 if i % 2 == 0 else 108
        edge = {
            "from": "q", "to": f"c{i}",
            "role": "main" if verdict == "accept" else verdict,
            "width": round(0.5 + conf * 2.5, 2),
        }
        if verdict in ("accept", "branch"):
            edge["label"] = f"{conf:.2f}"
            edge["labelAt"] = [label_x, label_y]
        edges.append(edge)
        if verdict == "accept":
            main_path.append(f"c{i}")

    if overall == "blindspot":
        lanes.append({"id": "gapLane", "label": "盲区", "variant": "exception"})
        nodes.append({"id": "gap", "lane": "gapLane", "col": 2, "kind": "blindspot",
                      "verdict": "blindspot", "label": "无条件闭合",
                      "sublabel": "声明未知"})
        edges.append({"from": "q", "to": "gap", "role": "defer", "variant": "dashed"})

    # 空角色边清理（label None 出 schema 违规）
    edges = [{k: v for k, v in e.items() if v is not None} for e in edges]

    doc = {
        "schema_version": 1,
        "diagram_type": "cognition",
        "meta": {
            "title": f"灵枢认知路由 · {question[:12]}",
            "locale": "zh-CN",
            "subtitle": "条件路由图 · 认知语义一等公民",
            "question": question,
            "verdict": overall,
            "quality_profile": "showcase",
            "viewBox": [720, max(500, 180 + 124 * len(lanes))],
        },
        "lanes": lanes,
        "nodes": nodes,
        "edges": edges,
    }
    if len(main_path) >= 2:
        doc["mainPath"] = main_path
    hit = top or {}
    doc["cards"] = [{
        "dot": "emerald" if accepted else "amber",
        "title": "可溯源性",
        "items": [
            f"判定 = {overall}（top 卡 card_hit={str(bool(hit.get('_card_hit'))).lower()}）",
            f"两阶段收敛候选 {len(routes)} 条，低分分支显式可见",
        ],
    }]
    return doc


def deliver(doc: dict, out_html: str) -> bool:
    cand = os.path.join(HERE, "_cognition_ir.candidate.json")
    json.dump(doc, open(cand, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    node = shutil.which("node") or "node"
    r = subprocess.run([node, ARCHIFY_BIN, "deliver", "cognition", cand, out_html,
                        "--quality", "showcase", "--json"],
                       capture_output=True, text=True)
    try:
        res = json.loads(r.stdout)
    except Exception:
        print("[deliver] 非法输出:", r.stdout[-300:], r.stderr[-200:], file=sys.stderr)
        return False
    if not res.get("ok"):
        print("[deliver 诊断]", (res.get("error") or "")[:400], file=sys.stderr)
        diags = res.get("diagnostics") or []
        for d in diags[:4]:
            print("  -", (d.get("message") or "")[:160], file=sys.stderr)
    return bool(res.get("ok"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))
    from wisdom_book import ConditionDex
    from semantic_translate import graph_retrieve

    db = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")
    dex = ConditionDex(db_path=db, fresh=False)
    try:
        routes = graph_retrieve(dex, args.question)
    finally:
        dex.close()

    doc = routes_to_cognition_ir(args.question, routes)
    out = args.out or os.path.join(HERE, "cognition_native.html")
    ok = deliver(doc, out)
    print(f"IR 构造      : verdict={doc['meta']['verdict']} 节点={len(doc['nodes'])} 边={len(doc['edges'])}")
    print(f"渲染交付     : {'✅ ' + out if ok else '❌ 失败（见诊断）'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
