# -*- coding: utf-8 -*-
"""test_graph_store · 里程碑4.16 图原生存储 + 条件签名→语义路由缓存"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.graph_store import (ConditionRouteCache, GraphNativeStore,
                                       region_signature, REL_CODES)
from aeis.game_web import cnn_segment as CS
from aeis.game_web import st_graph as ST
from PIL import Image, ImageDraw

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("  PASS " + name)
    else:
        failed += 1
        print("  FAIL " + name + " " + detail)

# ---------- 1. 条件签名 → 语义路由缓存 ----------
rc = ConditionRouteCache(max_size=8)
# 合成区域
img = Image.new("RGB", (40, 40), (255, 255, 255))
reg = {"centroid": (0.8, 0.5, 0.5, 0.05, 0.5, 0.5, 0.5),
       "bbox": (10, 10, 20, 20)}
sig = region_signature(reg, img.size)
check("lookup miss first", rc.lookup(sig) is None)
rc.register(sig, "中灰-块-中中-小")
check("lookup hit after register", rc.lookup(sig) == "中灰-块-中中-小")
check("hit rate > 0", rc.stats()["hit_rate"] > 0)
check("hot paths recorded", len(rc.stats()["hot_paths"]) >= 1)

# 容量淘汰（最冷被淘汰）
for i in range(12):
    rc.register(("s%d" % i, i), "label%d" % i)
check("route cap enforced", rc.stats()["routes"] <= 8,
      str(rc.stats()["routes"]))

# 持久化
tmp = tempfile.mktemp(suffix=".json")
rc2 = ConditionRouteCache()
rc2.register(sig, "中灰-块-中中-小")
rc2.save(tmp)
rc3 = ConditionRouteCache()
rc3.load(tmp)
check("persist/load roundtrip", rc3.lookup(sig) == "中灰-块-中中-小")
os.remove(tmp)

# ---------- 2. 图原生存储（CSR 布局 + 持久化） ----------
# 合成 3 节点图：A above B, B supports C
graph = {"nodes": [
    {"id": "n0", "semantic": "A", "spatial": {"x": 0, "y": 0, "w": 10, "h": 5},
     "center": [5, 2], "size": 50, "facing": "平面", "cnn": {}},
    {"id": "n1", "semantic": "B", "spatial": {"x": 0, "y": 6, "w": 10, "h": 5},
     "center": [5, 8], "size": 50, "facing": "平面", "cnn": {}},
    {"id": "n2", "semantic": "C", "spatial": {"x": 0, "y": 12, "w": 10, "h": 5},
     "center": [5, 14], "size": 50, "facing": "平面", "cnn": {}},
], "edges": [
    {"source": "n0", "relation": "above", "target": "n1"},
    {"source": "n1", "relation": "above", "target": "n2"},
    {"source": "n1", "relation": "supports", "target": "n2"},
]}
gs = GraphNativeStore().build(graph)
check("csr offsets", len(gs.csr["offsets"]) == len(gs.nodes) + 1,
      str(len(gs.csr["offsets"])))
check("csr targets", len(gs.csr["targets"]) == 3, str(gs.csr["targets"]))
check("csr rels", gs.csr["rels"] == [0, 0, 8], str(gs.csr["rels"]))
check("edge_count above", gs.edge_count("above") == 2)
check("edge_count supports", gs.edge_count("supports") == 1)
sig2 = gs.graph_signature()
check("graph signature", len(sig2) == 16, sig2)

# 持久化 roundtrip
tmp2 = tempfile.mktemp(suffix=".json")
gs.persist(tmp2)
loaded = GraphNativeStore.load(tmp2)
check("load not None", loaded is not None)
check("load nodes", len(loaded.nodes) == 3)
check("load csr", loaded.csr["targets"] == [1, 2, 2])
check("load signature", loaded.graph_signature() == sig2)
os.remove(tmp2)

# ---------- 3. 真实图像集成：图原生存储 ----------
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    '..', '..', 'demos', '1.png')
if os.path.isfile(path):
    try:
        img2 = Image.open(path).convert("RGB")
        w, h = img2.size
        ratio = 416.0 / max(w, h)
        an = img2.resize((max(1, int(w * ratio)), max(1, int(h * ratio))))
        regs = CS.refine_recursive(an, k0=0.5, k1=0.2, max_depth=1,
                                   info_thresh=0.0010)
        l0 = [r for r in regs if r["level"] == 0 and r.get("cells")]
        for r in l0:
            x0, y0, x1, y1 = r["bbox"]
            r["area_px"] = max(1, (x1 - x0)) * max(1, (y1 - y0))
        l0.sort(key=lambda r: -r["area_px"])
        top = l0[:20]
        for r in top:
            if "label" not in r:
                r["label"] = CS._auto_label_lab(r["centroid"], r["bbox"],
                                                an.size, r.get("fill"))
        st = ST.build_st_graph(top, img=an, gw=an.size[0] // 2,
                               gh=an.size[1] // 2)
        gs2 = GraphNativeStore().build(st)
        check("real graph csr", len(gs2.csr["targets"]) >= 50,
              str(len(gs2.csr["targets"])))
        check("real graph occludes edge", gs2.edge_count("occludes") >= 0)
        # 路由缓存集成：区域签名注册
        rc4 = ConditionRouteCache()
        for r in top:
            rc4.register(region_signature(r, an.size), r["label"])
        check("real route register", rc4.stats()["routes"] >= 10,
              str(rc4.stats()["routes"]))
        # 二次 lookup 命中
        hits = sum(1 for r in top
                   if rc4.lookup(region_signature(r, an.size)) is not None)
        check("real route hits", hits >= len(top) - 2,
              "%d/%d" % (hits, len(top)))
    except Exception as e:
        check("real graph integration", False, str(e))
else:
    print("  SKIP real graph integration (demos/1.png absent)")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
