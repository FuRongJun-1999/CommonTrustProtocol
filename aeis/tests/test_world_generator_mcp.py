# -*- coding: utf-8 -*-
"""test_world_generator_mcp · 里程碑4.3 world_generator MCP 集成测试"""
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

# scene 场景解析
r1 = eng.world_generator("scene", {"text": "森林里有狼追兔子"})
check("scene ok", r1["status"] == "ok" and "spec" in r1["scene"]
      and len(r1["scene"]["spec"]["entities"]) == 2, str(r1))

# image 文字生图
r2 = eng.world_generator("image", {"text": "森林里有狼追兔子", "size": 320})
png = base64.b64decode(r2["image_b64"])
check("image ok", r2["status"] == "ok" and png[:8] == b"\x89PNG\r\n\x1a\n"
      and len(png) > 3000 and "summary" in r2, str(r2)[:120])
r2b = eng.world_generator("image", {"text": "森林里有狼追兔子", "size": 320})
check("image deterministic", r2["image_b64"] == r2b["image_b64"], "")

# video 文字生视频
r3 = eng.world_generator("video", {"text": "森林里狼追兔子", "ticks": 8, "fps": 4, "size": 240})
gif = base64.b64decode(r3["gif_b64"])
check("video ok", r3["status"] == "ok" and gif[:6] == b"GIF89a"
      and r3["frames"] == 8 and len(gif) > 2000, str(r3)[:120])

# save 存文件
r4 = eng.world_generator("save", {"text": "湖边有守卫巡逻", "kind": "image",
                                  "path": os.path.join(d, "gen")})
check("save image", r4["status"] == "ok" and os.path.isfile(r4["path"])
      and os.path.getsize(r4["path"]) > 3000, str(r4))
r5 = eng.world_generator("save", {"text": "湖边有守卫巡逻", "kind": "video",
                                  "path": os.path.join(d, "genv")})
check("save video", r5["status"] == "ok" and os.path.isfile(r5["path"])
      and os.path.getsize(r5["path"]) > 2000, str(r5))

# unknown
r6 = eng.world_generator("bogus", {})
check("unknown action error", r6["status"] == "error", str(r6))

print(f"\nWORLDGEN-MCP result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
