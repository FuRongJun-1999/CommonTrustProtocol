# -*- coding: utf-8 -*-
"""test_semantics_web · 里程碑4.9 语义分割可视化网页测试"""
import os, sys, json, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.semantics_web import SemanticWebServer
from aeis.game_web.character_render import render_steps

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ---------- 1. 服务器初始化（加载 1.png） ----------
sw = SemanticWebServer(image_path=r"D:\Program Files\2_ai\demos\1.png", size=320, display=420)
check("decomp loaded", sw._decomp is not None and sw._decomp.get("person"), "")

# ---------- 2. 语义区域（一个语义 → 原图对应内容） ----------
seg = sw.segment()
check("regions non-empty", len(seg["regions"]) >= 4, str(len(seg["regions"])))
sems = [r["semantic"] for r in seg["regions"]]
check("hair region", any("发" in s for s in sems), str(sems))
check("face region", "脸" in sems, str(sems))
check("bowtie region", "蝴蝶结" in sems, str(sems))
check("torso region", "躯干" in sems, str(sems))
check("region bbox valid", all(len(r["bbox"]) == 4 and r["bbox"][2] > r["bbox"][0]
                               for r in seg["regions"]), "")
check("region color", all("color" in r for r in seg["regions"]), "")
check("desc present", "分解描述" in seg.get("description", "") or len(seg["description"]) > 0, "")

# ---------- 3. 逐步重现（通过生成逐步重现） ----------
st = sw.steps()
check("steps count", len(st) == 7, str(len(st)))
sems2 = [s["semantic"] for s in st]
check("step order", sems2 == ["legs", "torso", "bowtie", "neck", "head", "face", "hair"],
      str(sems2))
check("step pngs", all(s["png"] and len(s["png"]) > 200 for s in st), "")
# 步骤递增：每步图应不同（逐步累积）
imgs = [len(s["png"]) for s in st]
check("steps grow", imgs[-1] >= imgs[0], str(imgs))

# ---------- 4. 递归语义结构树 ----------
gr = sw.graph()
tree = gr["tree"]
check("tree root 人物", tree["name"] == "人物", str(tree))
names = json.dumps(tree, ensure_ascii=False)
check("tree has 头部/躯干/双腿", "头部" in names and "躯干" in names
      and "双腿" in names, names[:200])
check("tree has spec", "spec" in gr and gr["spec"].get("hair_color") == "pink",
      str(gr.get("spec")))

# ---------- 5. 显示图 ----------
disp = sw.display_image()
check("display image", len(disp) > 1000, str(len(disp)))
from PIL import Image
im = Image.open(io.BytesIO(disp))
check("display aspect", max(im.size) <= 420, str(im.size))

print(f"\nSEMWEB result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
