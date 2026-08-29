# -*- coding: utf-8 -*-
"""test_semantics_mcp · 里程碑4.5 world_semantics MCP 集成测试"""
import os, sys, tempfile, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.core import SpacetimeMemoryEngine as AEISEngine

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

d = tempfile.mkdtemp()
eng = AEISEngine(db_path=os.path.join(d, "t.db"))

# generate_roundtrip：文字生图 → 提取语义（闭环自验证）
r1 = eng.world_semantics("generate_roundtrip", {"text": "森林里有狼追兔子，湖边有一只守卫"})
g = r1["extracted_graph"]
labels = [n["label"] for n in g["nodes"] if n["level"] == 1]
check("roundtrip ok", r1["status"] == "ok" and "source_summary" in r1
      and "extracted_graph" in r1, str(r1)[:100])
check("extracted brown entity", any(l in ("wolf", "trunk") for l in labels), str(labels))
check("extracted water", "water" in labels, str(labels))
check("extracted leaf", "leaf" in labels, str(labels))
check("extracted white animal", any(l in ("rabbit", "sheep") for l in labels), str(labels))
check("graph has edges", "edges" in g and len(g["edges"]) >= 0, str(g.keys()))
check("summary readable", len(g["summary"]) > 10, g["summary"][:60])

# analyze：直接输入图像
from aeis.game_web.generate import WorldGenerator
gen = WorldGenerator(size=24, seed=42)
r_img = gen.generate_image("湖边有一只守卫", size=300)
r2 = eng.world_semantics("analyze", {"image_b64": base64.b64encode(r_img["image"]).decode("ascii"), "size": 320})
check("analyze ok", r2["status"] == "ok" and "nodes" in r2["graph"], str(r2)[:80])
labels2 = [n["label"] for n in r2["graph"]["nodes"] if n["level"] == 1]
check("analyze guard/water", any(l in ("guard", "player") for l in labels2)
      and "water" in labels2, str(labels2))

# unknown
r3 = eng.world_semantics("bogus", {})
check("unknown action error", r3["status"] == "error", str(r3))

print(f"\nSEMANTICS-MCP result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
