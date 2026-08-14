#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉面 v1 回归测试（BODY-REV1 视觉 = 信息差处理）
====================================================
快速路线：locate（模板匹配，opencv→numpy 降级）/ diff（区域对比）
思考路线：visual_check（记忆预期 vs 实际，回写形成过去）
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from aeis.api import Agent  # noqa: E402

PASS = 0
TOTAL = 0


def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        print(f"  [FAIL] {name} {detail}")


def make_icon(size=64, color=(30, 144, 255)):
    """带纹理图标（对角条纹 → 匹配有判别力，模拟真实图标）。"""
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:, :] = color
    for i in range(size):
        for j in range(size):
            if (i + j) % 8 < 3:
                arr[i, j] = (255, 255, 255)
    return Image.fromarray(arr)


def make_screen(icon_pos=None, size=(800, 600)):
    arr = np.full((size[1], size[0], 3), 240, dtype=np.uint8)
    if icon_pos:
        x, y = icon_pos
        icon = np.array(make_icon())
        arr[y:y + 64, x:x + 64] = icon
    return Image.fromarray(arr)


def make_noise_icon(size=32, seed=7):
    """随机噪声图案（与图标结构无关 → 匹配必然低置信）。"""
    rng = np.random.default_rng(seed)
    arr = rng.integers(0, 256, (size, size, 3), dtype=np.uint8)
    return Image.fromarray(arr)


def test_locate():
    ws = tempfile.mkdtemp()
    screen = make_screen(icon_pos=(300, 200))
    screen.save(os.path.join(ws, "screen.png"))
    make_icon().save(os.path.join(ws, "icon.png"))
    make_noise_icon().save(os.path.join(ws, "absent.png"))

    a = Agent(identity="vision-locate", db_path=":memory:")
    r = a.device_call("screen", "locate", {
        "template": os.path.join(ws, "icon.png"),
        "screen": os.path.join(ws, "screen.png"), "threshold": 0.6})
    check("locate 精确命中", r["ok"] and r["data"]["found"]
          and r["data"]["x"] == 300 and r["data"]["y"] == 200,
          f"x={r['data'].get('x')} y={r['data'].get('y')} conf={r['data'].get('confidence')}")
    check("locate 方法", r["ok"] and r["data"]["method"] in ("opencv", "numpy"))
    check("locate 容器隔离", r["provenance"] == "device:screen" and r["is_directive"] is False)

    r2 = a.device_call("screen", "locate", {
        "template": os.path.join(ws, "absent.png"),
        "screen": os.path.join(ws, "screen.png"), "threshold": 0.6})
    check("locate 未找到拒绝", r2["ok"] and not r2["data"]["found"],
          f"best conf={r2['data'].get('confidence')}")

    r3 = a.device_call("screen", "locate", {"template": "no_such.png"})
    check("locate 缺模板拦截", not r3["ok"])


def test_diff():
    ws = tempfile.mkdtemp()
    base = make_screen(icon_pos=(300, 200))
    base.save(os.path.join(ws, "base.png"))
    changed = make_screen(icon_pos=(500, 150))  # 图标移动 = 变化
    changed.save(os.path.join(ws, "changed.png"))

    a = Agent(identity="vision-diff", db_path=":memory:")
    r = a.device_call("screen", "diff", {
        "reference": os.path.join(ws, "base.png"),
        "target": os.path.join(ws, "changed.png"), "block": 16})
    check("diff 检测变化", r["ok"] and r["data"]["changed"] is True,
          f"ratio={r['data'].get('change_ratio')} 区域={r['data'].get('region_count')}")
    check("diff 变化区域", r["ok"] and r["data"]["region_count"] >= 1)

    r2 = a.device_call("screen", "diff", {
        "reference": os.path.join(ws, "base.png"),
        "target": os.path.join(ws, "base.png")})
    check("diff 相同图无变化", r2["ok"] and r2["data"]["changed"] is False)


def test_visual_check_loop():
    """思考路线闭环：基线建立 → 记忆预期 → 对照 → 回写形成过去。"""
    ws = tempfile.mkdtemp()
    os.environ["AEIS_WORKSPACE"] = ws
    db = os.path.join(ws, "mem.db")
    a = Agent(identity="vision-loop", db_path=db)

    r1 = a.visual_check()
    check("首轮建立基线", r1["status"] == "ok" and r1.get("established") is True)

    results = a.search("屏幕状态", 5)
    found = [n for n, _ in results if "screen_state" in (n.tags or [])]
    check("基线写入记忆", len(found) >= 1, f"nodes={len(found)}")

    r2 = a.visual_check()
    check("记忆预期对照一致", r2["status"] == "ok" and r2.get("consistent") is True,
          f"ratio={r2.get('data', {}).get('change_ratio')}")
    check("对照回写记忆", r2["status"] == "ok")

    results3 = a.search("屏幕状态", 5)
    check("记忆持续累积", len([n for n, _ in results3 if "screen_state" in (n.tags or [])]) >= 2)


def test_mcp_visual_check():
    """MCP 层 visual_check 工具注册（41 工具）。"""
    import json
    import subprocess
    import sys as _sys

    env = {**_os_env(), "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.Popen(
        [_sys.executable, "-m", "aeis.mcp.server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        env=env, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def send(msg):
        """发送请求并读响应（带 id 的请求才有响应）。"""
        proc.stdin.write(json.dumps(msg).encode() + b"\n")
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())

    def notify(msg):
        """发送无响应通知（不读）。"""
        proc.stdin.write(json.dumps(msg).encode() + b"\n")
        proc.stdin.flush()

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "t", "version": "0"}}})
    notify({"jsonrpc": "2.0", "method": "notifications/initialized"})
    r = send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = [t["name"] for t in r["result"]["tools"]]
    check("MCP 41 工具", len(names) == 41, f"count={len(names)}")
    check("visual_check 已注册", "visual_check" in names)
    proc.stdin.close()
    proc.wait(timeout=10)


def _os_env():
    env = dict(os.environ)
    env.setdefault("AEIS_DB", ":memory:")
    env.setdefault("AEIS_IDENTITY", "mcp-test")
    return env


def main():
    test_locate()
    test_diff()
    test_visual_check_loop()
    test_mcp_visual_check()
    print(f"\n===== 视觉面 v1 回归: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
