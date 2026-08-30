# -*- coding: utf-8 -*-
"""test_template_lib · 里程碑4.23 模板库（生成式自举闭环存储层）"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.template_lib import TemplateLibrary
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

tmp = tempfile.mkdtemp(prefix="tpl_test_")
lib = TemplateLibrary(root=tmp)

# 1. 登记模板（PIL 图 + 路径两种）
img = Image.new("RGB", (80, 80), (235, 215, 210))
d = ImageDraw.Draw(img)
d.rectangle([10, 10, 30, 30], fill=(40, 90, 220))     # 蓝块
d.rectangle([40, 10, 60, 30], fill=(200, 50, 40))     # 红块
e1 = lib.register(img=img, domain="test", prompt="blue and red blocks")
check("register via image", e1["id"].startswith("test_") and e1["image"],
      str(e1))
check("register label", e1["label"] != "", e1.get("label"))
# 路径方式
path = os.path.join(tmp, "src.png")
img.save(path)
e2 = lib.register(image_path=path, domain="test", prompt="from path")
check("register via path", e2["id"].startswith("test_"))
check("image file exists", os.path.isfile(os.path.join(tmp, e1["image"])))

# 2. 索引/查询
st = lib.stats()
check("stats", st["templates"] >= 2 and st["domains"].get("test", 0) >= 2,
      str(st))
hits = lib.search(e1["signature"])
check("search by signature", len(hits) >= 1, str(hits[:1]))
es = lib.entries(domain="test")
check("entries by domain", len(es) == 2, str(len(es)))

# 3. 持久化（新实例加载）
lib2 = TemplateLibrary(root=tmp)
check("persist reload", lib2.stats()["templates"] >= 2,
      str(lib2.stats()))
check("persist search", len(lib2.search(e1["signature"])) >= 1)

import shutil
shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
