# -*- coding: utf-8 -*-
"""dsh 嵌套认知图往返验证（zcode 认知图软件线 × dsh 世界模型线接口）。

输入：AEIS/data/roundtrip/dsh_run/image_semantics_nested_cg.json
  （dsh 端产出：18 节点 5 层嵌套图像语义认知图，subgraph 递归+part_of 边）

两段：
  导入段（幂等）：嵌套节点展平 → STNode(modality=visual)+HIERARCHICAL 边
    （child→parent 层级语义）；已导入（标签计数≥18）则跳过。
  验证段：root 出发 in 方向 traverse（层级语义=子指向父），
    可达 17 子节点+root=18 → PASS。

用法：
  python tools/dsh_nested_cg_roundtrip.py            # 导入+验证
  python tools/dsh_nested_cg_roundtrip.py --verify-only
"""
import sys
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))

JSON_PATH = r"D:\Program Files\2_ai\AEIS\data\roundtrip\dsh_run\image_semantics_nested_cg.json"
MAP_PATH = os.path.join(HERE, "dsh_nested_cg_import_map.json")


def main(verify_only=False):
    from aeis import Agent, EdgeType

    a = Agent(db_path=os.path.join(ROOT, "aeis", "data", "aeis_memory.db"))
    d = json.load(open(JSON_PATH, encoding="utf-8"))
    m = json.load(open(MAP_PATH, encoding="utf-8"))
    root_id = m["img_person"]

    # ---------- 验证段 ----------
    nodes = a.engine.store.traverse(root_id, relation_types=["hierarchical"],
                                    direction="in", max_depth=5)
    ids = [r["node_id"] for r in nodes] + [root_id]
    src_map = {v: k for k, v in m.items()}
    ok = len(nodes) >= 17
    print("回读可达:", len(nodes), "子节点 (+root =", len(ids), ")")
    print("判定:", "PASS" if ok else "FAIL")
    if verify_only:
        a.close()
        return 0 if ok else 1

    # ---------- 导入段（幂等护栏） ----------
    c = a.engine.store.conn.cursor()
    c.execute("SELECT COUNT(*) AS n FROM nodes WHERE tags LIKE '%dsh_nested_cg%'")
    have = c.fetchone()["n"]
    if have >= 18:
        print("已导入（dsh_nested_cg 节点", have, "个），跳过导入段")
        a.close()
        return 0 if ok else 1

    def flat(node, parent_src_id=None):
        cs = node.get("condition_space", {})
        coord = node.get("spatial_coordinates", {}).get("image2d", [0, 0])
        n = a.engine.add_perception(
            content=json.dumps({"semantic": node.get("content", {}).get("semantic", ""),
                                "color": node.get("content", {}).get("color", ""),
                                "source_img": cs.get("source_img", ""),
                                "layer": cs.get("layer", ""), "nested_cg": True},
                               ensure_ascii=False),
            modality="visual",
            spatial_coordinates={"image2d_x": float(coord[0]) if coord else 0.0,
                                 "image2d_y": float(coord[1]) if len(coord) > 1 else 0.0},
            importance=float(node.get("importance", 0.5)),
            tags=["dsh_nested_cg", "img:" + node["id"]],
            entities=[node["id"]], skip_dedup=True)
        imported[node["id"]] = n.id
        if parent_src_id:
            a.engine.add_edge(source_id=n.id, target_id=imported[parent_src_id],
                              relation_type=EdgeType.HIERARCHICAL, confidence=0.9,
                              source_evidence="dsh_nested_cg_part_of")
        for sub in node.get("subgraph", {}).get("nodes", []):
            flat(sub, node["id"])

    imported = {}
    flat(d["root"])
    json.dump(imported, open(MAP_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("导入节点:", len(imported))
    a.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(verify_only="--verify-only" in sys.argv))
